# tasky

Task and roadmap management for any project. Features, tasks, milestones — all in markdown files under `agents/docs/tasky/`.


## Setup

```
$tasky init
```

Creates `TASKY.md` at the project root. Edit it to set your default roadmap, data directory, and any conventions you want tasky to follow.


## Tasks

```
$tasky list                          # all features
$tasky list auth                     # tasks in a feature
$tasky next auth                     # next unblocked task
$tasky show auth 03                  # full task detail
$tasky add auth "add OAuth flow"     # new task
$tasky done auth 03                  # mark complete
$tasky update auth 03                # edit fields
```

Tasks live in `agents/docs/tasky/tasks/{feature}/tasks/`. Each task is a markdown file with STATUS, DEPENDS, IMPACTS, and optional PROCESS/REFERENCES/GUARDS fields.


## Roadmaps & Milestones

```
$tasky roadmap list                              # all roadmaps
$tasky roadmap create v1                         # new roadmap
$tasky roadmap show v1                           # Gantt chart
$tasky milestone create v1 "beta"                # new milestone
$tasky milestone assign v1 beta auth 03          # assign task
$tasky timeline v1                               # visual timeline
```


## Task Fields

```
STATUS: pending | active | completed
DEPENDS: 01, 02          # blocked until these are done
IMPACTS: src/auth.ts     # files this touches
PROCESS: auth/oauth      # how to approach it (inferred if not set)
REFERENCES: brain/...    # docs, decisions, links
GUARDS: don't break SSO  # things not to break
```

PROCESS/REFERENCES/GUARDS can also be set on a milestone and inherited by all its tasks.


## Status Cascade

Marking a task done cascades automatically — task file → manifest → feature → milestone → roadmap. Never update indexes by hand; tasky handles it.


## Files

```
agents/docs/tasky/
  tasks/{feature}/
    index.md             # feature overview
    tasks/index.md       # task manifest
    tasks/01-slug.md     # task file
  roadmaps/{name}/
    milestones/index.md  # milestone index
    milestones/01 - name.md
```


---

# Examples


## $tasky roadmap show product-v1

```
product-v1               │  1  │  2  │  3  │  4  │
─────────────────────────┼─────┼─────┼─────┼─────┤
 01 Core          (3/3)  │█████│     │     │     │
 02 Auth          (2/8)  │· · ·│▓▓▓▓▓│     │     │
 03 Dashboard     (0/6)  │     │     │░░░░░│     │
 04 API           (0/5)  │     │     │░░░░░│░░░░░│
 11 Infra         (1/4)  │· · ·│▓▓▓▓▓│▓▓▓▓▓│▓▓▓▓▓│

█ completed  ▓ active  ▒ at risk  ░ planned
```

Leader dots show phases before a milestone starts. Infra (phase 2–4) runs in parallel across phases 2, 3, and 4.


## $tasky list auth

```
auth — Task Manifest

 ID   Title                        Depends   Status
 01   Create user model            —         completed
 02   Add password hashing         —         completed
 03   Build login endpoint         01, 02    active
 04   Add session tokens           03        pending
 05   Write auth tests             03        pending
```


## $tasky show me task 03 deps  (or: "show dependencies for auth", "what's blocking task 4")

```
auth — Dependency Report

 01 Create user model       completed
 02 Add password hashing    completed
 03 Build login endpoint    active      depends: 01 ✓, 02 ✓
 04 Add session tokens      pending     depends: 03 (active) — blocked
 05 Write auth tests        pending     depends: 03 (active) — blocked

Dependency tree:

 01 Create user model ───────┐
 02 Add password hashing ────┴──► 03 Build login endpoint ──► 04 Add session tokens
                                                           └──► 05 Write auth tests

No cycles. 1 task ready to start: 03 (all deps complete, status still active).
```

Dep checks catch missing refs, cycles, and tasks whose deps are all done but status hasn't moved.


## Task file — agents/docs/tasky/tasks/auth/tasks/03-login-endpoint.md

```markdown
# Task 03 — Build login endpoint

STATUS: active
DEPENDS: 01, 02
MILESTONE: product-v1/02-auth
IMPACTS: src/routes/auth.ts, src/middleware/session.ts
GUARDS: don't break existing /health and /status routes

## Description

POST /auth/login — validates credentials, creates session, returns token.
Runs after user model (01) and password hashing (02) are complete.

## Spec

- Accept email + password in request body
- Return 401 on bad credentials, 200 + token on success
- Session TTL: 24h, stored in Redis

## Acceptance Criteria

- [ ] Returns 200 with token on valid login
- [ ] Returns 401 on wrong password
- [ ] Returns 401 on unknown email
- [ ] Token expires after 24h
```
