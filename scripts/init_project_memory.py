#!/usr/bin/env python3
"""Initialize AGENTS.md and PROJECT_MEMORY.md for a research project."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


AGENTS_TEMPLATE = """# AGENTS.md

本文件只对当前研究项目生效，用于补充全局 AGENTS.md。全局规则仍然有效；本文件只记录本项目额外需要遵守的工作方式。

## 项目工作定位

Codex 在本项目中应以社会科学研究助理的方式工作，重点维护研究问题、概念口径、材料状态、论证结构、文件安全和写作连续性。项目可能涉及人口学、社会学、政策研究、课题申请、研究报告或学术论文写作。

## 写作与分析要求

- 使用正式、规范、平实有力的中文学术表达。
- 涉及人口、民族、政策、治理等议题时，使用审慎、准确、符合中国政治话语体系和学术规范的表述。
- 研究问题、文献综述、数据方法、研究发现、讨论和政策建议应保持功能区分。
- 不把未经验证的经验描述上升为机制性结论，不用空泛判断替代材料、数据和文献支撑。
- 优先提供可直接进入论文、报告或课题文本的连贯段落；操作说明、文件状态和待办事项可用简明条目。

## 项目记忆规则

- 开始实质性工作前，先查看 `PROJECT_MEMORY.md`，理解项目背景、当前任务、关键决策和文件状态。
- 当研究题目、研究问题、文章边界、概念口径、章节结构、文件状态或未完成任务发生重要变化时，及时更新 `PROJECT_MEMORY.md`。
- 如果思路发生变化，不直接删除旧判断；应标注为“已调整”或“已替代”，并说明新判断及原因。

## 文件安全

- 不覆盖原始 Word、PPT、数据、脚本或重要草稿，除非用户明确要求直接修改。
- 直接编辑文件后，必须通过文本抽取、结构检查、脚本运行或其他合适方式验证结果。
"""


PROJECT_MEMORY_TEMPLATE = """# PROJECT_MEMORY.md

本文件用于保存当前研究项目的持续性记忆，帮助 Codex 在上下文压缩后恢复项目背景、关键决策、术语口径、文件状态和未完成任务。它不是聊天记录，应只记录对后续工作有实际影响的信息。

## 1. Project Overview

- 项目名称：
- 项目类型：论文 / 研究报告 / 课题申请 / 文献综述 / 数据分析 / 其他
- 研究领域：
- 当前目标：
- 初始化日期：{today}

## 2. Research Questions and Scope

- 当前研究问题：
- 当前成果边界：
- 暂不处理或已经排除的内容：

## 3. Concepts, Terms, and Expression Rules

- 核心概念：
- 变量、分类或指标口径：
- 需要保持一致的表述：
- 不宜使用或需要避免的表述：

## 4. Key Decisions

- {today}: 初始化项目记忆文件。后续重要研究判断、结构调整和写作口径应记录在此。

## 5. File Map and Status

- 主稿文件：
- 数据文件：
- 分析脚本：
- 参考材料：
- 输出文件：

## 6. Current Task

- 当前正在推进：
- 下一步优先事项：

## 7. Open Issues

- 尚未确定的问题：

## 8. Risks and Cautions

- 容易混淆或过度承诺的地方：
- 与既有成果、政策表述或数据限制相关的注意事项：

## 9. Update Log

- {today}: 创建 `AGENTS.md` 和 `PROJECT_MEMORY.md` 的项目上下文维护框架。
"""


REQUIRED_MEMORY_HEADINGS = [
    "## 1. Project Overview",
    "## 2. Research Questions and Scope",
    "## 3. Concepts, Terms, and Expression Rules",
    "## 4. Key Decisions",
    "## 5. File Map and Status",
    "## 6. Current Task",
    "## 7. Open Issues",
    "## 8. Risks and Cautions",
    "## 9. Update Log",
]


REQUIRED_AGENTS_HEADINGS = [
    "## 项目工作定位",
    "## 写作与分析要求",
    "## 项目记忆规则",
    "## 文件安全",
]


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


def create_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", default=".")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    agents_path = project_dir / "AGENTS.md"
    memory_path = project_dir / "PROJECT_MEMORY.md"

    created_agents = create_if_missing(agents_path, AGENTS_TEMPLATE)
    created_memory = create_if_missing(
        memory_path, PROJECT_MEMORY_TEMPLATE.format(today=today)
    )

    missing_agents = [] if created_agents else append_missing_sections(
        agents_path, REQUIRED_AGENTS_HEADINGS
    )
    missing_memory = [] if created_memory else append_missing_sections(
        memory_path, REQUIRED_MEMORY_HEADINGS
    )

    print(f"Project directory: {project_dir}")
    print(f"AGENTS.md: {'created' if created_agents else 'already existed'}")
    if missing_agents:
        print(f"AGENTS.md appended sections: {', '.join(missing_agents)}")
    print(f"PROJECT_MEMORY.md: {'created' if created_memory else 'already existed'}")
    if missing_memory:
        print(f"PROJECT_MEMORY.md appended sections: {', '.join(missing_memory)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
