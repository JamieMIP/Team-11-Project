import customtkinter as ctk
from base import Page
from theme_config import ThemeManager



# Sidebar colours. A palette can override these with nav_bg / nav_hover / nav_selected
# keys; otherwise these defaults (a muted navy) are used, so buttons are never uncoloured.
NAV_BG = "#2D4B73"
NAV_HOVER = "#3B82F6"
NAV_SELECTED = "#1E40AF"

# Sidebar packing: tweak these to taste
NAV_PADX = 10          # left/right gap between buttons and the panel edge
NAV_PADY = 10           # vertical gap between buttons
NAV_CHILD_INDENT = 24  # extra left indent for items inside a dropdown


def _shade(hex_colour, factor):
    """Scale a #RRGGBB colour towards black (factor < 1). Returns None if not a hex colour."""
    try:
        h = hex_colour.lstrip("#")
        if len(h) != 6:
            return None
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except (AttributeError, ValueError):
        return None
    return "#{:02X}{:02X}{:02X}".format(int(r * factor), int(g * factor), int(b * factor))


def _nav_colors(palette):
    """(normal, hover, selected) nav colours: blue from the palette's primary."""
    hover = palette.get("nav_hover") or palette.get("primary_hover") or NAV_HOVER
    return (
        palette.get("nav_bg") or palette.get("primary") or NAV_BG,
        hover,
        palette.get("nav_selected") or _shade(hover, 0.7) or NAV_SELECTED,
    )


class Dashboard(ctk.CTkFrame):
    """Top bar of the app, displays active user details and action button."""
    def __init__(self, master, user_info=None, on_logout=None):
        super().__init__(master, corner_radius=0)

        size = 50
        self.circle_btn = ctk.CTkButton(
            self,
            text="AM",
            width=size,
            height=size,
            corner_radius=size // 2
        )
        self.circle_btn.pack(side="right", padx=20, pady=10)

        # Log Out: closes the app window and goes back to the login screen
        if on_logout is not None:
            self.logout_btn = ctk.CTkButton(self, text="Log Out", width=90, command=on_logout)
            self.logout_btn.pack(side="right", padx=(10, 0), pady=10)

        # Active user label (updated from the login session)
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
    """Sidebar navigation with dynamic sections for permitted teams.

    Colours, corner radius, button height and font all come from ThemeManager,
    so the panel restyles itself whenever the palette or style changes.
    """
    def __init__(self, master, command=None, team_items=None, extra_items=None, width=230):
        super().__init__(master, width=width, corner_radius=0)
        self.pack_propagate(False)            # keep the fixed sidebar width
        self.command = command                # App.show_page
        self.dropdowns = {}
        self.links = []                       # plain (non-dropdown) nav buttons
        self.selected = None                  # title of the page currently shown

        # One shared font object: changing its family restyles every button at once
        self.nav_font = ctk.CTkFont(size=13)

        # 1. Personal To-do List Dropdown
        self.personal_dd = Dropdown(
            self,
            title="Personal To-do List",
            items=["List 1"],
            command=self._on_select,
            font=self.nav_font
        )
        self.personal_dd.pack(fill="x", padx=NAV_PADX, pady=(NAV_PADY))
        self.dropdowns["personal"] = self.personal_dd

        # 2. Team To-do List Dropdown (Populated with permitted teams)
        teams = team_items if team_items is not None else ["Team 1"]
        self.team_dd = Dropdown(
            self,
            title="Team To-do List",
            items=teams,
            command=self._on_select,
            font=self.nav_font
        )
        self.team_dd.pack(fill="x", padx=NAV_PADX, pady=(NAV_PADY))
        self.dropdowns["team"] = self.team_dd

        # 3. Knowledge Base direct button
        self._add_link("Knowledge Base")

        # 4. Role-based links (My Tasks, Dashboard, New Project, Manage Teams & Roles)
        for title in extra_items or []:
            self._add_link(title)

        # Keep this LAST: subscribe() styles the panel immediately,
        # so every widget above must already exist.
        ThemeManager.subscribe(self.apply_theme)

    # ---- theming ----
    def apply_theme(self, palette, style):
        self.configure(fg_color=palette["card_bg"], corner_radius=0)

        self.nav_font.configure(family=style["font_family"])
        for dd in self.dropdowns.values():
            dd.restyle(palette, style)
        for btn in self.links:
            btn.restyle(palette, style)

    def destroy(self):
        ThemeManager.unsubscribe(self.apply_theme)
        super().destroy()

    # ---- navigation ----
    def _add_link(self, title):
        btn = NavButton(self, title, command=self._on_select, font=self.nav_font)
        btn.pack(fill="x", padx=NAV_PADX, pady=NAV_PADY)
        self.links.append(btn)

    def _on_select(self, name):
        """A sidebar button was clicked: highlight it, then tell the App."""
        self.select(name)
        if self.command:
            self.command(name)

    def select(self, name):
        """Highlight the button for the page currently shown (doesn't change the page)."""
        self.selected = name
        self._refresh_selection()

    def _refresh_selection(self):
        for btn in self.links:
            btn.set_selected(btn.title == self.selected)
        for dd in self.dropdowns.values():
            dd.mark_selected(self.selected)

    def update_teams(self, team_list: list):
        """Allows dynamic refreshing of team entries based on user permissions."""
        if "team" in self.dropdowns:
            self.dropdowns["team"].set_items(team_list)
            self._refresh_selection()


class NavButton(ctk.CTkButton):
    """A sidebar entry that goes straight to a page (no dropdown)."""
    def __init__(self, master, title, command=None, indent=0, **kwargs):
        kwargs.setdefault("fg_color", NAV_BG)
        kwargs.setdefault("hover_color", NAV_HOVER)
        kwargs.setdefault("text_color", "#FFFFFF")
        super().__init__(
            master,
            text=f"{' ' * indent}{title}",
            anchor="w",
            command=lambda: command(title) if command else None,
            **kwargs
        )
        self.title = title
        self.selected = False
        self._theme = None                   # last (palette, style) applied

    def set_selected(self, selected):
        self.selected = selected
        self.restyle()

    def restyle(self, palette=None, style=None):
        print("restyle", self.title, self.selected)
        if palette is not None:
            self._theme = (palette, style)

        if self._theme is None:
            colour = NAV_SELECTED if self.selected else NAV_BG
            self.configure(fg_color=colour, hover_color=colour if self.selected else NAV_HOVER)
            return

        p, s = self._theme
        bg, hover, selected = _nav_colors(p)
        self.configure(
            fg_color=selected if self.selected else bg,
            hover_color=selected if self.selected else hover,   # no colour flicker on hover
            text_color="#FFFFFF",
            border_color=p["text"],
            corner_radius=s["widget_radius"],
            height=s["btn_height"] - 4
        )


class Dropdown(ctk.CTkFrame):
    """Collapsible dropdown menu for the side panel."""
    def __init__(self, master, title, items, command=None, font=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self.title = title
        self.open = False
        self.command = command
        self.nav_font = font
        self.buttons = []
        self._theme = None
        self.header_selected = False

        font_kw = {"font": font} if font is not None else {}
        self.header = ctk.CTkButton(
            self,
            text=f"▶ {title}",
            anchor="w",
            fg_color=NAV_BG,
            hover_color=NAV_HOVER,
            text_color="#FFFFFF",
            command=self.toggle,
            **font_kw
        )
        self.header.pack(fill="x")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.set_items(items)

    def set_items(self, items):
        """Destroys and recreates child buttons cleanly when teams change."""
        for child in self.body.winfo_children():
            child.destroy()
        self.buttons = []

        font_kw = {"font": self.nav_font} if self.nav_font is not None else {}
        for item in items:
            btn = NavButton(self.body, item, command=self._clicked, **font_kw)
            btn.pack(fill="x", padx=(NAV_CHILD_INDENT, 0), pady=NAV_PADY - 1)
            self.buttons.append(btn)

        if self._theme is not None:           # new buttons pick up the current theme
            self.restyle(*self._theme)

    def restyle(self, palette, style):
        self._theme = (palette, style)
        self._style_header()
        for btn in self.buttons:
            btn.restyle(palette, style)

    def _style_header(self):
        if self._theme is None:
            self.header.configure(fg_color=NAV_SELECTED if self.header_selected else NAV_BG)
            return
        p, s = self._theme
        bg, hover, selected = _nav_colors(p)
        self.header.configure(
            fg_color=selected if self.header_selected else bg,
            hover_color=selected if self.header_selected else hover,
            text_color="#FFFFFF",
            corner_radius=s["widget_radius"],
            height=s["btn_height"] - 4
        )

    def mark_selected(self, name):
        """Highlight the matching item; tint the header and open the dropdown if it's inside."""
        inside = any(b.title == name for b in self.buttons)
        for btn in self.buttons:
            btn.set_selected(btn.title == name)
        self.header_selected = inside
        self._style_header()
        if inside and not self.open:
            self.toggle()

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


class PostCard(ctk.CTkFrame):
    def __init__(self, master, post, size=300):
        super().__init__(master, width=size, height=size,
                         corner_radius=12, border_width=2,
                         border_color="gray40")
        self.pack_propagate(False)
        self.post = post

        ctk.CTkLabel(self, text=post["title"], anchor="w", justify="left",
                     wraplength=size - 30,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(fill="x", padx=12, pady=(12, 0))
        ctk.CTkLabel(self, text=f"by {post['author']}", anchor="w",
                     text_color="gray").pack(fill="x", padx=12)
        ctk.CTkLabel(self, text=post["body"], anchor="nw", justify="left",
                     wraplength=size - 30).pack(fill="both", expand=True, padx=12, pady=(6, 12))

        ctk.CTkButton(self, text="Expand", width=80, height=30, command=self.expand_post).pack(side="right", padx=10, pady=10)
        ctk.CTkButton(self, text="Reply", width=80, height=30, command=self.reply_post).pack(side="right", padx=10, pady=10)

    def expand_post(self):
        """Expand the post to show full content in a new window."""
        top = ctk.CTkToplevel(self)
        top.title(self.post["title"])
        top.geometry("400x400")

        top.transient(self.winfo_toplevel())
        top.after(100, top.lift)
        top.after(100, top.focus)

        ctk.CTkLabel(top, text=self.post["title"], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 0))
        ctk.CTkLabel(top, text=f"by {self.post['author']}", text_color="gray").pack()
        ctk.CTkLabel(top, text=self.post["body"], wraplength=380).pack(pady=10, padx=10)

    def reply_post(self):
        """Open a reply window to allow the user to reply to the post."""
        top = ctk.CTkToplevel(self)
        top.title(f"Reply to {self.post['title']}")
        top.geometry("600x450")

        top.transient(self.winfo_toplevel())
        top.after(100, top.lift)
        top.after(100, top.focus)

        ctk.CTkLabel(top, text=f"Replying to: {self.post['title']}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 0))
        reply_entry = ctk.CTkEntry(top, placeholder_text="Type your reply here...")
        reply_entry.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top, text="Submit Reply", command=lambda: self.submit_reply(reply_entry.get(), top)).pack(pady=10)

print("LOADED widgets from:", __file__)
