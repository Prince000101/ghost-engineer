import os
import random
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from engine import GhostEngine
from ui.dialogs import askyesno, showinfo, showwarning


class AddRepoDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_submit):
        super().__init__(parent)
        self.on_submit = on_submit
        self.title("Add Repository")
        self.geometry("520x300")
        self.resizable(False, False)
        self.transient(parent)
        self.after(50, self.grab_set)

        ctk.CTkLabel(self, text="Project Name", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(18, 2))
        self.entry_name = ctk.CTkEntry(self, placeholder_text="e.g. my-awesome-project")
        self.entry_name.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(self, text="Local Path (leave blank to clone)", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(4, 2))
        fp = ctk.CTkFrame(self, fg_color="transparent")
        fp.pack(padx=20, pady=(0, 8), fill="x")
        self.entry_path = ctk.CTkEntry(fp)
        self.entry_path.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(fp, text="Browse", width=70, command=self._browse).pack(
            side="right", padx=(5, 0))

        ctk.CTkLabel(self, text="Remote URL (git@github.com:user/repo.git)", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(4, 2))
        self.entry_remote = ctk.CTkEntry(self, placeholder_text="git@github.com:user/repo.git")
        self.entry_remote.pack(padx=20, pady=(0, 14), fill="x")

        br = ctk.CTkFrame(self, fg_color="transparent")
        br.pack(pady=(0, 16))
        ctk.CTkButton(br, text="Save", command=self._submit).pack(side="left", padx=5)
        ctk.CTkButton(br, text="Cancel", fg_color="gray", command=self.destroy).pack(
            side="left", padx=5)

    def _browse(self):
        d = filedialog.askdirectory(title="Select project directory")
        if d:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, d)

    def _submit(self):
        n = self.entry_name.get().strip()
        p = self.entry_path.get().strip()
        r = self.entry_remote.get().strip()
        if not n:
            showwarning(self, "Missing", "Project name is required")
            return
        if not r:
            showwarning(self, "Missing", "Remote URL is required")
            return
        self.on_submit(n, p, r)
        self.destroy()


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, cfg, on_settings):
        super().__init__(master, corner_radius=0)
        self.cfg = cfg
        self.on_settings = on_settings

        self.engine = GhostEngine()
        self.selected_repo = None
        self.running = False

        self._build_ui()
        self._refresh_repo_list()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        hbar = ctk.CTkFrame(self, fg_color="transparent", height=44)
        hbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(6, 0))
        hbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hbar, text="Ghost Engineer",
                      font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")

        ssh_ok = self.cfg.has_ssh_key()
        c = "#2ecc71" if ssh_ok else "#e74c3c"
        ctk.CTkLabel(hbar, text=f"SSH: {'✓' if ssh_ok else '✗'}",
                      font=ctk.CTkFont(size=12), text_color=c).pack(side="right", padx=(0, 10))
        ctk.CTkButton(hbar, text="Settings", width=90,
                       command=self.on_settings).pack(side="right", padx=(4, 0))

        left = ctk.CTkFrame(self, corner_radius=12)
        left.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(6, 10))
        left.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="Repositories",
                      font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, pady=(12, 6), padx=12, sticky="w")
        self.repo_container = ctk.CTkScrollableFrame(left, corner_radius=8)
        self.repo_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

        bf = ctk.CTkFrame(left, fg_color="transparent")
        bf.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        bf.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(bf, text="+ Add", command=self._add_repo).grid(
            row=0, column=0, padx=2, sticky="ew")
        ctk.CTkButton(bf, text="\u2212 Remove", fg_color="#c0392b",
                       hover_color="#a93226", command=self._remove_repo).grid(
            row=0, column=1, padx=2, sticky="ew")
        ctk.CTkButton(bf, text="\U0001f50d  Scan Directory", fg_color="#2c3e50",
                       hover_color="#34495e", command=self._scan_dir).grid(
            row=1, column=0, columnspan=2, padx=2, pady=(4, 0), sticky="ew")

        right = ctk.CTkFrame(self, corner_radius=12)
        right.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(6, 10))
        right.grid_rowconfigure(3, weight=1)

        dh = ctk.CTkFrame(right, fg_color="transparent")
        dh.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        ctk.CTkLabel(dh, text="Repository Details",
                      font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.repo_name_label = ctk.CTkLabel(dh, text="",
                                             font=ctk.CTkFont(size=13), text_color="gray")
        self.repo_name_label.pack(side="left", padx=(10, 0))

        det = ctk.CTkFrame(right, fg_color="transparent")
        det.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))
        det.grid_columnconfigure(1, weight=1)
        self.detail_values = []
        for i, t in enumerate(["Local Path", "Remote URL"]):
            ctk.CTkLabel(det, text=t, font=ctk.CTkFont(size=13)).grid(
                row=i, column=0, sticky="w", pady=3, padx=(0, 10))
            v = ctk.CTkLabel(det, text="\u2014", anchor="w",
                             fg_color=("gray90", "gray20"),
                             corner_radius=6, padx=8, pady=3)
            v.grid(row=i, column=1, sticky="ew", pady=3)
            self.detail_values.append(v)

        ctrl = ctk.CTkFrame(right, fg_color="transparent")
        ctrl.grid(row=2, column=0, sticky="ew", padx=16, pady=8)
        ctrl.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(ctrl, text="Total Commits:").grid(row=0, column=0, padx=(0, 8), pady=3, sticky="w")
        self.commit_slider = ctk.CTkSlider(ctrl, from_=10, to=200, number_of_steps=190,
                                            command=self._update_info)
        self.commit_slider.set(60)
        self.commit_slider.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=3)
        self.commit_label = ctk.CTkLabel(ctrl, text="60", width=36)
        self.commit_label.grid(row=0, column=2, pady=3)

        ctk.CTkLabel(ctrl, text="Spread (days):").grid(row=1, column=0, padx=(0, 8), pady=3, sticky="w")
        self.days_slider = ctk.CTkSlider(ctrl, from_=1, to=60, number_of_steps=59,
                                          command=self._update_info)
        self.days_slider.set(7)
        self.days_slider.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=3)
        self.days_label = ctk.CTkLabel(ctrl, text="7 days", width=36)
        self.days_label.grid(row=1, column=2, pady=3)

        self.info_label = ctk.CTkLabel(ctrl, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.info_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))

        br = ctk.CTkFrame(right, fg_color="transparent")
        br.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 8))
        br.grid_columnconfigure((0, 1), weight=1)
        self.start_btn = ctk.CTkButton(
            br, text="\U0001f680  Start Ghosting", height=42,
            font=ctk.CTkFont(size=14, weight="bold"), command=self._start)
        self.start_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        ctk.CTkButton(
            br, text="\U0001f3b2  Random Ghost", height=42,
            font=ctk.CTkFont(size=14, weight="bold"), fg_color="#8e44ad",
            hover_color="#7d3c98", command=self._random_ghost).grid(
            row=0, column=1, padx=(3, 0), sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(right, mode="indeterminate")
        self.progress_bar.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 2))
        self.progress_bar.grid_remove()

        ctk.CTkLabel(right, text="Console", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=5, column=0, sticky="w", padx=16, pady=(6, 2))
        self.log_box = ctk.CTkTextbox(right, corner_radius=8,
                                       font=ctk.CTkFont(size=12, family="monospace"))
        self.log_box.grid(row=6, column=0, sticky="nsew", padx=16, pady=(0, 14))
        self.log_box.configure(state="disabled")

        self._update_info()

    def _refresh_repo_list(self):
        for w in self.repo_container.winfo_children():
            w.destroy()
        repos = self.cfg.get_repos()
        if not repos:
            ctk.CTkLabel(self.repo_container, text="No repos yet.\nClick '+ Add' to start.",
                          text_color="gray", justify="center").pack(expand=True, pady=40)
            return
        for r in repos:
            row = ctk.CTkFrame(self.repo_container, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=2)
            row.grid_columnconfigure(0, weight=1)

            name_btn = ctk.CTkButton(
                row, text=r["name"], anchor="w",
                fg_color="transparent", border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray85", "gray25"),
                command=lambda n=r["name"]: self._select_repo(n))
            name_btn.grid(row=0, column=0, sticky="ew")

            del_btn = ctk.CTkButton(
                row, text="\u2715", width=32,
                fg_color="transparent", border_width=1,
                border_color=("gray70", "gray30"),
                hover_color="#c0392b",
                text_color=("gray40", "gray60"),
                command=lambda n=r["name"]: self._remove_repo_direct(n))
            del_btn.grid(row=0, column=1, padx=(4, 0))

    def _select_repo(self, name):
        self.selected_repo = name
        r = next((x for x in self.cfg.get_repos() if x["name"] == name), None)
        if r:
            for v, lbl in zip([r["path"] or "\u2014", r["remote"]], self.detail_values):
                lbl.configure(text=v)
            self.repo_name_label.configure(text=f"\u00b7 {name}")

    def _add_repo(self):
        AddRepoDialog(self, self._on_repo_added)

    def _on_repo_added(self, name, path, remote):
        self.cfg.add_repo(name, path, remote)
        self._refresh_repo_list()
        self._select_repo(name)

    def _scan_dir(self):
        d = filedialog.askdirectory(title="Scan for Git repositories")
        if not d:
            return
        found = []
        for root, dirs, files in os.walk(d):
            if ".git" in dirs:
                name = os.path.basename(root)
                remote = self._get_remote(root)
                found.append({"name": name, "path": root, "remote": remote})
                dirs.remove(".git")
        if not found:
            showinfo(self, "No repos found", f"No Git repositories found in:\n{d}")
            return
        added = 0
        for r in found:
            if self.cfg.add_repo(r["name"], r["path"], r["remote"]):
                added += 1
        self._refresh_repo_list()
        showinfo(self, "Scan complete",
                 f"Found {len(found)} repo(s), {added} new.\n"
                 f"Existing duplicates were updated.")

    def _get_remote(self, repo_path):
        try:
            r = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=repo_path, capture_output=True, text=True, timeout=10
            )
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""

    def _remove_repo(self):
        if not self.selected_repo:
            showinfo(self, "No selection", "Select a repo first")
            return
        if askyesno(self, "Remove", f"Remove '{self.selected_repo}'?"):
            self.cfg.remove_repo(self.selected_repo)
            self.selected_repo = None
            self._refresh_repo_list()
            self.repo_name_label.configure(text="")
            for lbl in self.detail_values:
                lbl.configure(text="\u2014")

    def _remove_repo_direct(self, name):
        self.cfg.remove_repo(name)
        if self.selected_repo == name:
            self.selected_repo = None
            self.repo_name_label.configure(text="")
            for lbl in self.detail_values:
                lbl.configure(text="\u2014")
        self._refresh_repo_list()

    def _update_info(self, *_):
        c = int(self.commit_slider.get())
        d = int(self.days_slider.get())
        self.commit_label.configure(text=str(c))
        self.days_label.configure(text=f"{d} days")
        self.info_label.configure(text=f"~{max(1, round(c/d))} commits/day \u00d7 {d} days  |  auto-cleaned after push")

    def _start(self):
        if self.running:
            return
        if not self.selected_repo:
            showwarning(self, "No repo", "Select a repo from the list first.")
            return
        if not self._confirm():
            return

        self.running = True
        self.start_btn.configure(state="disabled", text="\u23f3  Running...")
        self.progress_bar.grid()
        self.progress_bar.start()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        c = int(self.commit_slider.get())
        d = int(self.days_slider.get())
        ssh_key = self.cfg.get_ssh_key_path()
        token = self.cfg.get_github_token()

        threading.Thread(
            target=self._run_thread,
            args=(self.selected_repo, c, d, ssh_key, token),
            daemon=True,
        ).start()

    def _confirm(self):
        c = int(self.commit_slider.get())
        d = int(self.days_slider.get())
        p = max(1, round(c / d))
        key_ok = self.cfg.has_ssh_key()
        return askyesno(
            self, "Confirm",
            f"Ghost {c} commits into:\n\n"
            f"   {self.selected_repo}\n\n"
            f"   Schedule: ~{p}/day \u00d7 {d} days\n"
            f"   SSH key: {'\u2713' if key_ok else '\u2717 (set in Settings)'}\n"
            f"   Branch: main (direct push)\n"
            f"   Cleanup: files deleted after push\n\n"
            f"Proceed?"
        )

    def _random_ghost(self):
        repos = self.cfg.get_repos()
        if not repos:
            showwarning(self, "No repos", "Add repos first.")
            return
        repo = random.choice(repos)
        self._select_repo(repo["name"])
        c = random.randint(20, 70)
        d = random.randint(1, 7)
        self.commit_slider.set(c)
        self.days_slider.set(d)
        self._update_info()
        self._random_start(c, d)

    def _random_start(self, c, d):
        if self.running:
            return
        self.running = True
        self.start_btn.configure(state="disabled", text="\u23f3  Running...")
        self.progress_bar.grid()
        self.progress_bar.start()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        ssh_key = self.cfg.get_ssh_key_path()
        token = self.cfg.get_github_token()

        threading.Thread(
            target=self._run_thread,
            args=(self.selected_repo, c, d, ssh_key, token),
            daemon=True,
        ).start()

    def _run_thread(self, rname, count, days, ssh_key, token):
        repos = self.cfg.get_repos()
        repo = next((r for r in repos if r["name"] == rname), None)
        if not repo:
            self.after(0, lambda n=rname: self._log("error", f"Repo '{n}' not found"))
            self.after(0, self._done)
            return

        name, email = self.cfg.get_identity()

        def cb(level, msg):
            self.after(0, lambda l=level, m=msg: self._log(l, m))

        try:
            self.engine.run(
                repo["path"], repo["remote"], count,
                days_back=days, ssh_key_path=ssh_key,
                github_token=token, git_name=name, git_email=email,
                callback=cb,
            )
        except Exception as ex:
            err = str(ex)
            self.after(0, lambda e=err: self._log("error", f"ERROR: {e}"))
        finally:
            self.after(0, self._done)

    def _log(self, level, message):
        self.log_box.configure(state="normal")
        icons = {"error": "\u2717", "warning": "\u26a0", "success": "\u2713", "done": "\u2713", "info": "\u2192", "progress": " "}
        colors = {"error": "#e74c3c", "warning": "#f39c12", "success": "#2ecc71",
                  "done": "#2ecc71", "info": "#85c1e9", "progress": "gray"}
        icon = icons.get(level, " ")
        self.log_box.insert("end", f"{icon} {message}\n")
        if level in colors:
            self.log_box.tag_config(level, foreground=colors[level])
            self.log_box.tag_add(level, "end-2l", "end-1l")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _done(self):
        self.running = False
        self.start_btn.configure(state="normal", text="\U0001f680  Start Ghosting")
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
