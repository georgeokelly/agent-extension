# Skills Catalog / Skill 目录

## What is a Skill? / 什么是 Skill？

A **Skill** is a structured prompt file (`SKILL.md`) that gives a Cursor Agent step-by-step instructions for a repeatable, domain-specific task. When the agent detects a relevant request, it reads the skill file and follows its procedure — effectively extending the agent with new capabilities without modifying core rules.

**Skill** 是一个结构化的提示文件（`SKILL.md`），为 Cursor Agent 提供可复用的、领域特定任务的分步执行指引。Agent 识别到相关请求时，会读取并遵循该文件的流程，从而在不修改核心规则的前提下扩展 Agent 能力。

## How to Use / 如何使用

Skills are deployed by `agent-sync` to all three tools:
- Cursor: `.cursor/skills/<skill-name>/`
- Claude Code: `.claude/skills/<skill-name>/`
- Codex: `.agents/skills/<skill-name>/`

Skill 由 `agent-sync` 同时部署至三个工具：
- Cursor: `.cursor/skills/<skill-name>/`
- Claude Code: `.claude/skills/<skill-name>/`
- Codex: `.agents/skills/<skill-name>/`

Once deployed, reference a skill in your prompt / 部署完成后，直接描述任务即可触发对应 skill：

> "Use the `parse-ncu` skill to analyze this profile."
> "帮我用 `cluster-launch` skill 在 umbriel-b200-236 上启动任务。"

## How to Add / 如何新增

```bash
mkdir -p skills/<skill-name>
# Create skills/<skill-name>/SKILL.md — cross-tool format (Cursor + CC)
git add skills/<skill-name>
git commit -m "Add <skill-name> skill"
```

See [Naming Conventions](../README.md#naming-conventions--命名约定) in the root README for naming rules.

命名规范见根目录 README 的 [Naming Conventions](../README.md#naming-conventions--命名约定) 一节。

### SKILL.md Frontmatter Checklist

Required:
- `name` — skill name / 技能名称
- `description` — concise one-line description / 简洁描述

Recommended (CC-native / CC 原生字段):
- `when_to_use` — tells the model when to trigger this skill / 告诉模型何时触发此 skill
- `argument-hint` — parameter format hint / 参数格式提示

Optional:
- `paths` — conditional activation by file path, use YAML list syntax / 按路径条件激活（使用 YAML 列表格式）
- `allowed-tools` — restrict available tools during skill execution / 限制可用工具
- `context` — `inline` (default) or `fork` (sub-agent) / 内联或子 agent

Note: CC ignores unknown frontmatter fields, Cursor ignores CC-specific fields. One SKILL.md serves both tools.

注意：CC 忽略不认识的字段，Cursor 也忽略 CC 特有字段。一份 SKILL.md 同时服务两个工具。

---

## Catalog / 目录

| Name / 名称 | Description / 描述 | Source / 来源 | License |
|---|---|---|---|
| `drawio` | Generate draw.io diagrams (.drawio) with optional PNG/SVG/PDF export, HTML embedding, and Cursor canvas preview / 生成 draw.io 图表，支持导出、HTML 交互嵌入和 Cursor 内联预览 | [drawio-mcp](https://github.com/jgraph/drawio-mcp) | Apache-2.0 |
| `render-html` | Render self-contained HTML documents from Markdown or HTML with embedded local image assets and arXiv-like academic styling / 从 Markdown 或 HTML 渲染自包含 HTML 文档，支持本地图片内嵌和 arXiv-like 学术排版 | Original, adapted from legacy `convert-md2html` | MIT |
| `visualize-data` | Analyze data and generate 27 chart types using Python (matplotlib/seaborn/plotly/plotext). Includes intent-driven chart selection, data profiling, anti-pattern validation, and multi-option recommendations with pros/cons / 数据可视化：27 种图表生成，意图驱动的图表选择，数据 profiling，反模式检查 | Original | — |
| `write-plan` | Generate implementation plans as executable contracts with contract profiles (delivery/refactor/migration/exploration), dependency graph, checkpoints, verification, decision points, and a runtime stage-claims ledger. Includes validator script and tests / 将实施计划生成为可执行契约：contract profile、dependency graph、checkpoints、verification、decision points 和 runtime stage-claims ledger，附带校验脚本与测试 | Original | — |
| `cli-just` | Expert guidance for Just command runner — create justfiles, write recipes with attributes/dependencies/parameters, configure settings, use built-in terminal-formatting constants, and implement check/write automation patterns / Just 命令运行器指南：创建 justfile、编写带 attribute/依赖/参数的 recipe、配置 settings、使用内置终端格式化常量、实现 check/write 自动化模式 | [PaulRBerg/agent-skills](https://github.com/PaulRBerg/agent-skills/tree/main/skills/cli-just) | MIT |
