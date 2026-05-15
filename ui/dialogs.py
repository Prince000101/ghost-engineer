import customtkinter as ctk


def _center_on_parent(dialog, parent):
    dialog.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_x()
    py = parent.winfo_y()
    dw = dialog.winfo_width()
    dh = dialog.winfo_height()
    x = px + (pw - dw) // 2
    y = py + (ph - dh) // 2
    dialog.geometry(f"+{x}+{y}")


class GhostDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, buttons=None, width=400):
        super().__init__(parent)
        self.result = None

        if buttons is None:
            buttons = ["OK"]

        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.after(50, self.grab_set)

        line_count = message.count('\n') + 1
        est_lines = max(line_count, len(message) // 48 + 1)
        height = max(160, est_lines * 22 + 100)
        self.geometry(f"{width}x{height}")

        msg = ctk.CTkLabel(self, text=message, wraplength=width - 60,
                           font=ctk.CTkFont(size=13), justify="center")
        msg.pack(expand=True, padx=30, pady=(24, 8))

        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(pady=(4, 20))

        self._btns = []
        for text in buttons:
            fg = None if text == "Cancel" else None
            if text == "Yes" or text == "OK":
                fg = "#2ecc71"
                hov = "#27ae60"
            elif text == "No" or text == "Cancel":
                fg = "gray"
                hov = "#666666"
            elif text == "Delete":
                fg = "#c0392b"
                hov = "#a93226"
            else:
                fg = None
                hov = None

            btn = ctk.CTkButton(bf, text=text, width=100,
                                fg_color=fg, hover_color=hov,
                                command=lambda t=text: self._done(t))
            btn.pack(side="left", padx=6)
            self._btns.append(btn)

        _center_on_parent(self, parent)

    def _done(self, value):
        self.result = value
        self.grab_release()
        self.destroy()


def askyesno(parent, title, message):
    d = GhostDialog(parent, title, message, buttons=["Yes", "No"])
    parent.wait_window(d)
    return d.result == "Yes"


def showinfo(parent, title, message):
    d = GhostDialog(parent, title, message, buttons=["OK"])
    parent.wait_window(d)


def showwarning(parent, title, message):
    d = GhostDialog(parent, title, message, buttons=["OK"])
    parent.wait_window(d)


def showerror(parent, title, message):
    d = GhostDialog(parent, title, message, buttons=["OK"])
    parent.wait_window(d)


def ask_yes_no_cancel(parent, title, message):
    d = GhostDialog(parent, title, message, buttons=["Yes", "No", "Cancel"])
    parent.wait_window(d)
    return d.result


def show_public_key(parent, key_content):
    d = ctk.CTkToplevel(parent)
    d.title("Public Key")
    d.geometry("580x260")
    d.resizable(False, False)
    d.transient(parent)
    d.after(50, d.grab_set)

    ctk.CTkLabel(d, text="Copy this SSH public key to GitHub:",
                  font=ctk.CTkFont(size=13)).pack(padx=20, pady=(16, 4))

    tb = ctk.CTkTextbox(d, height=90, font=ctk.CTkFont(size=11, family="monospace"),
                         wrap="word")
    tb.pack(fill="x", padx=20, pady=(4, 10))
    tb.insert("1.0", key_content)
    tb.configure(state="disabled")

    ctk.CTkLabel(d, text="Tip: select all (Ctrl+A) then copy (Ctrl+C)",
                  font=ctk.CTkFont(size=11), text_color="gray").pack()

    bf = ctk.CTkFrame(d, fg_color="transparent")
    bf.pack(pady=(8, 16))

    def _copy():
        d.clipboard_clear()
        d.clipboard_append(key_content)
        btn.configure(text="Copied!", fg_color="#2ecc71")
        d.after(2000, lambda: btn.configure(text="Copy Again", fg_color=None))

    btn = ctk.CTkButton(bf, text="Copy Again", width=120, command=_copy)
    btn.pack(side="left", padx=6)
    ctk.CTkButton(bf, text="Done", width=100, command=d.destroy).pack(side="left", padx=6)

    _center_on_parent(d, parent)
