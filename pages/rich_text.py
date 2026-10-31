"""Rich text for the Knowledge Base: showing **bold**, *italic*, `code`
and [links](https://...) in posts and replies, and buttons that add
that formatting while writing.

Posts are stored as plain text with these Markdown markers (the forum
already strips them for searching), so nothing changes in the backend.
"""

import re
import tkinter as tk
import webbrowser

import customtkinter as ctk

# One match per piece of formatting, tried left to right.
INLINE = re.compile(
    r"\*\*(?P<bold>.+?)\*\*"
    r"|\*(?P<italic>.+?)\*"
    r"|`(?P<code>.+?)`"
    r"|\[(?P<label>[^\]]+)\]\((?P<url>[^)\s]+)\)"
    r"|(?P<bare>https?://[^\s)]+)"
)
SAFE_LINKS = ("http://", "https://", "mailto:")   # never open files or run programs


def parse_markdown(text):
    """Split a post body into pieces: (text, style, url).

    style is "plain", "bold", "italic", "code", "link" or "quote";
    url is only set for links. "# Heading" lines come out bold and
    "> quote" lines as quotes.
    """
    pieces = []
    for number, line in enumerate(text.split("\n")):
        if number:
            pieces.append(("\n", "plain", None))

        line_style = "plain"
        if line.startswith("#"):
            line, line_style = line.lstrip("#").strip(), "bold"
        elif line.startswith(">"):
            line, line_style = line.lstrip(">").strip(), "quote"

        position = 0
        for match in INLINE.finditer(line):
            if match.start() > position:
                pieces.append((line[position:match.start()], line_style, None))
            if match.group("bold"):
                pieces.append((match.group("bold"), "bold", None))
            elif match.group("italic"):
                pieces.append((match.group("italic"), "italic", None))
            elif match.group("code"):
                pieces.append((match.group("code"), "code", None))
            else:
                url = match.group("url") or match.group("bare")
                label = match.group("label") or url
                if url.lower().startswith(SAFE_LINKS):
                    pieces.append((label, "link", url))
                else:
                    pieces.append((label, line_style, None))
            position = match.end()
        if position < len(line):
            pieces.append((line[position:], line_style, None))
    return pieces

class RichText(tk.Text):
    """Read-only formatted text that wraps to its width and grows to fit,
    so it sits in a card like a label. Links open in the web browser.

    It's a plain tkinter Text (CustomTkinter's textbox doesn't allow a
    different font per word), so it themes itself in apply_theme.
    """

    def __init__(self, master, text, size=14):
        super().__init__(master, wrap="word", height=1, width=1, borderwidth=0,
                         highlightthickness=0, padx=0, pady=0, cursor="arrow",
                         takefocus=False)
        self.size = size
        self.last_width = None

        for number, (piece, style, url) in enumerate(parse_markdown(text)):
            tags = (style,)
            if url:
                link_tag = f"link{number}"
                tags = (style, link_tag)
                self.tag_bind(link_tag, "<Button-1>", lambda event, u=url: webbrowser.open(u))
                self.tag_bind(link_tag, "<Enter>", lambda event: self.configure(cursor="hand2"))
                self.tag_bind(link_tag, "<Leave>", lambda event: self.configure(cursor="arrow"))
            self.insert("end", piece, tags)

        self.configure(state="disabled")    # read-only, but text can still be selected
        self.bind("<Configure>", self.fit_height)

    def fit_height(self, event=None):
        """After the width changes, make it exactly as many lines tall as the wrapped text."""
        width = self.winfo_width()
        if width <= 1 or width == self.last_width:
            return
        self.last_width = width
        # "update" makes Tk finish wrapping first; counting to "end" gives the total lines
        lines = self.count("1.0", "end", "update", "displaylines")
        if isinstance(lines, tuple):
            lines = lines[0]
        self.configure(height=max(1, lines or 1))

    def apply_theme(self, p, s, background):
        """background is whatever the text sits on (a card, a reply, ...)."""
        scale = ctk.ScalingTracker.get_widget_scaling(self.master)
        family = s["font_family"]
        size = -round(self.size * scale)        # negative = pixels, matching CustomTkinter
        self.configure(bg=background, fg=p["text"], font=(family, size),
                       selectbackground=p["primary"], selectforeground=p["card_bg"],
                       inactiveselectbackground=p["border"])
        self.tag_config("bold", font=(family, size, "bold"))
        self.tag_config("italic", font=(family, size, "italic"))
        self.tag_config("code", font=("Courier", size), background=p["bg"])
        self.tag_config("quote", foreground=p["subtext"], font=(family, size, "italic"))
        self.tag_config("link", foreground=p["primary"], underline=True)
        self.last_width = None      # font changed, so the height needs working out again
        self.fit_height()