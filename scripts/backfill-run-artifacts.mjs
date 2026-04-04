#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";

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

  const events = [];
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
    const answererName = stripCode(questionFields["Answerer"] ?? answerFields["Asked by"] ?? rulingFields["Answerer"]);
    const questionText = extractSection(questionMd, "Question");
    const intendedAnswer = extractSection(judgeNoteMd, "Intended Answer");
    const validityReason = extractSection(judgeNoteMd, "Validity Reason");
    const evidencePaths = parseListSection(extractSection(judgeNoteMd, "Evidence Paths"));
    const answerText = extractSection(answerMd, "Answer");
    const flawClaimText = extractSection(answerMd, "Flaw Claim");
    const artifactPaths = parseListSection(extractSection(answerMd, "Artifact Paths"));
    const outcome = stripCode(rulingFields["Outcome"]);
    const reason = extractSection(rulingMd, "Reason");
    const scoreAfterTurn = stripCode(rulingFields["Score after turn"]);
    const askerDelta = Number(stripCode(rulingFields["Asker delta"]));
    const answererDelta = Number(stripCode(rulingFields["Answerer delta"]));
    const issuedByRunner = stripCode(rulingFields["Issued by runner"] ?? "") === "true";

    latestScore = scoreAfterTurn || latestScore;
    latestTurn = Math.max(latestTurn, turn);

    const questionJson = {
      publicQuestion: questionText,
      judgeNote: {
        intendedAnswer,
        validityReason,
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

    events.push({
      eventId: `${turnDirName}-${roleStemFromFile(questionMdName, "question")}-question`,
      turn,
      phase,
      speakerName: askerName,
      speakerRole: "participant",
      recipientName: `${answererName} and ${judgeName}`,
      eventType: "question_submission",
      body: [
        `Question from ${askerName} to ${answererName}.`,
        "",
        "Public question:",
        "",
        questionText,
        "",
        "Hidden judge note:",
        "",
        `- Intended answer: ${intendedAnswer}`,
        `- Validity reason: ${validityReason}`,
        `- Evidence paths: ${formatPathListInline(evidencePaths)}`,
      ].join("\n"),
      structuredData: questionJson,
    });

    events.push({
      eventId: `${turnDirName}-${roleStemFromFile(answerMdName, "answer")}-answer`,
      turn,
      phase,
      speakerName: answererName,
      speakerRole: "participant",
      recipientName: `${askerName} and ${judgeName}`,
      eventType: "answer_submission",
      body: [
        `Answer from ${answererName} to ${askerName}.`,
        "",
        "Answer:",
        "",
        answerText,
        "",
        `Flaw claim: ${normalizeOptionalText(flawClaimText) ?? "(none)"}`,
        `Artifact paths: ${formatPathListInline(artifactPaths)}`,
      ].join("\n"),
      structuredData: answerJson,
    });

    events.push({
      eventId: `${turnDirName}-${roleStemFromFile(rulingMdName, "ruling")}-ruling`,
      turn,
      phase,
      speakerName: issuedByRunner ? "match runner" : judgeName,
      speakerRole: issuedByRunner ? "runner" : "judge",
      recipientName: `${askerName} and ${answererName}`,
      eventType: issuedByRunner ? "automatic_ruling" : "judge_ruling",
      body: [
        `${issuedByRunner ? "Automatic ruling" : `Ruling`} for turn ${turn}.`,
        "",
        `Outcome: ${outcome}`,
        `Reason: ${reason}`,
        `Score change: ${askerName} ${formatSignedDelta(askerDelta)}, ${answererName} ${formatSignedDelta(answererDelta)}`,
        `Score after turn: ${scoreAfterTurn}`,
      ].join("\n"),
      structuredData: rulingJson,
    });
  }

  const messageLogPath = path.join(matchDir, "messages.jsonl");
  await fs.writeFile(
    messageLogPath,
    `${events.map((event) => JSON.stringify(event)).join("\n")}\n`,
    "utf8",
  );

  const transcriptPath = path.join(matchDir, "transcript.md");
  await fs.writeFile(
    transcriptPath,
    renderTranscript({
      matchId,
      participantAName,
      participantBName,
      judgeName,
      currentScore: latestScore,
      latestCompletedTurn: latestTurn,
      events,
    }),
    "utf8",
  );
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

function roleStemFromFile(fileName, suffix) {
  return fileName.replace(new RegExp(`-${suffix}\\.(md|json)$`), "");
}

function formatSignedDelta(value) {
  return value > 0 ? `+${value}` : String(value);
}

function formatPathListInline(paths) {
  return paths.length > 0 ? paths.map((entry) => `\`${entry}\``).join(", ") : "(none)";
}

function formatPhaseLabel(phase) {
  return phase === "standard" ? "standard match" : "sudden death";
}

function transcriptHeading(event) {
  switch (event.eventType) {
    case "question_submission":
      return `${event.speakerName} question package`;
    case "answer_submission":
      return `${event.speakerName} answer package`;
    case "judge_ruling":
      return `${event.speakerName} ruling`;
    case "automatic_ruling":
      return "Automatic ruling from the match runner";
    default:
      throw new Error(`Unsupported event type: ${event.eventType}`);
  }
}

function renderTranscript({ matchId, participantAName, participantBName, judgeName, currentScore, latestCompletedTurn, events }) {
  const lines = [
    "# Hearing Transcript",
    "",
    `- Match ID: \`${matchId}\``,
    `- Participant A: \`${participantAName}\``,
    `- Participant B: \`${participantBName}\``,
    `- Judge: \`${judgeName}\``,
    `- Current score: \`${currentScore}\``,
    `- Latest completed turn: \`${latestCompletedTurn}\``,
    "",
    "This file is generated by the flow from the per-turn messages that participants and the judge submitted.",
    "",
  ];

  if (events.length === 0) {
    lines.push("No participant or judge messages have been recorded yet.", "");
    return `${lines.join("\n").trimEnd()}\n`;
  }

  let currentTurn = null;
  for (const event of events) {
    if (event.turn !== currentTurn) {
      if (currentTurn !== null) {
        lines.push("");
      }
      lines.push(`## Turn ${event.turn} (${formatPhaseLabel(event.phase)})`, "");
      currentTurn = event.turn;
    }

    lines.push(`### ${transcriptHeading(event)}`, "");
    lines.push(event.body, "");

    if (event.structuredData !== undefined) {
      lines.push("```json", JSON.stringify(event.structuredData, null, 2), "```", "");
    }
  }

  return `${lines.join("\n").trimEnd()}\n`;
}

await main();
