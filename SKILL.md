---
name: research-project-memory
description: Initialize and maintain project-level AGENTS.md and PROJECT_MEMORY.md for long-running social science research projects. Use when Codex is working inside any user-chosen project directory, including a new or empty folder, and the conversation concerns population studies, sociology, demography, academic papers, research reports, grant applications, literature reviews, data analysis, document drafting, or other sustained research work. Do not use for ordinary chat outside a directory-based project.
---

# Research Project Memory

## Purpose

Use this skill to keep long-running research projects continuous across context compression. Treat `AGENTS.md` as the project-specific instruction layer and `PROJECT_MEMORY.md` as the durable recovery point for background, decisions, terminology, file status, and unfinished work.

This skill is for the user's social science research work, especially demography, sociology, population studies, policy-facing research reports, grant applications, literature reviews, and academic writing.

## Activation Rule

When the conversation is taking place inside a filesystem directory selected for work, treat that directory as a project directory unless it is clearly a generic location such as the user home folder, Desktop root, Downloads, or a temporary directory.

Apply this rule even when the directory is empty. A new empty folder may be the beginning of a research project, and early discussion of research ideas may need to be preserved.

Do not initialize these files during ordinary chat when there is no meaningful project directory or when the user is not working in a directory-backed project.

## First Action in a Project Directory

Inspect the current working directory. If `AGENTS.md` or `PROJECT_MEMORY.md` is missing, create or update them with:

```bash
python3 <path-to-this-skill>/scripts/init_project_memory.py .
```

The script must preserve existing content. It creates missing files and appends missing required sections without overwriting project-specific notes.

If the current directory is ambiguous, make a conservative judgment from the user's request. If the user is clearly beginning a research project, initialize the files. Ask only when writing files would be surprising or risky.

## AGENTS.md Role

Use `AGENTS.md` only for durable project instructions that supplement global instructions. Keep it concise and practical. Include:

- Project working stance: act as a social science research assistant.
- Writing requirements: formal Chinese academic style, clear logic, careful political and policy language, concrete evidence, no empty praise or overclaiming.
- Project workflow: check `PROJECT_MEMORY.md` at the start of substantive work and update it at key points.
- File safety: do not overwrite original drafts, Word files, PPTs, data, or scripts unless the user explicitly asks.
- Verification: after direct file edits, verify by reading text, inspecting file structure, or running the appropriate tool.

Do not duplicate the user's global AGENTS.md. Add only rules that are specific to the current project.

## PROJECT_MEMORY.md Role

Use `PROJECT_MEMORY.md` as a compact, current reconstruction point. It should help a future Codex instance understand the project after context compression without rereading every prior conversation.

Maintain these sections:

1. Project Overview
2. Research Questions and Scope
3. Concepts, Terms, and Expression Rules
4. Key Decisions
5. File Map and Status
6. Current Task
7. Open Issues
8. Risks and Cautions
9. Update Log

Write memory entries in Chinese unless the project itself is primarily English. Prefer concise paragraphs and dated bullets. Record decisions and rationales, not every chat turn.

## Update Triggers

Update `PROJECT_MEMORY.md` when any of these events occur:

- The user changes or confirms the research topic, title, research question, article boundary, report structure, or grant-application framing.
- Codex produces or substantially revises an introduction, literature review, data-method section, findings section, discussion, policy recommendation, abstract, or application module.
- The user confirms a concept definition, variable construction, classification standard, model choice, citation scope, data source, or wording rule.
- Codex directly edits, creates, renames, or verifies important files.
- The user says phrases such as "记一下", "以后按这个来", "这个口径确定了", "后面都按这个", or equivalent.
- A long conversation reaches a new stage and the memory file would help preserve continuity.

When ideas change, do not erase the old decision silently. Mark it as superseded and record the new decision with the date and reason.

## Writing Discipline

For research memory, preserve the user's intellectual process without turning the file into a transcript. Capture:

- what the project is currently trying to accomplish;
- what has already been ruled in or ruled out;
- which files matter and what state they are in;
- which terms, concepts, and policy expressions must stay consistent;
- what remains unresolved.

Avoid vague notes such as "continued revising" or "discussed literature". State the concrete object and result, for example: "2026-05-10: 确认文章不讨论族际通婚家庭子女民族成份选择，避免与已发表成果重复。"

## Before Final Response

If this skill initialized or updated files, mention the changed files briefly in the final answer. If the directory was not a project directory and no files were created, state that no project memory action was needed.
