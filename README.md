# Ghost Engineer

A desktop application that generates realistic, backdated commit histories across your GitHub repositories. Features multi-user profiles, SSH key management, and per-repository configuration — all through a dark-themed customtkinter GUI.

> **⚠️ Disclaimer:** This tool creates artificial commit activity. Use it for portfolio demonstration purposes only. Artificially inflating contribution graphs may violate GitHub's terms of service.

---

## Features

- **Multi-user profiles** — each user has their own account, SSH keys, tokens, and repo list. Passwords hashed with PBKDF2.
- **SSH key management** — generate ed25519 keys or import existing ones directly in the app. One-click copy to clipboard. Links to GitHub's SSH settings page.
- **GitHub token support** — store a personal access token for HTTPS remotes.
- **Per-repo config** — add any number of repos with local path + remote URL. The app can clone repos that don't exist locally yet.
- **Realistic commit generation** — commits are backdated across multiple days with natural time distributions (peak hours weighted higher). Includes:
  - **Dynamic messages** — conventional commits format (`feat(scope): description`), ~18% with multi-line bodies, ~20% with issue references, ~6% with co-authors
  - **Real code changes** — 8 file types with templated content (Python, JS/TS, CSS/SCSS, HTML, JSON, YAML, shell scripts, SQL, Markdown docs)
  - **Multi-file commits** — 25% of commits touch 2-4 files at once
  - **File continuity** — the same files get modified across multiple commits, mimicking real feature development
  - **Natural scheduling** — weekends get fewer commits, no commits between midnight-7am
- **Safe branching** — all commits go to an `activity/YYYYMMDD-HHMMSS` branch, never touching main
- **Custom dark-themed dialogs** — no jarring white popups
- **Slide transitions** — smooth page animations between login, dashboard, and settings

## Screenshots

*(Add screenshots here)*

## Requirements

- **Python 3.10+**
- **Git 2.20+**
- **pip** (for installing the dependency)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ghost-engineer.git
cd ghost-engineer

# Install the only dependency
pip install customtkinter

# Run it
python3 main.py
```

No other dependencies needed — everything else is Python standard library.

## Quick Start

### 1. Create your account

Launch the app. On first run, it shows a "Create Account" form. Pick any username and password (4+ characters). Email is optional.

### 2. Set up an SSH key

Go to **Settings** and click **Generate New Key**. The app creates an ed25519 key pair and offers to open GitHub's SSH settings page. Copy your public key and add it there.

> HTTPS users: instead of SSH, go to Settings and paste a [GitHub personal access token](https://github.com/settings/tokens).

### 3. Add a repository

From the **Dashboard**, click **+ Add**. Fill in:
- **Project Name** — any label (e.g. `my-api`)
- **Local Path** — where the repo lives on disk (leave blank to auto-clone)
- **Remote URL** — `git@github.com:user/repo.git` (SSH) or `https://github.com/user/repo.git` (HTTPS)

### 4. Generate commits

Select the repo from the list, adjust the sliders:
- **Total Commits** — how many commits to generate (10–200)
- **Spread (days)** — distribute them across how many days (1–60)

Click **🚀 Start Ghosting**. The console logs progress in real-time. When done, the `activity/...` branch is pushed to GitHub.

You can review the branch on GitHub and merge it into main if desired.

## Project Structure

```
ghost-engineer/
├── main.py              ← Entry point
├── engine.py            ← Commit generation engine
├── user_manager.py      ← User auth, SSH keys, credentials, repos
├── messages.py          ← Fallback commit messages
├── requirements.txt     ← customtkinter
├── ui/
│   ├── __init__.py
│   ├── login.py         ← Login / Register screen
│   ├── dashboard.py     ← Main dashboard
│   ├── settings.py      ← SSH key & token management
│   └── dialogs.py       ← Custom dark-themed popups
└── data/                ← Created at runtime (stored locally)
    ├── users.json       ← Hashed passwords
    ├── keys/            ← SSH key pairs per user
    └── configs/         ← Repo lists and tokens per user
```

## How it works

### Time distribution

Commits are spread across waking hours (8 AM – 11 PM) with a realistic peak weight:

| Hour | Weight |
|------|--------|
| 8 AM | Low |
| 9-11 AM | High |
| 12 PM | Medium |
| 1-5 PM | High |
| 6-11 PM | Low |

Weekends receive ~30% the commit volume of weekdays, with a higher chance of having zero commits.

### Commit types

| Type | Weight | Description |
|---|---|---|
| Single file | 50% | Creates or appends to one source file |
| Multi-file | 25% | Changes 2-4 files simultaneously |
| Documentation | 20% | Adds or updates docs |
| Empty | 5% | `--allow-empty` commits (rare) |

### File pools

Files are organized into 8 modules with ~80 total paths:

- `auth/` — login, registration, sessions, permissions
- `api/` — routes, middleware, serializers, pagination
- `db/` — models, migrations, queries, connection pool
- `ui/` — components (Button, Modal, Table), pages, hooks, styles
- `core/` — config, logging, cache, events, health checks
- `deps/` — requirements.txt, package.json, Docker configs
- `ci/` — GitHub Actions workflows, deploy scripts, Makefile
- `docs/` — README, contributing guide, API docs

Each commit picks files from a module, creating new files on first touch and appending content on subsequent modifications.

## Security

- Passwords are hashed with **PBKDF2-SHA256** (100,000 iterations, random 128-bit salt)
- SSH keys are stored in `data/keys/<username>/` with `chmod 600`
- GitHub tokens are stored in `data/configs/<username>.json`
- All data stays **local** — no telemetry, no cloud sync, no network calls except git operations
- The app never sends data anywhere except to `git push` targets you configure

## FAQ

**Q: Does this actually push to GitHub?**  
Yes. It runs `git push` just like you would from the terminal. It uses your SSH key or GitHub token for authentication.

**Q: Will GitHub show these commits in my contribution graph?**  
Yes, commits pushed to the default branch (or any branch that eventually merges) count toward the contribution graph.

**Q: Can I use this with private repos?**  
Yes. Works with any Git remote — GitHub, GitLab, self-hosted, or local bare repos.

**Q: What happens to my existing changes?**  
The engine stashes any uncommitted changes before starting and leaves them intact on the original branch.

**Q: How do I merge the activity into main?**  
On GitHub, create a pull request from the `activity/...` branch and merge it. Or locally:
```bash
git checkout main
git merge activity/20260514-223315
git push
```

## License

MIT
