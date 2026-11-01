# GUI_main.py
import customtkinter as ctk
from datetime import datetime

from widgets import Dashboard, SidePanel
from base import PlaceholderPage
from pages.personal_todo_list import PersonalListPage
from pages.team_projects import TeamProjectsPage
from pages.knowledge_base import KnowledgeBasePage
from pages.my_tasks import MyTasksPage
from pages.manager_dashboard import DashboardPage
from pages.new_project import NewProjectPage
from pages.manage_teams import ManageTeamsPage
from pages.themes_page import ThemesPage

from theme_config import ThemeManager
from sample_data import LIVE_USERS
from organisation import Permission, organisation

# Base static page bindings (Teams are loaded dynamically per-team key)
PAGES = {
    "Personal To-do List": PersonalListPage,
    "List 1": PersonalListPage,
    "Knowledge Base": KnowledgeBasePage,
    "My Tasks": MyTasksPage,
    "Dashboard": DashboardPage,
    "New Project": NewProjectPage,
    "Manage Teams & Roles": ManageTeamsPage,
    "Themes": ThemesPage,
}


def nav_items_for(email: str) -> list[str]:
    """Sidebar links this user's role is allowed to see."""
    items = ["My Tasks"]
    if organisation.can(email, Permission.VIEW_DASHBOARD):
        items.append("Dashboard")
    if organisation.can(email, Permission.CREATE_PROJECTS):
        items.append("New Project")
    if organisation.can(email, Permission.CREATE_TEAMS):
        items.append("Manage Teams & Roles")
    items.append("Themes")
    return items


def teams_for_user(email: str) -> dict:
    """Team name -> team ID, for the teams this user can open."""
    return {team.name: team.id for team in organisation.teams_for(email)}


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
        self.allowed_teams = teams_for_user(self.current_user["email"])

        self.title("Productivity & Task Management Platform")
        self.geometry("1200x900")
        self.minsize(500, 400)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # 1. Dashboard (Top Bar) with user profile attached
        self.logged_out = False      # True if the user pressed Log Out
        self.dashboard = Dashboard(self, user_info=self.current_user, on_logout=self.logout)
        self.dashboard.grid(row=0, column=0, columnspan=2, sticky="ew")

        # 2. SidePanel with only the permitted team options
        permitted_team_names = list(self.allowed_teams.keys())
        self.sidePanel = SidePanel(
            self,
            command=self.show_page,
            team_items=permitted_team_names,
            extra_items=nav_items_for(self.current_user["email"])
        )
        self.sidePanel.grid(row=1, column=0, sticky="ns")

        # When a manager creates a team, add it to the sidebar straight away
        organisation.on_change(self.refresh_teams)

        # 3. Main Content Container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.pages = {}
        self.current = None

        # Automatically open the first available team on login
        initial_page = permitted_team_names[0] if permitted_team_names else "Personal To-do List"
        self.show_page(initial_page)

        # Live Theme Engine integration (ThemeStudioWindow removed; now inside "Themes" page)
        ThemeManager.subscribe(self.apply_theme)

    def show_page(self, name):
        if self.current:
            self.current.pack_forget()

        # Cache pages so task updates persist during the session
        if name not in self.pages:
            if name in self.allowed_teams:
                self.pages[name] = TeamProjectsPage(self.content, self, team_key=name)
            else:
                page_class = PAGES.get(name)
                if page_class:
                    self.pages[name] = page_class(self.content, self)
                else:
                    self.pages[name] = PlaceholderPage(self.content, self, name)

        self.current = self.pages[name]
        self.current.pack(fill="both", expand=True)
        self.sidePanel.select(name)

        if hasattr(self.current, "on_show") and callable(self.current.on_show):
            self.current.on_show()

        # Refresh theme on newly opened screens
        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def logout(self):
        """Close this window. main.py then shows the login screen again.
        Data is kept, so changes made by one user are seen by the next."""
        ThemeManager.unsubscribe(self.apply_theme)
        organisation.remove_listener(self.refresh_teams)
        self.logged_out = True
        self.destroy()

    def refresh_teams(self):
        """Update the Team To-do List dropdown if the user's teams changed."""
        teams = teams_for_user(self.current_user["email"])
        if list(teams) != list(self.allowed_teams):
            self.allowed_teams = teams
            self.sidePanel.update_teams(list(teams))
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

            # Do not overwrite miniature preview boxes on the Themes gallery page
            if getattr(child, "_skip_global_theme", False):
                continue

            # Delegate to custom apply_theme if defined (e.g., SidePanel or Page)
            if hasattr(child, "apply_theme") and callable(child.apply_theme):
                child.apply_theme(p, s)
                continue

            try:
                # 1. Buttons
                if isinstance(child, ctk.CTkButton):
                    txt = str(child.cget("text")).strip()
                    if child.cget("fg_color") == "transparent":
                        child.configure(text_color=p["text"])
                    elif txt == "AM" or child.cget("width") == child.cget("height"):
                        # Keep avatar circle button round
                        child.configure(
                            fg_color=p["primary"],
                            hover_color=p["primary_hover"],
                            text_color=btn_text,
                            border_width=b_width,
                            border_color=p["border"],
                            font=(font_fam, 13, "bold")
                        )
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

                # 2. Entries & Textboxes
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
                elif isinstance(child, ctk.CTkTextbox):
                    child.configure(
                        fg_color=p["entry_bg"],
                        text_color=p["text"],
                        border_color=p["border"],
                        corner_radius=w_radius,
                        border_width=b_width,
                        font=(font_fam, 13)
                    )

                # 3. OptionMenus & ComboBoxes
                elif isinstance(child, (ctk.CTkOptionMenu, ctk.CTkComboBox)):
                    child.configure(
                        fg_color=p["secondary"],
                        button_color=p["primary"],
                        button_hover_color=p["primary_hover"],
                        text_color="#FFFFFF",
                        corner_radius=w_radius,
                        font=(font_fam, 13)
                    )

                # 4. CheckBoxes, Switches, RadioButtons
                elif isinstance(child, (ctk.CTkCheckBox, ctk.CTkSwitch, ctk.CTkRadioButton)):
                    child.configure(
                        fg_color=p["primary"],
                        hover_color=p["primary_hover"],
                        text_color=p["text"],
                        border_color=p["border"],
                        font=(font_fam, 13)
                    )

                # 5. Progress Bars (Styles progress bars on Manager Dashboard & Team Projects)
                elif isinstance(child, ctk.CTkProgressBar):
                    child.configure(
                        progress_color=p["primary"],
                        fg_color=p["entry_bg"],
                        border_color=p["border"],
                        border_width=max(0, b_width - 1),
                        corner_radius=w_radius
                    )

                # 6. Labels (Preserves CTkFont sizes while applying font_family & status colours)
                elif isinstance(child, ctk.CTkLabel):
                    txt = str(child.cget("text"))
                    if "[OVERDUE" in txt or "[OVERLOADED]" in txt or "[ACCESS ENDED]" in txt:
                        child.configure(text_color=p["error"])
                    elif txt.startswith("Logged in:") or txt == "Current selection":
                        child.configure(text_color=p["subtext"])
                    else:
                        child.configure(text_color=p["text"])

                    curr_font = child.cget("font")
                    if isinstance(curr_font, ctk.CTkFont):
                        curr_font.configure(family=font_fam)
                    elif isinstance(curr_font, tuple) and len(curr_font) >= 2:
                        child.configure(font=(font_fam, *curr_font[1:]))

                # 7. Scrollable Frames (Removes the dark grey background on Manager Dashboard)
                elif isinstance(child, ctk.CTkScrollableFrame):
                    child.configure(
                        fg_color="transparent",
                        scrollbar_button_color=p["secondary"],
                        scrollbar_button_hover_color=p["primary"]
                    )

                # 8. Standard Frames & Cards
                elif isinstance(child, ctk.CTkFrame):
                    if child is not self.content and child.cget("fg_color") != "transparent":
                        # Remember original border_width from creation (0 = section header, 1 = card, 2 = overdue)
                        if not hasattr(child, "_orig_border"):
                            child._orig_border = child.cget("border_width")

                        orig_b = child._orig_border
                        if orig_b == 0:
                            child.configure(
                                fg_color=p["card_bg"],
                                border_color=p["border"],
                                corner_radius=0 if child is self.dashboard else s["card_radius"],
                                border_width=0
                            )
                        elif orig_b >= 2:
                            child.configure(
                                fg_color=p["card_bg"],
                                border_color=p["error"],
                                corner_radius=s["card_radius"],
                                border_width=max(2, b_width)
                            )
                        else:
                            child.configure(
                                fg_color=p["card_bg"],
                                border_color=p["border"],
                                corner_radius=s["card_radius"],
                                border_width=b_width
                            )
            except Exception:
                pass

            # Traverse all child containers (including raw tkinter.Canvas inside CTkScrollableFrame)
            if child.winfo_children():
                self._style_widget_tree(child, p, s)


def start_main_application(user_id, login_time=None):
    """Entry point called by main.py after login succeeds.
    Returns True if the user pressed Log Out, False if they closed the window."""
    app = App(user_id=user_id, login_time=login_time)
    app.mainloop()
    return app.logged_out