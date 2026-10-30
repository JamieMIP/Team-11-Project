# base.py
import customtkinter as ctk
from theme_config import ThemeManager


class Page(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.configure(fg_color="transparent")

        # Defer subscription until all child widgets in subclass __init__ are constructed
        self.after_idle(self._subscribe_theme)

    def _subscribe_theme(self):
        try:
            ThemeManager.subscribe(self.apply_theme)
        except Exception:
            pass

    def destroy(self):
        try:
            ThemeManager.unsubscribe(self.apply_theme)
        except Exception:
            pass
        super().destroy()

    def on_show(self):
        self.apply_theme()

    def apply_theme(self, p=None, s=None):
        """Override in subclasses if needed, or leave to global styling."""
        pass


class PlaceholderPage(Page):
    def __init__(self, master, app, name="Page"):
        super().__init__(master, app)
        self.label = ctk.CTkLabel(self, text=f"{name} (Coming Soon)", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(expand=True)