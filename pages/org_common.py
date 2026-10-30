"""Shared pieces for the team, project, dashboard and admin pages.

OrgPage works the same way as PersonalListPage:
  * self.email is the logged-in user's email
  * self.message_label shows mistakes ("Couldn't do that: ...")
  * run_service(...) calls the organisation service as that user, shows
    any error, and redraws the page if it worked
All the rules live in organisation/service.py; pages only draw and pass
button clicks on.
"""

from datetime import date, datetime

import customtkinter as ctk

from base import Page
from organisation import OrgError, Priority, organisation
from theme_config import ThemeManager

PRIORITY_NAMES = [priority.value for priority in Priority]        # Low ... Critical


class OrgPage(Page):
    """Base class for every page that uses the organisation service."""

    def __init__(self, master, app):
        super().__init__(master, app)
        self.email = app.current_user["email"]
        self.user = organisation.get_employee(self.email)

    def add_message_label(self):
        """Call once in __init__ where the message line should appear."""
        self.message_label = ctk.CTkLabel(self, text="", anchor="w", justify="left",
                                          wraplength=900)
        self.message_label.pack(fill="x")

    def show_message(self, text):
        """Show a short message above the content, or clear it with ""."""
        self.message_label.configure(text=text)

    def run_service(self, action, *args, **kwargs):
        """Call a service method as the logged-in user, show any error,
        and redraw if it worked. Returns the result, or None if refused."""
        try:
            result = action(self.email, *args, **kwargs)
        except (OrgError, ValueError) as error:
            self.show_message(f"Couldn't do that: {error}")
            return None
        self.show_message("")
        self.refresh()
        return True if result is None else result      # e.g. delete returns nothing

    def on_show(self):
        """Runs every time the page is opened from the sidebar."""
        self.refresh()

    def refresh(self):
        raise NotImplementedError

    def redraw_theme(self):
        """New widgets need the team's colour theme applied to them."""
        if hasattr(self.app, "apply_theme"):
            self.app.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())


def parse_date(text: str) -> date | None:
    """'2026-11-20' -> date. Blank -> None. Anything else -> ValueError."""
    text = text.strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Dates must look like 2026-11-20.") from None


def show_date(day: date | None) -> str:
    """Same format as the team page and the date boxes: 2026-11-20."""
    return day.isoformat() if day else "N/A"


def name_of(email: str | None) -> str:
    return organisation.get_employee(email).name if email else "Unassigned"


def clear(frame) -> None:
    """Remove everything inside a frame, ready to redraw it."""
    for widget in frame.winfo_children():
        widget.destroy()


def people_menu_values(emails) -> tuple[list[str], dict[str, str]]:
    """Names for a dropdown, plus a dict to turn the chosen name back into
    an email. Overloaded people are marked so the assigner can see it."""
    labels, lookup = [], {}
    for email in emails:
        label = name_of(email)
        if organisation.is_overloaded(email):
            label += " (overloaded)"
        labels.append(label)
        lookup[label] = email
    return labels, lookup


def ask_yes_no(parent, question: str) -> bool:
    """A small 'Are you sure?' pop-up. Waits for an answer."""
    answer = {"yes": False}
    window = ctk.CTkToplevel(parent)
    window.title("Please confirm")
    window.geometry("360x140")
    window.transient(parent.winfo_toplevel())
    ctk.CTkLabel(window, text=question, wraplength=320).pack(pady=(20, 12))
    buttons = ctk.CTkFrame(window, fg_color="transparent")
    buttons.pack()

    def choose(value):
        answer["yes"] = value
        window.destroy()

    ctk.CTkButton(buttons, text="Yes", width=90, command=lambda: choose(True)).pack(side="left", padx=6)
    ctk.CTkButton(buttons, text="Cancel", width=90, command=lambda: choose(False)).pack(side="left", padx=6)
    window.after(100, window.grab_set)
    parent.wait_window(window)
    return answer["yes"]
