# Widgets for the Knowledge Base page: the scrolling feed and its post cards.

import customtkinter as ctk

from theme_config import ThemeManager
from forums import Announcement, ForumPost
from pages.rich_text import RichText

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
        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def apply_theme(self, p, s):
        fill, edge, ink = {
            "filled": (p["primary"], p["primary"], p["card_bg"]),    # Announcement
            "outline": (p["card_bg"], p["primary"], p["primary"]),   # Solved
            "quiet": (p["card_bg"], p["border"], p["subtext"]),      # Unsolved
            "muted": (p["bg"], p["bg"], p["subtext"]),               # topic name
        }[self.kind]
        self.configure(fg_color=fill, border_color=edge)
        self.label.configure(text_color=ink, font=(s["font_family"], 12, "bold"))

class ReplyRow(ctk.CTkFrame):
    """One reply: small avatar, name and time, then the text. The accepted
    solution is outlined, and the post's author gets a button to mark or
    unmark it."""

    def __init__(self, master, comment, is_solution, can_mark, on_toggle):
        super().__init__(master, corner_radius=10, border_width=1)
        self.is_solution = is_solution

        self.avatar = ctk.CTkLabel(self, text=initials(comment.author_name),
                                   width=28, height=28, corner_radius=14)
        self.avatar.pack(side="left", anchor="n", padx=10, pady=10)

        text = ctk.CTkFrame(self, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True, pady=8)

        heading = ctk.CTkFrame(text, fg_color="transparent")
        heading.pack(fill="x")
        self.name_label = ctk.CTkLabel(heading, text=comment.author_name, height=18)
        self.name_label.pack(side="left")
        self.when_label = ctk.CTkLabel(heading, text=comment.created_at.strftime("%d %b %H:%M"),
                                       height=18)
        self.when_label.pack(side="left", padx=(8, 0))

        self.solution_label = None
        if is_solution:
            self.solution_label = ctk.CTkLabel(heading, text="Accepted solution", height=18)
            self.solution_label.pack(side="left", padx=(8, 0))

        self.mark_button = None
        if can_mark:
            self.mark_button = ctk.CTkButton(
                heading, text="Unmark solution" if is_solution else "Mark as solution",
                width=0, height=22, fg_color="transparent", command=on_toggle)
            self.mark_button.pack(side="right", padx=(0, 10))

        self.body_label = ctk.CTkLabel(text, text=comment.plain_text(), anchor="w", justify="left")
        self.body_label.pack(fill="x")

        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def set_wrap(self, width):
        self.body_label.configure(wraplength=width)

    def apply_theme(self, p, s):
        font = s["font_family"]
        if self.is_solution:
            self.configure(fg_color=p["card_bg"], border_color=p["primary"])
        else:
            self.configure(fg_color=p["bg"], border_color=p["bg"])
        self.avatar.configure(fg_color=p["primary"], text_color=p["card_bg"],
                              font=(font, 11, "bold"))
        self.name_label.configure(text_color=p["text"], font=(font, 13, "bold"))
        self.when_label.configure(text_color=p["subtext"], font=(font, 12))
        self.body_label.configure(text_color=p["text"], font=(font, 13))
        if self.solution_label is not None:
            self.solution_label.configure(text_color=p["primary"], font=(font, 12, "bold"))
        if self.mark_button is not None:
            self.mark_button.configure(text_color=p["primary"], hover_color=p["card_bg"],
                                       font=(font, 12))

class ReplyPanel(ctk.CTkFrame):
    """The replies under a post, oldest first, and a box to write a new one.

    It doesn't talk to the forum itself: on_send(text) and
    on_toggle_solution(comment) are given to it by the card.
    """

    def __init__(self, master, post, can_mark, on_send, on_toggle_solution):
        super().__init__(master)
        self.post = post
        self.can_mark = can_mark
        self.on_send = on_send
        self.on_toggle_solution = on_toggle_solution
        self.rows = []
        self.wrap_width = 400

        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="x", padx=12, pady=(12, 0))

        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(fill="x", padx=12, pady=12)
        self.entry = ctk.CTkEntry(box, placeholder_text="Write a reply...", height=34)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda event: self.send())
        self.send_button = ctk.CTkButton(box, text="Send", width=80, height=34,
                                         command=self.send)
        self.send_button.pack(side="left", padx=(10, 0))

        self.show_rows()
        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def show_rows(self):
        """Redraw every reply (after a new one, or when the solution changes)."""
        for row in self.rows:
            row.destroy()
        solution = getattr(self.post, "accepted_solution", None)   # Announcements have none
        self.rows = [
            ReplyRow(self.list_frame, comment, comment is solution, self.can_mark,
                     on_toggle=lambda c=comment: self.on_toggle_solution(c))
            for comment in self.post.comments()
        ]
        for row in self.rows:
            row.pack(fill="x", pady=(0, 6))
            row.set_wrap(self.wrap_width)

    def send(self):
        """Send what's in the box, unless it's blank."""
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.on_send(text)

    def focus_entry(self):
        self.entry.focus_set()

    def set_wrap(self, card_width):
        """Work out how wide reply text can be inside a card this wide."""
        # card padding, panel padding and the reply's avatar all take space
        self.wrap_width = card_width - 2 * 12 - 2 * 12 - 48 - 12
        for row in self.rows:
            row.set_wrap(self.wrap_width)

    def apply_theme(self, p, s):
        font = s["font_family"]
        self.configure(fg_color=p["bg"], corner_radius=min(s["card_radius"], 12))
        self.entry.configure(fg_color=p["entry_bg"], text_color=p["text"],
                             placeholder_text_color=p["subtext"], border_color=p["border"],
                             border_width=s["border_width"], corner_radius=s["widget_radius"],
                             font=(font, 13))
        self.send_button.configure(fg_color=p["primary"], hover_color=p["primary_hover"],
                                   text_color=p["card_bg"], corner_radius=s["widget_radius"],
                                   font=(font, 13, "bold"))
        for row in self.rows:
            row.apply_theme(p, s)

class FeedPostCard(ctk.CTkFrame):
    """One post in the feed: who posted it and when, its topic and status,
    then the title, the text and how many replies it has."""

    def __init__(self, master, post, reason, page):
        super().__init__(master)
        self.post = post
        self.page = page            # the Knowledge Base page, which talks to the forum
        self.wrap_width = 600

        # Top row: avatar, name and time on the left, badges on the right
        self.top = ctk.CTkFrame(self, fg_color="transparent")
        self.top.pack(fill="x", padx=20, pady=(16, 8))

        self.avatar = ctk.CTkLabel(self.top, text=initials(post.author_name),
                                   width=36, height=36, corner_radius=18)
        self.avatar.pack(side="left")

        who = ctk.CTkFrame(self.top, fg_color="transparent")
        who.pack(side="left", padx=(12, 0))
        self.name_label = ctk.CTkLabel(who, text=post.author_name, anchor="w", height=18)
        self.name_label.pack(anchor="w")
        when = post.created_at.strftime("%d %b %H:%M")
        self.when_label = ctk.CTkLabel(who, text=f"{when} · {reason}" if reason else when,
                                       anchor="w", height=16)
        self.when_label.pack(anchor="w")

        # Packed from the right, so the status badge ends up furthest right
        self.badges = []
        self.show_badges()

        # Title and text
        self.title_label = ctk.CTkLabel(self, text=post.title, anchor="w", justify="left")
        self.title_label.pack(fill="x", padx=20)
        self.body_label = ctk.CTkLabel(self, text=post.plain_text(), anchor="w", justify="left")
        self.body_label.pack(fill="x", padx=20, pady=(4, 14))

        # Tags, if the post has any: "#vpn  #windows"
        self.tags_label = None
        if post.tags:
            self.tags_label = ctk.CTkLabel(self, text="  ".join(f"#{tag}" for tag in post.tags),
                                           anchor="w", height=16)
            self.tags_label.pack(fill="x", padx=20, pady=(0, 12))

        # Bottom strip: Show/Hide replies on the left, Reply on the right
        self.divider = ctk.CTkFrame(self, height=1, corner_radius=0)
        self.divider.pack(fill="x", padx=2)
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=12, pady=4)

        self.footer_label = ctk.CTkLabel(self.footer, text="", anchor="w")
        self.toggle_button = ctk.CTkButton(self.footer, text="", width=0, height=28,
                                           fg_color="transparent", command=self.toggle_replies)
        self.reply_button = None
        if post.allows_comments():
            self.reply_button = ctk.CTkButton(self.footer, text="Reply", width=70, height=28,
                                              fg_color="transparent", command=self.start_reply)
            self.reply_button.pack(side="right")

        # Delete: on your own posts, or on every post if you're a Manager
        self.delete_button = None
        if page.can_delete(post):
            self.delete_button = ctk.CTkButton(self.footer, text="Delete", width=70, height=28,
                                               fg_color="transparent",
                                               command=lambda: self.page.delete_post(self.post))
            self.delete_button.pack(side="right")

        # The replies are only built the first time someone opens them
        self.replies = None
        self.replies_open = False
        self.update_footer()

        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    # ----- PARTS THAT CHANGE -----

    def show_badges(self):
        """(Re)draw the topic and status badges. Packed from the right,
        so the status badge ends up furthest right."""
        for badge in self.badges:
            badge.destroy()
        self.badges = [Badge(self.top, text, kind) for text, kind in status_badges(self.post)]
        self.badges.append(Badge(self.top, self.post.topic.name, "muted"))
        for badge in self.badges:
            badge.pack(side="right", padx=(8, 0))

    def update_footer(self):
        """Show 'Show 2 replies' / 'Hide 2 replies' as a button, or plain text
        when there's nothing to open."""
        count = self.post.comment_count()
        if count and self.post.allows_comments():
            word = "reply" if count == 1 else "replies"
            action = "Hide" if self.replies_open else "Show"
            self.toggle_button.configure(text=f"{action} {count} {word}")
            self.footer_label.pack_forget()
            self.toggle_button.pack(side="left")
        else:
            self.footer_label.configure(text=reply_summary(self.post))
            self.toggle_button.pack_forget()
            self.footer_label.pack(side="left", padx=8)

    def refresh(self):
        """Redraw after a reply is added or the solution changes."""
        self.show_badges()
        self.update_footer()
        if self.replies is not None:
            self.replies.show_rows()

    # ----- OPENING AND CLOSING THE REPLIES -----

    def toggle_replies(self):
        if self.replies_open:
            self.close_replies()
        else:
            self.open_replies()

    def open_replies(self):
        if self.replies is None:
            can_mark = isinstance(self.post, ForumPost) and self.post.is_author(self.page.user_email)
            self.replies = ReplyPanel(self, self.post, can_mark,
                                      on_send=self.send_reply,
                                      on_toggle_solution=self.toggle_solution)
            self.replies.set_wrap(self.wrap_width)
        self.replies.pack(fill="x", padx=12, pady=(0, 12))
        self.replies_open = True
        self.update_footer()

    def close_replies(self):
        self.replies.pack_forget()
        self.replies_open = False
        self.update_footer()

    def start_reply(self):
        """The Reply button: open the replies and put the cursor in the box."""
        self.open_replies()
        self.replies.focus_entry()

    # ----- ACTIONS (the page does the forum work, the card redraws) -----

    def send_reply(self, text):
        self.page.send_reply(self.post, text)
        self.refresh()

    def toggle_solution(self, comment):
        self.page.toggle_solution(self.post, comment)
        self.refresh()

    def set_wrap(self, width):
        """Wrap the title, text and replies to fit a card this wide."""
        self.wrap_width = width
        self.title_label.configure(wraplength=width - 44)
        self.body_label.configure(wraplength=width - 44)
        if self.replies is not None:
            self.replies.set_wrap(width)

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
        if self.tags_label is not None:
            self.tags_label.configure(text_color=p["primary"], font=(font, 12))
        self.divider.configure(fg_color=p["border"])
        self.footer_label.configure(text_color=p["subtext"], font=(font, 12))

        for button in (self.toggle_button, self.reply_button):
            if button is not None:
                button.configure(text_color=p["primary"], hover_color=p["bg"],
                                 corner_radius=s["widget_radius"], font=(font, 13))

        if self.delete_button is not None:
            self.delete_button.configure(text_color=p["error"], hover_color=p["bg"],
                                         corner_radius=s["widget_radius"], font=(font, 13))
        for badge in self.badges:
            badge.apply_theme(p, s)
        if self.replies is not None:
            self.replies.apply_theme(p, s)
        

class PostFeed(ctk.CTkScrollableFrame):
    # The scrolling list of post cards, in a centred column no wider than MAX_WIDTH.

    def __init__(self, master, page):
        super().__init__(master, fg_color="transparent")
        self.page = page
        self.cards = []
        self.empty_label = None
        self.last_width = None

        self.column = ctk.CTkFrame(self, fg_color="transparent")
        self.column.pack(fill="x")
        self.bind("<Configure>", self.on_resize, add="+")

        # gui_main's theme pass can't reach inside a scrollable frame,
        # so listen for theme changes directly (this also styles it now)
        ThemeManager.subscribe(self.apply_theme)
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """Stop listening for theme changes once the feed is gone (e.g. on Log Out)."""
        if event.widget is self:
            ThemeManager.unsubscribe(self.apply_theme)

    def show(self, posts, reasons):
        """Replace the cards with one for each post. reasons maps post ID -> why it's in the feed."""
        for widget in self.column.winfo_children():
            widget.destroy()
        self.cards = [FeedPostCard(self.column, post, reasons.get(post.id, ""), self.page)
                    for post in posts]
        for card in self.cards:
            card.pack(fill="x", pady=(0, 14))

        self.empty_label = None
        if not posts:
            self.empty_label = ctk.CTkLabel(self.column, text="No posts to show.")
            self.empty_label.pack(pady=40)
            self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

        self.last_width = None      # new cards need wrapping
        self.on_resize()
        self._parent_canvas.yview_moveto(0)  # start from the top of the new list
    
    def remove(self, post):
        """Take one post's card out (after it's deleted), leaving the rest where they are."""
        for card in self.cards:
            if card.post is post:
                card.destroy()
                self.cards.remove(card)
                break
        if not self.cards:
            self.show([], {})       # shows "No posts to show."

    def on_resize(self, event=None):
        """Centre the column, cap its width and re-wrap the cards' text."""
        width = self.winfo_width()
        if width <= 1 or width == self.last_width:
            return
        self.last_width = width

        padding = centred_padding(self, width)
        self.column.pack_configure(padx=padding)

        scale = ctk.ScalingTracker.get_widget_scaling(self)
        column_width = width / scale - 2 * padding
        for card in self.cards:
            card.set_wrap(column_width)

    def apply_theme(self, p, s):
        # The feed sits straight on the page background. Setting it, then
        # "transparent" again, makes the scroll area pick up the new colour.
        self.configure(bg_color=p["bg"])
        self.configure(fg_color="transparent", scrollbar_button_color=p["border"],
                       scrollbar_button_hover_color=p["subtext"])
        if self.empty_label is not None:
            self.empty_label.configure(text_color=p["subtext"], font=(s["font_family"], 14))
        for card in self.cards:
            card.apply_theme(p, s)


FORUM_POST = "Forum post"
ANNOUNCEMENT = "Announcement"
KINDS_WITH_TAGS = (FORUM_POST,)     # announcements don't take tags


class NewPostDialog(ctk.CTkToplevel):
    """The Add New Post window.

    Managers choose between a forum post and an announcement; everyone else
    only writes forum posts. It doesn't talk to the forum itself: the page
    gives it on_submit(kind, title, topic_name, body, tags), which returns
    an error message to show, or None if the post went up.
    """

    def __init__(self, master, topic_names, post_kinds, on_submit, start_topic=None):
        super().__init__(master)
        self.on_submit = on_submit
        self.title("Add new post")
        self.geometry("600x620")
        self.minsize(460, 560)
        self.transient(master.winfo_toplevel())
        self.after(100, self.lift)
        self.after(100, self.focus)

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=20)

        self.heading = ctk.CTkLabel(form, text="Add new post", anchor="w")
        self.heading.pack(fill="x", pady=(0, 12))
        self.field_labels = []

        # Post type: one button per kind this user is allowed to make
        self.kind = ctk.StringVar(value=post_kinds[0])
        self.kind_buttons = []
        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", pady=(0, 12))
        for kind in post_kinds:
            button = ctk.CTkRadioButton(row, text=kind, value=kind, variable=self.kind,
                                        command=self.on_kind_change)
            button.pack(side="left", padx=(0, 24))
            self.kind_buttons.append(button)

        self.add_label(form, "Title")
        self.title_entry = ctk.CTkEntry(form, placeholder_text="What's it about?", height=34)
        self.title_entry.pack(fill="x", pady=(0, 12))

        self.add_label(form, "Topic")
        self.topic_menu = ctk.CTkOptionMenu(form, values=topic_names, height=34)
        self.topic_menu.set(start_topic or topic_names[0])
        self.topic_menu.pack(fill="x", pady=(0, 12))

        self.add_label(form, "Post")
        self.body_box = ctk.CTkTextbox(form, height=170, wrap="word")
        self.body_box.pack(fill="both", expand=True, pady=(0, 12))

        # Tags: forum posts only (announcements don't have them)
        self.tags_area = ctk.CTkFrame(form, fg_color="transparent")
        self.tags_area.pack(fill="x")
        self.add_label(self.tags_area, "Tags")
        self.tags_entry = ctk.CTkEntry(self.tags_area, height=34,
                                       placeholder_text="Separated by commas, e.g. vpn, windows (optional)")
        self.tags_entry.pack(fill="x", pady=(0, 12))

        self.error_label = ctk.CTkLabel(form, text="", anchor="w", justify="left")
        self.error_label.pack(fill="x")
        self.on_kind_change() 

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.pack(fill="x", pady=(8, 0))
        self.post_button = ctk.CTkButton(buttons, text="Post", width=110, height=36,
                                         command=self.submit)
        self.post_button.pack(side="right")
        self.cancel_button = ctk.CTkButton(buttons, text="Cancel", width=90, height=36,
                                           fg_color="transparent", command=self.destroy)
        self.cancel_button.pack(side="right", padx=(0, 10))

        # gui_main doesn't theme pop-up windows, so this one themes itself
        ThemeManager.subscribe(self.apply_theme)
        self.bind("<Destroy>", self.on_destroy)
    def add_label(self, parent, text):
        label = ctk.CTkLabel(parent, text=text, anchor="w", height=20)
        label.pack(fill="x", pady=(0, 4))
        self.field_labels.append(label)

    def on_kind_change(self):
        """Show the tags box only for kinds of post that have tags."""
        if self.kind.get() in KINDS_WITH_TAGS:
            self.tags_area.pack(fill="x", before=self.error_label)
        else:
            self.tags_area.pack_forget()

    def submit(self):
        """Hand everything to the page. Close if it worked, otherwise show why not."""
        tags = self.tags_entry.get().split(",") if self.kind.get() in KINDS_WITH_TAGS else []
        error = self.on_submit(self.kind.get(), self.title_entry.get(), self.topic_menu.get(),
                               self.body_box.get("1.0", "end-1c"), tags)
        if error:
            self.error_label.configure(text=error)
        else:
            self.destroy()

    def on_destroy(self, event):
        if event.widget is self:
            ThemeManager.unsubscribe(self.apply_theme)

    def apply_theme(self, p, s):
        font = s["font_family"]
        radius = s["widget_radius"]
        self.configure(fg_color=p["bg"])
        self.heading.configure(text_color=p["text"], font=(font, 18, "bold"))
        for label in self.field_labels:
            label.configure(text_color=p["subtext"], font=(font, 12, "bold"))
        for button in self.kind_buttons:
            button.configure(fg_color=p["primary"], hover_color=p["primary_hover"],
                             border_color=p["border"], text_color=p["text"], font=(font, 13))
        for entry in (self.title_entry, self.tags_entry):
            entry.configure(fg_color=p["entry_bg"], text_color=p["text"],
                            placeholder_text_color=p["subtext"], border_color=p["border"],
                            border_width=s["border_width"], corner_radius=radius, font=(font, 13))
        self.topic_menu.configure(fg_color=p["secondary"], button_color=p["primary"],
                                  button_hover_color=p["primary_hover"], text_color=p["text"],
                                  dropdown_fg_color=p["card_bg"], dropdown_text_color=p["text"],
                                  dropdown_hover_color=p["border"], corner_radius=radius,
                                  font=(font, 13))
        self.body_box.configure(fg_color=p["entry_bg"], text_color=p["text"],
                                border_color=p["border"], border_width=s["border_width"],
                                corner_radius=radius, font=(font, 13),
                                scrollbar_button_color=p["border"],
                                scrollbar_button_hover_color=p["subtext"])
        self.error_label.configure(text_color=p["error"], font=(font, 13))
        self.post_button.configure(fg_color=p["primary"], hover_color=p["primary_hover"],
                                   text_color=p["card_bg"], corner_radius=radius,
                                   font=(font, 13, "bold"))
        self.cancel_button.configure(text_color=p["primary"], hover_color=p["card_bg"],
                                     corner_radius=radius, font=(font, 13))