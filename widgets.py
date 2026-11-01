import customtkinter as ctk
from base import Page
from theme_config import ThemeManager
import os
from PIL import Image


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
    """Sidebar navigation with icon-based buttons for each main section.

    Colours, corner radius and font all come from ThemeManager,
    so the panel restyles itself whenever the palette or style changes.
    """

    # Icons used for each navigation button
    ICON_MAP = {
        "Personal To-do List": "list-checks",
        "Team To-do List": "user-group",
        "Knowledge Base": "notebook-pen",
        "My Tasks": "layers-plus",
        "Dashboard": "layout-grid-circles",
        "New Project": "layers-plus",
        "Manage Teams & Roles": "users"
    }

    # Text displayed on each button
    DISPLAY_NAMES = {
        "Personal To-do List": "Personal\nTo-do List",
        "Team To-do List": "Team\nTo-do List",
        "Manage Teams & Roles": "Manage Teams\n& Roles"
    }

    def __init__(self, master, command=None, extra_items=None, width=128):
        super().__init__(master, width=width, corner_radius=0)

        self.pack_propagate(False)          
        self.command = command              
        self.links = []                     
        self.selected = None                
        self.icons = {}                     

        # One shared font object for all navigation buttons
        self.nav_font = ctk.CTkFont(size=11)

        # 1. Main navigation buttons
        self._add_link("Personal To-do List")
        self._add_link("Team To-do List")
        self._add_link("Knowledge Base")

        # 2. Role-based links
        items = extra_items or []

        # Add Dashboard if it is not already included
        if "Dashboard" not in items:
            items = list(items) + ["Dashboard"]

        # Prevent duplicate buttons
        added = {
            "Personal To-do List",
            "Team To-do List",
            "Knowledge Base"
        }

        for title in items:
            if title not in added and title in self.ICON_MAP:
                self._add_link(title)
                added.add(title)

        # Keep this LAST: subscribe() applies the theme immediately
        ThemeManager.subscribe(self.apply_theme)

    # ---- icons ----
    def get_icon(self, name):
        """Loads an icon from the icons folder and caches it for reuse."""

        if name not in self.icons:
            path = os.path.join(
                os.path.dirname(__file__),
                "icons",
                name + ".png"
            )

            with Image.open(path) as source:
                image = source.convert("RGBA")

            self.icons[name] = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(26, 26) # to change the size of the icons edit this
            )

        return self.icons[name]

    # ---- theming ----
    def apply_theme(self, palette, style):
        self.configure(
            fg_color=palette["card_bg"],
            corner_radius=0
        )

        self.nav_font.configure(family=style["font_family"])

        for btn in self.links:
            btn.restyle(palette, style)

    def destroy(self):
        ThemeManager.unsubscribe(self.apply_theme)
        super().destroy()

    # ---- navigation ----
    def _add_link(self, title):
        icon_name = self.ICON_MAP[title]
        display_name = self.DISPLAY_NAMES.get(title, title)

        btn = NavButton(
            self,
            title,
            display_name=display_name,
            image=self.get_icon(icon_name),
            command=self._on_select,
            font=self.nav_font
        )

        btn.pack(fill="x", padx=10, pady=0)
        self.links.append(btn)

    def _on_select(self, name):
        """A sidebar button was clicked: highlight it, then tell the App."""

        self.select(name)

        if self.command:
            self.command(name)

    def select(self, name):
        """Highlight the button for the page currently shown."""

        self.selected = name
        self._refresh_selection()

    def _refresh_selection(self):
        for btn in self.links:
            btn.set_selected(btn.title == self.selected)



class NavButton(ctk.CTkButton):
    """A sidebar entry with an icon above its text."""

    def __init__(self, master, title, command=None, display_name=None, **kwargs):

        image = kwargs.pop("image", None)
        font = kwargs.pop("font", None)

        super().__init__(
            master,
            text=display_name or title,
            image=image,
            compound="top",
            anchor="center",
            width=0,
            height=60,
            font=font,
            fg_color="transparent",
            hover_color=NAV_BG,
            hover=False,
            text_color="#FFFFFF",
            border_width=0,
            corner_radius=0,
            command=lambda: command(title) if command else None,
            **kwargs
        )

        self.title = title
        self.selected = False
        self._theme = None

    def set_selected(self, selected):
        self.selected = selected
        self.restyle()

    def restyle(self, palette=None, style=None):

        if palette is not None:
            self._theme = (palette, style)

        if self._theme is None:
            self.configure(
                fg_color="transparent",
                hover_color=NAV_BG,
                text_color="#FFFFFF",
                border_width=0
            )
            return

        p, s = self._theme

        # Apply the theme
        self.configure(
            fg_color="transparent",
            hover_color=NAV_BG,
            text_color=p["text"],
            border_width=0,
            corner_radius=0,
            height=90
        )


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
