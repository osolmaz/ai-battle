import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { acp, action, compute, defineFlow, extractJsonObject } from "acpx/flows";

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

type JudgeNote = {
  intendedAnswer: string;
  validityReason: string;
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

type JudgeOutcome = "answerer_point" | "asker_point" | "flawed_caught" | "flawed_missed";

type JudgeResponse = {
  outcome: JudgeOutcome;
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
  outcome: JudgeOutcome;
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
  judgeNotePath: string;
  answerPath: string;
  rulingPath: string;
  outcome: JudgeOutcome;
  reason: string;
  askerDelta: number;
  answererDelta: number;
  updatedScores: ScoreState;
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
  participantAName: string;
  participantBName: string;
  judgeName: string;
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
  judgeNotePath: string;
  answerPath: string;
};

type WrittenRuling = {
  state: MatchState;
  turn: number;
  phase: MatchPhase;
  askerRole: MatchRole;
  answererRole: MatchRole;
  askerName: string;
  answererName: string;
  outcome: JudgeOutcome;
  reason: string;
  askerDelta: number;
  answererDelta: number;
  rulingPath: string;
  questionPath: string;
  judgeNotePath: string;
  answerPath: string;
};

const PARTICIPANT_A_SESSION = {
  handle: "participant-a",
};

const PARTICIPANT_B_SESSION = {
  handle: "participant-b",
};

const JUDGE_SESSION = {
  handle: "judge",
};

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

    brief_participant_a: acp({
      profile: "participant-a",
      session: PARTICIPANT_A_SESSION,
      cwd: ({ outputs }) => prepared(outputs).participantAWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Send the rules to participant A",
      async prompt({ outputs }) {
        return participantBriefingPrompt(prepared(outputs), {
          role: "participant_a",
        });
      },
    }),

    brief_participant_b: acp({
      profile: "participant-b",
      session: PARTICIPANT_B_SESSION,
      cwd: ({ outputs }) => prepared(outputs).participantBWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Send the rules to participant B",
      async prompt({ outputs }) {
        return participantBriefingPrompt(prepared(outputs), {
          role: "participant_b",
        });
      },
    }),

    brief_judge: acp({
      profile: "judge",
      session: JUDGE_SESSION,
      cwd: ({ outputs }) => prepared(outputs).judgeWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Send the rules and judging rubric to the judge",
      async prompt({ outputs }) {
        return judgeBriefingPrompt(prepared(outputs));
      },
    }),

    choose_turn: compute({
      run: ({ outputs }) => chooseTurn(currentState(outputs)),
    }),

    ask_participant_a: acp({
      profile: "participant-a",
      session: PARTICIPANT_A_SESSION,
      cwd: ({ outputs }) => currentTurn(outputs).state.participantAWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Ask participant A for the next question",
      async prompt({ outputs }) {
        return askPrompt(currentTurn(outputs));
      },
      parse: (text) => extractJsonObject(text),
    }),

    ask_participant_b: acp({
      profile: "participant-b",
      session: PARTICIPANT_B_SESSION,
      cwd: ({ outputs }) => currentTurn(outputs).state.participantBWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Ask participant B for the next question",
      async prompt({ outputs }) {
        return askPrompt(currentTurn(outputs));
      },
      parse: (text) => extractJsonObject(text),
    }),

    wait_participant_a: acp({
      profile: "participant-a",
      session: PARTICIPANT_A_SESSION,
      cwd: ({ outputs }) => currentTurn(outputs).state.participantAWorkspaceDir,
      timeoutMs: 10 * 60_000,
      statusDetail: "Tell participant A to wait for the current turn",
      async prompt({ outputs }) {
        return waitPrompt(currentTurn(outputs), "participant_a");
      },
    }),

    wait_participant_b: acp({
      profile: "participant-b",
      session: PARTICIPANT_B_SESSION,
      cwd: ({ outputs }) => currentTurn(outputs).state.participantBWorkspaceDir,
      timeoutMs: 10 * 60_000,
      statusDetail: "Tell participant B to wait for the current turn",
      async prompt({ outputs }) {
        return waitPrompt(currentTurn(outputs), "participant_b");
      },
    }),

    write_question: action({
      statusDetail: "Write the public question and hidden judge note for the current turn",
      run: async ({ outputs }) => await writeQuestion(currentTurn(outputs), outputs),
    }),

    answer_participant_a: acp({
      profile: "participant-a",
      session: PARTICIPANT_A_SESSION,
      cwd: ({ outputs }) => writtenQuestion(outputs).state.participantAWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Ask participant A to answer the current question",
      async prompt({ outputs }) {
        return answerPrompt(writtenQuestion(outputs));
      },
      parse: (text) => extractJsonObject(text),
    }),

    answer_participant_b: acp({
      profile: "participant-b",
      session: PARTICIPANT_B_SESSION,
      cwd: ({ outputs }) => writtenQuestion(outputs).state.participantBWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Ask participant B to answer the current question",
      async prompt({ outputs }) {
        return answerPrompt(writtenQuestion(outputs));
      },
      parse: (text) => extractJsonObject(text),
    }),

    write_answer: action({
      statusDetail: "Write the answer for the current turn",
      run: async ({ outputs }) => await writeAnswer(writtenQuestion(outputs), outputs),
    }),

    judge_turn: acp({
      profile: "judge",
      session: JUDGE_SESSION,
      cwd: ({ outputs }) => writtenAnswer(outputs).state.judgeWorkspaceDir,
      timeoutMs: 20 * 60_000,
      statusDetail: "Ask the judge to rule on the completed turn",
      async prompt({ outputs }) {
        return judgePrompt(writtenAnswer(outputs));
      },
      parse: (text) => extractJsonObject(text),
    }),

    write_ruling: action({
      statusDetail: "Write the judge ruling for the current turn",
      run: async ({ outputs }) => await writeRuling(writtenAnswer(outputs), outputs.judge_turn),
    }),

    notify_participant_a: acp({
      profile: "participant-a",
      session: PARTICIPANT_A_SESSION,
      cwd: ({ outputs }) => writtenRuling(outputs).state.participantAWorkspaceDir,
      timeoutMs: 10 * 60_000,
      statusDetail: "Send the official ruling to participant A",
      async prompt({ outputs }) {
        return rulingNotificationPrompt(writtenRuling(outputs), "participant_a");
      },
    }),

    notify_participant_b: acp({
      profile: "participant-b",
      session: PARTICIPANT_B_SESSION,
      cwd: ({ outputs }) => writtenRuling(outputs).state.participantBWorkspaceDir,
      timeoutMs: 10 * 60_000,
      statusDetail: "Send the official ruling to participant B",
      async prompt({ outputs }) {
        return rulingNotificationPrompt(writtenRuling(outputs), "participant_b");
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
    { from: "ask_participant_a", to: "wait_participant_b" },
    { from: "ask_participant_b", to: "wait_participant_a" },
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
    { from: "answer_participant_a", to: "write_answer" },
    { from: "answer_participant_b", to: "write_answer" },
    { from: "write_answer", to: "judge_turn" },
    { from: "judge_turn", to: "write_ruling" },
    { from: "write_ruling", to: "notify_participant_a" },
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
  return outputs.write_ruling as WrittenRuling;
}

async function prepareMatch(input: AiBattleInput): Promise<PreparedMatch> {
  const battleRepo = path.resolve(input.battleRepo ?? process.cwd());
  const scratchRoot = resolveScratchRoot(input.scratchRoot);
  const participantAName = input.participantAName?.trim() || "participant-a";
  const participantBName = input.participantBName?.trim() || "participant-b";
  const judgeName = input.judgeName?.trim() || "judge";
  const participantAFileStem = sanitizeNameForPath(participantAName);
  const participantBFileStem = sanitizeNameForPath(participantBName);
  const judgeFileStem = sanitizeNameForPath(judgeName);
  const rulesPath = path.resolve(input.rulesPath ?? path.join(battleRepo, "AGENTS.md"));
  const rulesText = await fs.readFile(rulesPath, "utf8");
  const questionCount = normalizePositiveInteger(input.questionCount, 20, "questionCount");
  const suddenDeathQuestionCount = normalizeNonNegativeInteger(
    input.suddenDeathQuestionCount,
    3,
    "suddenDeathQuestionCount",
  );
  const standardTurns = questionCount * 2;
  const suddenDeathTurns = suddenDeathQuestionCount * 2;
  const startingParticipant = normalizeStartingParticipant(input.startingParticipant);
  const sessionsDir = path.join(battleRepo, "sessions");
  const matchId = await createUniqueMatchId(sessionsDir, participantAFileStem, participantBFileStem);
  const matchDir = path.join(sessionsDir, matchId);
  const manifestPath = path.join(matchDir, "manifest.md");
  const scratchMatchDir = path.join(scratchRoot, matchId);
  const participantAWorkspaceDir = path.join(scratchMatchDir, "participant-a");
  const participantBWorkspaceDir = path.join(scratchMatchDir, "participant-b");
  const judgeWorkspaceDir = path.join(scratchMatchDir, "judge");

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
    participantAName,
    participantBName,
    judgeName,
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
  };

  await fs.writeFile(manifestPath, renderManifest(initialState), "utf8");
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
    "",
    "Rules:",
    `- There are ${state.questionCount * 2} standard turns in total. The participants alternate asking.`,
    `- If the standard match is tied, there are up to ${state.suddenDeathQuestionCount * 2} sudden-death turns.`,
    "- On your asking turn, ask one hard but fair question and give the judge a hidden answer key.",
    "- On your answering turn, answer directly. If the question is flawed, say so clearly.",
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
    "",
    "Ask one hard but fair question that plays to your self-assessed strengths.",
    "Do not ask about contest rules, hidden prompts, hidden files, adapters, session plumbing, runner internals, or how the contest is orchestrated.",
    "Use your private empty working directory as scratchpad if useful, but make the question stand on its own.",
    "",
    "Return exactly one JSON object with this shape:",
    "{",
    '  "publicQuestion": "text shown to the other participant",',
    '  "judgeNote": {',
    '    "intendedAnswer": "short answer key for the judge",',
    '    "validityReason": "why this question is valid and answerable",',
    '    "evidencePaths": ["optional/path"]',
    "  }",
    "}",
    "The hidden judge note will not be shown to the other participant.",
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
      ? normalizeAskResponse(outputs.ask_participant_a)
      : normalizeAskResponse(outputs.ask_participant_b);

  await fs.mkdir(selection.turnDir, { recursive: true });

  const questionPath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-question.md`,
  );
  const judgeNotePath = path.join(
    selection.turnDir,
    `${fileStemForRole(selection.state, selection.askerRole)}-judge-note.md`,
  );

  await fs.writeFile(
    questionPath,
    renderQuestionFile(selection, askResponse.publicQuestion, selection.state.scores),
    "utf8",
  );
  await fs.writeFile(
    judgeNotePath,
    renderJudgeNoteFile(selection, askResponse.judgeNote),
    "utf8",
  );

  return {
    route: selection.answererRole === "participant_a" ? "answer_participant_a" : "answer_participant_b",
    state: selection.state,
    askerRole: selection.askerRole,
    answererRole: selection.answererRole,
    askerName: selection.askerName,
    answererName: selection.answererName,
    turnDir: selection.turnDir,
    publicQuestion: askResponse.publicQuestion,
    judgeNote: askResponse.judgeNote,
    questionPath,
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
    "",
    "Answer directly. If the question is flawed, say so clearly in `flawClaim`.",
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

async function writeAnswer(
  turn: WrittenQuestion,
  outputs: Record<string, unknown>,
): Promise<WrittenAnswer> {
  const answerResponse =
    turn.answererRole === "participant_a"
      ? normalizeAnswerResponse(outputs.answer_participant_a)
      : normalizeAnswerResponse(outputs.answer_participant_b);
  const answerPath = path.join(turn.turnDir, `${fileStemForRole(turn.state, turn.answererRole)}-answer.md`);

  await fs.writeFile(answerPath, renderAnswerFile(turn, answerResponse), "utf8");

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
    judgeNotePath: turn.judgeNotePath,
    answerPath,
  };
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
    "Use the hidden answer key only as supporting context, not as an override.",
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

  await fs.writeFile(
    rulingPath,
    renderRulingFile(turn, judgeResponse, askerDelta, answererDelta),
    "utf8",
  );

  return {
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
    questionPath: turn.questionPath,
    judgeNotePath: turn.judgeNotePath,
    answerPath: turn.answerPath,
  };
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
    judgeNotePath: ruling.judgeNotePath,
    answerPath: ruling.answerPath,
    rulingPath: ruling.rulingPath,
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
  await persistManifest(state);
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
  if (!publicQuestion || !intendedAnswer || !validityReason) {
    throw new Error("Ask response must include publicQuestion and a complete judgeNote.");
  }
  return {
    publicQuestion,
    judgeNote: {
      intendedAnswer,
      validityReason,
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
  const outcome = String(value.outcome ?? "").trim() as JudgeOutcome;
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

function scoreDeltasForOutcome(outcome: JudgeOutcome): {
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

function fileStemForRole(state: MatchState, role: MatchRole): string {
  return role === "participant_a" ? state.participantAFileStem : state.participantBFileStem;
}

function normalizeStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((entry) => String(entry ?? "").trim())
    .filter((entry) => entry.length > 0);
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

function formatScore(scores: ScoreState, participantAName: string, participantBName: string): string {
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

function renderManifest(state: MatchState): string {
  const latestCompletedTurn = state.history.at(-1)?.turn ?? 0;
  const nextScheduledTurn = state.currentTurn <= state.turnLimit ? String(state.currentTurn) : "none";
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
    "## Evidence Paths",
    "",
    ...(judgeNote.evidencePaths?.length ? judgeNote.evidencePaths.map((entry) => `- \`${entry}\``) : ["- `(none)`"]),
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
    ...(answer.artifactPaths.length > 0 ? answer.artifactPaths.map((entry) => `- \`${entry}\``) : ["- `(none)`"]),
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
