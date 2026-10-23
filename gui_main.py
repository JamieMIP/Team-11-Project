import customtkinter as ctk
from widgets import Dashboard, SidePanel, Dropdown
from base import PlaceholderPage
from pages.personal_todo_list import PersonalListPage
from pages.team_todo_list import TeamListPage

from theme_config import ThemeManager
from theme_studio import ThemeStudioWindow

PAGES = {
    "List 1": PersonalListPage,
    "Team 1": TeamListPage,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My First App")
        self.geometry("1200x900")
        self.minsize(400, 300)

        self.columnconfigure(1, weight=1)   # content column stretches
        self.rowconfigure(1, weight=1)      # content row stretches

        self.dashboard = Dashboard(self)
        self.dashboard.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.sidePanel = SidePanel(self, command=self.show_page)
        self.sidePanel.grid(row=1, column=0, sticky="ns")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.pages = {}
        self.current = None

        # Hook into the global ThemeManager and launch the live Theme Studio
        ThemeManager.subscribe(self.apply_theme)
        self.theme_studio = ThemeStudioWindow(self)

    def show_page(self, name):
        if self.current:
            self.current.pack_forget()

        if name not in self.pages:
            page_class = PAGES.get(name)
            if page_class:
                self.pages[name] = page_class(self.content, self)
            else:
                self.pages[name] = PlaceholderPage(self.content, self, name)

        self.current = self.pages[name]
        self.current.pack(fill="both", expand=True)
        self.current.on_show()

        # Immediately theme newly instantiated or displayed pages
        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def apply_theme(self, p, s):
        """Applies active palette (p) and geometry style (s) across the entire GUI."""
        self.configure(fg_color=p["bg"])
        self._style_widget_tree(self, p, s)

    def _style_widget_tree(self, parent, p, s):
        """Recursively styles all child CustomTkinter widgets without altering their logic."""
        btn_text = "#000000" if ThemeManager.current_palette_name == "Cyber Neon" else "#FFFFFF"
        font_fam = s["font_family"]
        w_radius = s["widget_radius"]
        b_width = s["border_width"]

        for child in parent.winfo_children():
            # Skip floating Toplevel windows like the Theme Studio itself
            if isinstance(child, ctk.CTkToplevel):
                continue

            # If a teammate wrote a custom apply_theme(p, s) method on their widget, run it
            if hasattr(child, "apply_theme") and callable(child.apply_theme):
                child.apply_theme(p, s)
                continue

            try:
                if isinstance(child, ctk.CTkButton):
                    child.configure(
                        fg_color=p["primary"],
                        hover_color=p["primary_hover"],
                        text_color=btn_text,
                        corner_radius=w_radius,
                        border_width=b_width,
                        border_color=p["border"],
                        font=(font_fam, 13, "bold")
                    )
                elif isinstance(child, ctk.CTkEntry):
                    child.configure(
                        fg_color=p["entry_bg"],
                        text_color=p["text"],
                        placeholder_text_color=p["subtext"],
                        border_color=p["border"],
                        corner_radius=w_radius,
                        border_width=b_width,
                        font=(font_fam, 13)
                    )
                elif isinstance(child, (ctk.CTkOptionMenu, ctk.CTkComboBox)):
                    child.configure(
                        fg_color=p["secondary"],
                        button_color=p["primary"],
                        button_hover_color=p["primary_hover"],
                        text_color="#FFFFFF",
                        corner_radius=w_radius,
                        font=(font_fam, 13)
                    )
                elif isinstance(child, (ctk.CTkCheckBox, ctk.CTkSwitch, ctk.CTkRadioButton)):
                    child.configure(
                        fg_color=p["primary"],
                        hover_color=p["primary_hover"],
                        text_color=p["text"],
                        border_color=p["border"],
                        font=(font_fam, 13)
                    )
                elif isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=p["text"])
                elif isinstance(child, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                    # Keep transparent layout wrappers transparent; style visible cards/panels
                    if child is not self.content and child.cget("fg_color") != "transparent":
                        child.configure(
                            fg_color=p["card_bg"],
                            border_color=p["border"],
                            corner_radius=s["card_radius"],
                            border_width=b_width
                        )
            except Exception:
                pass

            # Recurse into container frames to style nested widgets inside pages and panels
            if isinstance(child, (ctk.CTkFrame, ctk.CTkScrollableFrame, ctk.CTkTabview)):
                self._style_widget_tree(child, p, s)


if __name__ == "__main__":
    app = App()
    app.mainloop()