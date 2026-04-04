function formatPhaseLabel(phase) {
  return phase === "sudden_death" ? "sudden death" : "standard match";
}

function parseJsonObject(text) {
  const trimmed = String(text ?? "").trim();
  if (!trimmed.startsWith("{") || !trimmed.endsWith("}")) {
    return undefined;
  }
  try {
    return JSON.parse(trimmed);
  } catch {
    return undefined;
  }
}

function fenced(code, info = "") {
  return `\`\`\`${info}\n${String(code ?? "").trimEnd()}\n\`\`\``;
}

function normalizeToolCommand(input) {
  if (!input || typeof input !== "object") {
    return undefined;
  }
  if (typeof input.command === "string") {
    return input.command;
  }
  if (Array.isArray(input.command)) {
    return input.command.map((part) => String(part)).join(" ");
  }
  return undefined;
}

function normalizeToolDescription(part) {
  const input = part?.ToolUse?.input;
  if (input && typeof input === "object" && typeof input.description === "string") {
    return input.description.trim();
  }
  const rawInput = part?.ToolUse?.raw_input;
  if (typeof rawInput === "string") {
    try {
      const parsed = JSON.parse(rawInput);
      if (parsed && typeof parsed.description === "string") {
        return parsed.description.trim();
      }
    } catch {
      // ignore
    }
  }
  const name = part?.ToolUse?.name;
  if (typeof name === "string" && name.trim().length > 0) {
    return name.split("\n")[0].trim();
  }
  return undefined;
}

function normalizeToolResultText(result) {
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

function buildAgentReplyBody(agentMessage) {
  const lines = [];
  const content = Array.isArray(agentMessage?.content) ? agentMessage.content : [];
  const toolResults = agentMessage?.tool_results && typeof agentMessage.tool_results === "object"
    ? agentMessage.tool_results
    : {};
  let structuredData;

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
      const thinkingText = String(part.Thinking?.text ?? "").trim();
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
      const resultText = normalizeToolResultText(toolResults[tool.id]);
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
}) {
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
}) {
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
}) {
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

function renderEventHeading(event) {
  if (event.eventType === "runner_prompt") {
    return `match runner to ${event.recipientName}`;
  }
  if (event.eventType === "agent_reply") {
    return `${event.speakerName} to match runner`;
  }
  return "match runner";
}

function renderPromptTypeLine(event) {
  return event.promptType ? `Type: ${event.promptType}` : null;
}

export function renderTranscript(meta, events) {
  const lines = [
    "# Hearing Transcript",
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

  const repliesByPrompt = new Map();
  for (const event of events) {
    if (event.eventType === "agent_reply" && event.promptEventId) {
      const existing = repliesByPrompt.get(event.promptEventId) ?? [];
      existing.push(event);
      repliesByPrompt.set(event.promptEventId, existing);
    }
  }

  let currentSection = null;
  const renderedReplies = new Set();

  const ensureSection = (event) => {
    const section =
      event.turn === 0
        ? "setup"
        : `turn-${event.turn}-${event.phase ?? "standard"}`;
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

  const renderSingleEvent = (event) => {
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
