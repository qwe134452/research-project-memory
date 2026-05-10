# research-project-memory

`research-project-memory` is a Codex skill for initializing and maintaining project-level context files in long-running research projects.

It creates or completes two files in the current project directory:

- `AGENTS.md`: project-specific instructions that supplement global Codex rules.
- `PROJECT_MEMORY.md`: durable project memory for background, decisions, terminology, file status, current tasks, open issues, and risks.

The skill is designed for directory-based research work, including new empty folders. It is useful when a project will involve sustained discussion, writing, revision, data analysis, grant preparation, research reports, academic papers, or literature review work.

## Installation

Install from a GitHub repository with:

```bash
skill-installer --repo <owner>/<repo> --path research-project-memory
```

If the repository root is this folder itself, use the installer path appropriate for that repository layout.

## Recommended Global Rule

Add a short rule to the global `AGENTS.md` so Codex checks for project context files automatically in directory-based projects:

```markdown
项目上下文初始化规则：当 Codex 在用户创建、指定或进入的目录型项目中对话时，应触发 `research-project-memory` skill，检查并在缺失时初始化该目录下的 `AGENTS.md` 和 `PROJECT_MEMORY.md`。即使该目录为空，也按目录型项目处理。普通对话或没有明确项目目录承载的临时问答不执行该规则。
```

## Files

```text
research-project-memory/
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

The script preserves existing content. It creates missing files and appends missing required sections without overwriting project-specific notes.
