<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-8A2BE2">
  <img src="https://img.shields.io/badge/License-MIT-green">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen">
</p>

<h1 align="center">👻 Ghost Engineer</h1>
<p align="center"><i>Fill your GitHub contribution graph with realistic past commits — and leave zero traces.</i></p>

---

> **⚠️ Disclaimer:** This tool generates artificial commit activity. Use for portfolio demonstration only. Artificially inflating contribution graphs may violate GitHub's terms of service.

---

## 📖 What it does

| Step | What happens |
|------|-------------|
| **1** | You set: *"50 commits spread over 7 days"* |
| **2** | Creates a hidden `_ge/` folder in your repo |
| **3** | Generates random source files with realistic content & backdates each commit |
| **4** | Pushes everything to GitHub |
| **5** | **Deletes `_ge/`** and pushes the cleanup — zero traces left |

✅ **Result:** Your GitHub graph shows 7 days of green squares. Your repo is spotless.

---

## 🛡️ Safety features

- ✅ **Never touches existing files** — checks every path before writing
- ✅ **Protected files** — README, LICENSE, .gitignore are blocked at the code level
- ✅ **All garbage goes in `_ge/`** — never scattered across your repo
- ✅ **Auto-cleanup** — `git rm -rf _ge/` after the final push
- ✅ **Stash & restore** — your uncommitted work is saved and reapplied

---

## 📥 Download

### Pre-built executable (no Python required)

| Platform | File | How to get it |
|----------|------|--------------|
| 🐧 **Linux** | `GhostEngineer` | Run `./build.sh` in the cloned repo → `dist/GhostEngineer` |
| 🪟 **Windows** | `GhostEngineer.exe` | Run `setup_windows.bat` → desktop shortcut created automatically |
| 🍎 **macOS** | `GhostEngineer` | Run `./build.sh` in the cloned repo → `dist/GhostEngineer` |

### Run from source

```bash
git clone https://github.com/Prince000101/ghost-engineer.git
cd ghost-engineer
pip install customtkinter
python3 main.py          # Linux/macOS
# or: python main.py     # Windows
```

---

## 🚀 Setup

### Linux

```bash
# 1. Clone
git clone https://github.com/Prince000101/ghost-engineer.git
cd ghost-engineer

# 2. Build standalone executable
./build.sh

# 3. Put it on your desktop
cp dist/GhostEngineer ~/Desktop/

# 4. Pre-populate your data (if migrating from source)
cp -r data/ ~/.ghost-engineer/

# 5. Create desktop launcher icon
cat > ~/Desktop/ghost-engineer.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Ghost Engineer
Comment=Generate realistic git commit histories
Exec=/home/$USER/Desktop/GhostEngineer
Icon=utilities-terminal
Terminal=false
Categories=Development;Utility;
EOF

chmod +x ~/Desktop/ghost-engineer.desktop

# Allow launching (GNOME)
gio set ~/Desktop/ghost-engineer.desktop metadata::trusted true
# or (KDE / others)
chmod +x ~/Desktop/GhostEngineer
```

<details>
<summary><b>🐧 Linux — app menu launcher (optional)</b></summary>

```bash
# Install system-wide (app launcher + PATH)
sudo cp dist/GhostEngineer /usr/local/bin/ghost-engineer

# App menu entry
sudo tee /usr/share/applications/ghost-engineer.desktop > /dev/null << 'EOF'
[Desktop Entry]
Type=Application
Name=Ghost Engineer
Comment=Generate realistic git commit histories
Exec=/usr/local/bin/ghost-engineer
Icon=utilities-terminal
Terminal=false
Categories=Development;Utility;
EOF
```
</details>

---

### Windows

```cmd
:: 1. Clone the repo (or download ZIP from GitHub)
git clone https://github.com/Prince000101/ghost-engineer.git
cd ghost-engineer

:: 2. Double-click setup_windows.bat — it does everything:
::    - Checks Python & Git are installed
::    - Installs dependencies (customtkinter, pyinstaller)
::    - Builds GhostEngineer.exe
::    - Copies it to your desktop
::    - Migrates config to C:\Users\<you>\.ghost-engineer\
```

<details>
<summary><b>🪟 Windows — desktop icon (manual)</b></summary>

```cmd
:: The .exe is already on your desktop after setup_windows.bat.
:: To pin to taskbar: right-click GhostEngineer.exe → "Pin to taskbar"
:: To create a shortcut: right-click → "Send to" → "Desktop (create shortcut)"
```
</details>

---

### macOS

```bash
# Clone & build
git clone https://github.com/Prince000101/ghost-engineer.git
cd ghost-engineer
./build.sh

# Copy to desktop
cp dist/GhostEngineer ~/Desktop/

# Optional: create a .app bundle
cat > ~/Desktop/GhostEngineer.app/Contents/MacOS/GhostEngineer << 'EOF'
#!/bin/bash
exec "$(dirname "$0")/../../GhostEngineer"
EOF
chmod +x ~/Desktop/GhostEngineer.app/Contents/MacOS/GhostEngineer
```

---

## ⚡ Quick Start

### 1️⃣ Set your identity

Go to **Settings** → enter your GitHub username + email → **Save Identity**.  
An SSH key is generated automatically.

### 2️⃣ Authenticate

| Method | What to do |
|--------|-----------|
| 🔑 **SSH** | Copy your public key from Settings → add at [github.com/settings/keys](https://github.com/settings/keys) |
| 🔐 **HTTPS** | Paste a [GitHub token](https://github.com/settings/tokens) (`repo` scope) in Settings |

### 3️⃣ Add a repo

From **Dashboard** → **+ Add**:

| Field | What to enter |
|-------|--------------|
| **Project Name** | Any label (e.g. `my-api`) |
| **Local Path** | Leave blank to auto-clone, or browse to existing repo |
| **Remote URL** | `git@github.com:user/repo.git` (SSH) or `https://github.com/user/repo.git` (HTTPS) |

💡 Click **Scan Directory** to auto-detect Git repos in a folder.

### 4️⃣ Generate commits

1. Select a repo from the list
2. Adjust sliders: **Total Commits** (10–200) × **Spread** (1–60 days)
3. Click **🚀 Start Ghosting** — or **🎲 Random Ghost** for surprise settings

✅ When done, the console shows:

```
✓ Done — 50 commits across 7 days pushed to 'main'
✓ Ghost files deleted from repo and pushed — clean ✓
✓ All done — changes committed, pushed, and cleaned ✓
✓ Restoring your uncommitted changes...
```

---

## 📁 Project Structure

```
ghost-engineer/
├── main.py               🟢 Entry point — starts the desktop app
├── engine.py             🔧 Commit engine — creates files, commits, pushes, cleans up
├── config_manager.py     ⚙️  Config — repos, SSH keys, tokens, identity
├── messages.py           💬 Pre-written commit messages (fallback pool)
├── requirements.txt      📦 Only dependency: customtkinter
├── build.sh              🐧 Linux/macOS build script
├── setup_windows.bat     🪟 Windows setup script
├── .gitignore
├── ui/
│   ├── dashboard.py      📊 Main screen — repo list, sliders, start/random, console
│   ├── settings.py       ⚙️  Settings — identity, SSH keys, tokens
│   └── dialogs.py        🗔  Dark-themed popup dialogs
└── data/                 📂 Dev config (gitignored)
    ├── config.json       ← Repos, token, git identity
    ├── keys/             ← SSH key pairs
    └── users.json
```

**Data is stored in `~/.ghost-engineer/`** (Linux/macOS) or `C:\Users\<you>\.ghost-engineer\` (Windows) — a hidden folder in your home directory. The executable is portable and keeps nothing alongside itself.

---

## 🧠 How commits are generated

### ⏰ Time distribution

Commits span waking hours (08:00–23:00) with realistic peaks:

| Hours | Weight | Activity level |
|-------|--------|:--------------:|
| 08:00 | Low | 🌅 |
| 09:00–11:00 | **High** | 🔥🔥🔥 |
| 12:00 | Medium | 🔥🔥 |
| 13:00–17:00 | **High** | 🔥🔥🔥 |
| 18:00–23:00 | Low | 🔥 |

📅 Weekends get ~30% the volume of weekdays.

### 📦 Commit types

| Type | Chance | What it does |
|------|:------:|-------------|
| **Single file** | 50% | Creates or appends to one source file |
| **Multi-file** | 25% | Changes 2–4 files simultaneously |
| **Documentation** | 20% | Adds Markdown docs |
| **Empty** | 5% | `--allow-empty` (rare) |

### 📄 File templates

10+ languages with realistic templated content: Python, JavaScript, TypeScript, CSS, SCSS, HTML, JSON, YAML, Shell, SQL, Markdown.

Filenames look like `update_handler_base.py`, messages follow conventional commits: `feat(api): add pagination support to query handler`.

---

## ❓ FAQ

<details>
<summary><b>Does this actually push to GitHub?</b></summary>
Yes. It runs <code>git push</code> using your SSH key or GitHub token.
</details>

<details>
<summary><b>Will it show on my contribution graph?</b></summary>
Yes — commits pushed to the default branch count toward the graph. Past dates appear in the correct position.
</details>

<details>
<summary><b>Can I use it with private repos?</b></summary>
Yes. Works with GitHub, GitLab, self-hosted, or even local bare repos.
</details>

<details>
<summary><b>Will it mess up my existing files?</b></summary>
No. The code explicitly checks: never writes to an existing file, never touches protected files (README, LICENSE, .gitignore).
</details>

<details>
<summary><b>What about my uncommitted changes?</b></summary>
The engine stashes them before starting and restores them when done — your working tree is untouched.
</details>

<details>
<summary><b>How does cleanup work?</b></summary>
All generated files go into <code>_ge/</code>. After the final push, the engine runs <code>git rm -rf _ge/</code>, commits the deletion, and pushes it. Zero traces left.
</details>

---

## 📜 License

MIT — do whatever you want, just don't blame me.
