# Ghost Engineer

A desktop app that fills your GitHub contribution graph with realistic-looking past commits. It creates random code files, commits them with backdated timestamps, pushes to your repo, then **deletes all the temporary files** — leaving zero mess behind.

> **⚠️ Disclaimer:** This tool generates artificial commit activity. Use for portfolio demonstration only. Artificially inflating contribution graphs may violate GitHub's terms of service.

---

## What it does (in simple words)

1. You tell it: "I want 50 commits spread over 7 days"
2. It creates a hidden folder `_ge/` in your repo
3. Every few minutes (backdated), it creates/modifies a random-looking source file inside `_ge/` and commits it
4. When done, it pushes everything to GitHub, **deletes the `_ge/` folder**, and pushes the cleanup
5. Your repo is clean — no leftover files, no mess

**Result:** Your GitHub graph shows 7 days of green squares.

---

## Safety features

- **Never touches existing files** — checks every path before writing; if a file already exists, it skips it
- **Never touches README, LICENSE, .gitignore** — protected files are blocked at the code level
- **All generated files go into a single folder (`_ge/`)** — never scattered across your repo
- **Auto-cleanup** — after the last commit, the `_ge/` folder is deleted and the deletion is committed + pushed
- **One-click delete** — the X button on any repo removes it instantly, no confirmation popup

---

## Requirements

- **Python 3.10+**
- **Git 2.20+**
- **pip** (for installing the one dependency)

## Installation

```bash
# 1. Download
git clone https://github.com/Prince000101/ghost-engineer.git
cd ghost-engineer

# 2. Install the only dependency
pip install customtkinter

# 3. Run it
python3 main.py
```

That's it. All other modules are Python standard library — no extra packages needed.

On first run, the app creates a `data/` folder (gitignored) to store your settings, SSH keys, and tokens locally.

## Quick Start

### 1. Set your identity

Go to **Settings** → enter your GitHub username and email → click **Save Identity**.  
An SSH key is auto-generated for you.

### 2. Authenticate

Choose one:
- **SSH**: Copy your public key from Settings and add it at [github.com/settings/keys](https://github.com/settings/keys)
- **HTTPS**: Go to Settings and paste a [GitHub personal access token](https://github.com/settings/tokens) (needs `repo` scope)

### 3. Add a repository

From the **Dashboard**, click **+ Add**. Fill in:
- **Project Name** — any label (e.g. `my-api`)
- **Local Path** — where the repo is on disk (leave blank to auto-clone)
- **Remote URL** — `git@github.com:user/repo.git` (SSH) or `https://github.com/user/repo.git` (HTTPS)

You can also click **Scan Directory** to auto-detect Git repos in a folder.

### 4. Generate commits

Select a repo from the list, adjust the sliders:
- **Total Commits** — how many (10–200)
- **Spread (days)** — distribute across how many days (1–60)

Click **🚀 Start Ghosting**. The console shows progress in real-time.  
Or click **🎲 Random Ghost** for a random commit burst.

When done, you'll see in green:

```
✓ Done — 50 commits across 7 days pushed to 'main'
✓ Ghost files deleted from repo and pushed — clean ✓
✓ All done — changes committed, pushed, and cleaned ✓
✓ Restoring your uncommitted changes...
```

---

## Project Structure

```
ghost-engineer/
├── main.py              ← Entry point — starts the desktop app
├── engine.py            ← Commit engine — creates files, commits, pushes, cleans up
├── config_manager.py    ← Manages repos, SSH keys, tokens, identity
├── messages.py          ← Pre-written commit messages (fallback pool)
├── requirements.txt     ← Only dependency: customtkinter
├── .gitignore           ← Excludes data/ and __pycache__/
├── ui/
│   ├── dashboard.py     ← Main screen — repo list, sliders, start/random buttons, console
│   ├── settings.py      ← Settings — identity, SSH keys, tokens
│   └── dialogs.py       ← Dark-themed popup dialogs (confirm, info, errors)
└── data/                ← Created at runtime — gitignored, stays local
    ├── config.json      ← Repos, token, git identity
    ├── keys/            ← SSH key pairs
    ├── configs/         ← Per-user configs
    └── users.json       ← User data (local only)
```

---

## How commits are generated

### Time distribution

Commits are spread across waking hours (8 AM – 11 PM) with realistic peak weighting:

| Period | Weight |
|--------|--------|
| 8 AM | Low |
| 9-11 AM | High |
| 12 PM | Medium |
| 1-5 PM | High |
| 6-11 PM | Low |

Weekends receive ~30% the commit volume of weekdays.

### Commit types

| Type | Chance | Description |
|------|--------|-------------|
| Single file | 50% | Creates or appends to one source file |
| Multi-file | 25% | Changes 2-4 files simultaneously |
| Documentation | 20% | Adds Markdown docs |
| Empty | 5% | `--allow-empty` commit (rare) |

### File content

8 file types with realistic templated content:
- Python, JavaScript, TypeScript, CSS/SCSS, HTML, JSON, YAML, Shell, SQL, Markdown

Each file gets a unique name like `update_handler_base.py` or `fix_service_core.ts`.  
Messages follow conventional commits: `feat(api): add pagination support...`

---

## FAQ

**Q: Does this actually push to GitHub?**  
Yes. It runs `git push` using your SSH key or GitHub token.

**Q: Will it show on my contribution graph?**  
Yes — commits pushed to the default branch count toward the graph.

**Q: Can I use it with private repos?**  
Yes. Works with GitHub, GitLab, self-hosted, or local bare repos.

**Q: Will it mess up my existing files?**  
No. The code explicitly checks: never writes to a file that already exists, never touches protected files (README, LICENSE, .gitignore).

**Q: What about my uncommitted changes?**  
The engine stashes them before starting and restores them when done.

**Q: How does cleanup work?**  
All generated files go into `_ge/`. After the final push, the engine runs `git rm -rf _ge/`, commits the deletion, and pushes it. Zero traces left.

---

## License

MIT
