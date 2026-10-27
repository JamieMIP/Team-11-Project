# GUI_main.py
import customtkinter as ctk
from datetime import datetime

from widgets import Dashboard, SidePanel
from base import PlaceholderPage
from pages.personal_todo_list import PersonalListPage
from pages.team_todo_list import TeamListPage
from pages.knowledge_base import KnowledgeBasePage

from theme_config import ThemeManager
from theme_studio import ThemeStudioWindow
from sample_data import LIVE_USERS, get_user_teams

# Base static page bindings (Teams are loaded dynamically per-team key)
PAGES = {
    "List 1": PersonalListPage,
    "Knowledge Base": KnowledgeBasePage,
}


def _parse_user_id(raw_id) -> int:
    """Safely converts login user_id into 0, 1, or 2."""
    if isinstance(raw_id, int) and raw_id in (0, 1, 2):
        return raw_id
    raw_str = str(raw_id).strip()
    if raw_str in ("0", "1", "2"):
        return int(raw_str)
    for digit in ("0", "1", "2"):
        if digit in raw_str:
            return int(digit)
    return 2


class App(ctk.CTk):
    def __init__(self, user_id=2, login_time=None):
        super().__init__()
        self.current_user_id = _parse_user_id(user_id)
        self.login_time = login_time or datetime.now()

        # Retrieve user profile & permitted teams
        self.current_user = LIVE_USERS.get(self.current_user_id, LIVE_USERS[2])
        self.allowed_teams = get_user_teams(self.current_user_id)

        self.title("Productivity & Task Management Platform")
        self.geometry("1200x900")
        self.minsize(500, 400)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # 1. Dashboard (Top Bar) with user profile attached
        self.dashboard = Dashboard(self, user_info=self.current_user)
        self.dashboard.grid(row=0, column=0, columnspan=2, sticky="ew")

        # 2. SidePanel with only the permitted team options
        permitted_team_names = list(self.allowed_teams.keys())
        self.sidePanel = SidePanel(
            self, 
            command=self.show_page, 
            team_items=permitted_team_names
        )
        self.sidePanel.grid(row=1, column=0, sticky="ns")

        # 3. Main Content Container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.pages = {}
        self.current = None

        # Automatically open the first available team on login
        initial_page = permitted_team_names[0] if permitted_team_names else "List 1"
        self.show_page(initial_page)

        # Live Theme Engine integration
        ThemeManager.subscribe(self.apply_theme)
        self.theme_studio = ThemeStudioWindow(self)

    def show_page(self, name):
        if self.current:
            self.current.pack_forget()

        # Cache pages so task updates persist during the session
        if name not in self.pages:
            if name in self.allowed_teams:
                self.pages[name] = TeamListPage(self.content, self, team_key=name)
            else:
                page_class = PAGES.get(name)
                if page_class:
                    self.pages[name] = page_class(self.content, self)
                else:
                    self.pages[name] = PlaceholderPage(self.content, self, name)

        self.current = self.pages[name]
        self.current.pack(fill="both", expand=True)

        if hasattr(self.current, "on_show") and callable(self.current.on_show):
            self.current.on_show()

        # Refresh theme on newly opened screens
        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def apply_theme(self, p, s):
        """Applies active palette (p) and geometry style (s) across the entire GUI."""
        self.configure(fg_color=p["bg"])
        self._style_widget_tree(self, p, s)

    def _style_widget_tree(self, parent, p, s):
        btn_text = "#000000" if ThemeManager.current_palette_name == "Cyber Neon" else "#FFFFFF"
        font_fam = s["font_family"]
        w_radius = s["widget_radius"]
        b_width = s["border_width"]

        for child in parent.winfo_children():
            if isinstance(child, ctk.CTkToplevel):
                continue

            if hasattr(child, "apply_theme") and callable(child.apply_theme):
                child.apply_theme(p, s)
                continue

            try:
                if isinstance(child, ctk.CTkButton):
                    # Keep transparent text nav buttons transparent
                    if child.cget("fg_color") == "transparent":
                        child.configure(text_color=p["text"])
                    else:
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
                    if child is not self.content and child.cget("fg_color") != "transparent":
                        child.configure(
                            fg_color=p["card_bg"],
                            border_color=p["border"],
                            corner_radius=s["card_radius"],
                            border_width=b_width
                        )
            except Exception:
                pass

            if isinstance(child, (ctk.CTkFrame, ctk.CTkScrollableFrame, ctk.CTkTabview)):
                self._style_widget_tree(child, p, s)


def start_main_application(user_id, login_time=None):
    """Entry point called by main.py after login succeeds."""
    app = App(user_id=user_id, login_time=login_time)
    app.mainloop()