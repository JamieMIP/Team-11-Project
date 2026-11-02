# Make-It-All Productivity & Knowledge Management System

**COB290 Team Project, Part 1 prototype · Team 11 · Loughborough University**

A Python desktop application that gives Make-It-All's staff one place to manage their work and share what they know. It combines personal to-do lists, team project tasks, a manager dashboard and a company knowledge base, with what each person can see and do decided by their role.

> **Status:** Part 1 static prototype. It has the look and feel of the final system, but it uses hard-coded logins and in-memory demo data. A database, real authentication and multi-user support come in Part 2.

---

## Contents

- [About the project](#about-the-project)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the app](#running-the-app)
- [Demo accounts](#demo-accounts)
- [A quick tour](#a-quick-tour)
- [Project structure](#project-structure)
- [How it fits together](#how-it-fits-together)
- [Running the tests](#running-the-tests)
- [Configuration](#configuration)
- [Development conventions](#development-conventions)
- [Known limitations](#known-limitations)
- [Future work (Part 2)](#future-work-part-2)
- [Further documentation](#further-documentation)
- [Team](#team)

---

## About the project

Make-It-All is a medium-sized company based at the Science and Enterprise Park in Loughborough. Its CTO asked for an internal system to fix two problems:

1. **Productivity.** Individuals and teams track their daily tasks informally, which makes project progress very hard to follow.
2. **Knowledge.** Technical knowledge (configurations, bugs, fixes) and non-technical knowledge (admin processes such as ordering printer paper) isn't documented or shared in one place.

This prototype addresses both. Requirements came from the client's specification letter and from questions our team asked the client representatives on the module forums. The full list of requirements, the client's answers and our design decisions are in the Part 1 report rather than here.

The system has three roles, as the client requested: **Employee**, **Team Leader** and **Manager**. There is no separate Admin role. Managers hold the administrative powers.

---

## Features

### Productivity
- **Personal to-do lists**, private to each employee. Every employee has a General list that can't be deleted, plus any custom or team lists they add. Items completed more than 30 days ago are archived automatically.
- **Team project tasks** with a priority, an adjustable deadline and progress. Only Team Leaders and Managers can create, assign, edit, reassign or delete tasks, and deletion asks for confirmation first.
- **High-risk tasks** go to *Pending Approval* when completed, and a Team Leader or Manager has to approve them. Routine tasks are completed directly by the person assigned.
- **Overdue tasks** stay open and are highlighted for the employee, their Team Leader and their Manager.
- **My Tasks** brings together every project task assigned to you, across all your teams.

### Oversight
- **Dashboard** for Team Leaders (their own teams) and Managers (all teams). It shows project progress bars, how many tasks each person has, overload warnings and a list of overdue tasks.
- **Project progress** is calculated automatically as the average progress of the project's tasks.
- **Overload warning** at 5 or more unfinished tasks. It's a warning only, never a hard limit.
- **New Project** (Managers): create a project, then see every team ranked by its spare capacity before the deadline, with a suggested team.
- **Manage Teams & Roles** (Managers): create teams, appoint or replace leaders, promote and demote staff, and set an access end date for temporary staff.

### Knowledge base
- **Ranked home feed** that puts posts from followed topics and team topics, active discussions and unsolved technical questions first, with each post explaining why it's shown.
- **Forum posts** (anyone) and **announcements** (Managers only), filed under topics such as *Software Issues* or *Printing*.
- **Replies**, with the post's author able to mark one as the **accepted solution**.
- **Rich text**: `**bold**`, `*italic*`, `` `code` ``, `> quotes` and `[links](https://...)`, with formatting buttons. Only `http`, `https` and `mailto` links will open.
- **Search** by keyword, filtered by topic, with clickable tags and `#tag` search.
- **Follow topics**, and delete your own posts. Managers can remove any post.
- The author's name is always shown. There's no anonymous posting.

### General
- **Role-based sidebar**: you only see the pages your role allows.
- **Themes**: 20 colour palettes and 3 design styles, applied live across the app.

---

## Tech stack

| Area | Choice |
|------|--------|
| Language | Python 3.10+ |
| GUI | [CustomTkinter](https://customtkinter.tomschimansky.com/) (built on Tkinter) |
| Images and icons | Pillow |
| Data | In-memory Python objects (`sample_data.py`); no database in Part 1 |
| Testing | pytest and unittest |
| Code style | PEP 8 |
| Version control | Git and GitHub; one branch per feature, merged through pull requests |
| Editor | VS Code |

We chose CustomTkinter over PySide6/PyQt6 because it gives a modern look with theming and dark mode, and the whole team could pick it up quickly.

---

## Getting started

### Prerequisites

- **Python 3.10 or newer.** The code uses the `X | None` type syntax.
- **Tkinter.** It comes with the python.org installers for Windows and macOS. On Linux, install it with your package manager, e.g. `sudo apt install python3-tk`.
- **Git**, to clone the repository.

### Installation

```bash
git clone https://github.com/JamieMIP/Team-11-Project.git
cd Team-11-Project

# Optional but recommended: a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install customtkinter pillow pytest
```

### Running the app

From the **root of the repository**, run:

```bash
python main.py
```

Always run it from the repository root. The project uses flat imports (`from base import Page`), and these only work when the root folder is the working directory.

The login window opens first. After you log in, the main window opens. **Log Out** in the top bar takes you back to the login screen, and closing the window quits the app.

---

## Demo accounts

Logins are hard-coded for the prototype. Type the number in the username box, even though it says *Email*, and leave the password blank.

| Username | Password | Demo user | Role | Teams |
|----------|----------|-----------|------|-------|
| `0` | *(blank)* | Alice | Manager | Can see all teams |
| `1` | *(blank)* | Dilip | Team Leader | Leads Team 1 and Team 2 |
| `2` | *(blank)* | Liam | Employee | Member of Team 1 and Team 2 |

**Login with SSO** is a placeholder that logs straight in as Alice (Manager).

The demo data also includes other staff who can't log in but appear in teams and tasks. These include a second and third Team Leader, an intern whose access ends in 40 days, and a contractor whose access has already ended. There's also an unassigned project, *Staff Training Portal*, for trying out team suggestions. Everything resets when you close the app.

---

## A quick tour

| Page | Who sees it | What to try |
|------|-------------|-------------|
| Personal To-do List | Everyone | Add a list, add items, start and finish them |
| Team To-do List | Everyone (only your own teams; Managers see all) | Pick a team, switch between its projects, add or edit a task as a leader, request approval for a high-risk task |
| Knowledge Base | Everyone | Read the feed, follow a topic, write a post with formatting, reply, mark a solution, search `#printer` |
| My Tasks | Everyone | Use *+25% Progress* and *Mark Complete* on your own tasks |
| Dashboard | Team Leaders, Managers | Check progress bars, the workload list with `[OVERLOADED]`, and overdue tasks |
| New Project | Managers | Create a project or open *Staff Training Portal*, change the deadline and watch the team ranking change |
| Manage Teams & Roles | Managers | Create a team, change a leader, promote or demote someone, set an access end date |
| Themes | Everyone | Change the palette and style |

A good order for a demo is to log in as **Liam**, then **Dilip**, then **Alice**. That shows how the sidebar and permissions change with each role.

---

## Project structure

```text
Team-11-Project/
├── main.py                  # Entry point: login → main window → back to login on Log Out
├── login_module.py          # Login window (hard-coded demo logins)
├── gui_main.py              # Main window, PAGES registry, role-based sidebar, navigation
├── base.py                  # Page base class (theming, on_show)
├── widgets.py               # Top bar, sidebar and other shared widgets
├── theme_config.py          # Colour palettes, design styles and ThemeManager
├── sample_data.py           # All demo data in one place (replaced by a database in Part 2)
├── icons/                   # Sidebar icons
│
├── pages/                   # One file per screen. Draws the UI and calls the services
│   ├── personal_todo_list.py
│   ├── team_projects.py       # Team To-do List (team project pages)
│   ├── my_tasks.py
│   ├── manager_dashboard.py
│   ├── new_project.py
│   ├── manage_teams.py
│   ├── knowledge_base.py
│   ├── knowledge_base_widgets.py
│   ├── rich_text.py           # Markdown-style formatting for posts and replies
│   ├── themes_page.py
│   └── org_common.py          # Shared helpers for the organisation pages
│
├── organisation/            # Users, roles, permissions, teams, projects and tasks (logic only)
│   ├── models.py              # Data classes and tunable settings
│   ├── permissions.py         # Which role can do what
│   ├── service.py             # OrganisationService, the single entry point for the GUI
│   └── demo_data.py
│
├── personal_todo/           # Personal to-do lists (logic only)
├── forums/                  # Knowledge base: topics, posts, comments, feed and search (logic only)
│   └── forum_analysis_files/  # Class and flow diagrams (draw.io)
│
├── tests/                   # Tests for the organisation package
└── project-task/            # Earlier standalone task prototype with its diagrams (not used by the app)
```

Some files are left over from earlier versions and aren't used by the running app: `GUI.py`, `pages/team_todo_list.py`, `pages/template_knowledge_base.py`, `pages/template_team_todo.py` and the `project-task/` folder. They will be removed during Part 2.

---

## How it fits together

```text
main.py
  └─ run_login()                      login_module.py  → returns the demo user ID
  └─ start_main_application()         gui_main.py
        ├─ top bar shows the user and role, with Log Out
        ├─ sidebar lists only the pages the role allows
        └─ show_page(name)
              ├─ looks the name up in PAGES
              ├─ creates the page on first visit, then caches it
              └─ calls page.on_show() to reload fresh data
                    │
                    ▼
     pages/*.py  ──calls──▶  service classes (logic only, no GUI imports)
                             ├─ OrganisationService   (organisation/)
                             ├─ PersonalTodoService   (personal_todo/)
                             └─ ForumService          (forums/)
                                     │
                                     ▼
                              in-memory data (sample_data.py)
```

The main design rules are:

- **Pages only draw screens. Services hold every rule.** Permission checks, validation and calculations all live in the service classes, so the GUI can't bypass them by accident.
- **Services tell pages when to refresh.** Each service has an `on_change()` hook that pages subscribe to, so every open screen updates after a change.
- **One source of demo data.** All demo data lives in `sample_data.py`. In Part 2 it will be replaced by database calls inside the services, without changing the pages.

---

## Running the tests

From the repository root:

```bash
python -m pytest
```

This runs the organisation tests in `tests/` and the forum and search tests in `forums/`. The forum tests also run with the standard library:

```bash
python -m unittest -v
```

The tests cover the client's rules directly, for example:
- employees can't assign tasks
- high-risk tasks need approval
- overdue tasks stay open
- only authors and Managers can delete posts
- feed ranking
- search matching
- team suggestions

---

## Configuration

The main settings are constants, kept together so they're easy to find and change.

| Setting | Where | Default |
|---------|-------|---------|
| Overload warning threshold | `organisation/models.py` → `OVERLOAD_THRESHOLD` | 5 unfinished tasks |
| Priority weights for team suggestions | `organisation/models.py` → `PRIORITY_WEIGHTS` | Low 0.5, Medium 1, High 1.5, Critical 2 |
| A "full" weekly workload | `organisation/models.py` → `FULL_WEEKLY_LOAD` | 3.0 |
| Assumed project length with no deadline | `organisation/models.py` → `DEFAULT_PROJECT_WEEKS` | 4 weeks |
| Personal to-do archive period | `PersonalTodoService(archive_after_days=...)` | 30 days |
| Feed ranking weights | `forums/forum_feed.py` → `FeedRanker` | See `forums/README.md` |
| Themes | `theme_config.py` → `COLOR_PALETTES`, `DESIGN_STYLES` | Midnight Slate |

---

## Development conventions

- **PEP 8** naming and layout throughout.
- **Branches:** each person works on their own feature branch (e.g. `feature/personal-todo`, `fix/employee-dashboard`) and merges into `main` through a pull request that someone else reviews.
- **Logic and GUI stay separate:** the packages (`organisation`, `personal_todo`, `forums`) never import CustomTkinter, and pages never hold business rules.
- **Errors:** each package raises its own exception types (e.g. `ForumError`, `TodoError`), and pages catch them to show a friendly message.
- **Demo data:** add any new demo data to `sample_data.py`, not to separate files.
- **Adding a page:** create `pages/<name>.py` subclassing `Page`, add it to `PAGES` in `gui_main.py`, and make sure the sidebar text matches the key exactly.

---

## Known limitations

This is a Part 1 prototype, so some things are deliberately incomplete:

- **No real authentication.** Logins are hard-coded, passwords aren't checked, there's no registration page, and the login uses demo IDs (`0`, `1`, `2`) instead of staff email addresses.
- **No persistence.** All data is held in memory and resets every time the app closes.
- **Single user.** Only one person can use the app at a time, with no sessions or concurrency.
- **Temporary staff end dates** are enforced by the services and shown as `[ACCESS ENDED]`, but the login screen doesn't check them yet.
- **Permissions are fixed per role.** Extra permissions for individual employees aren't built yet.
- **Topic creation** exists in `ForumService` (Managers only) but has no screen yet. The technical/non-technical category filter in search isn't on screen yet either.
- **Training insight:** the forum service can count unsolved technical posts per topic, but this isn't shown on the dashboard yet.
- **No file attachments** on posts. The client listed these as optional.
- **No notifications.** Overdue and overload warnings only appear inside the app.
- The overload threshold of 5 is a placeholder until the client confirms a value.

---

## Future work (Part 2)

- **Database:** replace the in-memory data with a database behind the existing service classes, with indexing and pagination so the system can grow with the company.
- **Registration and login:** registration limited to staff email addresses, with one account per email. Passwords will follow the NCSC guidance: long passphrases, a blocklist of common passwords, and no forced complexity rules or regular resets.
- **Sessions:** login on several devices at once, with new-login alerts, session timeouts and a list of active sessions.
- **Step-up security:** Managers re-confirm their identity (password or 2FA) before sensitive actions such as changing roles or deleting content.
- **Individual permission overrides** on top of each role's default permissions.
- **Temporary staff:** block login automatically after the access end date.
- **Knowledge base:** a topic management screen, a category filter, file attachments if time allows, and a "where training is needed" view built from unsolved posts per topic.
- **Notifications** for overdue tasks, approvals and replies.
- **Clean-up:** remove the legacy files listed in [Project structure](#project-structure).

---

## Further documentation

| Document | What it covers |
|----------|----------------|
| [`forums/README.md`](forums/README.md) | Knowledge base design, feed scoring, the full `ForumService` API, class and flow diagrams |
| [`personal_todo/README.md`](personal_todo/README.md) | Personal to-do list design and API |
| [`TEAMS_AND_DATA_INTEGRATION.md`](TEAMS_AND_DATA_INTEGRATION.md) | How user identity, teams and theming are passed through the app |
| [`README_GUI.md`](README_GUI.md) | Notes on the GUI framework and navigation |
| [`Login_Module.md`](Login_Module.md) | The login window |
| `forums/forum_analysis_files/` | draw.io class diagram and feed flow diagrams |

The Part 1 report contains the full client requirements, the Q&A with the client and our design decisions.

---

## Team

**Team 11**: Alex Whawell, Brandon Richardson, Dominic Stachura, Jakub Krzyskow, Jamie Price, Nicole Wong, Owen Dorrington.

Built for the COB290 Team Projects module at Loughborough University. This is coursework for a fictional client (Make-It-All) and isn't licensed for reuse.
