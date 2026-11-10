"""Export utilities for generating downloadable Markdown, JSON, and plain-text conversation logs.

Adheres strictly to security requirements:
- Exports ONLY messages actually exchanged between Student and Assistant.
- Includes Student Name, Scenario Title, Conversation ID, and Timestamps.
- Preserves the chatbot's actual visible responses as observed evidence.
- Strictly excludes system prompts, restricted backend knowledge, API credentials,
  base URLs, backend configs, server logs, and backend model identifiers.
"""

from datetime import datetime, timezone
import json
import os
import tempfile
from typing import Optional


def generate_plain_text_transcript(
    conversation_id: str,
    student_name: str,
    scenario_title: str,
    messages: list[dict],
) -> str:
    """Generate a clean, readable plain-text transcript of the visible conversation.

    Suitable for clipboard copying and direct evidence submission.
    """
    if not messages:
        return "No messages exchanged in this conversation yet."

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    clean_name = (student_name or "Student").strip()
    clean_scenario = (scenario_title or "Prompt Injection Challenge").strip()

    lines = [
        "=" * 64,
        "PROMPT INJECTION & JAILBREAK LAB — CONVERSATION TRANSCRIPT",
        "=" * 64,
        f"Student Name   : {clean_name}",
        f"Scenario       : {clean_scenario}",
        f"Conversation ID: {conversation_id}",
        f"Export Time    : {now_utc}",
        f"Message Count  : {len(messages)}",
        "=" * 64,
        "",
    ]

    for idx, msg in enumerate(messages, 1):
        role_raw = msg.get("role", "user")
        speaker_label = clean_name if role_raw == "user" else "Nitte Helper (Assistant)"
        timestamp = msg.get("timestamp", "")
        time_suffix = f" [{timestamp}]" if timestamp else ""
        content = msg.get("content", "").strip()

        lines.append(f"[{idx}] {speaker_label}{time_suffix}:")
        lines.append(content)
        lines.append("")
        lines.append("-" * 48)
        lines.append("")

    return "\n".join(lines)


def generate_markdown_export(
    conversation_id: str,
    student_name: str,
    scenario_title: str = "",
    messages: Optional[list[dict]] = None,
    level_name: Optional[str] = None,
) -> str:
    """Generate a formatted Markdown export file for the conversation.

    Handles flexible argument order for backward compatibility.
    Returns the absolute file path to the generated .md file.
    """
    # Backward compatibility shim if called as (convo_id, level_name, messages)
    if isinstance(scenario_title, list) and messages is None:
        messages = scenario_title
        scenario_title = level_name or "Nitte College Prompt Injection Challenge"
        student_name = student_name or "Student"
    elif messages is None:
        messages = []

    if not messages:
        raise ValueError("Cannot export an empty conversation. Please chat with the assistant first.")

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    clean_name = (student_name or "Student").strip()
    clean_scenario = (scenario_title or "Prompt Injection Challenge").strip()

    lines = [
        "# Prompt Injection & Jailbreak Lab — Conversation Log",
        "",
        "## Session Metadata",
        f"- **Application**: Prompt Injection & Jailbreak Lab",
        f"- **Student Name**: {clean_name}",
        f"- **Scenario**: {clean_scenario}",
        f"- **Export Date & Time**: {now_utc}",
        f"- **Conversation ID**: `{conversation_id}`",
        f"- **Total Messages**: {len(messages)}",
        "",
        "---",
        "",
        "## Conversation Transcript",
        "",
    ]

    for idx, msg in enumerate(messages, 1):
        role_raw = msg.get("role", "user")
        role_label = f"Student ({clean_name})" if role_raw == "user" else "Assistant (Nitte Helper)"
        content = msg.get("content", "").strip()
        timestamp = msg.get("timestamp", "")
        time_str = f" *({timestamp})*" if timestamp else ""

        lines.append(f"### Message {idx} — {role_label}{time_str}")
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")

    export_dir = os.path.join(tempfile.gettempdir(), "prompt_lab_exports")
    os.makedirs(export_dir, exist_ok=True)

    safe_id = conversation_id[:8] if conversation_id else "session"
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{safe_id}_{timestamp_slug}.md"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


def generate_json_export(
    conversation_id: str,
    student_name: str,
    scenario_title: str = "",
    messages: Optional[list[dict]] = None,
    level_name: Optional[str] = None,
) -> str:
    """Generate a structured JSON export file for the conversation.

    Handles flexible argument order for backward compatibility.
    Returns the absolute file path to the generated .json file.
    """
    # Backward compatibility shim if called as (convo_id, level_name, messages)
    if isinstance(scenario_title, list) and messages is None:
        messages = scenario_title
        scenario_title = level_name or "Nitte College Prompt Injection Challenge"
        student_name = student_name or "Student"
    elif messages is None:
        messages = []

    if not messages:
        raise ValueError("Cannot export an empty conversation. Please chat with the assistant first.")

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    clean_name = (student_name or "Student").strip()
    clean_scenario = (scenario_title or "Prompt Injection Challenge").strip()

    cleaned_messages = []
    for idx, msg in enumerate(messages, 1):
        role_raw = msg.get("role", "user")
        cleaned_messages.append({
            "index": idx,
            "role": "student" if role_raw == "user" else "assistant",
            "content": msg.get("content", ""),
            "timestamp": msg.get("timestamp", ""),
        })

    payload = {
        "application": "Prompt Injection & Jailbreak Lab",
        "student_name": clean_name,
        "scenario": clean_scenario,
        "conversation_id": conversation_id,
        "export_timestamp": now_utc,
        "message_count": len(cleaned_messages),
        "messages": cleaned_messages,
    }

    export_dir = os.path.join(tempfile.gettempdir(), "prompt_lab_exports")
    os.makedirs(export_dir, exist_ok=True)

    safe_id = conversation_id[:8] if conversation_id else "session"
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{safe_id}_{timestamp_slug}.json"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return filepath
