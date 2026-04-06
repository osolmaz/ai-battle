import { randomUUID } from "node:crypto";
import { realpathSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

type AcpRuntimeHandle = {
  sessionKey: string;
  backend: string;
  runtimeSessionName: string;
  cwd?: string;
  acpxRecordId?: string;
  backendSessionId?: string;
  agentSessionId?: string;
};

type AcpRuntimeEvent =
  | {
      type: "text_delta";
      text: string;
      stream?: "output" | "thought";
    }
  | {
      type: "done";
      stopReason?: string;
    }
  | {
      type: "error";
      message: string;
      code?: string;
      retryable?: boolean;
    }
  | {
      type: "status" | "tool_call";
      text: string;
    };

type AcpRuntime = {
  ensureSession(input: {
    sessionKey: string;
    agent: string;
    mode: "persistent" | "oneshot";
    cwd?: string;
  }): Promise<AcpRuntimeHandle>;
  runTurn(input: {
    handle: AcpRuntimeHandle;
    text: string;
    mode: "prompt" | "steer";
    requestId: string;
    timeoutMs?: number;
    signal?: AbortSignal;
  }): AsyncIterable<AcpRuntimeEvent>;
  cancel(input: { handle: AcpRuntimeHandle; reason?: string }): Promise<void>;
};

type RuntimeModule = {
  createAcpRuntime: (options: {
    cwd: string;
    sessionStore: unknown;
    agentRegistry: unknown;
    permissionMode: "approve-all";
  }) => AcpRuntime;
  createAgentRegistry: () => unknown;
  createFileSessionStore?: (options: { stateDir: string }) => unknown;
  createRuntimeStore?: (options: { stateDir: string }) => unknown;
};

type PendingInformationalPrompt = {
  controller: AbortController;
  completion: Promise<void>;
};

export type AcpxBattleSessionTarget = {
  profile: string;
  workspaceDir: string;
  sessionName: string;
};

export type AgentPromptResult = {
  rawText: string;
  timedOut: boolean;
  retryable: boolean;
  errorMessage?: string;
};

export type AcpxBattleRuntime = {
  ensureSession(target: AcpxBattleSessionTarget): Promise<void>;
  prompt(
    target: AcpxBattleSessionTarget,
    options: { prompt: string; timeoutMs: number },
  ): Promise<AgentPromptResult>;
  queueNotice(
    target: AcpxBattleSessionTarget,
    options: { prompt: string; timeoutMs: number },
  ): Promise<void>;
  cancelPrompt(target: AcpxBattleSessionTarget, reason?: string): Promise<void>;
  getSessionRecordPath(sessionName: string): string | undefined;
};

function resolveAcpxRuntimeModulePath(): string {
  const cliEntry = process.argv[1];
  if (!cliEntry) {
    throw new Error("Unable to resolve the acpx runtime module from process.argv[1].");
  }

  const resolvedCliEntry = realpathSync(path.resolve(cliEntry));
  if (/\.(cts|mts|ts|tsx)$/i.test(resolvedCliEntry)) {
    return path.resolve(path.dirname(resolvedCliEntry), "runtime.ts");
  }
  return path.resolve(path.dirname(resolvedCliEntry), "runtime.js");
}

async function loadRuntimeModule(): Promise<RuntimeModule> {
  try {
    const runtimeModulePath = resolveAcpxRuntimeModulePath();
    return (await import(pathToFileURL(runtimeModulePath).href)) as RuntimeModule;
  } catch {
    return (await import("acpx/runtime")) as RuntimeModule;
  }
}

function sessionRecordPathForHandle(stateDir: string, handle: AcpRuntimeHandle): string {
  const recordId = handle.acpxRecordId ?? handle.sessionKey;
  return path.join(stateDir, "sessions", `${encodeURIComponent(recordId)}.json`);
}

function summarizePromptRuntimeFailure(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export function createAcpxBattleRuntime(options: {
  cwd: string;
  stateDir: string;
  onInformationalPromptFailure?: (params: {
    sessionName: string;
    errorMessage: string;
  }) => void;
}): AcpxBattleRuntime {
  const runtimePromise = (async () => {
    const runtimeModule = await loadRuntimeModule();
    const createSessionStore =
      runtimeModule.createFileSessionStore ?? runtimeModule.createRuntimeStore;
    if (!createSessionStore) {
      throw new Error("The active acpx runtime module does not export a file-backed session store.");
    }

    return runtimeModule.createAcpRuntime({
      cwd: options.cwd,
      sessionStore: createSessionStore({ stateDir: options.stateDir }),
      agentRegistry: runtimeModule.createAgentRegistry(),
      permissionMode: "approve-all",
    });
  })();

  const runtimeSessionHandles = new Map<string, AcpRuntimeHandle>();
  const runtimeSessionRecordPaths = new Map<string, string>();
  const pendingInformationalPrompts = new Map<string, PendingInformationalPrompt>();

  async function getRuntime(): Promise<AcpRuntime> {
    return await runtimePromise;
  }

  async function ensureSession(target: AcpxBattleSessionTarget): Promise<AcpRuntimeHandle> {
    const cached = runtimeSessionHandles.get(target.sessionName);
    if (cached) {
      return cached;
    }

    const runtime = await getRuntime();
    const handle = await runtime.ensureSession({
      sessionKey: target.sessionName,
      agent: target.profile,
      mode: "persistent",
      cwd: target.workspaceDir,
    });
    runtimeSessionHandles.set(target.sessionName, handle);
    runtimeSessionRecordPaths.set(
      target.sessionName,
      sessionRecordPathForHandle(options.stateDir, handle),
    );
    return handle;
  }

  async function waitForPendingInformationalPrompt(sessionName: string): Promise<void> {
    const pending = pendingInformationalPrompts.get(sessionName);
    if (!pending) {
      return;
    }

    await pending.completion.catch(() => {
      // Best effort sequencing before the next prompt on this session.
    });
  }

  async function consumePrompt(options: {
    target: AcpxBattleSessionTarget;
    prompt: string;
    timeoutMs: number;
    signal?: AbortSignal;
  }): Promise<AgentPromptResult> {
    let rawText = "";
    let errorMessage: string | undefined;
    let timedOut = false;
    let retryable = false;
    let abortedByCaller = false;
    let abortedByTimeout = false;

    const runtime = await getRuntime();
    const handle = await ensureSession(options.target);
    const turnController = new AbortController();
    const onCallerAbort = () => {
      abortedByCaller = true;
      turnController.abort();
    };
    const timeoutHandle = setTimeout(() => {
      abortedByTimeout = true;
      turnController.abort();
    }, options.timeoutMs);

    if (options.signal) {
      if (options.signal.aborted) {
        onCallerAbort();
      } else {
        options.signal.addEventListener("abort", onCallerAbort, { once: true });
      }
    }

    try {
      for await (const event of runtime.runTurn({
        handle,
        text: options.prompt,
        mode: "prompt",
        requestId: randomUUID(),
        timeoutMs: options.timeoutMs,
        signal: turnController.signal,
      })) {
        if (event.type === "text_delta" && event.stream !== "thought") {
          rawText += event.text;
          continue;
        }
        if (event.type === "error") {
          errorMessage = event.message;
          timedOut = timedOut || event.code === "TIMEOUT";
          retryable = retryable || event.retryable === true;
        }
      }
    } catch (error) {
      if (!abortedByCaller && !abortedByTimeout) {
        throw error;
      }
    } finally {
      clearTimeout(timeoutHandle);
      options.signal?.removeEventListener("abort", onCallerAbort);
    }

    if (abortedByTimeout) {
      timedOut = true;
    }

    if (timedOut && !errorMessage) {
      errorMessage = `timed out after ${Math.round(options.timeoutMs / 1000)} seconds`;
    }

    if (abortedByCaller && !abortedByTimeout && !timedOut && !errorMessage) {
      return {
        rawText: rawText.trim(),
        timedOut: false,
        retryable: false,
      };
    }

    return {
      rawText: rawText.trim(),
      timedOut,
      retryable,
      errorMessage,
    };
  }

  return {
    async ensureSession(target) {
      await ensureSession(target);
    },

    async prompt(target, promptOptions) {
      await waitForPendingInformationalPrompt(target.sessionName);
      return await consumePrompt({
        target,
        prompt: promptOptions.prompt,
        timeoutMs: promptOptions.timeoutMs,
      });
    },

    async queueNotice(target, promptOptions) {
      await waitForPendingInformationalPrompt(target.sessionName);
      await ensureSession(target);

      const controller = new AbortController();
      const completion = (async () => {
        try {
          const result = await consumePrompt({
            target,
            prompt: promptOptions.prompt,
            timeoutMs: promptOptions.timeoutMs,
            signal: controller.signal,
          });
          if (result.errorMessage && !controller.signal.aborted) {
            options.onInformationalPromptFailure?.({
              sessionName: target.sessionName,
              errorMessage: result.errorMessage,
            });
          }
        } catch (error) {
          if (!controller.signal.aborted) {
            options.onInformationalPromptFailure?.({
              sessionName: target.sessionName,
              errorMessage: summarizePromptRuntimeFailure(error),
            });
          }
        } finally {
          const pending = pendingInformationalPrompts.get(target.sessionName);
          if (pending?.completion === completion) {
            pendingInformationalPrompts.delete(target.sessionName);
          }
        }
      })();

      pendingInformationalPrompts.set(target.sessionName, {
        controller,
        completion,
      });
    },

    async cancelPrompt(target, reason) {
      const runtime = await getRuntime();
      const handle = await ensureSession(target);
      await runtime.cancel({
        handle,
        reason,
      });
    },

    getSessionRecordPath(sessionName) {
      return runtimeSessionRecordPaths.get(sessionName);
    },
  };
}
