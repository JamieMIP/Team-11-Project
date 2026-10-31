import customtkinter as ctk
from base import Page

class Dashboard(ctk.CTkFrame):
    """Top bar of the app, displays active user details and action button."""
    def __init__(self, master, user_info=None, on_logout=None):
        super().__init__(master)

        size = 40
        self.circle_btn = ctk.CTkButton(
            self,
            text="+",
            width=size,
            height=size,
            corner_radius=size // 2
        )
        self.circle_btn.pack(side="right", padx=15, pady=8)

        # Log Out: closes the app window and goes back to the login screen
        if on_logout is not None:
            self.logout_btn = ctk.CTkButton(self, text="Log Out", width=90, command=on_logout)
            self.logout_btn.pack(side="right", padx=(10, 0), pady=8)

        # Active user label (updated dynamically from login session)
        self.label = ctk.CTkLabel(
            self, 
            text="Not Logged In", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label.pack(side="right", pady=2, padx=10)

        if user_info:
            self.set_user(user_info)

    def set_user(self, user_info: dict):
        """Updates the dashboard label with the active user's name and role."""
        name = user_info.get("name", "Unknown")
        role = user_info.get("role", "User")
        self.label.configure(text=f"{name}  •  {role}")


class SidePanel(ctk.CTkFrame):
    """Sidebar navigation with dynamic sections for permitted teams."""
    def __init__(self, master, command=None, team_items=None, extra_items=None):
        super().__init__(master)
        self.command = command
        self.dropdowns = {}

        # 1. Personal To-do List Dropdown
        self.personal_dd = Dropdown(
            self, 
            title="Personal To-do List", 
            items=["List 1"], 
            command=command
        )
        self.personal_dd.pack(fill="x", padx=(10, 20), pady=10)
        self.dropdowns["personal"] = self.personal_dd

        # 2. Team To-do List Dropdown (Populated with permitted teams)
        teams = team_items if team_items is not None else ["Team 1"]
        self.team_dd = Dropdown(
            self, 
            title="Team To-do List", 
            items=teams, 
            command=command
        )
        self.team_dd.pack(fill="x", padx=(10, 20), pady=10)
        self.dropdowns["team"] = self.team_dd

        # 3. Knowledge Base direct button
        NavButton(self, "Knowledge Base", command=command).pack(
            fill="x", padx=(10, 20), pady=10
        )

        # 4. Role-based links (My Tasks, Dashboard, New Project, Manage Teams & Roles)
        for title in extra_items or []:
            NavButton(self, title, command=command).pack(
                fill="x", padx=(10, 20), pady=10
            )

    def update_teams(self, team_list: list):
        """Allows dynamic refreshing of team entries based on user permissions."""
        if "team" in self.dropdowns:
            self.dropdowns["team"].set_items(team_list)


class NavButton(ctk.CTkFrame):
    """A sidebar entry that goes straight to a page (no dropdown)."""
    def __init__(self, master, title, command=None, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkButton(
            self, 
            text=f"   {title}", 
            anchor="w", 
            fg_color="transparent",
            command=lambda: command(title) if command else None
        ).pack(fill="x")


class Dropdown(ctk.CTkFrame):
    """Collapsible dropdown menu for the side panel."""
    def __init__(self, master, title, items, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        self.open = False
        self.command = command

        self.header = ctk.CTkButton(
            self, 
            text=f"▶ {title}", 
            anchor="w",
            fg_color="transparent", 
            command=self.toggle
        )
        self.header.pack(fill="x")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.set_items(items)

    def set_items(self, items):
        """Destroys and recreates child buttons cleanly when teams change."""
        for child in self.body.winfo_children():
            child.destroy()

        for item in items:
            ctk.CTkButton(
                self.body, 
                text=item, 
                anchor="w",
                command=lambda i=item: self._clicked(i)
            ).pack(fill="x", padx=(20, 0), pady=1)

    def _clicked(self, item):
        if self.command:
            self.command(item)

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.body.pack(fill="x")
            self.header.configure(text=f"▼ {self.title}")
        else:
            self.body.pack_forget()
            self.header.configure(text=f"▶ {self.title}")


