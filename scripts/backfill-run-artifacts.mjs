#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import {
  buildAgentReplyEvent,
  buildRunnerNoticeEvent,
  buildRunnerPromptEvent,
  renderTranscript,
} from "../lib/hearing-transcript.js";

async function main() {
  const matchDirArg = process.argv[2];
  if (!matchDirArg) {
    throw new Error("Usage: node scripts/backfill-run-artifacts.mjs <match-dir>");
  }

  const matchDir = path.resolve(matchDirArg);
  const manifestPath = path.join(matchDir, "manifest.md");
  const manifest = await fs.readFile(manifestPath, "utf8");
  const manifestFields = parseBulletFields(manifest);
  const participantAName = stripCode(manifestFields["Participant A"]);
  const participantBName = stripCode(manifestFields["Participant B"]);
  const judgeName = stripCode(manifestFields["Judge"]);
  const matchId = stripCode(manifestFields["Match ID"]);

  const turnDirs = (await fs.readdir(matchDir, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory() && /^turn-\d+$/.test(entry.name))
    .map((entry) => entry.name)
    .sort();

  const turnSummaries = [];
  let latestScore = `${participantAName} 0, ${participantBName} 0`;
  let latestTurn = 0;

  for (const turnDirName of turnDirs) {
    const turnDir = path.join(matchDir, turnDirName);
    const files = (await fs.readdir(turnDir)).sort();

    const questionMdName = requireSingle(files, /-question\.md$/);
    const answerMdName = requireSingle(files, /-answer\.md$/);
    const judgeNoteMdName = requireSingle(files, /-judge-note\.md$/);
    const rulingMdName = requireSingle(files, /-ruling\.md$/);

    const questionMdPath = path.join(turnDir, questionMdName);
    const answerMdPath = path.join(turnDir, answerMdName);
    const judgeNoteMdPath = path.join(turnDir, judgeNoteMdName);
    const rulingMdPath = path.join(turnDir, rulingMdName);

    const questionMd = await fs.readFile(questionMdPath, "utf8");
    const answerMd = await fs.readFile(answerMdPath, "utf8");
    const judgeNoteMd = await fs.readFile(judgeNoteMdPath, "utf8");
    const rulingMd = await fs.readFile(rulingMdPath, "utf8");

    const questionFields = parseBulletFields(questionMd);
    const answerFields = parseBulletFields(answerMd);
    const rulingFields = parseBulletFields(rulingMd);

    const phase = parsePhase(stripCode(questionFields["Phase"] ?? rulingFields["Phase"]));
    const turn = Number(stripCode(questionFields["Turn"] ?? rulingFields["Turn"]));
    const askerName = stripCode(questionFields["Asker"] ?? rulingFields["Asker"]);
    const answererName = stripCode(
      questionFields["Answerer"] ?? answerFields["Asked by"] ?? rulingFields["Answerer"],
    );
    const questionText = extractSection(questionMd, "Question");
    const intendedAnswer = extractSection(judgeNoteMd, "Intended Answer");
    const validityReason = extractSection(judgeNoteMd, "Validity Reason");
    const edgeReason = normalizeOptionalText(extractSection(judgeNoteMd, "Comparative Edge Reason"));
    const evidencePaths = parseListSection(extractSection(judgeNoteMd, "Evidence Paths"));
    const answerText = extractSection(answerMd, "Answer");
    const flawClaimText = extractSection(answerMd, "Flaw Claim");
    const artifactPaths = parseListSection(extractSection(answerMd, "Artifact Paths"));
    const outcome = stripCode(rulingFields["Outcome"]);
    const reason = extractSection(rulingMd, "Reason");
    const scoreAfterTurn = stripCode(rulingFields["Score after turn"]);
    const issuedByRunner = stripCode(rulingFields["Issued by runner"] ?? "") === "true";

    latestScore = scoreAfterTurn || latestScore;
    latestTurn = Math.max(latestTurn, turn);

    const questionJson = {
      publicQuestion: questionText,
      judgeNote: {
        intendedAnswer,
        validityReason,
        ...(edgeReason ? { edgeReason } : {}),
        evidencePaths,
      },
    };
    const answerJson = {
      answer: answerText,
      flawClaim: normalizeOptionalText(flawClaimText),
      artifactPaths,
    };
    const rulingJson = issuedByRunner
      ? {
          issuedByRunner: true,
          outcome,
          reason,
        }
      : {
          outcome,
          reason,
        };

    await fs.writeFile(
      path.join(turnDir, questionMdName.replace(/\.md$/, ".json")),
      `${JSON.stringify(questionJson, null, 2)}\n`,
      "utf8",
    );
    await fs.writeFile(
      path.join(turnDir, answerMdName.replace(/\.md$/, ".json")),
      `${JSON.stringify(answerJson, null, 2)}\n`,
      "utf8",
    );
    await fs.writeFile(
      path.join(turnDir, rulingMdName.replace(/\.md$/, ".json")),
      `${JSON.stringify(rulingJson, null, 2)}\n`,
      "utf8",
    );

    turnSummaries.push({
      turn,
      phase,
      askerName,
      answererName,
      outcome,
      reason,
      issuedByRunner,
    });
  }

  const sessionDir = path.join(matchDir, "acpx-sessions");
  const participantASession = await readSessionMessages(
    path.join(sessionDir, `${participantAName}-participant.session.json`),
  );
  const participantBSession = await readSessionMessages(
    path.join(sessionDir, `${participantBName}-participant.session.json`),
  );
  const judgeSession = await readSessionMessages(
    path.join(sessionDir, `${judgeName}-judge.session.json`),
  );

  const participantAExchanges = buildPromptExchanges(participantASession);
  const participantBExchanges = buildPromptExchanges(participantBSession);
  const judgeExchanges = buildPromptExchanges(judgeSession);

  let eventCounter = 1;
  const nextEventId = (prefix) => `${prefix}-${String(eventCounter++).padStart(6, "0")}`;
  const events = [];

  const appendExchange = (exchange, speakerName, speakerRole, turn, phase, promptType) => {
    if (!exchange) {
      return;
    }
    const promptEventId = nextEventId("prompt");
    events.push(
      buildRunnerPromptEvent({
        eventId: promptEventId,
        turn,
        phase,
        recipientName: speakerName,
        promptType,
        body: exchange.promptText,
      }),
    );
    if (exchange.agentMessage) {
      events.push(
        buildAgentReplyEvent({
          eventId: nextEventId("reply"),
          turn,
          phase,
          speakerName,
          speakerRole,
          promptEventId,
          promptType,
          agentMessage: exchange.agentMessage,
        }),
      );
    }
  };

  appendExchange(
    participantAExchanges.shift(),
    participantAName,
    "participant",
    0,
    "standard",
    "rules briefing",
  );
  appendExchange(
    participantBExchanges.shift(),
    participantBName,
    "participant",
    0,
    "standard",
    "rules briefing",
  );
  appendExchange(
    judgeExchanges.shift(),
    judgeName,
    "judge",
    0,
    "standard",
    "rules briefing",
  );

  for (const summary of turnSummaries) {
    const askerIsA = summary.askerName === participantAName;
    const askerExchanges = askerIsA ? participantAExchanges : participantBExchanges;
    const answererExchanges = askerIsA ? participantBExchanges : participantAExchanges;

    appendExchange(
      askerExchanges.shift(),
      summary.askerName,
      "participant",
      summary.turn,
      summary.phase,
      "asking turn",
    );
    appendExchange(
      answererExchanges.shift(),
      summary.answererName,
      "participant",
      summary.turn,
      summary.phase,
      "wait notice",
    );
    appendExchange(
      answererExchanges.shift(),
      summary.answererName,
      "participant",
      summary.turn,
      summary.phase,
      "answering turn",
    );

    if (!summary.issuedByRunner) {
      appendExchange(
        judgeExchanges.shift(),
        judgeName,
        "judge",
        summary.turn,
        summary.phase,
        "judge turn",
      );
    } else {
      events.push(
        buildRunnerNoticeEvent({
          eventId: nextEventId("notice"),
          turn: summary.turn,
          phase: summary.phase,
          title: "automatic ruling",
          body: [
            `Automatic ruling for turn ${summary.turn}.`,
            "",
            `Outcome: ${summary.outcome}`,
            `Reason: ${summary.reason}`,
          ].join("\n"),
          structuredData: {
            issuedByRunner: true,
            outcome: summary.outcome,
            reason: summary.reason,
          },
        }),
      );
    }

    appendExchange(
      askerExchanges.shift(),
      summary.askerName,
      "participant",
      summary.turn,
      summary.phase,
      "ruling notice",
    );
    appendExchange(
      answererExchanges.shift(),
      summary.answererName,
      "participant",
      summary.turn,
      summary.phase,
      "ruling notice",
    );
  }

  const finalScoreboardPath = path.join(matchDir, "final", "scoreboard.md");
  const finalScoreboardExists = await fileExists(finalScoreboardPath);
  if (finalScoreboardExists) {
    const scoreboard = await fs.readFile(finalScoreboardPath, "utf8");
    const result = stripCode(parseBulletFields(scoreboard)["Result"]);
    events.push(
      buildRunnerNoticeEvent({
        eventId: nextEventId("notice"),
        turn: latestTurn,
        phase: turnSummaries.at(-1)?.phase ?? "standard",
        title: "final result",
        body: [
          "Final scoreboard written.",
          "",
          `Result: ${result}`,
          `Final score: ${latestScore}`,
          `Scoreboard: ${finalScoreboardPath}`,
        ].join("\n"),
        structuredData: {
          result,
          scoreboardPath: finalScoreboardPath,
        },
      }),
    );
  }

  const messageLogPath = path.join(matchDir, "messages.jsonl");
  await fs.writeFile(
    messageLogPath,
    events.length > 0 ? `${events.map((event) => JSON.stringify(event)).join("\n")}\n` : "",
    "utf8",
  );

  const transcriptPath = path.join(matchDir, "transcript.md");
  await fs.writeFile(
    transcriptPath,
    renderTranscript(
      {
        matchId,
        participantAName,
        participantBName,
        judgeName,
        currentScore: latestScore,
        latestCompletedTurn: latestTurn,
      },
      events,
    ),
    "utf8",
  );
}

async function readSessionMessages(filePath) {
  const raw = JSON.parse(await fs.readFile(filePath, "utf8"));
  return Array.isArray(raw.messages) ? raw.messages : [];
}

function buildPromptExchanges(messages) {
  const exchanges = [];
  let pendingUser = null;

  for (const message of messages) {
    if (message?.User) {
      pendingUser = {
        promptText: collectUserText(message.User),
      };
      continue;
    }
    if (message?.Agent) {
      exchanges.push({
        promptText: pendingUser?.promptText ?? "(prompt unavailable)",
        agentMessage: message.Agent,
      });
      pendingUser = null;
    }
  }

  return exchanges;
}

function collectUserText(userMessage) {
  const content = Array.isArray(userMessage?.content) ? userMessage.content : [];
  return content
    .map((part) => (part && typeof part.Text === "string" ? part.Text : ""))
    .filter((text) => text.trim().length > 0)
    .join("\n\n")
    .trim();
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function requireSingle(files, pattern) {
  const matches = files.filter((file) => pattern.test(file));
  if (matches.length !== 1) {
    throw new Error(`Expected exactly one match for ${pattern}, got ${matches.length}`);
  }
  return matches[0];
}

function parseBulletFields(markdown) {
  const fields = {};
  for (const line of markdown.split("\n")) {
    const match = line.match(/^- ([^:]+): (.+)$/);
    if (match) {
      fields[match[1].trim()] = match[2].trim();
    }
  }
  return fields;
}

function stripCode(value) {
  return String(value ?? "").trim().replace(/^`|`$/g, "");
}

function extractSection(markdown, title) {
  const marker = `## ${title}`;
  const start = markdown.indexOf(marker);
  if (start === -1) {
    return "";
  }
  const afterHeading = markdown.indexOf("\n", start);
  const contentStart = markdown.indexOf("\n\n", afterHeading);
  if (contentStart === -1) {
    return "";
  }
  const rest = markdown.slice(contentStart + 2);
  const nextHeadingIndex = rest.search(/\n## /);
  const content = nextHeadingIndex === -1 ? rest : rest.slice(0, nextHeadingIndex);
  return content.trim();
}

function parseListSection(sectionText) {
  const items = sectionText
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("- "))
    .map((line) => line.slice(2).trim().replace(/^`|`$/g, ""));
  return items.filter((item) => item !== "(none)");
}

function normalizeOptionalText(value) {
  const text = String(value ?? "").trim();
  return text === "" || text === "(none)" ? null : text;
}

function parsePhase(label) {
  return label === "sudden death" ? "sudden_death" : "standard";
}

await main();
