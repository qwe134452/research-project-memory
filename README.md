# research-project-memory

Version: 2.0

`research-project-memory` is a Codex skill for maintaining layered memory in long-running, directory-based research projects.

It creates and maintains:

- `AGENTS.md`: project-local operating protocol.
- `PROJECT_MEMORY.md`: project-level coordinator memory.
- `CONVERSATIONS_MEMORY/`: conversation-specific memory files for parallel work branches. Each file is named after the Codex thread title.

The design is intended for projects that may be discussed across multiple Codex conversations, such as academic papers, research reports, grant applications, literature reviews, data analysis, and other sustained writing or research work.

## Installation

Install from a GitHub repository with:

```bash
python3 /Users/wangli/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo qwe134452/research-project-memory --path . --name research-project-memory
```

The repository root is the skill directory itself, so `--path . --name research-project-memory` is required.

## Recommended Global Rule

Add a short rule to the global `AGENTS.md` so Codex triggers the skill in directory-based projects:

```markdown
项目上下文初始化规则：当 Codex 在用户创建、指定或进入的目录型项目中对话时，应触发 `research-project-memory` skill，检查并在缺失时初始化该目录下的 `AGENTS.md`、`PROJECT_MEMORY.md` 和 `CONVERSATIONS_MEMORY/`。即使该目录为空，也按目录型项目处理。普通对话或没有明确项目目录承载的临时问答不执行该规则。具体项目规则、总体记忆和对话分支记忆分别交由项目自身的 `AGENTS.md`、`PROJECT_MEMORY.md` 与 `CONVERSATIONS_MEMORY/` 承载。
```

## Memory Model

`PROJECT_MEMORY.md` is the coordinator. It records project-level context, cross-branch decisions, authoritative files, branch status, dependencies, and risks.

`CONVERSATIONS_MEMORY/` contains one memory file per conversation or work branch. Each file records the branch task, materials used, effective judgments, outputs, open issues, and items that may need project-level synchronization. The filename should match the Codex thread title; if the thread title changes, rerun the initializer with the new title so the file and project index can be renamed.

Project `AGENTS.md` is not a progress log. It should contain only stable project-wide operating rules.

## Context Cost Policy

The initializer is lightweight and should run at the start of each substantive project conversation. It only checks local metadata and small files.

After initialization, Codex should read only:

- `AGENTS.md`
- `PROJECT_MEMORY.md`
- the current thread's file in `CONVERSATIONS_MEMORY/`

Other conversation memory files should not be loaded by default. Load them only when the user explicitly asks, names specific branches, or the current task depends on another branch.

## Files

```text
research-project-memory/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── init_project_memory.py
```

## Script Usage

Run the initializer directly if needed:

```bash
python3 scripts/init_project_memory.py /path/to/project
```

The script is idempotent and should be run at the start of each substantive project conversation. It reads `CODEX_THREAD_ID` from the environment and looks up the current Codex thread title from local Codex state when available. The conversation memory filename follows that thread title, preserving normal spaces and replacing only filesystem-unsafe characters. Rerunning the script after a thread-title change will rename the memory file and update the project index.

If automatic detection is unavailable, pass the title explicitly:

```bash
python3 scripts/init_project_memory.py /path/to/project --thread-title "引言重构"
```

If the Codex thread title changes and automatic detection is unavailable but a stable thread id is available:

```bash
python3 scripts/init_project_memory.py /path/to/project --thread-title "新的线程标题" --thread-id "<stable-thread-id>"
```

If no stable thread id is available, pass the existing memory file explicitly:

```bash
python3 scripts/init_project_memory.py /path/to/project --thread-title "新的线程标题" --conversation-file "CONVERSATIONS_MEMORY/旧的线程标题.md"
```

The script preserves existing content. It creates missing files, appends missing required sections, creates `CONVERSATIONS_MEMORY/`, creates or renames a conversation-specific memory file, and updates the `PROJECT_MEMORY.md` index.
