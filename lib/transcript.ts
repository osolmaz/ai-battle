export type TranscriptPhase = "standard" | "sudden_death";
export type TranscriptEventType = "runner_prompt" | "runner_notice" | "agent_reply";
export type TranscriptSpeakerRole = "participant" | "judge" | "runner";

type JsonObject = Record<string, unknown>;

type ToolUseInput = {
  command?: string | unknown[];
  description?: string;
};

type ToolResult = {
  output?: unknown;
  content?: {
    Text?: unknown;
  };
};

type AgentMessagePart = {
  Text?: unknown;
  Thinking?: {
    text?: unknown;
  };
  ToolUse?: {
    id?: string;
    name?: string;
    input?: ToolUseInput;
    raw_input?: unknown;
  };
};

type AgentMessage = {
  content?: AgentMessagePart[];
  tool_results?: Record<string, ToolResult | undefined>;
};

export type TranscriptEvent = {
  eventId: string;
  turn: number;
  phase: TranscriptPhase;
  eventType: TranscriptEventType;
  speakerName: string;
  speakerRole: TranscriptSpeakerRole;
  recipientName: string;
  promptType?: string;
  promptEventId?: string;
  body: string;
  structuredData?: unknown;
};

export type TranscriptMeta = {
  matchId: string;
  participantAName: string;
  participantBName: string;
  judgeName: string;
  currentScore: string;
  latestCompletedTurn: number;
};

function formatPhaseLabel(phase: TranscriptPhase): string {
  return phase === "sudden_death" ? "sudden death" : "standard match";
}

function parseJsonObject(text: string): JsonObject | undefined {
  const trimmed = String(text ?? "").trim();
  if (!trimmed.startsWith("{") || !trimmed.endsWith("}")) {
    return undefined;
  }
  try {
    const parsed = JSON.parse(trimmed);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? (parsed as JsonObject)
      : undefined;
  } catch {
    return undefined;
  }
}

function fenced(code: string, info = ""): string {
  return `\`\`\`${info}\n${String(code ?? "").trimEnd()}\n\`\`\``;
}

function normalizeToolCommand(input: unknown): string | undefined {
  if (!input || typeof input !== "object") {
    return undefined;
  }
  const command = (input as ToolUseInput).command;
  if (typeof command === "string") {
    return command;
  }
  if (Array.isArray(command)) {
    return command.map((part) => String(part)).join(" ");
  }
  return undefined;
}

function normalizeToolDescription(part: AgentMessagePart): string | undefined {
  const input = part.ToolUse?.input;
  if (input && typeof input === "object" && typeof input.description === "string") {
    return input.description.trim();
  }
  const rawInput = part.ToolUse?.raw_input;
  if (typeof rawInput === "string") {
    try {
      const parsed = JSON.parse(rawInput) as ToolUseInput;
      if (parsed && typeof parsed.description === "string") {
        return parsed.description.trim();
      }
    } catch {
      // ignore invalid raw_input JSON
    }
  }
  const name = part.ToolUse?.name;
  if (typeof name === "string" && name.trim().length > 0) {
    return name.split("\n")[0]?.trim();
  }
  return undefined;
}

function normalizeToolResultText(result: ToolResult | undefined): string | undefined {
  if (!result || typeof result !== "object") {
    return undefined;
  }
  if (typeof result.output === "string" && result.output.trim() !== "") {
    return result.output.trim();
  }
  if (
    result.content &&
    typeof result.content === "object" &&
    typeof result.content.Text === "string" &&
    result.content.Text.trim() !== ""
  ) {
    return result.content.Text.trim();
  }
  return undefined;
}

function buildAgentReplyBody(agentMessage: AgentMessage): {
  body: string;
  structuredData?: JsonObject;
} {
  const lines: string[] = [];
  const content = Array.isArray(agentMessage?.content) ? agentMessage.content : [];
  const toolResults =
    agentMessage?.tool_results && typeof agentMessage.tool_results === "object"
      ? agentMessage.tool_results
      : {};
  let structuredData: JsonObject | undefined;

  for (const part of content) {
    if (part?.Text !== undefined) {
      const text = String(part.Text ?? "").trim();
      if (!text) {
        continue;
      }
      const maybeStructured = parseJsonObject(text);
      if (maybeStructured !== undefined) {
        structuredData = maybeStructured;
        lines.push("Visible reply:", "", fenced(text, "json"), "");
      } else {
        lines.push(text, "");
      }
      continue;
    }

    if (part?.Thinking) {
      const thinkingText = String(part.Thinking.text ?? "").trim();
      if (thinkingText) {
        lines.push("Thinking:", "", fenced(thinkingText, "text"), "");
      }
      continue;
    }

    if (part?.ToolUse) {
      const tool = part.ToolUse;
      const description = normalizeToolDescription(part);
      const command = normalizeToolCommand(tool.input) ?? normalizeToolCommand(tool.raw_input);
      lines.push(`Tool use: ${description ?? "tool call"}`, "");
      if (command) {
        lines.push(fenced(command, "sh"), "");
      }
      const resultText =
        typeof tool.id === "string" ? normalizeToolResultText(toolResults[tool.id]) : undefined;
      if (resultText) {
        lines.push("Tool result:", "", fenced(resultText, "text"), "");
      }
      continue;
    }
  }

  if (lines.length === 0) {
    lines.push("(no visible content)", "");
  }

  return {
    body: lines.join("\n").trimEnd(),
    structuredData,
  };
}

export function buildRunnerPromptEvent({
  eventId,
  turn,
  phase,
  recipientName,
  promptType,
  body,
}: {
  eventId: string;
  turn: number;
  phase: TranscriptPhase;
  recipientName: string;
  promptType?: string;
  body: string;
}): TranscriptEvent {
  return {
    eventId,
    turn,
    phase,
    eventType: "runner_prompt",
    speakerName: "match runner",
    speakerRole: "runner",
    recipientName,
    promptType,
    body: String(body ?? "").trim(),
  };
}

export function buildRunnerNoticeEvent({
  eventId,
  turn,
  phase,
  body,
  title,
  structuredData,
}: {
  eventId: string;
  turn: number;
  phase: TranscriptPhase;
  body: string;
  title: string;
  structuredData?: unknown;
}): TranscriptEvent {
  return {
    eventId,
    turn,
    phase,
    eventType: "runner_notice",
    speakerName: "match runner",
    speakerRole: "runner",
    recipientName: "all participants",
    promptType: title,
    body: String(body ?? "").trim(),
    structuredData,
  };
}

export function buildAgentReplyEvent({
  eventId,
  turn,
  phase,
  speakerName,
  speakerRole,
  promptEventId,
  promptType,
  agentMessage,
}: {
  eventId: string;
  turn: number;
  phase: TranscriptPhase;
  speakerName: string;
  speakerRole: Exclude<TranscriptSpeakerRole, "runner">;
  promptEventId?: string;
  promptType?: string;
  agentMessage: AgentMessage;
}): TranscriptEvent {
  const rendered = buildAgentReplyBody(agentMessage);
  return {
    eventId,
    turn,
    phase,
    eventType: "agent_reply",
    speakerName,
    speakerRole,
    recipientName: "match runner",
    promptEventId,
    promptType,
    body: rendered.body,
    ...(rendered.structuredData !== undefined ? { structuredData: rendered.structuredData } : {}),
  };
}

function renderEventHeading(event: TranscriptEvent): string {
  if (event.eventType === "runner_prompt") {
    return `match runner to ${event.recipientName}`;
  }
  if (event.eventType === "agent_reply") {
    return `${event.speakerName} to match runner`;
  }
  return "match runner";
}

function renderPromptTypeLine(event: TranscriptEvent): string | null {
  return event.promptType ? `Type: ${event.promptType}` : null;
}

export function renderTranscript(meta: TranscriptMeta, events: TranscriptEvent[]): string {
  const lines = [
    "# Transcript",
    "",
    `- Match ID: \`${meta.matchId}\``,
    `- Participant A: \`${meta.participantAName}\``,
    `- Participant B: \`${meta.participantBName}\``,
    `- Judge: \`${meta.judgeName}\``,
    `- Current score: \`${meta.currentScore}\``,
    `- Latest completed turn: \`${meta.latestCompletedTurn}\``,
    "",
    "This file is generated from runner prompts and ACP session replies.",
    "",
  ];

  if (!events.length) {
    lines.push("No transcript events have been recorded yet.", "");
    return `${lines.join("\n").trimEnd()}\n`;
  }

  const repliesByPrompt = new Map<string, TranscriptEvent[]>();
  for (const event of events) {
    if (event.eventType === "agent_reply" && event.promptEventId) {
      const existing = repliesByPrompt.get(event.promptEventId) ?? [];
      existing.push(event);
      repliesByPrompt.set(event.promptEventId, existing);
    }
  }

  let currentSection: string | null = null;
  const renderedReplies = new Set<string>();

  const ensureSection = (event: TranscriptEvent) => {
    const section =
      event.turn === 0 ? "setup" : `turn-${event.turn}-${event.phase ?? "standard"}`;
    if (section === currentSection) {
      return;
    }
    if (currentSection !== null) {
      lines.push("");
    }
    if (event.turn === 0) {
      lines.push("## Match Setup", "");
    } else {
      lines.push(`## Turn ${event.turn} (${formatPhaseLabel(event.phase)})`, "");
    }
    currentSection = section;
  };

  const renderSingleEvent = (event: TranscriptEvent) => {
    ensureSection(event);
    lines.push(`### ${renderEventHeading(event)}`, "");
    const promptTypeLine = renderPromptTypeLine(event);
    if (promptTypeLine) {
      lines.push(promptTypeLine, "");
    }
    lines.push(event.body, "");
    if (event.structuredData !== undefined) {
      lines.push(fenced(JSON.stringify(event.structuredData, null, 2), "json"), "");
    }
  };

  for (const event of events) {
    if (event.eventType === "agent_reply" && event.promptEventId) {
      continue;
    }
    renderSingleEvent(event);
    if (event.eventType === "runner_prompt") {
      const replies = repliesByPrompt.get(event.eventId) ?? [];
      for (const reply of replies) {
        renderedReplies.add(reply.eventId);
        renderSingleEvent(reply);
      }
    }
  }

  for (const event of events) {
    if (event.eventType !== "agent_reply" || renderedReplies.has(event.eventId)) {
      continue;
    }
    renderSingleEvent(event);
  }

  return `${lines.join("\n").trimEnd()}\n`;
}
