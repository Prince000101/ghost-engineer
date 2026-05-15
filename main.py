import customtkinter as ctk
from config_manager import ConfigManager
from ui.dashboard import DashboardFrame
from ui.settings import SettingsFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class GhostApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ghost Engineer")
        self.geometry("980x680")
        self.minsize(820, 560)

        self.cfg = ConfigManager()
        self._go_to_dashboard()

    def _switch_to(self, frame_cls, **kwargs):
        for w in self.winfo_children():
            w.destroy()
        new = frame_cls(self, **kwargs)
        new.pack(fill="both", expand=True)

    def _go_to_dashboard(self):
        self._switch_to(DashboardFrame, cfg=self.cfg,
                        on_settings=self._go_to_settings)

    def _go_to_settings(self):
        self._switch_to(SettingsFrame, cfg=self.cfg,
                        on_back=self._go_to_dashboard)


if __name__ == "__main__":
    app = GhostApp()
    app.mainloop()
