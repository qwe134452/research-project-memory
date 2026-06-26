#!/usr/bin/env python3
"""Initialize layered project memory files for a Codex research project."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from datetime import date
from pathlib import Path


AGENTS_TEMPLATE = """# AGENTS.md

本文件只记录当前项目的本地工作协议。全局写作规范、学术表达要求和通用文件处理规则由全局 `AGENTS.md` 负责；本文件不重复全局规则。

## 项目记忆协议

- 开始实质性工作前，先读取 `PROJECT_MEMORY.md`，理解项目总体目标、当前阶段、关键决策和分支任务状态。
- 每次开始或继续项目对话时，应触发 `research-project-memory` skill，以检查记忆结构并同步当前 Codex 线程标题。
- 每个对话应在 `CONVERSATIONS_MEMORY/` 下创建或维护一份专属记忆文件。
- 对话记忆文件名应与 Codex 线程标题保持一致；线程标题改变时，应同步重命名对应的对话记忆文件，并更新 `PROJECT_MEMORY.md` 中的索引。
- 默认只读取 `PROJECT_MEMORY.md` 和当前线程对应的对话记忆文件；除非用户明确要求、点名相关分支，或当前任务明显依赖其他分支，不主动读取其他对话记忆文件。
- 普通推进只更新本对话记忆；只有形成项目级决策、跨分支影响、权威文件状态变化或重要风险时，才同步更新 `PROJECT_MEMORY.md`。
- 更新记忆时只记录会影响后续工作的内容，不写聊天流水账。
- 项目 `AGENTS.md` 只沉淀长期稳定、整个项目都必须遵守的工作规则；项目进度和阶段性判断写入 `PROJECT_MEMORY.md` 或对话记忆。

## 项目专属规则

当前暂无额外项目规则。只有用户明确确认某项要求对本项目长期有效时，才写入本节。

## 文件与材料约定

当前暂无固定文件约定。主稿、数据、参考材料和输出文件的动态状态优先记录在 `PROJECT_MEMORY.md`；只有长期稳定的文件安全规则或目录约定，才写入本节。
"""


PROJECT_MEMORY_TEMPLATE = """# PROJECT_MEMORY.md

本文件是项目总控记忆，用于统筹各个对话分支的推进脉络。它不是聊天记录，也不替代 `CONVERSATIONS_MEMORY/` 下的分支记忆；只记录会影响整个项目理解、跨分支协同和后续决策的信息。

## 1. Project Snapshot

- 项目名称：
- 项目类型：论文 / 研究报告 / 课题申请 / 文献综述 / 数据分析 / 其他
- 研究领域：
- 当前总目标：
- 当前阶段：
- 初始化日期：{today}

## 2. Overall Research Questions and Scope

- 当前总体研究问题：
- 当前成果边界：
- 已排除或暂不处理的内容：
- 已被替代的重要方向：

## 3. Global Terms and Expression Rules

- 影响多个分支的核心概念：
- 全项目统一的变量、分类或指标口径：
- 需要保持一致的政策表述或术语：
- 不宜使用或需要避免的表述：

## 4. Conversation Memory Index

记录各对话分支的任务、状态和相互关系。只写索引和摘要，不写分支细节。

| 对话记忆文件 | 分支任务 | 状态 | 关联与影响 |
|---|---|---|---|
{conversation_index_row}

## 5. Project-Level Decisions

- {today}: 初始化分层项目记忆结构。`PROJECT_MEMORY.md` 负责总控，`CONVERSATIONS_MEMORY/` 负责各对话分支记忆。

## 6. Cross-Branch Dependencies and Conflicts

- 跨分支依赖：
- 口径冲突或待统一事项：
- 需要用户定夺的问题：

## 7. Authoritative Files and Material Status

- 主稿文件：
- 数据文件：
- 分析脚本：
- 参考材料：
- 输出文件：
- 已过期或仅供参考的材料：

## 8. Overall Next Steps

- 项目层面的下一步：
- 需要优先协调的分支：

## 9. Risks and Cautions

- 容易混淆或过度承诺的地方：
- 与既有成果、政策表述或数据限制相关的注意事项：

## 10. Update Log

- {today}: 创建项目总控记忆、对话记忆目录和首个对话记忆文件。
"""


CONVERSATION_TEMPLATE = """<!-- codex-thread-id: {thread_id} -->
# {title}

本文件是单个对话的分支记忆，只记录本对话中对后续工作有实际影响的信息。它不替代 `PROJECT_MEMORY.md`；只有形成项目级决策、跨分支影响、权威文件状态变化或重要风险时，才把摘要同步到 `PROJECT_MEMORY.md`。

## 1. Conversation Identity

- Codex 线程标题：{title}
- Codex 线程标识：{thread_id_label}
- 对话主题：{title}
- 对话记忆文件：`CONVERSATIONS_MEMORY/{filename}`
- 创建日期：{today}
- 当前状态：进行中
- 所属项目关系：

## 2. Task Scope

- 本对话负责：
- 本对话不负责：
- 与项目总目标的关系：

## 3. Materials Used

- 已读取或使用的文件：
- 已采用的用户口径：
- 已参考的数据、文献或材料：

## 4. Effective Judgments

记录经过筛选后仍然有效的判断。每条尽量包含“结论、理由、适用范围、状态”。

- {today}: 初始化本对话记忆。后续只记录会影响继续工作的判断，不记录聊天流水账。

## 5. Outputs and File Changes

- 已产出的文本：
- 已创建、修改或验证的文件：
- 尚未验证的输出：

## 6. Branch-Level Open Issues

- 本分支仍需处理：
- 需要用户确认：

## 7. Items to Sync to PROJECT_MEMORY

只有当本对话产生项目级影响时，才在这里列出需要同步到 `PROJECT_MEMORY.md` 的摘要。

- 暂无。

## 8. Update Log

- {today}: 创建本对话分支记忆文件。
"""


REQUIRED_AGENTS_HEADINGS = [
    "## 项目记忆协议",
    "## 项目专属规则",
    "## 文件与材料约定",
]


REQUIRED_PROJECT_HEADINGS = [
    "## 1. Project Snapshot",
    "## 2. Overall Research Questions and Scope",
    "## 3. Global Terms and Expression Rules",
    "## 4. Conversation Memory Index",
    "## 5. Project-Level Decisions",
    "## 6. Cross-Branch Dependencies and Conflicts",
    "## 7. Authoritative Files and Material Status",
    "## 8. Overall Next Steps",
    "## 9. Risks and Cautions",
    "## 10. Update Log",
]


REQUIRED_CONVERSATION_HEADINGS = [
    "## 1. Conversation Identity",
    "## 2. Task Scope",
    "## 3. Materials Used",
    "## 4. Effective Judgments",
    "## 5. Outputs and File Changes",
    "## 6. Branch-Level Open Issues",
    "## 7. Items to Sync to PROJECT_MEMORY",
    "## 8. Update Log",
]


def slugify(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|#`]+", "-", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:48] or "conversation"


def detect_codex_thread_id() -> str | None:
    value = os.environ.get("CODEX_THREAD_ID", "").strip()
    return value or None


def title_from_session_index(thread_id: str | None) -> str | None:
    if not thread_id:
        return None
    path = Path.home() / ".codex" / "session_index.jsonl"
    if not path.exists():
        return None
    title = None
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if item.get("id") == thread_id and item.get("thread_name"):
                    title = str(item["thread_name"]).strip()
    except OSError:
        return None
    return title or None


def title_from_state_db(thread_id: str | None) -> str | None:
    if not thread_id:
        return None
    candidates = [
        Path.home() / ".codex" / "state_5.sqlite",
        Path.home() / ".codex" / "sqlite" / "state_5.sqlite",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=1)
            try:
                row = conn.execute(
                    "SELECT title FROM threads WHERE id = ? LIMIT 1",
                    (thread_id,),
                ).fetchone()
            finally:
                conn.close()
        except sqlite3.Error:
            continue
        if row and row[0]:
            return str(row[0]).strip() or None
    return None


def detect_codex_thread_title(thread_id: str | None) -> str | None:
    return title_from_session_index(thread_id) or title_from_state_db(thread_id)


def unique_path(directory: Path, stem: str, suffix: str = ".md") -> Path:
    candidate = directory / f"{stem}{suffix}"
    if not candidate.exists():
        return candidate
    counter = 2
    while True:
        candidate = directory / f"{stem}-{counter:02d}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_thread_id(path: Path) -> str | None:
    text = read_text_if_exists(path)
    match = re.search(r"<!--\s*codex-thread-id:\s*(.*?)\s*-->", text)
    if match:
        value = match.group(1).strip()
        return value or None
    match = re.search(r"^- Codex 线程标识：(.+)$", text, flags=re.MULTILINE)
    if match:
        value = match.group(1).strip()
        if value and value != "未提供":
            return value
    return None


def find_conversation_by_thread_id(directory: Path, thread_id: str | None) -> Path | None:
    if not thread_id:
        return None
    for path in sorted(directory.glob("*.md")):
        if extract_thread_id(path) == thread_id:
            return path
    return None


def resolve_conversation_file(conversations_dir: Path, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        if path.parts and path.parts[0] == "CONVERSATIONS_MEMORY":
            path = conversations_dir.parent / path
        else:
            path = conversations_dir / path
    path = path.resolve()
    if path.exists() and path.is_file():
        return path
    return None


def create_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def append_missing_sections(path: Path, required_headings: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    missing = [heading for heading in required_headings if heading not in text]
    if not missing:
        return []

    additions = ["\n\n<!-- research-project-memory: missing standard sections appended -->"]
    for heading in missing:
        additions.append(f"\n\n{heading}\n\n- 待补充：")
    path.write_text(text.rstrip() + "".join(additions) + "\n", encoding="utf-8")
    return missing


def replace_or_add_line(text: str, prefix: str, replacement: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}.*$", flags=re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    identity_heading = "## 1. Conversation Identity"
    if identity_heading in text:
        return text.replace(identity_heading, identity_heading + "\n\n" + replacement, 1)
    return text.rstrip() + "\n" + replacement + "\n"


def refresh_conversation_metadata(
    path: Path,
    title: str,
    filename: str,
    thread_id: str | None,
) -> None:
    text = read_text_if_exists(path)
    marker = f"<!-- codex-thread-id: {thread_id or ''} -->"
    if text.startswith("<!-- codex-thread-id:"):
        text = re.sub(r"^<!--\s*codex-thread-id:\s*.*?\s*-->", marker, text, count=1)
    else:
        text = marker + "\n" + text

    text = re.sub(r"^# .*$", f"# {title}", text, count=1, flags=re.MULTILINE)
    text = replace_or_add_line(text, "- Codex 线程标题：", f"- Codex 线程标题：{title}")
    text = replace_or_add_line(
        text,
        "- Codex 线程标识：",
        f"- Codex 线程标识：{thread_id or '未提供'}",
    )
    text = replace_or_add_line(text, "- 对话主题：", f"- 对话主题：{title}")
    text = replace_or_add_line(
        text,
        "- 对话记忆文件：",
        f"- 对话记忆文件：`CONVERSATIONS_MEMORY/{filename}`",
    )
    path.write_text(text, encoding="utf-8")


def update_project_index_row(
    memory_path: Path,
    conversation_file: str,
    title: str,
    old_conversation_file: str | None = None,
) -> bool:
    text = memory_path.read_text(encoding="utf-8")
    row = f"| `CONVERSATIONS_MEMORY/{conversation_file}` | {title} | 进行中 | 待补充 |"
    if old_conversation_file and old_conversation_file in text:
        pattern = re.compile(
            r"\| `CONVERSATIONS_MEMORY/"
            + re.escape(old_conversation_file)
            + r"` \| ([^|]*) \| ([^|]*) \| ([^|]*) \|"
        )
        match = pattern.search(text)
        if match:
            status = match.group(2).strip() or "进行中"
            relation = match.group(3).strip() or "待补充"
            replacement = (
                f"| `CONVERSATIONS_MEMORY/{conversation_file}` | {title} | {status} | {relation} |"
            )
            text = pattern.sub(replacement, text, count=1)
            memory_path.write_text(text, encoding="utf-8")
            return True
        text = text.replace(old_conversation_file, conversation_file)
        memory_path.write_text(text, encoding="utf-8")
        return True

    if conversation_file in text:
        pattern = re.compile(
            r"\| `CONVERSATIONS_MEMORY/"
            + re.escape(conversation_file)
            + r"` \| ([^|]*) \| ([^|]*) \| ([^|]*) \|"
        )
        match = pattern.search(text)
        if match:
            status = match.group(2).strip() or "进行中"
            relation = match.group(3).strip() or "待补充"
            replacement = (
                f"| `CONVERSATIONS_MEMORY/{conversation_file}` | {title} | {status} | {relation} |"
            )
            text = pattern.sub(replacement, text, count=1)
            memory_path.write_text(text, encoding="utf-8")
            return True
        return False
    marker = "|---|---|---|---|"
    if marker in text:
        marker_pos = text.index(marker) + len(marker)
        next_heading_pos = text.find("\n## ", marker_pos)
        if next_heading_pos == -1:
            text = text.rstrip() + "\n" + row + "\n"
        else:
            table_text = text[:next_heading_pos].rstrip()
            text = table_text + "\n" + row + "\n\n" + text[next_heading_pos + 1 :]
    else:
        text = text.rstrip() + "\n\n## Conversation Memory Index\n\n| 对话记忆文件 | 分支任务 | 状态 | 关联与影响 |\n|---|---|---|---|\n" + row + "\n"
    memory_path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--conversation-title",
        default=None,
        help="Backward-compatible alias for --thread-title.",
    )
    parser.add_argument(
        "--thread-title",
        default=None,
        help="Current Codex thread title. The conversation memory filename will match this title.",
    )
    parser.add_argument(
        "--thread-id",
        default=None,
        help="Stable Codex thread identifier. Use it to rename the same conversation memory when the thread title changes.",
    )
    parser.add_argument(
        "--conversation-file",
        default=None,
        help="Existing conversation memory file to reuse or rename when no thread id is available.",
    )
    parser.add_argument(
        "--no-conversation",
        action="store_true",
        help="Only initialize project-level files and directory; do not create a conversation memory file.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    agents_path = project_dir / "AGENTS.md"
    project_memory_path = project_dir / "PROJECT_MEMORY.md"
    conversations_dir = project_dir / "CONVERSATIONS_MEMORY"

    conversations_dir.mkdir(exist_ok=True)

    thread_id = (
        args.thread_id.strip()
        if args.thread_id and args.thread_id.strip()
        else detect_codex_thread_id()
    )
    detected_title = detect_codex_thread_title(thread_id)
    title = (
        args.thread_title
        or args.conversation_title
        or detected_title
        or "未命名对话"
    ).strip() or "未命名对话"
    slug = slugify(title)
    conversation_path = None
    conversation_filename = f"{slug}.md"
    conversation_index_row = "| 待创建 | 待补充 | 待补充 | 待补充 |"
    old_conversation_filename = None
    renamed_conversation = False

    if not args.no_conversation:
        existing_by_thread = find_conversation_by_thread_id(conversations_dir, thread_id)
        existing_by_file = resolve_conversation_file(conversations_dir, args.conversation_file)
        conversation_path = existing_by_thread or existing_by_file
        target_path = conversations_dir / f"{slug}.md"

        if conversation_path is not None:
            old_conversation_filename = conversation_path.name
            if conversation_path.resolve() != target_path.resolve():
                if target_path.exists() and target_path.resolve() != conversation_path.resolve():
                    target_thread_id = extract_thread_id(target_path)
                    if thread_id and target_thread_id and target_thread_id != thread_id:
                        target_path = unique_path(conversations_dir, slug)
                conversation_path.rename(target_path)
                conversation_path = target_path
                renamed_conversation = True
        else:
            if target_path.exists() and thread_id:
                target_thread_id = extract_thread_id(target_path)
                if target_thread_id and target_thread_id != thread_id:
                    target_path = unique_path(conversations_dir, slug)
            conversation_path = target_path

        conversation_filename = conversation_path.name
        conversation_index_row = f"| `CONVERSATIONS_MEMORY/{conversation_filename}` | {title} | 进行中 | 待补充 |"

    created_agents = create_if_missing(agents_path, AGENTS_TEMPLATE)
    created_project_memory = create_if_missing(
        project_memory_path,
        PROJECT_MEMORY_TEMPLATE.format(
            today=today,
            conversation_index_row=conversation_index_row,
        ),
    )

    missing_agents = [] if created_agents else append_missing_sections(
        agents_path, REQUIRED_AGENTS_HEADINGS
    )
    missing_project = [] if created_project_memory else append_missing_sections(
        project_memory_path, REQUIRED_PROJECT_HEADINGS
    )

    created_conversation = False
    missing_conversation = []
    if conversation_path is not None:
        created_conversation = create_if_missing(
            conversation_path,
            CONVERSATION_TEMPLATE.format(
                title=title,
                filename=conversation_filename,
                thread_id=thread_id or "",
                thread_id_label=thread_id or "未提供",
                today=today,
            ),
        )
        missing_conversation = [] if created_conversation else append_missing_sections(
            conversation_path, REQUIRED_CONVERSATION_HEADINGS
        )
        refresh_conversation_metadata(
            conversation_path,
            title=title,
            filename=conversation_filename,
            thread_id=thread_id,
        )
        if not created_project_memory:
            update_project_index_row(
                project_memory_path,
                conversation_filename,
                title,
                old_conversation_file=old_conversation_filename,
            )

    print(f"Project directory: {project_dir}")
    print(f"AGENTS.md: {'created' if created_agents else 'already existed'}")
    if missing_agents:
        print(f"AGENTS.md appended sections: {', '.join(missing_agents)}")
    print(f"PROJECT_MEMORY.md: {'created' if created_project_memory else 'already existed'}")
    if missing_project:
        print(f"PROJECT_MEMORY.md appended sections: {', '.join(missing_project)}")
    print("CONVERSATIONS_MEMORY/: ready")
    if conversation_path is not None:
        print(f"Conversation memory: {conversation_path.name} ({'created' if created_conversation else 'already existed'})")
        if thread_id:
            print(f"Codex thread id: {thread_id}")
        if detected_title:
            print(f"Detected thread title: {detected_title}")
        if renamed_conversation and old_conversation_filename:
            print(f"Conversation memory renamed: {old_conversation_filename} -> {conversation_path.name}")
        if missing_conversation:
            print(f"Conversation memory appended sections: {', '.join(missing_conversation)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
