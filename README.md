# AgenticExpert Skills

A suite of Claude Code skills for managing projects from idea to execution.


## Install

```
npx skills add agenticexpert/skills
```

Or install a single skill:

```
npx skills add agenticexpert/skills/tasky
npx skills add agenticexpert/skills/tracky
npx skills add agenticexpert/skills/brain
npx skills add agenticexpert/skills/thinky
```


## The Suite

```
thinky → tasky
          ↑
     tracky ← brain
```

- **thinky** — start here. capture the vision, goals, and pillars before anything gets built
- **tasky** — turn vision into tasks, milestones, and roadmaps. the main skill
- **tracky** — track decisions, specs, and open questions as the project evolves
- **brain** — shared knowledge index. always in context, keeps all skills informed

Each skill works standalone. They become more powerful together.


## Skills

| Skill | What it does | README |
|-------|-------------|--------|
| tasky | Tasks, features, milestones, roadmaps, Gantt charts | [docs](.claude/skills/tasky/README.md) |
| thinky | Vision, goals, pillars, idea capture, alignment | [docs](.claude/skills/thinky/README.md) |
| tracky | Decisions, specs, issues, fast-capture notes | [docs](.claude/skills/tracky/README.md) |
| brain | Project knowledge hub — Q&A, facts, category docs | [docs](.claude/skills/brain/README.md) |


## Get Started

New project — start with vision:
```
/thinky init
/tasky init
/brain init
/tracky init
```

Already know what you're building — jump straight to tasks:
```
/tasky init
```


## Requirements

- [Claude Code](https://claude.ai/code)
- [skills CLI](https://skills.sh) — `npx skills add`