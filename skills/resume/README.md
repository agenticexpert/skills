# Resume

Find out whether your resume gives each hiring reader enough reason to keep you moving—and fix only the parts that could change that decision.

Resume feedback can easily turn into 100 tiny edits with no clear payoff. This skill is built to prevent that. It looks for the few places where a reader may stop, misunderstand your value, or miss the proof that makes you worth calling.

It answers three practical questions:

- Will the applicant tracking system (ATS) pass your resume?
- Will a recruiter or HR screener call you?
- Will the hiring manager want an interview?

It does **not** reduce you to a “72% match.” A job description helps identify what the employer needs to believe, but the real question is whether your resume creates enough confidence and urgency to move you forward.

## Start here

Attach or paste your resume, then say:

```text
/resume Review my resume. Use standard depth and create the interactive report.
```

If you have a job description, attach it too:

```text
/resume Review my resume for this role. Tell me what could stop the call, what already earns attention, and the smallest changes that would matter. Create the interactive report.
```

You can also include your LinkedIn profile text, a LinkedIn export, or a short note about the roles you want. You do not need to prepare everything perfectly. The skill reads what you provide first and asks only for information it truly needs.

## Install

```bash
npx skills add agenticexpert/skills/resume
```

## What you receive

The report begins with a direct decision:

```text
MOVE FORWARD: not yet — the recruiter can see your area of work, but the result you owned is still unclear.
```

That is not a judgment of you. It is a judgment of what this version of the resume makes visible to a particular reader, under limited time.

The rest of the report explains the decision in this order:

1. **Must-Talk** — how much urgency the resume creates.
2. **ATS, screener, and manager** — where the hiring path is clear and where it may stop.
3. **Why the role exists** — when you provide a job description, the business reason the employer is likely hiring.
4. **What gets attention** — exact lines already helping you.
5. **Hotspots** — only the changes likely to affect the decision, proof, credibility, or repeated confusion.
6. **Do Next** — what to fix now, what to confirm, and what to be ready to defend in an interview.

## How to read the result

### Must-Talk

Must-Talk measures interview urgency, not your worth and not your percentage match.

| Score | What the resume currently gives the reader |
|---:|---|
| 0 | No clear reason to continue yet. |
| 1 | Possible qualifications, but the hiring story is easy to pass over. |
| 2 | Enough relevance for a screen, without a strong reason to act quickly. |
| 3 | A clear, credible reason to interview. |
| 4 | A reason to call before another employer does. |

The report always names the smallest repair most likely to raise the score. You should not have to guess what to work on next.

### The three hiring decisions

These are separate because each reader can stop the process for a different reason.

| Reader | Possible result | Plain meaning |
|---|---|---|
| ATS | `fail`, `risky`, `weak-pass`, `pass` | Can the resume be parsed and found for truthful, relevant requirements? |
| Screener | `no-call`, `maybe`, `call`, `urgent-call` | Does a recruiter or HR reader see a credible reason to speak with you? |
| Manager | `no`, `insufficient`, `interview`, `priority-interview` | Does the resume show that you can solve the problem behind the role? |

These are not three scores out of ten. They are decisions. The supporting reader notes explain what caused each one.

Without a job description, the ATS result covers parsing and general searchability. The skill will not pretend to know which missing keywords an unknown employer requires.

### Why the role exists

When a job description is available, the report tries to surface the business reason behind the list of duties:

```text
Role exists to protect renewals by identifying adoption risk early and coordinating recovery.
```

This may be marked:

- **Confirmed** — the source states the purpose directly.
- **Inferred** — the responsibilities strongly suggest it, but the report includes a question so you can verify it.
- **Unknown** — the posting is too generic to support an honest conclusion.

`Inferred` or `unknown` does not mean your resume failed. It means the job description did not prove the employer’s real buying reason, and the skill chose not to invent one.

### Hotspots

A hotspot is not every sentence that could be polished. It is a place where a reader could make the wrong decision, miss important proof, question credibility, or see the same unresolved problem several times.

Each hotspot tells you:

- where to look;
- what the reader may conclude;
- why that conclusion matters; and
- the one next action to take.

If the needed information is not in your resume, the report asks a specific question and tells you which item would use the answer. It will not write an achievement you have not confirmed.

Some reports may contain no hotspots. That is valid. The skill does not invent criticism to appear thorough.

## Work through one item at a time

The interactive report opens with only the important hotspots visible. You do not need to process the entire resume at once.

For any item:

1. Open it and read the reason and suggested action.
2. Choose **Converse** to add a small context packet to the **Conversation queue**.
3. Choose **Copy**, then paste that packet into your AI conversation.
4. Ask your question in ordinary language: “Why does this matter?”, “What information are you missing?”, or “Show me two truthful ways to rewrite this.”
5. Return to the report and mark the item `done`, leave it `open`, or set it to `ignore`.

The item packet contains only the selected issue, the minimum nearby context needed to understand it, prior decisions, and open questions. It does not reload your whole resume. This lets you have a detailed conversation about item 7 without also carrying items 1–6 and 8–100 into the discussion.

### What the controls do

| Control | What happens |
|---|---|
| **Expand** | Shows the evidence and detail behind the item. |
| **Converse** | Prepares the selected item’s small context packet for discussion. |
| **Export JSON** | Copies that item’s context only. |
| **Edit** | Lets you change the report’s reason, suggestion, notes, or proposed options. |
| **Save** | Saves those report-item edits. |
| **Cancel** | Discards the current unsaved edit. |
| **Accept rewrite** | Writes the selected wording into the resume held in the report and marks the item done. The change is saved to the report file, not just to the page. |
| **Status** | Cycles the item through `open`, `done`, and `ignore`. |
| **Show all observations** | Reveals supporting and already-clean items; it does not create new issues or change your saved data. |
| **Cross-item export** | Copies the entire report to your clipboard, for work that genuinely requires the whole resume. Use this intentionally. To save the resume as a file instead, see [Getting the resume back out](#getting-the-resume-back-out). |

Use **Show all observations** when you want the audit trail or want to understand why something was kept. Leave it closed when you simply want to know what to do next.

## Where your edits go

Every accepted rewrite, status change, and edit made through chat is written into the report file itself. The report page carries its own JSON, and that JSON is the copy of record. Nothing is lost when you close the tab.

Two files are *not* touched:

- the resume or LinkedIn file you originally handed in — it is read once and left alone;
- the JSON you passed to `render`, if you built the report that way — it is the starting material, not the running copy.

So the report is the current version of your resume, not a list of suggestions about it.

### Getting the resume back out

Ask for it:

> Give me the updated resume.

The skill reads the current version out of the report and writes it out for you. Ask for the LinkedIn text the same way.

This matters more than it sounds. A resume is easy for an AI assistant to *retype* from memory of the conversation, and a retyped resume quietly drifts — a bullet you rejected creeps back, a number shifts, an edit you accepted an hour ago goes missing. The skill is required to read the report file instead, so what you get back is what you actually approved.

If you would rather run it yourself, or want it on a schedule:

```bash
python3 references/agui_bridge.py export --report <report.html> --doc resume --out resume.md
```

`--doc linkedin` writes your LinkedIn text. `--format json` gives you the structured version instead of markdown, and `--doc island` gives you the whole report for archiving or reopening later. Leave off `--out` to print it to the screen.

Either way the export only reads the report, so you can run it as often as you like — after every session, or once at the end. It works whether or not the local server is running.

The file it writes contains your name and contact details. Keep it local.

## Useful requests

### Get a quick answer before applying

```text
/resume Quick scan this resume. Give me the decision, what gets attention, and only the top three hotspots.
```

### Run the normal review

```text
/resume Review this resume at standard depth. Create the interactive report and start with hotspots only.
```

### Compare the evidence to a job description

```text
/resume Review my resume with this job description as context. Do not give me a match percentage. Show why the role likely exists, what I already prove, and what still needs confirmation.
```

### Include LinkedIn

```text
/resume Review my resume and LinkedIn together. Keep LinkedIn findings separate and tell me which resume item each one could support.
```

### Rewrite after reviewing

```text
/resume Rewrite the summary and the two highest-impact bullets. Use only facts I have confirmed, preserve my voice, and flag anything you still need to ask me.
```

### Discuss one hotspot

```text
Using only this item packet, explain the concern in plain language and help me fix it without inventing a metric or outcome.
```

### See demonstrated skill strength

```text
/resume Run skillmatch for this job description. Grade only what my resume or LinkedIn actually proves and leave unsupported expectations ungraded.
```

Skillmatch uses a separate 0–5 evidence scale. It helps you see how strongly each skill is demonstrated; it is supporting evidence, not a fourth hiring decision and not a match percentage.

### Take the edited resume with you

```text
Give me the updated resume as a file.
```

You will get the version held in the report, with every edit you accepted. Ask for `the updated LinkedIn text` to get that document instead. See [Getting the resume back out](#getting-the-resume-back-out).

## What you can change safely

You can ask the skill to:

- clarify a confusing hotspot;
- show the exact line that caused a decision;
- ask you for the missing detail before rewriting;
- propose several truthful versions in your voice;
- shorten language without weakening the evidence;
- rewrite one bullet, one role, the summary, or the full resume;
- connect LinkedIn evidence to a specific resume item;
- show all supporting observations or hide them again;
- change an item’s status as you work;
- create a skill-evidence rubric against one or more job descriptions;
- record callback observations for different resume versions; or
- write the edited resume back out as a document when you are finished.

You remain in control of every factual claim. If a suggested rewrite sounds wrong, too strong, or unlike you, do not accept it. Tell the skill what is inaccurate or uncomfortable and ask for a version you could defend naturally in an interview.

## What the report will not do

- It will not promise that an edit will produce interviews.
- It will not invent numbers, ownership, tools, or outcomes.
- It will not lower your grade merely because a sentence could sound more polished.
- It will not create an issue for every resume line.
- It will not treat every job-description phrase as equally important.
- It will not turn an unsupported expectation into a demonstrated skill.

You can record what happened after a resume change, such as applications, callbacks, and interviews. The report keeps that useful history while labeling it **observed after, not attributed to**. That distinction helps future reviews learn from the pattern without claiming that one edit caused the outcome.

## Privacy and reopening a report

The HTML report and its resume data stay local. They contain personal information, so do not publish or upload the report unless you intend to share that information.

The local report server closes after it has been idle or when its session ends. Your report file remains on disk, with every edit you made still in it. To reopen it, run:

```bash
python3 references/agui_bridge.py serve --report <path-to-report.html>
```

On Windows, run it as `py -3 references/agui_bridge.py serve --report <path-to-report.html>`.

You do not need the server running to read the report or to export the resume from it.

## For maintainers

The report is one HTML file carrying a JSON island. That island is the durable product and the copy of record; the page around it is its working surface. The island is not a sidecar file — it lives inside the HTML, and every durable change rewrites it there.

Everything that reads or changes a report goes through a bridge verb. Reading one row is `getContext`; changing it is `patchResume`. Those two calls are the entire interaction for a named row:

```bash
python3 references/agui_bridge.py cmd --verb getContext --args '[15]'
python3 references/agui_bridge.py cmd --verb patchResume --args '{"path":"...","text":"..."}'
```

Reads are answered from the report file, so no browser tab need be open. Nothing should parse the island by hand, regex the HTML, or import the bridge to reach its internals — every field a caller needs is reachable through a verb, and a row costs one read and one write rather than the whole document.

See:

- [`references/connections.md`](references/connections.md) for the bridge verbs, addressing, and durability sequence.
- [`references/REPORT.md`](references/REPORT.md) for the report and workbench contract.
- [`references/READERS.md`](references/READERS.md) for the five hiring reads and decision roll-up.
- [`references/CRAFT.md`](references/CRAFT.md) for the winning bar and craft grading.
- [`references/REWRITE.md`](references/REWRITE.md) for truth-safe rewriting.
- [`references/SKILLMATCH.md`](references/SKILLMATCH.md) for the demonstrated-skill rubric.
- [`references/EVIDENCE.md`](references/EVIDENCE.md) for the verified-fact database behind tailoring.

Part of [Agentic Expert](../../README.md). Built by Shawn Bullock — [agenticexpert.ai](https://agenticexpert.ai).
