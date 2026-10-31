# Widgets for the Knowledge Base page: the scrolling feed and its post cards.

import customtkinter as ctk

from forums import Announcement
from theme_config import ThemeManager

MAX_WIDTH = 860     # the feed stops growing past this, like Teams does
GUTTER = 16         # smallest gap either side of the feed


def centred_padding(widget, pixel_width):
    """Padding for each side that keeps content centred and no wider than MAX_WIDTH.

    Tkinter reports sizes in real screen pixels, but CustomTkinter scales
    the padding we give it (Windows display scaling), so convert first.
    """
    scale = ctk.ScalingTracker.get_widget_scaling(widget)
    width = pixel_width / scale
    return max(GUTTER, (width - MAX_WIDTH) / 2)


def initials(name):
    """'Alice Vance' -> 'AV', 'Liam' -> 'L'."""
    return "".join(word[0] for word in name.split()[:2]).upper()


def status_badges(post):
    """The coloured badges a post gets next to its topic: (text, kind)."""
    if isinstance(post, Announcement):
        return [("Announcement", "filled")]
    if post.is_solved():
        return [("Solved", "outline")]
    if post.needs_answer():
        return [("Unsolved", "quiet")]
    return []


def reply_summary(post):
    """Text for the bottom of a card."""
    if isinstance(post, Announcement):
        return "Announcements don't take replies"
    count = post.comment_count()
    if count == 0:
        return "No replies yet"
    return "1 reply" if count == 1 else f"{count} replies"

class Badge(ctk.CTkFrame):
    """A small rounded label: a topic name, Announcement, Solved or Unsolved."""

    def __init__(self, master, text, kind):
        super().__init__(master, corner_radius=10, border_width=1)
        self.kind = kind
        self.label = ctk.CTkLabel(self, text=text, height=20)
        self.label.pack(padx=10, pady=2)

    def apply_theme(self, p, s):
        fill, edge, ink = {
            "filled": (p["primary"], p["primary"], p["card_bg"]),    # Announcement
            "outline": (p["card_bg"], p["primary"], p["primary"]),   # Solved
            "quiet": (p["card_bg"], p["border"], p["subtext"]),      # Unsolved
            "muted": (p["bg"], p["bg"], p["subtext"]),               # topic name
        }[self.kind]
        self.configure(fg_color=fill, border_color=edge)
        self.label.configure(text_color=ink, font=(s["font_family"], 12, "bold"))

class FeedPostCard(ctk.CTkFrame):
    """One post in the feed: who posted it and when, its topic and status,
    then the title, the text and how many replies it has."""

    def __init__(self, master, post, reason=""):
        super().__init__(master)
        self.post = post

        # Top row: avatar, name and time on the left, badges on the right
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(16, 8))

        self.avatar = ctk.CTkLabel(top, text=initials(post.author_name),
                                   width=36, height=36, corner_radius=18)
        self.avatar.pack(side="left")

        who = ctk.CTkFrame(top, fg_color="transparent")
        who.pack(side="left", padx=(12, 0))
        self.name_label = ctk.CTkLabel(who, text=post.author_name, anchor="w", height=18)
        self.name_label.pack(anchor="w")
        when = post.created_at.strftime("%d %b %H:%M")
        self.when_label = ctk.CTkLabel(who, text=f"{when} · {reason}" if reason else when,
                                       anchor="w", height=16)
        self.when_label.pack(anchor="w")

        # Packed from the right, so the status badge ends up furthest right
        self.badges = [Badge(top, text, kind) for text, kind in status_badges(post)]
        self.badges.append(Badge(top, post.topic.name, "muted"))
        for badge in self.badges:
            badge.pack(side="right", padx=(8, 0))

        # Title and text
        self.title_label = ctk.CTkLabel(self, text=post.title, anchor="w", justify="left")
        self.title_label.pack(fill="x", padx=20)
        self.body_label = ctk.CTkLabel(self, text=post.plain_text(), anchor="w", justify="left")
        self.body_label.pack(fill="x", padx=20, pady=(4, 14))

        # Bottom strip: how many replies (Section 3 turns this into Show replies / Reply)
        self.divider = ctk.CTkFrame(self, height=1, corner_radius=0)
        self.divider.pack(fill="x", padx=2)
        self.footer_label = ctk.CTkLabel(self, text=reply_summary(post), anchor="w")
        self.footer_label.pack(fill="x", padx=20, pady=6)

        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def set_wrap(self, width):
        """Wrap the title and text to fit a card this wide."""
        self.title_label.configure(wraplength=width - 44)
        self.body_label.configure(wraplength=width - 44)

    def apply_theme(self, p, s):
        font = s["font_family"]
        self.configure(fg_color=p["card_bg"], border_color=p["border"],
                       border_width=s["border_width"], corner_radius=s["card_radius"])
        self.avatar.configure(fg_color=p["primary"], text_color=p["card_bg"],
                              font=(font, 13, "bold"))
        self.name_label.configure(text_color=p["text"], font=(font, 14, "bold"))
        self.when_label.configure(text_color=p["subtext"], font=(font, 12))
        self.title_label.configure(text_color=p["text"], font=(font, 16, "bold"))
        self.body_label.configure(text_color=p["text"], font=(font, 14))
        self.divider.configure(fg_color=p["border"])
        self.footer_label.configure(text_color=p["subtext"], font=(font, 12))
        for badge in self.badges:
            badge.apply_theme(p, s)