import os
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from ui.dialogs import askyesno, showinfo, showwarning, showerror, show_public_key


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, cfg, on_back):
        super().__init__(master, corner_radius=0)
        self.cfg = cfg
        self.on_back = on_back

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 6))
        ctk.CTkButton(hdr, text="←  Back to Dashboard", command=self.on_back,
                       width=170, fg_color="transparent", border_width=1,
                       text_color=("black", "white")).pack(side="left")
        ctk.CTkLabel(hdr, text="Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(
            side="left", padx=30)

        scroll = ctk.CTkScrollableFrame(self, corner_radius=12)
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scroll.grid_columnconfigure(0, weight=1)

        # ── Your Identity ──
        self._section(scroll, "Your Identity", 0)
        self._divider(scroll, 1)

        nf = ctk.CTkFrame(scroll, fg_color=("gray95", "gray15"), corner_radius=8)
        nf.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        nf.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(nf, text="Name (GitHub username):", font=ctk.CTkFont(size=13)
                      ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))
        self.name_entry = ctk.CTkEntry(nf, height=34)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=(10, 4))

        ctk.CTkLabel(nf, text="Email (for git commits):", font=ctk.CTkFont(size=13)
                      ).grid(row=1, column=0, sticky="w", padx=14, pady=(4, 12))
        self.email_entry = ctk.CTkEntry(nf, height=34)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=(4, 10))

        self.identity_btn = ctk.CTkButton(nf, text="Save Identity",
                                           command=self._save_identity)
        self.identity_btn.grid(row=2, column=0, columnspan=2, pady=(0, 12))

        self.identity_status = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12))
        self.identity_status.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 6))

        # ── SSH Key ──
        self._section(scroll, "SSH Key (auto-managed)", 5)
        self._divider(scroll, 6)

        self.key_box = ctk.CTkFrame(scroll, fg_color=("gray95", "gray15"), corner_radius=8)
        self.key_box.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.key_box.grid_columnconfigure(1, weight=1)

        self.key_status = ctk.CTkLabel(self.key_box, text="", font=ctk.CTkFont(size=13))
        self.key_status.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 2))

        self.key_type = ctk.CTkLabel(self.key_box, text="",
                                      font=ctk.CTkFont(size=12), text_color="gray")
        self.key_type.grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 2))

        self.key_pub = ctk.CTkTextbox(self.key_box, height=50,
                                       font=ctk.CTkFont(size=10, family="monospace"), wrap="word")
        self.key_pub.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))
        self.key_pub.configure(state="disabled")

        kr = ctk.CTkFrame(scroll, fg_color="transparent")
        kr.grid(row=8, column=0, sticky="w", padx=10, pady=(0, 14))
        self.copy_btn = ctk.CTkButton(kr, text="Copy Public Key", command=self._copy_pubkey)
        self.copy_btn.pack(side="left", padx=(0, 6))
        ctk.CTkButton(kr, text="Regenerate Key", command=self._regenerate_key).pack(
            side="left", padx=(0, 6))
        ctk.CTkButton(kr, text="Import Existing Key", command=self._import_key).pack(
            side="left", padx=(0, 6))
        ctk.CTkButton(kr, text="Open GitHub Keys Page", fg_color="#2c3e50",
                       command=self._open_github).pack(side="left", padx=(0, 6))

        # ── GitHub Token ──
        self._section(scroll, "GitHub Token (for HTTPS remotes)", 10)
        self._divider(scroll, 11)

        tf = ctk.CTkFrame(scroll, fg_color="transparent")
        tf.grid(row=12, column=0, sticky="ew", padx=10, pady=(0, 12))
        tf.grid_columnconfigure(0, weight=1)

        self.token_entry = ctk.CTkEntry(tf, placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxx",
                                         show="*", height=36)
        self.token_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(tf, text="Save Token", width=110, command=self._save_token).grid(
            row=0, column=1)

        ctk.CTkLabel(scroll, text="Create a token at: github.com/settings/tokens",
                      font=ctk.CTkFont(size=11), text_color="gray").grid(
            row=13, column=0, sticky="w", padx=14, pady=(0, 18))

        # ── About ──
        self._section(scroll, "About", 15)
        self._divider(scroll, 16)

        ctk.CTkLabel(scroll, text="Ghost Engineer  ·  desktop app for generating realistic commit histories",
                      font=ctk.CTkFont(size=12), text_color="gray").grid(
            row=17, column=0, sticky="w", padx=14, pady=(0, 20))

        self._refresh()

    def _section(self, parent, text, row):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=14, pady=(18, 2))

    def _divider(self, parent, row):
        ctk.CTkFrame(parent, height=1, fg_color=("gray80", "gray30")).grid(
            row=row, column=0, sticky="ew", padx=10, pady=(0, 10))

    def _refresh(self):
        # identity
        name, email = self.cfg.get_identity()
        if name:
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, name)
        if email:
            self.email_entry.delete(0, "end")
            self.email_entry.insert(0, email)
        if name and email:
            self.identity_status.configure(text="✅  Identity saved", text_color="#2ecc71")
            self.identity_btn.configure(text="Update Identity")
        else:
            self.identity_status.configure(text="")
            self.identity_btn.configure(text="Save Identity")

        # ssh key
        pub = self.cfg.get_ssh_public_key()
        has_key = self.cfg.has_ssh_key()

        if has_key and pub:
            self.key_status.configure(text="✅  SSH key loaded", text_color="#2ecc71")
            parts = pub["content"].split()
            self.key_type.configure(text=f"Type: {parts[0] if parts else 'unknown'}")
            self.key_pub.configure(state="normal")
            self.key_pub.delete("1.0", "end")
            self.key_pub.insert("1.0", pub["content"])
            self.key_pub.configure(state="disabled")
            self.copy_btn.configure(state="normal")
        elif has_key:
            self.key_status.configure(text="⚠️  Private key found (no .pub file)", text_color="#f39c12")
            self.key_type.configure(text="")
            self.key_pub.configure(state="normal")
            self.key_pub.delete("1.0", "end")
            self.key_pub.configure(state="disabled")
            self.copy_btn.configure(state="disabled")
        else:
            self.key_status.configure(text="❌  No SSH key configured", text_color="#e74c3c")
            self.key_type.configure(text="")
            self.key_pub.configure(state="normal")
            self.key_pub.delete("1.0", "end")
            self.key_pub.configure(state="disabled")
            self.copy_btn.configure(state="disabled")

        # token
        token = self.cfg.get_github_token()
        if token:
            self.token_entry.delete(0, "end")
            self.token_entry.insert(0, "••••••••" + token[-4:])

    def _save_identity(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        if not name or not email:
            showwarning(self, "Missing fields", "Enter both name and email.")
            return
        self.cfg.save_identity(name, email)

        # auto-generate SSH key if none exists
        if not self.cfg.has_ssh_key():
            try:
                self.cfg.generate_ssh_key()
            except Exception as ex:
                showerror(self, "SSH Key Error",
                          f"Identity saved but SSH key generation failed:\n{ex}")
                self._refresh()
                return

        self._refresh()
        showinfo(self, "Done",
                 "Identity saved!\n\n"
                 "An SSH key was generated for you.\n"
                 "Copy it and add to GitHub to use SSH remotes.")

    def _regenerate_key(self):
        if not askyesno(self, "Regenerate Key",
                         "This will overwrite your existing SSH key.\nContinue?"):
            return
        try:
            self.cfg.generate_ssh_key()
            self._refresh()
            showinfo(self, "Key Regenerated",
                     "New SSH key created!\n"
                     "Copy it and add to GitHub.")
        except Exception as ex:
            showerror(self, "Error", str(ex))

    def _import_key(self):
        p = filedialog.askopenfilename(title="Select private key file",
                                        filetypes=[("All files", "*")])
        if not p:
            return
        if p.endswith(".pub"):
            showwarning(self, "Wrong file",
                        "Select the PRIVATE key (without .pub extension).")
            return
        try:
            self.cfg.import_ssh_key(p)
            self._refresh()
            showinfo(self, "Done", "SSH key imported successfully!")
        except Exception as ex:
            showerror(self, "Error", str(ex))

    def _open_github(self):
        webbrowser.open("https://github.com/settings/keys")

    def _copy_pubkey(self):
        pub = self.cfg.get_ssh_public_key()
        if not pub:
            showwarning(self, "No Key", "No public key found to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(pub["content"])
        self.copy_btn.configure(text="Copied!", fg_color="#2ecc71")
        self.after(2000, lambda: self.copy_btn.configure(
            text="Copy Public Key", fg_color=("#3a7ebf", "#1f538d")))
        show_public_key(self, pub["content"])

    def _save_token(self):
        t = self.token_entry.get().strip()
        if not t:
            showwarning(self, "Empty", "Enter a GitHub token first")
            return
        if len(t) < 10:
            showwarning(self, "Invalid", "That doesn't look like a valid token")
            return
        self.cfg.save_github_token(t)
        self.token_entry.delete(0, "end")
        self.token_entry.insert(0, "••••••••" + t[-4:])
        showinfo(self, "Saved", "GitHub token saved.")
