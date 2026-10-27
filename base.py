import customtkinter as ctk

class Page(ctk.CTkFrame):
    """Base class. Subclass this to make a new screen."""
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app          # gives access to the main window if needed

    def on_show(self):
        """Called every time the page is displayed. Override to refresh data."""
        pass

class PlaceholderPage(Page):
    def __init__(self, master, app, name):
        super().__init__(master, app)
        ctk.CTkLabel(self, text=f"{name} (not built yet)").pack(pady=20)

