import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { action, compute, defineFlow, extractJsonObject } from "acpx/flows";
import {
  buildAgentReplyEvent,
  buildRunnerNoticeEvent,
  buildRunnerPromptEvent,
  renderTranscript,
} from "../lib/transcript.ts";

type AiBattleInput = {
  battleRepo?: string;
  rulesPath?: string;
  scratchRoot?: string;
  participantAName?: string;
  participantBName?: string;
  judgeName?: string;
  questionCount?: number;
  suddenDeathQuestionCount?: number;
  startingParticipant?: MatchRole;
};

type MatchRole = "participant_a" | "participant_b";
type MatchPhase = "standard" | "sudden_death";
type TranscriptTarget = MatchRole | "judge";

type JudgeNote = {
  intendedAnswer: string;
  validityReason: string;
  edgeReason: string;
  evidencePaths?: string[];
};

type AskResponse = {
  publicQuestion: string;
  judgeNote: JudgeNote;
};

type AnswerResponse = {
  answer: string;
  flawClaim?: string | null;
  artifactPaths?: string[];
};

type JudgedOutcome = "answerer_point" | "asker_point" | "flawed_caught" | "flawed_missed";
type AutomaticOutcome = "asker_forfeit" | "answerer_forfeit";
type TurnOutcome = JudgedOutcome | AutomaticOutcome;

type JudgeResponse = {
  outcome: JudgedOutcome;
  reason: string;
};

type ScoreState = {
  participantA: number;
  participantB: number;
};

type RulingSummary = {
  turn: number;
  phase: MatchPhase;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  outcome: TurnOutcome;
  reason: string;
  askerDelta: number;
  answererDelta: number;
  updatedScores: ScoreState;
};

type TurnRecord = {
  turn: number;
  phase: MatchPhase;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  questionPath: string;
  questionJsonPath: string;
  judgeNotePath: string;
  answerPath: string;
  answerJsonPath: string;
  rulingPath: string;
  rulingJsonPath: string;
  outcome: TurnOutcome;
  reason: string;
  askerDelta: number;
  answererDelta: number;
  updatedScores: ScoreState;
};

type MatchMessageEventType = "runner_prompt" | "agent_reply" | "runner_notice";

type MatchMessageEvent = {
  eventId: string;
  turn: number;
  phase: MatchPhase;
  speakerName: string;
  speakerRole: "participant" | "judge" | "runner";
  recipientName: string;
  eventType: MatchMessageEventType;
  promptType?: string;
  promptEventId?: string;
  body: string;
  structuredData?: unknown;
};

type PendingTranscriptPrompt = {
  promptEventId: string;
  turn: number;
  phase: MatchPhase;
  promptType: string;
  recipientName: string;
};

type SessionTranscriptTracker = {
  processedMessageCount: number;
  pendingPrompts: PendingTranscriptPrompt[];
  sessionRecordPath?: string;
};

type MatchState = {
  battleRepo: string;
  rulesPath: string;
  rulesText: string;
  scratchRoot: string;
  scratchMatchDir: string;
  participantAWorkspaceDir: string;
  participantBWorkspaceDir: string;
  judgeWorkspaceDir: string;
  matchId: string;
  matchDir: string;
  manifestPath: string;
  transcriptPath: string;
  messageLogPath: string;
  participantAName: string;
  participantBName: string;
  judgeName: string;
  participantAAgentCommand: string;
  participantBAgentCommand: string;
  judgeAgentCommand: string;
  participantASessionName: string;
  participantBSessionName: string;
  judgeSessionName: string;
  participantAFileStem: string;
  participantBFileStem: string;
  judgeFileStem: string;
  questionCount: number;
  suddenDeathQuestionCount: number;
  standardTurns: number;
  suddenDeathTurns: number;
  totalTurnsScheduled: number;
  currentTurn: number;
  phase: MatchPhase;
  turnLimit: number;
  startingParticipant: MatchRole;
  scores: ScoreState;
  latestRuling: RulingSummary | null;
  history: TurnRecord[];
  nextTranscriptEventId: number;
  participantATranscript: SessionTranscriptTracker;
  participantBTranscript: SessionTranscriptTracker;
  judgeTranscript: SessionTranscriptTracker;
};

type PreparedMatch = MatchState;

type TurnSelection = {
  route: "ask_participant_a" | "ask_participant_b" | "write_final_scoreboard";
  state: MatchState;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  turnDir: string;
};

type WrittenQuestion = {
  route: "answer_participant_a" | "answer_participant_b";
  state: MatchState;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  turnDir: string;
  publicQuestion: string;
  judgeNote: JudgeNote;
  questionPath: string;
  questionJsonPath: string;
  judgeNotePath: string;
};

type WrittenAnswer = {
  state: MatchState;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  turnDir: string;
  publicQuestion: string;
  judgeNote: JudgeNote;
  answer: string;
  flawClaim: string | null;
  artifactPaths: string[];
  questionPath: string;
  questionJsonPath: string;
  judgeNotePath: string;
  answerPath: string;
  answerJsonPath: string;
};

type WrittenRuling = {
  state: MatchState;
  turn: number;
  phase: MatchPhase;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  outcome: TurnOutcome;
  reason: string;
  askerDelta: number;
  answererDelta: number;
  rulingPath: string;
  rulingJsonPath: string;
  questionPath: string;
  questionJsonPath: string;
  judgeNotePath: string;
  answerPath: string;
  answerJsonPath: string;
};

type AskTurnActionResult =
  | {
      route: "wait_participant_a" | "wait_participant_b";
      askResponse: AskResponse;
    }
  | {
      route: "write_ask_forfeit_turn";
      reason: string;
    };

type AnswerTurnActionResult =
  | {
      route: "write_answer";
      answerResponse: AnswerResponse;
    }
  | {
      route: "write_answer_forfeit_turn";
      reason: string;
    };

type ParticipantPromptSuccess<T> = {
  ok: true;
  value: T;
};

type ParticipantPromptFailure = {
  ok: false;
  reason: string;
};

type ParticipantPromptResult<T> = ParticipantPromptSuccess<T> | ParticipantPromptFailure;

const PARTICIPANT_TURN_TIMEOUT_MS = 30 * 60_000;
const PARTICIPANT_GRACE_TIMEOUT_MS = 60_000;
const BRIEFING_TIMEOUT_MS = 20 * 60_000;
const JUDGE_TIMEOUT_MS = 20 * 60_000;
const SHORT_ACK_TIMEOUT_MS = 10 * 60_000;
const PARTICIPANT_ACTION_TIMEOUT_MS =
  PARTICIPANT_TURN_TIMEOUT_MS + PARTICIPANT_GRACE_TIMEOUT_MS + 120_000;

export default defineFlow({
  name: "ai-battle",
  permissions: {
    requiredMode: "approve-all",
    requireExplicitGrant: true,
    reason:
      "This flow writes official match files into the battle repository and creates isolated scratch directories for the participants and judge.",
  },
  startAt: "prepare_match",
  nodes: {
    prepare_match: action({
      statusDetail: "Create the match directory and snapshot the rules",
      run: async ({ input }) => await prepareMatch(loadBattleInput(input)),
    }),

    initialize_match: compute({
      run: ({ outputs }) => outputs.prepare_match,
    }),

    brief_participant_a: action({
      timeoutMs: BRIEFING_TIMEOUT_MS,
      statusDetail: "Send the rules to participant A",
      run: async ({ outputs }) => {
        const state = prepared(outputs);
        await sendParticipantInformationalPrompt(
          state,
          "participant_a",
          "rules briefing",
          participantBriefingPrompt(state, {
            role: "participant_a",
          }),
          0,
          "standard",
          BRIEFING_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    brief_participant_b: action({
      timeoutMs: BRIEFING_TIMEOUT_MS,
      statusDetail: "Send the rules to participant B",
      run: async ({ outputs }) => {
        const state = prepared(outputs);
        await sendParticipantInformationalPrompt(
          state,
          "participant_b",
          "rules briefing",
          participantBriefingPrompt(state, {
            role: "participant_b",
          }),
          0,
          "standard",
          BRIEFING_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    brief_judge: action({
      timeoutMs: BRIEFING_TIMEOUT_MS,
      statusDetail: "Send the rules and judging rubric to the judge",
      run: async ({ outputs }) => {
        const state = prepared(outputs);
        await sendJudgeInformationalPrompt(
          state,
          "rules briefing",
          judgeBriefingPrompt(state),
          0,
          "standard",
          BRIEFING_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    choose_turn: compute({
      run: ({ outputs }) => chooseTurn(currentState(outputs)),
    }),

    ask_participant_a: action({
      timeoutMs: PARTICIPANT_ACTION_TIMEOUT_MS,
      statusDetail: "Ask participant A for the next question",
      run: async ({ outputs }) => await runAskTurn(currentTurn(outputs), "participant_a"),
    }),

    ask_participant_b: action({
      timeoutMs: PARTICIPANT_ACTION_TIMEOUT_MS,
      statusDetail: "Ask participant B for the next question",
      run: async ({ outputs }) => await runAskTurn(currentTurn(outputs), "participant_b"),
    }),

    wait_participant_a: action({
      timeoutMs: SHORT_ACK_TIMEOUT_MS,
      statusDetail: "Tell participant A to wait for the current turn",
      run: async ({ outputs }) => {
        const selection = currentTurn(outputs);
        await sendParticipantInformationalPrompt(
          selection.state,
          "participant_a",
          "wait notice",
          waitPrompt(selection, "participant_a"),
          selection.state.currentTurn,
          selection.state.phase,
          SHORT_ACK_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    wait_participant_b: action({
      timeoutMs: SHORT_ACK_TIMEOUT_MS,
      statusDetail: "Tell participant B to wait for the current turn",
      run: async ({ outputs }) => {
        const selection = currentTurn(outputs);
        await sendParticipantInformationalPrompt(
          selection.state,
          "participant_b",
          "wait notice",
          waitPrompt(selection, "participant_b"),
          selection.state.currentTurn,
          selection.state.phase,
          SHORT_ACK_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    write_question: action({
      statusDetail: "Write the public question and hidden judge note for the current turn",
      run: async ({ outputs }) => await writeQuestion(currentTurn(outputs), outputs),
    }),

    answer_participant_a: action({
      timeoutMs: PARTICIPANT_ACTION_TIMEOUT_MS,
      statusDetail: "Ask participant A to answer the current question",
      run: async ({ outputs }) => await runAnswerTurn(writtenQuestion(outputs), "participant_a"),
    }),

    answer_participant_b: action({
      timeoutMs: PARTICIPANT_ACTION_TIMEOUT_MS,
      statusDetail: "Ask participant B to answer the current question",
      run: async ({ outputs }) => await runAnswerTurn(writtenQuestion(outputs), "participant_b"),
    }),

    write_answer: action({
      statusDetail: "Write the answer for the current turn",
      run: async ({ outputs }) => await writeAnswer(writtenQuestion(outputs), outputs),
    }),

    write_ask_forfeit_turn: action({
      statusDetail: "Write the automatic ruling for a missed ask turn",
      run: async ({ outputs }) => await writeAskForfeitTurn(currentTurn(outputs), outputs),
    }),

    write_answer_forfeit_turn: action({
      statusDetail: "Write the automatic ruling for a missed answer turn",
      run: async ({ outputs }) => await writeAnswerForfeitTurn(writtenQuestion(outputs), outputs),
    }),

    judge_turn: action({
      timeoutMs: JUDGE_TIMEOUT_MS + PARTICIPANT_GRACE_TIMEOUT_MS + 60_000,
      statusDetail: "Ask the judge to rule on the completed turn",
      run: async ({ outputs }) => await runJudgeTurn(writtenAnswer(outputs)),
    }),

    write_ruling: action({
      statusDetail: "Write the judge ruling for the current turn",
      run: async ({ outputs }) => await writeRuling(writtenAnswer(outputs), outputs.judge_turn),
    }),

    select_ruling: compute({
      run: ({ outputs }) => selectWrittenRuling(outputs),
    }),

    notify_participant_a: action({
      timeoutMs: SHORT_ACK_TIMEOUT_MS,
      statusDetail: "Send the official ruling to participant A",
      run: async ({ outputs }) => {
        const ruling = writtenRuling(outputs);
        await sendParticipantInformationalPrompt(
          ruling.state,
          "participant_a",
          "ruling notice",
          rulingNotificationPrompt(ruling, "participant_a"),
          ruling.turn,
          ruling.phase,
          SHORT_ACK_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    notify_participant_b: action({
      timeoutMs: SHORT_ACK_TIMEOUT_MS,
      statusDetail: "Send the official ruling to participant B",
      run: async ({ outputs }) => {
        const ruling = writtenRuling(outputs);
        await sendParticipantInformationalPrompt(
          ruling.state,
          "participant_b",
          "ruling notice",
          rulingNotificationPrompt(ruling, "participant_b"),
          ruling.turn,
          ruling.phase,
          SHORT_ACK_TIMEOUT_MS,
        );
        return {
          acknowledged: true,
        };
      },
    }),

    advance_turn: action({
      statusDetail: "Advance the match state and update the manifest",
      run: async ({ outputs }) => await advanceTurn(currentState(outputs), writtenRuling(outputs)),
    }),

    write_final_scoreboard: action({
      statusDetail: "Write the final scoreboard and update the manifest",
      run: async ({ outputs }) => await writeFinalScoreboard(currentTurn(outputs).state),
    }),

    finalize: compute({
      run: ({ outputs }) => ({
        matchDir: outputs.write_final_scoreboard.matchDir,
        scoreboardPath: outputs.write_final_scoreboard.scoreboardPath,
        scores: outputs.write_final_scoreboard.scores,
        result: outputs.write_final_scoreboard.result,
        history: outputs.write_final_scoreboard.history,
      }),
    }),
  },
  edges: [
    { from: "prepare_match", to: "initialize_match" },
    { from: "initialize_match", to: "brief_participant_a" },
    { from: "brief_participant_a", to: "brief_participant_b" },
    { from: "brief_participant_b", to: "brief_judge" },
    { from: "brief_judge", to: "choose_turn" },
    {
      from: "choose_turn",
      switch: {
        on: "$.route",
        cases: {
          ask_participant_a: "ask_participant_a",
          ask_participant_b: "ask_participant_b",
          write_final_scoreboard: "write_final_scoreboard",
        },
      },
    },
    {
      from: "ask_participant_a",
      switch: {
        on: "$.route",
        cases: {
          wait_participant_b: "wait_participant_b",
          write_ask_forfeit_turn: "write_ask_forfeit_turn",
        },
      },
    },
    {
      from: "ask_participant_b",
      switch: {
        on: "$.route",
        cases: {
          wait_participant_a: "wait_participant_a",
          write_ask_forfeit_turn: "write_ask_forfeit_turn",
        },
      },
    },
    { from: "wait_participant_a", to: "write_question" },
    { from: "wait_participant_b", to: "write_question" },
    {
      from: "write_question",
      switch: {
        on: "$.route",
        cases: {
          answer_participant_a: "answer_participant_a",
          answer_participant_b: "answer_participant_b",
        },
      },
    },
    {
      from: "answer_participant_a",
      switch: {
        on: "$.route",
        cases: {
          write_answer: "write_answer",
          write_answer_forfeit_turn: "write_answer_forfeit_turn",
        },
      },
    },
    {
      from: "answer_participant_b",
      switch: {
        on: "$.route",
        cases: {
          write_answer: "write_answer",
          write_answer_forfeit_turn: "write_answer_forfeit_turn",
        },
      },
    },
    { from: "write_answer", to: "judge_turn" },
    { from: "judge_turn", to: "write_ruling" },
    { from: "write_ruling", to: "select_ruling" },
    { from: "write_ask_forfeit_turn", to: "select_ruling" },
    { from: "write_answer_forfeit_turn", to: "select_ruling" },
    { from: "select_ruling", to: "notify_participant_a" },
    { from: "notify_participant_a", to: "notify_participant_b" },
    { from: "notify_participant_b", to: "advance_turn" },
    { from: "advance_turn", to: "choose_turn" },
    { from: "write_final_scoreboard", to: "finalize" },
  ],
});

function loadBattleInput(input: unknown): AiBattleInput {
  return (input ?? {}) as AiBattleInput;
}

function prepared(outputs: Record<string, unknown>): PreparedMatch {
  return outputs.prepare_match as PreparedMatch;
}

function currentState(outputs: Record<string, unknown>): MatchState {
  return (outputs.advance_turn as MatchState | undefined) ?? prepared(outputs);
}

function currentTurn(outputs: Record<string, unknown>): TurnSelection {
  return outputs.choose_turn as TurnSelection;
}

function writtenQuestion(outputs: Record<string, unknown>): WrittenQuestion {
  return outputs.write_question as WrittenQuestion;
}

function writtenAnswer(outputs: Record<string, unknown>): WrittenAnswer {
  return outputs.write_answer as WrittenAnswer;
}

function writtenRuling(outputs: Record<string, unknown>): WrittenRuling {
  return outputs.select_ruling as WrittenRuling;
}

function askActionResult(raw: unknown): AskTurnActionResult {
  return raw as AskTurnActionResult;
}

function answerActionResult(raw: unknown): AnswerTurnActionResult {
  return raw as AnswerTurnActionResult;
}

function askResponseFromActionResult(raw: unknown): AskResponse {
  const result = askActionResult(raw);
  if (result.route === "write_ask_forfeit_turn") {
    throw new Error("Expected a valid ask response but received an automatic ask forfeit.");
  }
  return result.askResponse;
}

function answerResponseFromActionResult(raw: unknown): AnswerResponse {
  const result = answerActionResult(raw);
  if (result.route === "write_answer_forfeit_turn") {
    throw new Error("Expected a valid answer response but received an automatic answer forfeit.");
  }
  return result.answerResponse;
}

function selectWrittenRuling(outputs: Record<string, unknown>): WrittenRuling {
  const turn = currentTurn(outputs).state.currentTurn;
  const candidates = [
    outputs.write_ruling,
    outputs.write_ask_forfeit_turn,
    outputs.write_answer_forfeit_turn,
  ].filter((value): value is WrittenRuling => isWrittenRuling(value));

  const exactMatch = candidates.find((candidate) => candidate.turn === turn);
  if (exactMatch) {
    return exactMatch;
  }

  const latestMatch = candidates.sort((left, right) => right.turn - left.turn)[0];
  if (latestMatch) {
    return latestMatch;
  }

  throw new Error("No ruling output was produced for the current turn.");
}

function isWrittenRuling(value: unknown): value is WrittenRuling {
  return (
    typeof value === "object" &&
    value !== null &&
    "turn" in value &&
    typeof (value as { turn?: unknown }).turn === "number" &&
    "outcome" in value &&
    typeof (value as { outcome?: unknown }).outcome === "string"
  );
}

function createSessionTranscriptTracker(): SessionTranscriptTracker {
  return {
    processedMessageCount: 0,
    pendingPrompts: [],
  };
}

async function prepareMatch(input: AiBattleInput): Promise<PreparedMatch> {
  const battleRepo = path.resolve(input.battleRepo ?? process.cwd());
  const scratchRoot = resolveScratchRoot(input.scratchRoot);
  const agentCommands = await loadAgentCommands(battleRepo);
  const participantAName = input.participantAName?.trim() || "participant-a";
  const participantBName = input.participantBName?.trim() || "participant-b";
  const judgeName = input.judgeName?.trim() || "judge";
  const participantAFileStem = sanitizeNameForPath(participantAName);
  const participantBFileStem = sanitizeNameForPath(participantBName);
  const judgeFileStem = sanitizeNameForPath(judgeName);
  const rulesPath = path.resolve(input.rulesPath ?? path.join(battleRepo, "AGENTS.md"));
  const rulesText = await fs.readFile(rulesPath, "utf8");
  const questionCount = normalizePositiveInteger(input.questionCount, 10, "questionCount");
  const suddenDeathQuestionCount = normalizeNonNegativeInteger(
    input.suddenDeathQuestionCount,
    3,
    "suddenDeathQuestionCount",
  );
  const standardTurns = questionCount * 2;
  const suddenDeathTurns = suddenDeathQuestionCount * 2;
  const startingParticipant = normalizeStartingParticipant(input.startingParticipant);
  const sessionsDir = path.join(battleRepo, "sessions");
  const matchId = await createUniqueMatchId(
    sessionsDir,
    participantAFileStem,
    participantBFileStem,
  );
  const matchDir = path.join(sessionsDir, matchId);
  const manifestPath = path.join(matchDir, "manifest.md");
  const transcriptPath = path.join(matchDir, "transcript.md");
  const messageLogPath = path.join(matchDir, "messages.jsonl");
  const scratchMatchDir = path.join(scratchRoot, matchId);
  const participantAWorkspaceDir = path.join(scratchMatchDir, "participant-a");
  const participantBWorkspaceDir = path.join(scratchMatchDir, "participant-b");
  const judgeWorkspaceDir = path.join(scratchMatchDir, "judge");
  const participantASessionName = `${matchId}-participant-a`;
  const participantBSessionName = `${matchId}-participant-b`;
  const judgeSessionName = `${matchId}-judge`;

  await fs.mkdir(matchDir, { recursive: true });
  await fs.mkdir(participantAWorkspaceDir, { recursive: true });
  await fs.mkdir(participantBWorkspaceDir, { recursive: true });
  await fs.mkdir(judgeWorkspaceDir, { recursive: true });
  await fs.writeFile(path.join(matchDir, "rules.md"), rulesText, "utf8");

  const initialState: PreparedMatch = {
    battleRepo,
    rulesPath,
    rulesText,
    scratchRoot,
    scratchMatchDir,
    participantAWorkspaceDir,
    participantBWorkspaceDir,
    judgeWorkspaceDir,
    matchId,
    matchDir,
    manifestPath,
    transcriptPath,
    messageLogPath,
    participantAName,
    participantBName,
    judgeName,
    participantAAgentCommand: agentCommands.participantAAgentCommand,
    participantBAgentCommand: agentCommands.participantBAgentCommand,
    judgeAgentCommand: agentCommands.judgeAgentCommand,
    participantASessionName,
    participantBSessionName,
    judgeSessionName,
    participantAFileStem,
    participantBFileStem,
    judgeFileStem,
    questionCount,
    suddenDeathQuestionCount,
    standardTurns,
    suddenDeathTurns,
    totalTurnsScheduled: standardTurns + suddenDeathTurns,
    currentTurn: 1,
    phase: "standard",
    turnLimit: standardTurns,
    startingParticipant,
    scores: {
      participantA: 0,
      participantB: 0,
    },
    latestRuling: null,
    history: [],
    nextTranscriptEventId: 1,
    participantATranscript: createSessionTranscriptTracker(),
    participantBTranscript: createSessionTranscriptTracker(),
    judgeTranscript: createSessionTranscriptTracker(),
  };

  await fs.writeFile(manifestPath, renderManifest(initialState), "utf8");
  await initializeMessageArchive(initialState);
  return initialState;
}

function resolveScratchRoot(value: string | undefined): string {
  const trimmed = value?.trim();
  if (!trimmed) {
    return path.join(os.homedir(), "ai-battle");
  }
  if (trimmed === "~") {
    return os.homedir();
  }
  if (trimmed.startsWith("~/")) {
    return path.join(os.homedir(), trimmed.slice(2));
  }
  return path.resolve(trimmed);
}

async function createUniqueMatchId(
  sessionsDir: string,
  participantAFileStem: string,
  participantBFileStem: string,
): Promise<string> {
  await fs.mkdir(sessionsDir, { recursive: true });
  const stamp = formatMatchStamp(new Date());
  const base = `${stamp}-${participantAFileStem}-vs-${participantBFileStem}`;
  const existing = new Set(await fs.readdir(sessionsDir).catch(() => []));
  if (!existing.has(base)) {
    return base;
  }
  return `${base}-${Math.random().toString(36).slice(2, 8)}`;
}

function normalizePositiveInteger(
  value: number | undefined,
  defaultValue: number,
  fieldName: string,
): number {
  if (value === undefined) {
    return defaultValue;
  }
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`${fieldName} must be a positive integer, got ${JSON.stringify(value)}`);
  }
  return value;
}

function normalizeNonNegativeInteger(
  value: number | undefined,
  defaultValue: number,
  fieldName: string,
): number {
  if (value === undefined) {
    return defaultValue;
  }
  if (!Number.isInteger(value) || value < 0) {
    throw new Error(`${fieldName} must be a non-negative integer, got ${JSON.stringify(value)}`);
  }
  return value;
}

function normalizeStartingParticipant(value: MatchRole | undefined): MatchRole {
  if (value === undefined) {
    return "participant_a";
  }
  if (value !== "participant_a" && value !== "participant_b") {
    throw new Error(`startingParticipant must be "participant_a" or "participant_b".`);
  }
  return value;
}

function chooseTurn(state: MatchState): TurnSelection {
  if (state.currentTurn > state.turnLimit) {
    return {
      route: "write_final_scoreboard",
      state,
      askerRole: "participant_a",
      answererRole: "participant_b",
      askerName: state.participantAName,
      answererName: state.participantBName,
      turnDir: path.join(state.matchDir, formatTurnDir(state.currentTurn)),
    };
  }

  const askerRole = roleForTurn(state.currentTurn, state.startingParticipant);
  const answererRole = otherRole(askerRole);
  return {
    route: askerRole === "participant_a" ? "ask_participant_a" : "ask_participant_b",
    state,
    askerRole,
    answererRole,
    askerName: nameForRole(state, askerRole),
    answererName: nameForRole(state, answererRole),
    turnDir: path.join(state.matchDir, formatTurnDir(state.currentTurn)),
  };
}

async function loadAgentCommands(battleRepo: string): Promise<{
  participantAAgentCommand: string;
  participantBAgentCommand: string;
  judgeAgentCommand: string;
}> {
  const configPath = path.join(battleRepo, ".acpxrc.json");
  let rawConfig: string;
  try {
    rawConfig = await fs.readFile(configPath, "utf8");
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "ENOENT") {
      throw new Error(`Missing .acpxrc.json in battle repo: ${configPath}`);
    }
    throw error;
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(rawConfig);
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new Error(`Invalid JSON in ${configPath}: ${reason}`);
  }

  const agents = asObject(parsed)?.agents;
  const participantAAgentCommand = readAgentCommandFromConfig(agents, "participant-a", configPath);
  const participantBAgentCommand = readAgentCommandFromConfig(agents, "participant-b", configPath);
  const judgeAgentCommand = readAgentCommandFromConfig(agents, "judge", configPath);
  return {
    participantAAgentCommand,
    participantBAgentCommand,
    judgeAgentCommand,
  };
}

async function runAskTurn(
  selection: TurnSelection,
  expectedRole: MatchRole,
): Promise<AskTurnActionResult> {
  if (selection.askerRole !== expectedRole) {
    throw new Error(`Expected ${expectedRole} to ask on turn ${selection.state.currentTurn}.`);
  }

  const result = await sendParticipantStructuredPrompt(
    selection.state,
    selection.askerRole,
    askPrompt(selection),
    askGracePrompt(selection),
    normalizeAskResponse,
    "question",
  );

  if (result.ok) {
    return {
      route:
        selection.answererRole === "participant_a" ? "wait_participant_a" : "wait_participant_b",
      askResponse: result.value,
    };
  }

  return {
    route: "write_ask_forfeit_turn",
    reason: result.reason,
  };
}

async function runAnswerTurn(
  turn: WrittenQuestion,
  expectedRole: MatchRole,
): Promise<AnswerTurnActionResult> {
  if (turn.answererRole !== expectedRole) {
    throw new Error(`Expected ${expectedRole} to answer on turn ${turn.state.currentTurn}.`);
  }

  const result = await sendParticipantStructuredPrompt(
    turn.state,
    turn.answererRole,
    answerPrompt(turn),
    answerGracePrompt(turn),
    normalizeAnswerResponse,
    "answer",
  );

  if (result.ok) {
    return {
      route: "write_answer",
      answerResponse: result.value,
    };
  }

  return {
    route: "write_answer_forfeit_turn",
    reason: result.reason,
  };
}

async function runJudgeTurn(turn: WrittenAnswer): Promise<JudgeResponse> {
  return await sendJudgeStructuredPrompt(
    turn.state,
    judgePrompt(turn),
    judgeGracePrompt(turn),
    normalizeJudgeResponse,
  );
}

async function sendParticipantInformationalPrompt(
  state: MatchState,
  role: MatchRole,
  promptType: string,
  prompt: string,
  turn: number,
  phase: MatchPhase,
  _timeoutMs: number,
): Promise<void> {
  const command = participantAgentCommandForRole(state, role);
  const workspaceDir = participantWorkspaceDirForRole(state, role);
  const sessionName = participantSessionNameForRole(state, role);

  await ensureAgentSession(command, workspaceDir, sessionName);
  await recordRunnerPrompt(state, role, promptType, prompt, turn, phase);
  const result = await runAgentPromptCommand({
    agentCommand: command,
    workspaceDir,
    sessionName,
    prompt,
    noWait: true,
  });
  assertQueuedInformationalPrompt(result, `participant ${nameForRole(state, role)}`);
  await syncAllTranscriptSessions(state);
}

async function sendJudgeInformationalPrompt(
  state: MatchState,
  promptType: string,
  prompt: string,
  turn: number,
  phase: MatchPhase,
  _timeoutMs: number,
): Promise<void> {
  await ensureAgentSession(
    state.judgeAgentCommand,
    state.judgeWorkspaceDir,
    state.judgeSessionName,
  );
  await recordRunnerPrompt(state, "judge", promptType, prompt, turn, phase);
  const result = await runAgentPromptCommand({
    agentCommand: state.judgeAgentCommand,
    workspaceDir: state.judgeWorkspaceDir,
    sessionName: state.judgeSessionName,
    prompt,
    noWait: true,
  });
  assertQueuedInformationalPrompt(result, "judge");
  await syncAllTranscriptSessions(state);
}

async function sendParticipantStructuredPrompt<T>(
  state: MatchState,
  role: MatchRole,
  prompt: string,
  gracePrompt: string,
  normalize: (raw: unknown) => T,
  promptTypeLabel: "question" | "answer",
): Promise<ParticipantPromptResult<T>> {
  const command = participantAgentCommandForRole(state, role);
  const workspaceDir = participantWorkspaceDirForRole(state, role);
  const sessionName = participantSessionNameForRole(state, role);
  const participantName = nameForRole(state, role);

  await ensureAgentSession(command, workspaceDir, sessionName);
  await recordRunnerPrompt(
    state,
    role,
    promptTypeLabel === "question" ? "asking turn" : "answering turn",
    prompt,
    state.currentTurn,
    state.phase,
  );

  const mainResult = await runAgentPromptCommand({
    agentCommand: command,
    workspaceDir,
    sessionName,
    prompt,
    timeoutMs: PARTICIPANT_TURN_TIMEOUT_MS,
  });
  await syncAllTranscriptSessions(state);
  const mainAttempt = classifyStructuredPromptAttempt(mainResult, normalize);
  if (mainAttempt.ok) {
    return mainAttempt;
  }
  if (!mainAttempt.retryable) {
    throw new Error(
      `${participantName} failed during ${promptTypeLabel} turn: ${mainAttempt.reason}`,
    );
  }
  if (mainAttempt.timedOut) {
    await cancelAgentPrompt(command, workspaceDir, sessionName);
  }
  dropPendingTranscriptPrompt(
    state,
    role,
    (pendingPrompt) =>
      pendingPrompt.turn === state.currentTurn &&
      pendingPrompt.promptType ===
        (promptTypeLabel === "question" ? "asking turn" : "answering turn"),
  );

  await recordRunnerPrompt(
    state,
    role,
    `${promptTypeLabel === "question" ? "asking turn" : "answering turn"} finalization retry`,
    gracePrompt,
    state.currentTurn,
    state.phase,
  );
  const graceResult = await runAgentPromptCommand({
    agentCommand: command,
    workspaceDir,
    sessionName,
    prompt: gracePrompt,
    timeoutMs: PARTICIPANT_GRACE_TIMEOUT_MS,
  });
  await syncAllTranscriptSessions(state);
  const graceAttempt = classifyStructuredPromptAttempt(graceResult, normalize);
  if (graceAttempt.ok) {
    return graceAttempt;
  }
  if (!graceAttempt.retryable) {
    throw new Error(
      `${participantName} failed during ${promptTypeLabel} grace turn: ${graceAttempt.reason}`,
    );
  }
  if (graceAttempt.timedOut) {
    await cancelAgentPrompt(command, workspaceDir, sessionName);
  }
  dropPendingTranscriptPrompt(
    state,
    role,
    (pendingPrompt) =>
      pendingPrompt.turn === state.currentTurn &&
      pendingPrompt.promptType ===
        `${promptTypeLabel === "question" ? "asking turn" : "answering turn"} finalization retry`,
  );

  return {
    ok: false,
    reason: [
      `${participantName} did not return a valid ${promptTypeLabel} within the 30-minute turn window.`,
      `A one-minute finalization retry was sent, but no valid ${promptTypeLabel} was returned.`,
      `Main attempt: ${mainAttempt.reason}`,
      `Finalization retry: ${graceAttempt.reason}`,
      "Automatic turn loss recorded by the match runner.",
    ].join(" "),
  };
}

async function sendJudgeStructuredPrompt<T>(
  state: MatchState,
  prompt: string,
  gracePrompt: string,
  normalize: (raw: unknown) => T,
): Promise<T> {
  await ensureAgentSession(
    state.judgeAgentCommand,
    state.judgeWorkspaceDir,
    state.judgeSessionName,
  );
  await recordRunnerPrompt(state, "judge", "judge turn", prompt, state.currentTurn, state.phase);

  const mainResult = await runAgentPromptCommand({
    agentCommand: state.judgeAgentCommand,
    workspaceDir: state.judgeWorkspaceDir,
    sessionName: state.judgeSessionName,
    prompt,
    timeoutMs: JUDGE_TIMEOUT_MS,
  });
  await syncAllTranscriptSessions(state);
  const mainAttempt = classifyStructuredPromptAttempt(mainResult, normalize);
  if (mainAttempt.ok) {
    return mainAttempt.value;
  }
  if (mainAttempt.timedOut) {
    await cancelAgentPrompt(
      state.judgeAgentCommand,
      state.judgeWorkspaceDir,
      state.judgeSessionName,
    );
  }
  dropPendingTranscriptPrompt(
    state,
    "judge",
    (pendingPrompt) =>
      pendingPrompt.turn === state.currentTurn && pendingPrompt.promptType === "judge turn",
  );

  await recordRunnerPrompt(
    state,
    "judge",
    "judge finalization retry",
    gracePrompt,
    state.currentTurn,
    state.phase,
  );
  const graceResult = await runAgentPromptCommand({
    agentCommand: state.judgeAgentCommand,
    workspaceDir: state.judgeWorkspaceDir,
    sessionName: state.judgeSessionName,
    prompt: gracePrompt,
    timeoutMs: PARTICIPANT_GRACE_TIMEOUT_MS,
  });
  await syncAllTranscriptSessions(state);
  const graceAttempt = classifyStructuredPromptAttempt(graceResult, normalize);
  if (graceAttempt.ok) {
    return graceAttempt.value;
  }
  if (graceAttempt.timedOut) {
    await cancelAgentPrompt(
      state.judgeAgentCommand,
      state.judgeWorkspaceDir,
      state.judgeSessionName,
    );
  }
  dropPendingTranscriptPrompt(
    state,
    "judge",
    (pendingPrompt) =>
      pendingPrompt.turn === state.currentTurn &&
      pendingPrompt.promptType === "judge finalization retry",
  );

  throw new Error(
    [
      `Judge did not return a valid ruling.`,
      `Main attempt: ${mainAttempt.reason}`,
      `Finalization retry: ${graceAttempt.reason}`,
    ].join(" "),
  );
}

function classifyStructuredPromptAttempt<T>(
  result: CliCommandResult,
  normalize: (raw: unknown) => T,
):
  | {
      ok: true;
      value: T;
    }
  | {
      ok: false;
      retryable: boolean;
      timedOut: boolean;
      reason: string;
    } {
  if (result.exitCode === 0) {
    try {
      const raw = extractJsonObject(result.stdout);
      return {
        ok: true,
        value: normalize(raw),
      };
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      return {
        ok: false,
        retryable: true,
        timedOut: false,
        reason: `returned invalid structured output: ${reason}`,
      };
    }
  }

  if (isTimeoutCliResult(result)) {
    return {
      ok: false,
      retryable: true,
      timedOut: true,
      reason: `timed out after ${Math.round(result.timeoutMs / 1000)} seconds`,
    };
  }

  return {
    ok: false,
    retryable: false,
    timedOut: false,
    reason: describeCliFailure(result),
  };
}

async function ensureAgentSession(
  agentCommand: string,
  workspaceDir: string,
  sessionName: string,
): Promise<void> {
  const result = await runAcpxCommand({
    args: [
      "--approve-all",
      "--format",
      "quiet",
      "--cwd",
      workspaceDir,
      "--agent",
      agentCommand,
      "sessions",
      "ensure",
      "--name",
      sessionName,
    ],
    cwd: workspaceDir,
  });
  if (result.exitCode !== 0) {
    throw new Error(`Failed to ensure participant session: ${describeCliFailure(result)}`);
  }
}

async function cancelAgentPrompt(
  agentCommand: string,
  workspaceDir: string,
  sessionName: string,
): Promise<void> {
  const result = await runAcpxCommand({
    args: [
      "--approve-all",
      "--format",
      "quiet",
      "--cwd",
      workspaceDir,
      "--agent",
      agentCommand,
      "cancel",
      "-s",
      sessionName,
    ],
    cwd: workspaceDir,
  });

  if (
    result.exitCode !== 0 &&
    !/nothing to cancel/i.test(result.stdout) &&
    !/nothing to cancel/i.test(result.stderr)
  ) {
    throw new Error(`Failed to cancel participant prompt: ${describeCliFailure(result)}`);
  }
}

async function runAgentPromptCommand(options: {
  agentCommand: string;
  workspaceDir: string;
  sessionName: string;
  prompt: string;
  timeoutMs?: number;
  noWait?: boolean;
}): Promise<CliCommandResult> {
  return await runAcpxCommand({
    args: [
      "--approve-all",
      "--format",
      "quiet",
      ...(options.timeoutMs ? ["--timeout", String(Math.ceil(options.timeoutMs / 1000))] : []),
      "--cwd",
      options.workspaceDir,
      "--agent",
      options.agentCommand,
      "prompt",
      ...(options.noWait ? ["--no-wait"] : []),
      "-s",
      options.sessionName,
      "-f",
      "-",
    ],
    cwd: options.workspaceDir,
    stdin: options.prompt,
    timeoutMs: options.timeoutMs ? options.timeoutMs + 15_000 : 15_000,
  });
}

type CliCommandResult = {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  signal: NodeJS.Signals | null;
  timeoutMs: number;
};

async function runAcpxCommand(options: {
  args: string[];
  cwd: string;
  stdin?: string;
  timeoutMs?: number;
}): Promise<CliCommandResult> {
  const invocation = resolveAcpxCliInvocation();

  return await new Promise<CliCommandResult>((resolve, reject) => {
    const child = spawn(invocation.command, [...invocation.baseArgs, ...options.args], {
      cwd: options.cwd,
      env: process.env,
      stdio: ["pipe", "pipe", "pipe"],
    });

    const stdoutChunks: string[] = [];
    const stderrChunks: string[] = [];
    let settled = false;
    let timer: NodeJS.Timeout | undefined;

    const finish = (result: CliCommandResult) => {
      if (settled) {
        return;
      }
      settled = true;
      if (timer) {
        clearTimeout(timer);
      }
      resolve(result);
    };

    child.stdout.on("data", (chunk: Buffer | string) => {
      stdoutChunks.push(String(chunk));
    });
    child.stderr.on("data", (chunk: Buffer | string) => {
      stderrChunks.push(String(chunk));
    });
    child.on("error", (error) => {
      if (settled) {
        return;
      }
      settled = true;
      if (timer) {
        clearTimeout(timer);
      }
      reject(error);
    });
    child.on("close", (exitCode, signal) => {
      finish({
        stdout: stdoutChunks.join("").trim(),
        stderr: stderrChunks.join("").trim(),
        exitCode,
        signal,
        timeoutMs: options.timeoutMs ?? 0,
      });
    });

    if (options.timeoutMs && options.timeoutMs > 0) {
      timer = setTimeout(() => {
        void child.kill("SIGTERM");
      }, options.timeoutMs);
    }

    if (options.stdin) {
      child.stdin.end(options.stdin);
    } else {
      child.stdin.end();
    }
  });
}

function resolveAcpxCliInvocation(): {
  command: string;
  baseArgs: string[];
} {
  const cliEntry = process.argv[1];
  if (!cliEntry) {
    throw new Error("Unable to resolve the acpx CLI entrypoint from process.argv[1].");
  }
  if (/\.(cts|mts|ts|tsx)$/i.test(cliEntry)) {
    const tsxPath = path.resolve(path.dirname(cliEntry), "..", "node_modules", ".bin", "tsx");
    if (!existsSync(tsxPath)) {
      throw new Error(`Unable to find tsx next to source acpx CLI: ${tsxPath}`);
    }
    return {
      command: tsxPath,
      baseArgs: [cliEntry],
    };
  }
  return {
    command: process.execPath,
    baseArgs: [cliEntry],
  };
}

function isTimeoutCliResult(result: CliCommandResult): boolean {
  return (
    result.exitCode === 3 ||
    /Timed out after/i.test(result.stderr) ||
    /Timed out after/i.test(result.stdout)
  );
}

function describeCliFailure(result: CliCommandResult): string {
  const parts = [
    result.exitCode == null ? "process exited without code" : `exit code ${result.exitCode}`,
    ...(result.signal ? [`signal ${result.signal}`] : []),
    ...(result.stderr ? [`stderr: ${result.stderr}`] : []),
    ...(result.stdout ? [`stdout: ${result.stdout}`] : []),
  ];
  return parts.join(", ");
}

function assertQueuedInformationalPrompt(result: CliCommandResult, label: string): void {
  if (result.exitCode === 0) {
    return;
  }

  throw new Error(
    `Failed to queue informational prompt for ${label}: ${describeCliFailure(result)}`,
  );
}

function asObject(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

function readAgentCommandFromConfig(
  agentsValue: unknown,
  agentName: string,
  configPath: string,
): string {
  const agents = asObject(agentsValue);
  const entry = asObject(agents?.[agentName]);
  const command = entry?.command;
  if (typeof command !== "string" || command.trim() === "") {
    throw new Error(`Missing agents.${agentName}.command in ${configPath}`);
  }
  return command.trim();
}

function participantBriefingPrompt(
  state: MatchState,
  options: {
    role: MatchRole;
  },
): string {
  const selfName = nameForRole(state, options.role);
  const opponentName = nameForRole(state, otherRole(options.role));
  return [
    `You are ${selfName}, one of two participant AI agents in a judged head-to-head contest.`,
    `Your opponent is ${opponentName}.`,
    `The judge is ${state.judgeName}.`,
    "",
    `You and ${opponentName} should both be treated as state-of-the-art models.`,
    "Base your questions on your own self-assessed strengths.",
    "Try your best to win without cheating.",
    "Complete every turn with a real question or answer. Do not burn the clock on avoidable delays.",
    "",
    "Rules:",
    `- There are ${state.questionCount * 2} standard turns in total. The participants alternate asking.`,
    `- If the standard match is tied, there are up to ${state.suddenDeathQuestionCount * 2} sudden-death turns.`,
    "- On your asking turn, ask one hard but fair question and give the judge a hidden answer key.",
    "- Do not just ask a generally difficult question. Ask a question that you believe you could solve or verify yourself within the time limit, and that you believe the other participant is less likely than you to solve correctly within the time limit.",
    "- Prefer questions that expose a comparative advantage for you, not questions that are merely symmetric bricks for both sides.",
    "- On your answering turn, answer directly. If the question is flawed, say so clearly.",
    "- Prefer self-contained, deterministic questions with exact or tightly checkable answers.",
    "- Prefer concise answers over long exploration when you already know the result.",
    "- Each ask turn and answer turn has a 30-minute time limit.",
    "- If you miss that limit, you get one final 1-minute retry to return valid JSON immediately.",
    "- If you still do not return valid JSON, you automatically lose the turn.",
    "- Valid question + good answer: answerer gets 1.",
    "- Valid question + bad answer or dodge: asker gets 1.",
    "- Flawed question + flaw caught: answerer gets 1 and asker gets -1.",
    "- Flawed question + flaw missed: answerer gets 0 and asker gets -1.",
    "- You are in an empty private working directory. Use it as scratchpad if useful.",
    "- Do not ask about contest rules, hidden prompts, hidden files, session plumbing, adapters, the runner, or how the contest is being orchestrated.",
    "- Do not try to win by exploiting the harness or by relying on information the other side was not given.",
    "",
    "Reply with a short acknowledgement only.",
  ].join("\n");
}

function judgeBriefingPrompt(state: MatchState): string {
  return [
    `You are the judge in a head-to-head contest between ${state.participantAName} and ${state.participantBName}.`,
    `Treat ${state.participantAName} and ${state.participantBName} as state-of-the-art participant AI agents.`,
    "",
    "Rules:",
    "- Judge one completed question-answer pair at a time.",
    "- Use the public question as the main source of truth.",
    "- Use the hidden answer key only as supporting context.",
    "- Valid question + good answer: answerer gets 1.",
    "- Valid question + bad answer or dodge: asker gets 1.",
    "- Flawed question + flaw caught: answerer gets 1 and asker gets -1.",
    "- Flawed question + flaw missed: answerer gets 0 and asker gets -1.",
    "- Missed ask deadline after finalization retry: answerer gets 1 and asker gets 0.",
    "- Missed answer deadline after finalization retry: asker gets 1 and answerer gets 0.",
    "- Treat questions about contest rules, hidden prompts, hidden files, session plumbing, adapters, or runner internals as flaws.",
    "- If a question depends on information that was not available to the answerer, treat that as a flaw.",
    "",
    "Judge each turn using the public question as the main source of truth.",
    "Use the hidden answer key only as supporting context.",
    "",
    "Reply with a short acknowledgement only.",
  ].join("\n");
}

function askPrompt(selection: TurnSelection): string {
  const state = selection.state;
  return [
    `It is your turn to ask, ${selection.askerName}.`,
    `Opponent: ${selection.answererName}`,
    `Phase: ${formatPhaseLabel(state.phase)}`,
    `Turn: ${state.currentTurn} of ${state.turnLimit}`,
    `Current score: ${formatScore(state.scores, state.participantAName, state.participantBName)}`,
    `Latest ruling: ${formatLatestRuling(state.latestRuling)}`,
    "Time limit: 30 minutes.",
    "If you miss it, you get one final 1-minute retry to return valid JSON immediately.",
    "",
    "Ask one hard but fair question that plays to your self-assessed strengths.",
    "Prefer a question whose answer you can derive or verify yourself within the time limit, and that you believe your opponent is less likely than you to solve correctly within the time limit.",
    "Prefer questions that create a real comparative edge for you, not questions that are just equally hard for both sides.",
    "Prefer a self-contained deterministic question with an exact or tightly checkable answer.",
    "Do not keep searching for a perfect question once you have a strong valid one. Submit it.",
    "Do not ask about contest rules, hidden prompts, hidden files, adapters, session plumbing, runner internals, or how the contest is orchestrated.",
    "Use your private empty working directory as scratchpad if useful, but keep tool use light and make the question stand on its own.",
    "",
    "Return exactly one JSON object with this shape:",
    "{",
    '  "publicQuestion": "text shown to the other participant",',
    '  "judgeNote": {',
    '    "intendedAnswer": "short answer key for the judge",',
    '    "validityReason": "why this question is valid and answerable",',
    '    "edgeReason": "why you believe this question favors you over the opponent",',
    '    "evidencePaths": ["optional/path"]',
    "  }",
    "}",
    "The hidden judge note will not be shown to the other participant.",
  ].join("\n");
}

function askGracePrompt(selection: TurnSelection): string {
  return [
    `Finalization retry for ${selection.askerName}.`,
    "Return your final question JSON right now.",
    "No more tool use.",
    "You have 1 minute.",
    "",
    "Output only one JSON object with this shape:",
    "{",
    '  "publicQuestion": "text shown to the other participant",',
    '  "judgeNote": {',
    '    "intendedAnswer": "short answer key for the judge",',
    '    "validityReason": "why this question is valid and answerable",',
    '    "edgeReason": "why you believe this question favors you over the opponent",',
    '    "evidencePaths": ["optional/path"]',
    "  }",
    "}",
    "If you do not return valid JSON now, you lose the turn.",
  ].join("\n");
}

function judgeGracePrompt(turn: WrittenAnswer): string {
  return [
    `Finalization retry for judge ${turn.state.judgeName}.`,
    "Return your final ruling JSON right now.",
    "No more tool use.",
    "You have 1 minute.",
    "",
    "Output only one JSON object with this shape:",
    "{",
    '  "outcome": "answerer_point" | "asker_point" | "flawed_caught" | "flawed_missed",',
    '  "reason": "short explanation"',
    "}",
  ].join("\n");
}

function waitPrompt(selection: TurnSelection, waitingRole: MatchRole): string {
  const waitingName = nameForRole(selection.state, waitingRole);
  const askingName = nameForRole(selection.state, otherRole(waitingRole));
  return [
    `You are ${waitingName}.`,
    `${askingName} is asking the current question.`,
    `Current score: ${formatScore(selection.state.scores, selection.state.participantAName, selection.state.participantBName)}`,
    `Latest ruling: ${formatLatestRuling(selection.state.latestRuling)}`,
    "Do not answer yet. Wait for the next official message.",
    "Reply with a short acknowledgement only.",
  ].join("\n");
}

async function writeQuestion(
  selection: TurnSelection,
  outputs: Record<string, unknown>,
): Promise<WrittenQuestion> {
  const askResponse =
    selection.askerRole === "participant_a"
      ? askResponseFromActionResult(outputs.ask_participant_a)
      : askResponseFromActionResult(outputs.ask_participant_b);

  await fs.mkdir(selection.turnDir, { recursive: true });

  const questionPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-question.md`,
  );
  const questionJsonPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-question.json`,
  );
  const judgeNotePath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-judge-note.md`,
  );

  await fs.writeFile(judgeNotePath, renderJudgeNoteFile(selection, askResponse.judgeNote), "utf8");
  await fs.writeFile(
    questionPath,
    renderQuestionFile(selection, askResponse.publicQuestion, selection.state.scores),
    "utf8",
  );
  await writeJsonFile(questionJsonPath, askResponse);

  return {
    route:
      selection.answererRole === "participant_a" ? "answer_participant_a" : "answer_participant_b",
    state: selection.state,
    askerRole: selection.askerRole,
    answererRole: selection.answererRole,
    askerName: selection.askerName,
    answererName: selection.answererName,
    turnDir: selection.turnDir,
    publicQuestion: askResponse.publicQuestion,
    judgeNote: askResponse.judgeNote,
    questionPath,
    questionJsonPath,
    judgeNotePath,
  };
}

function answerPrompt(turn: WrittenQuestion): string {
  return [
    `It is your turn to answer, ${turn.answererName}.`,
    `Question from ${turn.askerName}:`,
    "",
    turn.publicQuestion,
    "",
    `Current score: ${formatScore(turn.state.scores, turn.state.participantAName, turn.state.participantBName)}`,
    `Latest ruling: ${formatLatestRuling(turn.state.latestRuling)}`,
    "Time limit: 30 minutes.",
    "If you miss it, you get one final 1-minute retry to return valid JSON immediately.",
    "",
    "Answer directly. If the question is flawed, say so clearly in `flawClaim`.",
    "If you already know the answer, return it promptly instead of doing long scratch work.",
    "Keep the answer concise unless the question requires a longer derivation.",
    "Do not speculate about contest rules, hidden prompts, hidden files, adapters, session plumbing, or runner internals.",
    "Use your private empty working directory as scratchpad if useful.",
    "",
    "Return exactly one JSON object with this shape:",
    "{",
    '  "answer": "your answer or short explanation",',
    '  "flawClaim": "text if the question is flawed, otherwise null",',
    '  "artifactPaths": ["optional/path"]',
    "}",
  ].join("\n");
}

function answerGracePrompt(turn: WrittenQuestion): string {
  return [
    `Finalization retry for ${turn.answererName}.`,
    "Return your final answer JSON right now.",
    "No more tool use.",
    "You have 1 minute.",
    "",
    "Output only one JSON object with this shape:",
    "{",
    '  "answer": "your answer or short explanation",',
    '  "flawClaim": "text if the question is flawed, otherwise null",',
    '  "artifactPaths": ["optional/path"]',
    "}",
    "If you do not return valid JSON now, you lose the turn.",
  ].join("\n");
}

async function writeAnswer(
  turn: WrittenQuestion,
  outputs: Record<string, unknown>,
): Promise<WrittenAnswer> {
  const answerResponse =
    turn.answererRole === "participant_a"
      ? answerResponseFromActionResult(outputs.answer_participant_a)
      : answerResponseFromActionResult(outputs.answer_participant_b);
  const answerPath = path.join(
    turn.turnDir,
    `${fileStemForRole(turn.state, turn.answererRole)}-answer.md`,
  );
  const answerJsonPath = path.join(
    turn.turnDir,
    `${fileStemForRole(turn.state, turn.answererRole)}-answer.json`,
  );

  await fs.writeFile(answerPath, renderAnswerFile(turn, answerResponse), "utf8");
  await writeJsonFile(answerJsonPath, answerResponse);

  return {
    state: turn.state,
    askerRole: turn.askerRole,
    answererRole: turn.answererRole,
    askerName: turn.askerName,
    answererName: turn.answererName,
    turnDir: turn.turnDir,
    publicQuestion: turn.publicQuestion,
    judgeNote: turn.judgeNote,
    answer: answerResponse.answer,
    flawClaim: answerResponse.flawClaim,
    artifactPaths: answerResponse.artifactPaths,
    questionPath: turn.questionPath,
    questionJsonPath: turn.questionJsonPath,
    judgeNotePath: turn.judgeNotePath,
    answerPath,
    answerJsonPath,
  };
}

async function writeAskForfeitTurn(
  selection: TurnSelection,
  outputs: Record<string, unknown>,
): Promise<WrittenRuling> {
  const failure =
    selection.askerRole === "participant_a"
      ? askActionResult(outputs.ask_participant_a)
      : askActionResult(outputs.ask_participant_b);
  if (failure.route !== "write_ask_forfeit_turn") {
    throw new Error("Expected an ask forfeit result.");
  }

  await fs.mkdir(selection.turnDir, { recursive: true });

  const questionPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-question.md`,
  );
  const questionJsonPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-question.json`,
  );
  const judgeNotePath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-judge-note.md`,
  );
  const answerPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.answererRole)}-answer.md`,
  );
  const answerJsonPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.answererRole)}-answer.json`,
  );

  await fs.writeFile(
    questionPath,
    renderAskForfeitQuestionFile(selection, selection.state.scores, failure.reason),
    "utf8",
  );
  await writeJsonFile(questionJsonPath, {
    issuedByRunner: true,
    status: "no_valid_submission",
    reason: failure.reason,
  });
  await fs.writeFile(
    judgeNotePath,
    renderAskForfeitJudgeNoteFile(selection, failure.reason),
    "utf8",
  );
  await fs.writeFile(answerPath, renderAskForfeitAnswerFile(selection), "utf8");
  await writeJsonFile(answerJsonPath, {
    issuedByRunner: true,
    status: "not_required",
    reason: "The asker forfeited before submitting a valid question.",
  });

  return await writeSyntheticRuling({
    state: selection.state,
    askerRole: selection.askerRole,
    answererRole: selection.answererRole,
    askerName: selection.askerName,
    answererName: selection.answererName,
    turnDir: selection.turnDir,
    outcome: "asker_forfeit",
    reason: failure.reason,
    questionPath,
    questionJsonPath,
    judgeNotePath,
    answerPath,
    answerJsonPath,
  });
}

async function writeAnswerForfeitTurn(
  turn: WrittenQuestion,
  outputs: Record<string, unknown>,
): Promise<WrittenRuling> {
  const failure =
    turn.answererRole === "participant_a"
      ? answerActionResult(outputs.answer_participant_a)
      : answerActionResult(outputs.answer_participant_b);
  if (failure.route !== "write_answer_forfeit_turn") {
    throw new Error("Expected an answer forfeit result.");
  }

  const answerPath = path.join(
    turn.turnDir,
    `${fileStemForRole(turn.state, turn.answererRole)}-answer.md`,
  );
  const answerJsonPath = path.join(
    turn.turnDir,
    `${fileStemForRole(turn.state, turn.answererRole)}-answer.json`,
  );
  await fs.writeFile(answerPath, renderAnswerForfeitFile(turn, failure.reason), "utf8");
  await writeJsonFile(answerJsonPath, {
    issuedByRunner: true,
    status: "no_valid_submission",
    reason: failure.reason,
  });

  return await writeSyntheticRuling({
    state: turn.state,
    askerRole: turn.askerRole,
    answererRole: turn.answererRole,
    askerName: turn.askerName,
    answererName: turn.answererName,
    turnDir: turn.turnDir,
    outcome: "answerer_forfeit",
    reason: failure.reason,
    questionPath: turn.questionPath,
    questionJsonPath: turn.questionJsonPath,
    judgeNotePath: turn.judgeNotePath,
    answerPath,
    answerJsonPath,
  });
}

async function writeSyntheticRuling(options: {
  state: MatchState;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  turnDir: string;
  outcome: AutomaticOutcome;
  reason: string;
  questionPath: string;
  questionJsonPath: string;
  judgeNotePath: string;
  answerPath: string;
  answerJsonPath: string;
}): Promise<WrittenRuling> {
  const { askerDelta, answererDelta } = scoreDeltasForOutcome(options.outcome);
  const rulingPath = path.join(options.turnDir, `${options.state.judgeFileStem}-ruling.md`);
  const rulingJsonPath = path.join(options.turnDir, `${options.state.judgeFileStem}-ruling.json`);

  const structuredRuling = {
    issuedByRunner: true,
    outcome: options.outcome,
    reason: options.reason,
  };
  const ruling: WrittenRuling = {
    state: options.state,
    turn: options.state.currentTurn,
    phase: options.state.phase,
    askerRole: options.askerRole,
    answererRole: options.answererRole,
    askerName: options.askerName,
    answererName: options.answererName,
    outcome: options.outcome,
    reason: options.reason,
    askerDelta,
    answererDelta,
    rulingPath,
    rulingJsonPath,
    questionPath: options.questionPath,
    questionJsonPath: options.questionJsonPath,
    judgeNotePath: options.judgeNotePath,
    answerPath: options.answerPath,
    answerJsonPath: options.answerJsonPath,
  };
  await recordRunnerNotice(
    options.state,
    ruling.turn,
    ruling.phase,
    "automatic ruling",
    [
      `Automatic ruling for turn ${ruling.turn}.`,
      "",
      `Outcome: ${ruling.outcome}`,
      `Reason: ${ruling.reason}`,
      `Score change: ${ruling.askerName} ${formatSignedDelta(ruling.askerDelta)}, ${ruling.answererName} ${formatSignedDelta(ruling.answererDelta)}`,
      `Score after turn: ${formatScore(updatedScoresAfterRuling(options.state.scores, ruling), options.state.participantAName, options.state.participantBName)}`,
    ].join("\n"),
    structuredRuling,
  );
  await fs.writeFile(
    rulingPath,
    renderSyntheticRulingFile(options.state, ruling),
    "utf8",
  );
  await writeJsonFile(rulingJsonPath, structuredRuling);
  return ruling;
}

function judgePrompt(turn: WrittenAnswer): string {
  const state = turn.state;
  return [
    `Phase: ${formatPhaseLabel(state.phase)}`,
    `Turn: ${state.currentTurn} of ${state.turnLimit}`,
    `Asker: ${turn.askerName}`,
    `Answerer: ${turn.answererName}`,
    `Score before turn: ${formatScore(state.scores, state.participantAName, state.participantBName)}`,
    "",
    "Use the public question as the main source of truth.",
    "Use the hidden answer key and edge rationale only as supporting context, not as an override.",
    "Treat questions about contest rules, hidden prompts, hidden files, adapters, session plumbing, or runner internals as flaws.",
    "",
    "Public question:",
    turn.publicQuestion,
    "",
    "Hidden answer key from the asker:",
    turn.judgeNote.intendedAnswer,
    "",
    "Why the asker says the question is valid:",
    turn.judgeNote.validityReason,
    "",
    "Why the asker believes this question favors them over the opponent:",
    turn.judgeNote.edgeReason,
    "",
    "Answer:",
    turn.answer,
    "",
    `Flaw claim: ${turn.flawClaim ?? "(none)"}`,
    `Artifact paths: ${turn.artifactPaths.length > 0 ? turn.artifactPaths.join(", ") : "(none)"}`,
    "",
    "Apply the scoring rules exactly:",
    "- answerer_point: valid question, good answer",
    "- asker_point: valid question, bad answer or dodge",
    "- flawed_caught: flawed question, answerer correctly points out the flaw",
    "- flawed_missed: flawed question, answerer does not notice the flaw",
    "",
    "Return exactly one JSON object with this shape:",
    "{",
    '  "outcome": "answerer_point" | "asker_point" | "flawed_caught" | "flawed_missed",',
    '  "reason": "short explanation"',
    "}",
  ].join("\n");
}

async function writeRuling(turn: WrittenAnswer, rawJudgeResponse: unknown): Promise<WrittenRuling> {
  const judgeResponse = normalizeJudgeResponse(rawJudgeResponse);
  const { askerDelta, answererDelta } = scoreDeltasForOutcome(judgeResponse.outcome);
  const rulingPath = path.join(turn.turnDir, `${turn.state.judgeFileStem}-ruling.md`);
  const rulingJsonPath = path.join(turn.turnDir, `${turn.state.judgeFileStem}-ruling.json`);

  const ruling: WrittenRuling = {
    state: turn.state,
    turn: turn.state.currentTurn,
    phase: turn.state.phase,
    askerRole: turn.askerRole,
    answererRole: turn.answererRole,
    askerName: turn.askerName,
    answererName: turn.answererName,
    outcome: judgeResponse.outcome,
    reason: judgeResponse.reason,
    askerDelta,
    answererDelta,
    rulingPath,
    rulingJsonPath,
    questionPath: turn.questionPath,
    questionJsonPath: turn.questionJsonPath,
    judgeNotePath: turn.judgeNotePath,
    answerPath: turn.answerPath,
    answerJsonPath: turn.answerJsonPath,
  };
  await fs.writeFile(
    rulingPath,
    renderRulingFile(turn, judgeResponse, askerDelta, answererDelta),
    "utf8",
  );
  await writeJsonFile(rulingJsonPath, judgeResponse);
  return ruling;
}

function rulingNotificationPrompt(ruling: WrittenRuling, recipientRole: MatchRole): string {
  const nextScores = updatedScoresAfterRuling(ruling.state.scores, ruling);
  return [
    `You are ${nameForRole(ruling.state, recipientRole)}.`,
    `Turn ${ruling.turn} is complete.`,
    `Asker: ${ruling.askerName}`,
    `Answerer: ${ruling.answererName}`,
    `Outcome: ${ruling.outcome}`,
    `Reason: ${ruling.reason}`,
    `Updated score: ${formatScore(nextScores, ruling.state.participantAName, ruling.state.participantBName)}`,
    "Wait for the next official message.",
    "Reply with a short acknowledgement only.",
  ].join("\n");
}

function advanceState(state: MatchState, ruling: WrittenRuling): MatchState {
  const nextScores = updatedScoresAfterRuling(state.scores, ruling);
  const summary: RulingSummary = {
    turn: ruling.turn,
    phase: ruling.phase,
    askerRole: ruling.askerRole,
    answererRole: ruling.answererRole,
    askerName: ruling.askerName,
    answererName: ruling.answererName,
    outcome: ruling.outcome,
    reason: ruling.reason,
    askerDelta: ruling.askerDelta,
    answererDelta: ruling.answererDelta,
    updatedScores: nextScores,
  };
  const record: TurnRecord = {
    turn: ruling.turn,
    phase: ruling.phase,
    askerRole: ruling.askerRole,
    answererRole: ruling.answererRole,
    askerName: ruling.askerName,
    answererName: ruling.answererName,
    questionPath: ruling.questionPath,
    questionJsonPath: ruling.questionJsonPath,
    judgeNotePath: ruling.judgeNotePath,
    answerPath: ruling.answerPath,
    answerJsonPath: ruling.answerJsonPath,
    rulingPath: ruling.rulingPath,
    rulingJsonPath: ruling.rulingJsonPath,
    outcome: ruling.outcome,
    reason: ruling.reason,
    askerDelta: ruling.askerDelta,
    answererDelta: ruling.answererDelta,
    updatedScores: nextScores,
  };

  const nextTurn = state.currentTurn + 1;
  const finishedStandardMatch =
    state.phase === "standard" &&
    state.currentTurn === state.standardTurns &&
    nextScores.participantA === nextScores.participantB &&
    state.suddenDeathTurns > 0;

  if (finishedStandardMatch) {
    return {
      ...state,
      currentTurn: nextTurn,
      phase: "sudden_death",
      turnLimit: state.standardTurns + state.suddenDeathTurns,
      scores: nextScores,
      latestRuling: summary,
      history: [...state.history, record],
    };
  }

  return {
    ...state,
    currentTurn: nextTurn,
    scores: nextScores,
    latestRuling: summary,
    history: [...state.history, record],
  };
}

async function advanceTurn(state: MatchState, ruling: WrittenRuling): Promise<MatchState> {
  const nextState = advanceState(state, ruling);
  await persistManifest(nextState);
  await persistTranscriptFromLog(nextState);
  return nextState;
}

function updatedScoresAfterRuling(scores: ScoreState, ruling: WrittenRuling): ScoreState {
  return {
    participantA:
      scores.participantA +
      (ruling.askerRole === "participant_a" ? ruling.askerDelta : ruling.answererDelta),
    participantB:
      scores.participantB +
      (ruling.askerRole === "participant_b" ? ruling.askerDelta : ruling.answererDelta),
  };
}

async function persistManifest(state: MatchState): Promise<void> {
  await fs.writeFile(state.manifestPath, renderManifest(state), "utf8");
}

async function initializeMessageArchive(state: MatchState): Promise<void> {
  await fs.writeFile(state.messageLogPath, "", "utf8");
  await persistTranscriptFromLog(state);
}

async function appendMessageEvent(
  state: MatchState,
  event: MatchMessageEvent,
  transcriptState?: MatchState,
): Promise<void> {
  const existing = await readTextIfExists(state.messageLogPath);
  const marker = `"eventId":"${event.eventId}"`;
  if (!existing.includes(marker)) {
    await fs.appendFile(state.messageLogPath, `${JSON.stringify(event)}\n`, "utf8");
  }
  await persistTranscriptFromLog(transcriptState ?? state);
}

async function persistTranscriptFromLog(state: MatchState): Promise<void> {
  const events = parseMessageEvents(await readTextIfExists(state.messageLogPath));
  await fs.writeFile(
    state.transcriptPath,
    renderTranscript(
      {
        matchId: state.matchId,
        participantAName: state.participantAName,
        participantBName: state.participantBName,
        judgeName: state.judgeName,
        currentScore: formatScore(state.scores, state.participantAName, state.participantBName),
        latestCompletedTurn: state.history.at(-1)?.turn ?? 0,
      },
      events,
    ),
    "utf8",
  );
}

function parseMessageEvents(raw: string): MatchMessageEvent[] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => JSON.parse(line) as MatchMessageEvent);
}

function nextTranscriptEventId(state: MatchState, prefix: string): string {
  const eventId = `${prefix}-${String(state.nextTranscriptEventId).padStart(6, "0")}`;
  state.nextTranscriptEventId += 1;
  return eventId;
}

function transcriptTrackerForTarget(
  state: MatchState,
  target: TranscriptTarget,
): SessionTranscriptTracker {
  switch (target) {
    case "participant_a":
      return state.participantATranscript;
    case "participant_b":
      return state.participantBTranscript;
    case "judge":
      return state.judgeTranscript;
  }
}

function transcriptSpeakerNameForTarget(state: MatchState, target: TranscriptTarget): string {
  switch (target) {
    case "participant_a":
      return state.participantAName;
    case "participant_b":
      return state.participantBName;
    case "judge":
      return state.judgeName;
  }
}

function transcriptSpeakerRoleForTarget(
  target: TranscriptTarget,
): "participant" | "judge" | "runner" {
  return target === "judge" ? "judge" : "participant";
}

function sessionNameForTranscriptTarget(state: MatchState, target: TranscriptTarget): string {
  switch (target) {
    case "participant_a":
      return state.participantASessionName;
    case "participant_b":
      return state.participantBSessionName;
    case "judge":
      return state.judgeSessionName;
  }
}

function dropPendingTranscriptPrompt(
  state: MatchState,
  target: TranscriptTarget,
  predicate: (prompt: PendingTranscriptPrompt) => boolean,
): void {
  const tracker = transcriptTrackerForTarget(state, target);
  const index = tracker.pendingPrompts.findIndex(predicate);
  if (index !== -1) {
    tracker.pendingPrompts.splice(index, 1);
  }
}

async function recordRunnerPrompt(
  state: MatchState,
  target: TranscriptTarget,
  promptType: string,
  prompt: string,
  turn: number,
  phase: MatchPhase,
): Promise<void> {
  const eventId = nextTranscriptEventId(state, "prompt");
  await appendMessageEvent(
    state,
    buildRunnerPromptEvent({
      eventId,
      turn,
      phase,
      recipientName: transcriptSpeakerNameForTarget(state, target),
      promptType,
      body: prompt,
    }) as MatchMessageEvent,
  );

  transcriptTrackerForTarget(state, target).pendingPrompts.push({
    promptEventId: eventId,
    turn,
    phase,
    promptType,
    recipientName: transcriptSpeakerNameForTarget(state, target),
  });
}

async function recordRunnerNotice(
  state: MatchState,
  turn: number,
  phase: MatchPhase,
  title: string,
  body: string,
  structuredData?: unknown,
): Promise<void> {
  await appendMessageEvent(
    state,
    buildRunnerNoticeEvent({
      eventId: nextTranscriptEventId(state, "notice"),
      turn,
      phase,
      title,
      body,
      structuredData,
    }) as MatchMessageEvent,
  );
}

async function syncAllTranscriptSessions(state: MatchState): Promise<void> {
  await syncTranscriptSession(state, "participant_a");
  await syncTranscriptSession(state, "participant_b");
  await syncTranscriptSession(state, "judge");
}

async function syncTranscriptSession(
  state: MatchState,
  target: TranscriptTarget,
): Promise<void> {
  const tracker = transcriptTrackerForTarget(state, target);
  const recordPath = await resolveSessionRecordPathForTarget(state, target, tracker);
  if (!recordPath) {
    return;
  }

  let sessionRecord: unknown;
  try {
    sessionRecord = JSON.parse(await fs.readFile(recordPath, "utf8"));
  } catch {
    return;
  }

  const rawMessages = asObject(sessionRecord)?.messages;
  const messages = Array.isArray(rawMessages) ? rawMessages : [];
  const startIndex = Math.min(tracker.processedMessageCount, messages.length);

  for (let index = startIndex; index < messages.length; index += 1) {
    const message = messages[index];
    const agentMessage = asObject(message)?.Agent;
    if (!agentMessage) {
      continue;
    }

    const pendingPrompt =
      tracker.pendingPrompts.shift() ?? {
        promptEventId: nextTranscriptEventId(state, "orphan-prompt"),
        turn: state.currentTurn,
        phase: state.phase,
        promptType: "session reply",
        recipientName: transcriptSpeakerNameForTarget(state, target),
      };

    await appendMessageEvent(
      state,
      buildAgentReplyEvent({
        eventId: nextTranscriptEventId(state, "reply"),
        turn: pendingPrompt.turn,
        phase: pendingPrompt.phase,
        speakerName: transcriptSpeakerNameForTarget(state, target),
        speakerRole: transcriptSpeakerRoleForTarget(target),
        promptEventId: pendingPrompt.promptEventId,
        promptType: pendingPrompt.promptType,
        agentMessage,
      }) as MatchMessageEvent,
    );
  }

  tracker.processedMessageCount = messages.length;
}

async function resolveSessionRecordPathForTarget(
  state: MatchState,
  target: TranscriptTarget,
  tracker: SessionTranscriptTracker,
): Promise<string | undefined> {
  if (tracker.sessionRecordPath && existsSync(tracker.sessionRecordPath)) {
    return tracker.sessionRecordPath;
  }

  const sessionsDir = path.join(os.homedir(), ".acpx", "sessions");
  let entries: string[];
  try {
    entries = await fs.readdir(sessionsDir);
  } catch {
    return undefined;
  }

  const sessionName = sessionNameForTranscriptTarget(state, target);
  let bestPath: string | undefined;
  let bestLastUsedAt = "";

  for (const entry of entries) {
    if (!entry.endsWith(".json") || entry.endsWith(".stream.ndjson")) {
      continue;
    }
    const candidatePath = path.join(sessionsDir, entry);
    let candidate: unknown;
    try {
      candidate = JSON.parse(await fs.readFile(candidatePath, "utf8"));
    } catch {
      continue;
    }
    const record = asObject(candidate);
    if (!record || record.name !== sessionName) {
      continue;
    }
    const lastUsedAt =
      typeof record.last_used_at === "string" ? record.last_used_at : "";
    if (!bestPath || lastUsedAt >= bestLastUsedAt) {
      bestPath = candidatePath;
      bestLastUsedAt = lastUsedAt;
    }
  }

  if (bestPath) {
    tracker.sessionRecordPath = bestPath;
  }
  return bestPath;
}

async function readTextIfExists(filePath: string): Promise<string> {
  try {
    return await fs.readFile(filePath, "utf8");
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "ENOENT") {
      return "";
    }
    throw error;
  }
}

async function writeJsonFile(filePath: string, value: unknown): Promise<void> {
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function writeFinalScoreboard(state: MatchState): Promise<{
  matchDir: string;
  scoreboardPath: string;
  scores: ScoreState;
  result: string;
  history: TurnRecord[];
}> {
  const finalDir = path.join(state.matchDir, "final");
  await fs.mkdir(finalDir, { recursive: true });
  const scoreboardPath = path.join(finalDir, "scoreboard.md");
  const result = finalResult(state);
  await fs.writeFile(scoreboardPath, renderScoreboard(state), "utf8");
  await syncAllTranscriptSessions(state);
  await recordRunnerNotice(
    state,
    state.history.at(-1)?.turn ?? 0,
    state.phase,
    "final result",
    [
      "Final scoreboard written.",
      "",
      `Result: ${result}`,
      `Final score: ${formatScore(state.scores, state.participantAName, state.participantBName)}`,
      `Scoreboard: ${scoreboardPath}`,
    ].join("\n"),
    {
      result,
      scoreboardPath,
      scores: state.scores,
    },
  );
  await persistManifest(state);
  await persistTranscriptFromLog(state);
  return {
    matchDir: state.matchDir,
    scoreboardPath,
    scores: state.scores,
    result,
    history: state.history,
  };
}

function normalizeAskResponse(raw: unknown): AskResponse {
  const value = raw as Partial<AskResponse>;
  const publicQuestion = String(value.publicQuestion ?? "").trim();
  const judgeNote = (value.judgeNote ?? {}) as Partial<JudgeNote>;
  const intendedAnswer = String(judgeNote.intendedAnswer ?? "").trim();
  const validityReason = String(judgeNote.validityReason ?? "").trim();
  const edgeReason = String(judgeNote.edgeReason ?? "").trim();
  if (!publicQuestion || !intendedAnswer || !validityReason || !edgeReason) {
    throw new Error("Ask response must include publicQuestion and a complete judgeNote.");
  }
  return {
    publicQuestion,
    judgeNote: {
      intendedAnswer,
      validityReason,
      edgeReason,
      evidencePaths: normalizeStringArray(judgeNote.evidencePaths),
    },
  };
}

function normalizeAnswerResponse(raw: unknown): AnswerResponse {
  const value = raw as Partial<AnswerResponse>;
  const answer = String(value.answer ?? "").trim();
  if (!answer) {
    throw new Error("Answer response must include a non-empty answer.");
  }
  return {
    answer,
    flawClaim:
      value.flawClaim == null || String(value.flawClaim).trim() === ""
        ? null
        : String(value.flawClaim).trim(),
    artifactPaths: normalizeStringArray(value.artifactPaths),
  };
}

function normalizeJudgeResponse(raw: unknown): JudgeResponse {
  const value = raw as Partial<JudgeResponse>;
  const outcome = String(value.outcome ?? "").trim() as JudgedOutcome;
  const reason = String(value.reason ?? "").trim();
  if (!reason) {
    throw new Error("Judge response must include a reason.");
  }
  if (
    outcome !== "answerer_point" &&
    outcome !== "asker_point" &&
    outcome !== "flawed_caught" &&
    outcome !== "flawed_missed"
  ) {
    throw new Error(`Unsupported judge outcome: ${JSON.stringify(value.outcome)}`);
  }
  return {
    outcome,
    reason,
  };
}

function scoreDeltasForOutcome(outcome: TurnOutcome): {
  askerDelta: number;
  answererDelta: number;
} {
  switch (outcome) {
    case "answerer_point":
      return {
        askerDelta: 0,
        answererDelta: 1,
      };
    case "asker_point":
      return {
        askerDelta: 1,
        answererDelta: 0,
      };
    case "flawed_caught":
      return {
        askerDelta: -1,
        answererDelta: 1,
      };
    case "flawed_missed":
      return {
        askerDelta: -1,
        answererDelta: 0,
      };
    case "asker_forfeit":
      return {
        askerDelta: 0,
        answererDelta: 1,
      };
    case "answerer_forfeit":
      return {
        askerDelta: 1,
        answererDelta: 0,
      };
  }
}

function roleForTurn(turn: number, startingParticipant: MatchRole): MatchRole {
  if (startingParticipant === "participant_a") {
    return turn % 2 === 1 ? "participant_a" : "participant_b";
  }
  return turn % 2 === 1 ? "participant_b" : "participant_a";
}

function otherRole(role: MatchRole): MatchRole {
  return role === "participant_a" ? "participant_b" : "participant_a";
}

function nameForRole(state: MatchState, role: MatchRole): string {
  return role === "participant_a" ? state.participantAName : state.participantBName;
}

function participantAgentCommandForRole(state: MatchState, role: MatchRole): string {
  return role === "participant_a" ? state.participantAAgentCommand : state.participantBAgentCommand;
}

function participantSessionNameForRole(state: MatchState, role: MatchRole): string {
  return role === "participant_a" ? state.participantASessionName : state.participantBSessionName;
}

function participantWorkspaceDirForRole(state: MatchState, role: MatchRole): string {
  return role === "participant_a" ? state.participantAWorkspaceDir : state.participantBWorkspaceDir;
}

function fileStemForRole(state: MatchState, role: MatchRole): string {
  return role === "participant_a" ? state.participantAFileStem : state.participantBFileStem;
}

function normalizeStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map((entry) => String(entry ?? "").trim()).filter((entry) => entry.length > 0);
}

function sanitizeNameForPath(value: string): string {
  return (
    value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "participant"
  );
}

function formatMatchStamp(date: Date): string {
  const iso = date.toISOString();
  const year = iso.slice(0, 4);
  const month = iso.slice(5, 7);
  const day = iso.slice(8, 10);
  const hour = iso.slice(11, 13);
  const minute = iso.slice(14, 16);
  return `${year}-${month}-${day}-${hour}${minute}`;
}

function formatTurnDir(turn: number): string {
  return `turn-${String(turn).padStart(2, "0")}`;
}

function formatScore(
  scores: ScoreState,
  participantAName: string,
  participantBName: string,
): string {
  return `${participantAName} ${scores.participantA}, ${participantBName} ${scores.participantB}`;
}

function formatLatestRuling(ruling: RulingSummary | null): string {
  if (!ruling) {
    return "none yet";
  }
  return [
    `turn ${ruling.turn}`,
    `phase ${formatPhaseLabel(ruling.phase)}`,
    `outcome ${ruling.outcome}`,
    `score now ${ruling.updatedScores.participantA}-${ruling.updatedScores.participantB}`,
  ].join(", ");
}

function formatPhaseLabel(phase: MatchPhase): string {
  return phase === "standard" ? "standard match" : "sudden death";
}

function finalResult(state: MatchState): string {
  if (state.scores.participantA === state.scores.participantB) {
    return "unresolved";
  }
  return state.scores.participantA > state.scores.participantB
    ? state.participantAName
    : state.participantBName;
}

function formatSignedDelta(value: number): string {
  return value > 0 ? `+${value}` : String(value);
}

function formatPathListInline(paths: string[]): string {
  return paths.length > 0 ? paths.map((entry) => `\`${entry}\``).join(", ") : "(none)";
}

function renderManifest(state: MatchState): string {
  const latestCompletedTurn = state.history.at(-1)?.turn ?? 0;
  const nextScheduledTurn =
    state.currentTurn <= state.turnLimit ? String(state.currentTurn) : "none";
  return [
    "# AI Battle Manifest",
    "",
    `- Match ID: \`${state.matchId}\``,
    `- Battle repo: \`${state.battleRepo}\``,
    `- Scratch root: \`${state.scratchRoot}\``,
    `- Participant A workspace: \`${state.participantAWorkspaceDir}\``,
    `- Participant B workspace: \`${state.participantBWorkspaceDir}\``,
    `- Judge workspace: \`${state.judgeWorkspaceDir}\``,
    `- Rules source: \`${state.rulesPath}\``,
    `- Transcript: \`${state.transcriptPath}\``,
    `- Message log: \`${state.messageLogPath}\``,
    `- Participant A: \`${state.participantAName}\``,
    `- Participant B: \`${state.participantBName}\``,
    `- Judge: \`${state.judgeName}\``,
    `- Questions per participant: \`${state.questionCount}\``,
    `- Sudden-death questions per participant: \`${state.suddenDeathQuestionCount}\``,
    `- Standard turns: \`${state.standardTurns}\``,
    `- Sudden-death turns: \`${state.suddenDeathTurns}\``,
    `- Current phase: \`${formatPhaseLabel(state.phase)}\``,
    `- Latest completed turn: \`${latestCompletedTurn}\``,
    `- Next scheduled turn: \`${nextScheduledTurn}\``,
    `- Current score: \`${formatScore(state.scores, state.participantAName, state.participantBName)}\``,
    `- Result if stopped now: \`${finalResult(state)}\``,
  ].join("\n");
}

function renderQuestionFile(
  selection: TurnSelection,
  publicQuestion: string,
  scores: ScoreState,
): string {
  return [
    `# ${selection.askerName} Question`,
    "",
    `- Phase: \`${formatPhaseLabel(selection.state.phase)}\``,
    `- Turn: \`${selection.state.currentTurn}\``,
    `- Asker: \`${selection.askerName}\``,
    `- Answerer: \`${selection.answererName}\``,
    `- Score before turn: \`${formatScore(scores, selection.state.participantAName, selection.state.participantBName)}\``,
    "",
    "## Question",
    "",
    publicQuestion,
    "",
  ].join("\n");
}

function renderAskForfeitQuestionFile(
  selection: TurnSelection,
  scores: ScoreState,
  reason: string,
): string {
  return [
    `# ${selection.askerName} Question`,
    "",
    `- Phase: \`${formatPhaseLabel(selection.state.phase)}\``,
    `- Turn: \`${selection.state.currentTurn}\``,
    `- Asker: \`${selection.askerName}\``,
    `- Answerer: \`${selection.answererName}\``,
    `- Score before turn: \`${formatScore(scores, selection.state.participantAName, selection.state.participantBName)}\``,
    "",
    "## Question",
    "",
    "(no valid question was returned before the deadline)",
    "",
    "## Runner Note",
    "",
    reason,
    "",
  ].join("\n");
}

function renderJudgeNoteFile(selection: TurnSelection, judgeNote: JudgeNote): string {
  return [
    `# ${selection.askerName} Judge Note`,
    "",
    `- Phase: \`${formatPhaseLabel(selection.state.phase)}\``,
    `- Turn: \`${selection.state.currentTurn}\``,
    `- For judge only: \`true\``,
    "",
    "## Intended Answer",
    "",
    judgeNote.intendedAnswer,
    "",
    "## Validity Reason",
    "",
    judgeNote.validityReason,
    "",
    "## Comparative Edge Reason",
    "",
    judgeNote.edgeReason,
    "",
    "## Evidence Paths",
    "",
    ...(judgeNote.evidencePaths?.length
      ? judgeNote.evidencePaths.map((entry) => `- \`${entry}\``)
      : ["- `(none)`"]),
    "",
  ].join("\n");
}

function renderAskForfeitJudgeNoteFile(selection: TurnSelection, reason: string): string {
  return [
    `# ${selection.askerName} Judge Note`,
    "",
    `- Phase: \`${formatPhaseLabel(selection.state.phase)}\``,
    `- Turn: \`${selection.state.currentTurn}\``,
    `- For judge only: \`true\``,
    "",
    "## Intended Answer",
    "",
    "(no valid hidden answer key was returned before the deadline)",
    "",
    "## Validity Reason",
    "",
    reason,
    "",
    "## Comparative Edge Reason",
    "",
    "(no comparative edge rationale was returned before the deadline)",
    "",
    "## Evidence Paths",
    "",
    "- `(none)`",
    "",
  ].join("\n");
}

function renderAnswerFile(turn: WrittenQuestion, answer: AnswerResponse): string {
  return [
    `# ${turn.answererName} Answer`,
    "",
    `- Phase: \`${formatPhaseLabel(turn.state.phase)}\``,
    `- Turn: \`${turn.state.currentTurn}\``,
    `- Asked by: \`${turn.askerName}\``,
    "",
    "## Answer",
    "",
    answer.answer,
    "",
    "## Flaw Claim",
    "",
    answer.flawClaim ?? "(none)",
    "",
    "## Artifact Paths",
    "",
    ...(answer.artifactPaths.length > 0
      ? answer.artifactPaths.map((entry) => `- \`${entry}\``)
      : ["- `(none)`"]),
    "",
  ].join("\n");
}

function renderAskForfeitAnswerFile(selection: TurnSelection): string {
  return [
    `# ${selection.answererName} Answer`,
    "",
    `- Phase: \`${formatPhaseLabel(selection.state.phase)}\``,
    `- Turn: \`${selection.state.currentTurn}\``,
    `- Asked by: \`${selection.askerName}\``,
    "",
    "## Answer",
    "",
    "(no answer was required because the asker forfeited before submitting a valid question)",
    "",
    "## Flaw Claim",
    "",
    "(none)",
    "",
    "## Artifact Paths",
    "",
    "- `(none)`",
    "",
  ].join("\n");
}

function renderAnswerForfeitFile(turn: WrittenQuestion, reason: string): string {
  return [
    `# ${turn.answererName} Answer`,
    "",
    `- Phase: \`${formatPhaseLabel(turn.state.phase)}\``,
    `- Turn: \`${turn.state.currentTurn}\``,
    `- Asked by: \`${turn.askerName}\``,
    "",
    "## Answer",
    "",
    "(no valid answer was returned before the deadline)",
    "",
    "## Flaw Claim",
    "",
    "(none)",
    "",
    "## Artifact Paths",
    "",
    "- `(none)`",
    "",
    "## Runner Note",
    "",
    reason,
    "",
  ].join("\n");
}

function renderRulingFile(
  turn: WrittenAnswer,
  judgeResponse: JudgeResponse,
  askerDelta: number,
  answererDelta: number,
): string {
  const nextScores = updatedScoresAfterRuling(turn.state.scores, {
    state: turn.state,
    turn: turn.state.currentTurn,
    phase: turn.state.phase,
    askerRole: turn.askerRole,
    answererRole: turn.answererRole,
    askerName: turn.askerName,
    answererName: turn.answererName,
    outcome: judgeResponse.outcome,
    reason: judgeResponse.reason,
    askerDelta,
    answererDelta,
    rulingPath: "",
    questionPath: turn.questionPath,
    judgeNotePath: turn.judgeNotePath,
    answerPath: turn.answerPath,
  });

  return [
    `# ${turn.state.judgeName} Ruling`,
    "",
    `- Phase: \`${formatPhaseLabel(turn.state.phase)}\``,
    `- Turn: \`${turn.state.currentTurn}\``,
    `- Asker: \`${turn.askerName}\``,
    `- Answerer: \`${turn.answererName}\``,
    `- Outcome: \`${judgeResponse.outcome}\``,
    `- Asker delta: \`${askerDelta}\``,
    `- Answerer delta: \`${answererDelta}\``,
    `- Score after turn: \`${formatScore(nextScores, turn.state.participantAName, turn.state.participantBName)}\``,
    "",
    "## Reason",
    "",
    judgeResponse.reason,
    "",
  ].join("\n");
}

function renderSyntheticRulingFile(state: MatchState, ruling: WrittenRuling): string {
  const nextScores = updatedScoresAfterRuling(state.scores, ruling);
  return [
    `# ${state.judgeName} Ruling`,
    "",
    `- Phase: \`${formatPhaseLabel(state.phase)}\``,
    `- Turn: \`${state.currentTurn}\``,
    `- Asker: \`${ruling.askerName}\``,
    `- Answerer: \`${ruling.answererName}\``,
    `- Outcome: \`${ruling.outcome}\``,
    `- Asker delta: \`${ruling.askerDelta}\``,
    `- Answerer delta: \`${ruling.answererDelta}\``,
    `- Score after turn: \`${formatScore(nextScores, state.participantAName, state.participantBName)}\``,
    `- Issued by runner: \`true\``,
    "",
    "## Reason",
    "",
    ruling.reason,
    "",
  ].join("\n");
}

function renderScoreboard(state: MatchState): string {
  const result = finalResult(state);

  return [
    "# Final Scoreboard",
    "",
    `- Participant A: \`${state.participantAName}\``,
    `- Participant B: \`${state.participantBName}\``,
    `- Judge: \`${state.judgeName}\``,
    `- Final score: \`${formatScore(state.scores, state.participantAName, state.participantBName)}\``,
    `- Result: \`${result}\``,
    `- Standard turns played: \`${Math.min(state.history.length, state.standardTurns)}\``,
    `- Sudden-death turns played: \`${Math.max(state.history.length - state.standardTurns, 0)}\``,
    "",
    "## Turn Summary",
    "",
    ...state.history.map(
      (turn) =>
        `- Turn ${turn.turn}: ${turn.askerName} asked, ${turn.answererName} answered, outcome \`${turn.outcome}\`, score now \`${formatScore(turn.updatedScores, state.participantAName, state.participantBName)}\``,
    ),
    "",
  ].join("\n");
}
