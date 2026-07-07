<div align="center">

# Agentic Expert

**A software-engineering suite for Claude Code — judgment, not ceremony.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-8-brightgreen.svg)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

</div>

> A curated suite of Claude Code skills for the whole engineering loop: **plan and execute the work, stress-test decisions before they bite, and engineer the prompts and memory that drive it all.**

Tasky, Seq, and Minion plan and move the work. Keeper, Lookback, and Ripper each poke holes in a decision before you commit. Fabble and Mem sit underneath — engineering the prompts you hand a model and the memory that survives the context window.

---

## 🧰 The Skills

### Plan & Execute

- **[Tasky](.claude/skills/tasky/README.md)** — turn a fuzzy deliverable into an execution plan: `project → roadmap → track → milestone → task`. Find what's next, what's blocked, execute, validate — all through conversation. Lightweight on purpose.
- **[Seq](.claude/skills/seq/README.md)** — run one tracked task inline through a named step-sequence (`audit → work → audit → report`). You see it happen and can course-correct mid-run.
- **[Minion](.claude/skills/minion/README.md)** — the delegated twin of Seq: hand a task (or a whole milestone) to a headless sub-agent so the heavy work stays out of your main context. Only a compact summary comes back.

### Stress-Test & Judge — *decision disciplines*

- **[Keeper](.claude/skills/keeper/README.md)** — keep-or-drop judgment for architecture and implementation. One verdict per element: `keep · fix · pivot · drop`. Every call is conditional and evidence-grounded.
- **[Lookback](.claude/skills/lookback/README.md)** — a solo premortem. Imagine the launch *already* failed, then work back to the top 5 reasons why. Each scenario is research-defended, classed `real · imagined · disregarded`, and carries a rollback spec.
- **[Ripper](.claude/skills/ripper/README.md)** — a retention premortem. Finds where allies, champions, and power users hesitate, drift, or stop advocating, then turns every cut into a retention action. 6 personas, each finding graded 1–10.

### Prompt & Context — *the layer underneath*

- **[Fabble](.claude/skills/fabble/README.md)** — get a prompt right *before* you spend an expensive run on it. Fable 5 is the most capable Claude model and the priciest to run, so Fabble tunes and checks the prompt first: **write** one from scratch out of a goal (`promptify`), **convert** an existing prompt to run on Fable 5 (`fablize`), **upgrade** a Sonnet/Opus prompt toward Fable-5 quality *without* switching models — as far as that model's ceiling allows (`fabelike`), or **audit** a finished prompt for a ready / not-ready verdict before you burn tokens (`audit`). `/until` sharpens a vague ask into a single-run goal.
- **[Mem](.claude/skills/mem/README.md)** — durable conversation memory. Structured, chronological summaries that survive `/clear` and compaction, hand off between agents and sessions, and split into idea threads or rejoin.

---

## 🎯 How It Feels to Use

These are **semantic skills** — there's no command to memorize. Claude reads your intent against each skill's description and loads the right one automatically. State what you're doing and the matching skill picks it up:

> Need to force it? Every skill is also loadable by name — `/tasky`, `/seq`, `/minion`, `/keeper`, `/lookback`, `/ripper`, `/fabble`, `/mem`.

**Plan & Execute**
- "Let's plan out the roadmap for `<topic>`." · "What's next?" · "What's blocked?" *(Tasky)*
- "Do `<task>` inline." · "Run `<task>` here so I can watch it." *(Seq)*
- "Minion task `<name>`." · "Delegate this without burning main context." *(Minion)*

**Stress-Test & Judge**
- "Is this auth design worth keeping, or should we pivot?" *(Keeper)*
- "We're a month out from ship. Run a premortem while we can still change course." *(Lookback)*
- "What would make our power users quietly stop recommending us — while we can still fix it?" *(Ripper)*

**Prompt & Context**
- "Upgrade this prompt for Fable 5." · "Is this prompt ready before I run it?" *(Fabble)*
- "Checkpoint this session." · "Continue from the last checkpoint." *(Mem)*

---

## 🚀 Installation

```bash
# All skills
npx skills add agenticexpert/skills

# A single skill
npx skills add agenticexpert/skills/tasky
npx skills add agenticexpert/skills/seq
npx skills add agenticexpert/skills/minion
npx skills add agenticexpert/skills/keeper
npx skills add agenticexpert/skills/lookback
npx skills add agenticexpert/skills/ripper
npx skills add agenticexpert/skills/fabble
npx skills add agenticexpert/skills/mem
```

## 🔄 Updates

```bash
# By repo source
npx skills update agenticexpert/skills

# By skill name
npx skills update tasky
```

---

## License

MIT. See [LICENSE](LICENSE).
