# Agent Toolkit / Agent 工具箱

Domain-specific skills for AI coding agents (Cursor, OpenAI Codex, Claude Code).

面向特定领域的 AI 编程代理扩展工具，适用于 Cursor、OpenAI Codex 和 Claude Code。

---

## 1. Overview / 概述

This repo is the **domain-specific extension layer** of the
[agent-rules](https://github.com/georgeokelly/agent-rules) system.

本仓库是 [agent-rules](https://github.com/georgeokelly/agent-rules) 系统的**领域扩展层**。

| Type / 类型 | Location / 路径 | Cursor | Claude Code | Codex |
|---|---|---|---|---|
| **Skills** | `skills/<name>/SKILL.md` | `.cursor/skills/<name>/` | `.claude/skills/<name>/` | `.agents/skills/<name>/` |

**Why a separate repo? / 为什么单独一个仓库？**

- Domain-specific tools evolve independently from core rules / 领域工具与核心规则节奏不同，独立迭代
- Optional — not every project needs every skill / 按需挂载，不是每个项目都需要全部工具
- Mounted as a git submodule in `agent-rules` for versioned, controlled updates / 以 git submodule 形式挂入，版本可控

---

## 2. Directory Structure / 目录结构

```
agent-toolkit/                   ← This repo / 本仓库
└── skills/                      ← Agent Skills (Cursor + Claude Code + Codex)
    └── <skill-name>/
        └── SKILL.md             # Cross-tool skill entry point / 跨工具技能入口
        └── references/          # Optional reference files / 可选参考文件
```

### Naming Conventions / 命名约定

| Type / 类型 | Format / 格式 | Pattern / 模式 | Examples / 示例 |
|---|---|---|---|
| `skill-name` | kebab-case | `<verb>-<noun>` | `parse-ncu`, `profile-kernel`, `cluster-launch` |

- **MUST** use lowercase letters and hyphens only — no underscores, no camelCase / 只允许小写字母和连字符，禁止下划线和驼峰
- **MUST** start with a verb for skills (`parse-`, `profile-`, `run-`) — names should describe *what the skill does* / Skill 名必须以动词开头，体现其功能
- **SHOULD** keep names under 24 characters / 名称建议不超过 24 个字符

---

## 3. Setup / 安装

This repo is consumed via `agent-sync` in `agent-rules`. See that repo for full setup instructions.

本仓库通过 `agent-rules` 中的 `agent-sync` 自动部署，完整安装说明见主仓库。

```bash
# In ~/.config/agent-rules — add this repo as a submodule
# 在 ~/.config/agent-rules 中添加为 submodule
git submodule add https://github.com/<you>/agent-toolkit extras/agent-toolkit
git commit -m "Add agent-toolkit as submodule"
```

---

## 4. Adding a New Skill / 新增 Skill

```bash
mkdir -p skills/<skill-name>
# Create skills/<skill-name>/SKILL.md — cross-tool format (Cursor + CC compatible)
# 创建 skills/<skill-name>/SKILL.md — 跨工具格式（Cursor + CC 兼容）
git add skills/<skill-name>
git commit -m "Add <skill-name> skill"
```

`agent-sync` deploys it to `.cursor/skills/`, `.claude/skills/`, and `.agents/skills/` on next run.

`agent-sync` 下次运行时会部署到 `.cursor/skills/`、`.claude/skills/` 和 `.agents/skills/`。

---

## 5. Skills Catalog / 技能目录

See [`skills/README.md`](skills/README.md) for the full catalog.

完整目录见 [`skills/README.md`](skills/README.md)。

---

## 6. Roadmap

- [ ] **Cluster Agent skill** — Provides a cluster-launched agent with structured working context: target compute node, Docker container, code/data paths, and an ordered task list; reports results after each step and halts on error.
  为在 cluster 上启动的 agent 提供结构化的工作环境上下文：目标 compute node、Docker 容器名、代码/数据路径，以及需要按序执行的任务列表；每步执行后报告结果，遇错即停。
- [ ] **Nsight Compute skill** — Parses `.ncu-rep` profile reports, extracts key metrics (memory throughput, compute throughput, warp efficiency, etc.), and provides targeted optimization recommendations.
  解析 `.ncu-rep` profile 报告，提取关键 metric（memory throughput、compute throughput、warp efficiency 等），并给出针对性的优化建议。
- [ ] **render-report skill** — Converts a structured Markdown analysis document into a self-contained, presentable HTML report: renders inline data as interactive charts, lays out conclusions as styled callouts, and presents principles with figures and prose side-by-side.
  将结构化的 Markdown 分析文档转换为独立 HTML 报告：内联数据渲染为交互式图表，分析结论以醒目样式呈现，原理部分支持图文并排排版，可直接在浏览器中展示或分发。
