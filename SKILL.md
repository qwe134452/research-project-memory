---
name: research-project-memory
description: Initialize and maintain layered project memory for long-running directory-based research projects. Use when Codex works inside a user-created or user-selected project directory, including a new empty folder, and needs AGENTS.md, PROJECT_MEMORY.md, and CONVERSATIONS_MEMORY/ files to coordinate multiple conversations in the same project. Do not use for ordinary chat or tasks without a meaningful project directory.
---

# Research Project Memory

Version: 2.0

## Purpose

Use this skill to maintain continuity across multiple Codex conversations in the same research project. It creates a layered memory system:

- `AGENTS.md`: project-local operating protocol, not a duplicate of global writing rules.
- `PROJECT_MEMORY.md`: project-level coordinator memory.
- `CONVERSATIONS_MEMORY/`: one memory file per conversation or work branch.

The skill is designed for social science research projects, including academic papers, research reports, grant applications, literature reviews, data analysis, and long-form writing work.

## Activation Rule

When the conversation occurs inside a user-created or user-selected directory, treat that directory as a project directory unless it is clearly ordinary chat, tool setup, account/environment discussion, the user home folder, Desktop root, Downloads, or a temporary directory.

Apply this rule even when the directory is empty. A new empty folder may be the beginning of a project, and early research ideas may need to be preserved.

## Initialization

At the start of every substantive project conversation, inspect the project root and run the initializer. Run it even when the memory files already exist, because it is idempotent and also synchronizes the conversation memory filename with the current Codex thread title.

```bash
python3 <path-to-this-skill>/scripts/init_project_memory.py .
```

The script detects `CODEX_THREAD_ID` from the environment and reads the current Codex thread title from local Codex state when available. The conversation memory filename should match the thread title, for example `CONVERSATIONS_MEMORY/引言重构.md`. Normal spaces are preserved; filesystem-unsafe characters are replaced.

If automatic detection is unavailable, pass the title explicitly:

```bash
python3 <path-to-this-skill>/scripts/init_project_memory.py . --thread-title "<current Codex thread title>"
```

The script preserves existing content. It creates missing files, appends missing standard sections, creates `CONVERSATIONS_MEMORY/`, creates or selects a conversation-specific memory file, and renames that file when the Codex thread title has changed.

When the Codex thread title changes, run the script again. If the environment exposes the same `CODEX_THREAD_ID`, the script should detect the new title, rename the old conversation memory file, and update the `PROJECT_MEMORY.md` index.

If automatic detection is unavailable, pass the new title and a stable identifier if available:

```bash
python3 <path-to-this-skill>/scripts/init_project_memory.py . --thread-title "<new Codex thread title>" --thread-id "<stable thread id>"
```

If no stable thread id is available but the previous memory file is known, pass it explicitly:

```bash
python3 <path-to-this-skill>/scripts/init_project_memory.py . --thread-title "<new Codex thread title>" --conversation-file "CONVERSATIONS_MEMORY/<old title>.md"
```

The script will rename the old conversation memory file and update the `PROJECT_MEMORY.md` index.

## Context Loading Policy

Running the initializer is cheap and should happen at the start of each substantive project conversation. It only performs local metadata checks and small file updates; it does not require loading all memory files into the model context.

After initialization, load only:

- project `AGENTS.md`, if present;
- `PROJECT_MEMORY.md`;
- the current thread's file under `CONVERSATIONS_MEMORY/`.

Do not read other conversation memory files by default. Read them only when the user explicitly asks, names specific files or branches, or the current task clearly depends on another branch listed in `PROJECT_MEMORY.md`. If cross-branch review is needed, prefer loading only the named or directly relevant files.

## File Roles

Use `AGENTS.md` only for stable project-local rules. Update it rarely. Write only rules that the whole project must follow for a long time, such as fixed terminology, non-overwrite rules, authoritative source rules, or user-confirmed project-wide requirements.

Use `PROJECT_MEMORY.md` as the project coordinator. It should record only project-level information:

- project snapshot, overall research question, scope, and current stage;
- global terms, expression rules, and important boundaries that affect more than one branch;
- index of conversation memory files and their status;
- project-level decisions and reasons;
- cross-branch dependencies, conflicts, or items requiring user decision;
- authoritative files, material status, overall next steps, and project-level risks.

Use `CONVERSATIONS_MEMORY/<thread-title>.md` as the current conversation's branch memory. The filename should follow the Codex thread title and should be renamed when the thread title changes. It should record only branch-level information:

- this conversation's task scope and relation to the whole project;
- files, data, literature, user instructions, or materials used in this branch;
- effective judgments with reason, scope, and status;
- outputs, file changes, verification status, and branch-level open issues;
- items that may need synchronization to `PROJECT_MEMORY.md`.

## Distillation Rules

Record only information that will affect later work. Do not write chat transcripts, routine process notes, ordinary attempts, rejected wording that no longer matters, or large copied source text.

For each durable memory item, prefer this structure:

```markdown
- YYYY-MM-DD｜决策：...
  理由：...
  影响：...
  状态：有效 / 已替代 / 待确认。
```

When an idea changes, do not silently delete the old decision if later work may depend on it. Mark it as superseded and record the new decision and reason.

## Synchronization Rule

Default to updating only the current conversation memory.

Update `PROJECT_MEMORY.md` only when the conversation produces project-level impact:

- the overall topic, research question, title, scope, or article/report structure changes;
- a term, variable, policy expression, file status, or source rule must apply across branches;
- a branch is completed, paused, superseded, or depends on another branch;
- a conflict appears between two branches;
- an output becomes authoritative for the project;
- the user explicitly says a rule or decision should apply to the whole project.

Update project `AGENTS.md` only when a stable project-wide operating rule is confirmed. Do not use it for progress, task status, or temporary decisions.

## Working Sequence

1. Run the initializer to check structure and synchronize the current Codex thread title.
2. Read project `AGENTS.md` if present.
3. Read `PROJECT_MEMORY.md` to understand the project-level context.
4. Create or select the current conversation memory under `CONVERSATIONS_MEMORY/`, using the Codex thread title as the filename.
5. Read only the current conversation memory unless cross-branch work is needed.
6. Work on the user's request.
7. Update the current conversation memory at meaningful checkpoints.
8. Sync a short summary to `PROJECT_MEMORY.md` only when the synchronization rule is met.
9. Mention changed memory files briefly in the final response.

## If Existing Old Files Are Found

If an older project has only `PROJECT_MEMORY.md` and no `CONVERSATIONS_MEMORY/`, create the directory and start a new conversation memory. Do not split old memory automatically unless the user asks. Treat old project memory as the initial coordinator memory and gradually clean it as future work proceeds.
