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
from theme_config import ThemeManager

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

def wrap_selection(box, before, after, placeholder):
    """Put markers round the selected text, e.g. **bold**. With nothing
    selected, insert them round a placeholder word and select it, ready
    to type over. Works on the post box (CTkTextbox) and the reply box
    (CTkEntry)."""
    if isinstance(box, ctk.CTkTextbox):
        selected = box.tag_ranges("sel")
        if selected:
            start = box.index(selected[0])
            chosen = box.get(selected[0], selected[1])
            box.delete(selected[0], selected[1])
        else:
            start = box.index("insert")
            chosen = placeholder
        box.insert(start, before + chosen + after)
        first = box.index(f"{start}+{len(before)}c")
        last = box.index(f"{first}+{len(chosen)}c")
        box.tag_remove("sel", "1.0", "end")
        box.tag_add("sel", first, last)
        box.mark_set("insert", last)
    else:
        if box.select_present():
            start, end = box.index("sel.first"), box.index("sel.last")
            chosen = box.get()[start:end]
            box.delete(start, end)
        else:
            start = box.index("insert") if box.get() else 0
            chosen = placeholder
        box.insert(start, before + chosen + after)
        first = start + len(before)
        box.select_range(first, first + len(chosen))
        box.icursor(first + len(chosen))
    box.focus_set()


class FormatBar(ctk.CTkFrame):
    """A row of small buttons (B, I, Code, Link) that format the text in `box`."""

    BUTTONS = (
        # text on the button, marker before, marker after, placeholder
        ("B", "**", "**", "bold text"),
        ("I", "*", "*", "italic text"),
        ("Code", "`", "`", "code"),
        ("Link", "[", "](https://)", "link text"),
    )

    def __init__(self, master, box):
        super().__init__(master, fg_color="transparent")
        self.buttons = []
        for label, before, after, placeholder in self.BUTTONS:
            button = ctk.CTkButton(
                self, text=label, width=44 if len(label) == 1 else 56, height=26,
                fg_color="transparent", border_width=1,
                command=lambda b=before, a=after, p=placeholder: wrap_selection(box, b, a, p))
            button.pack(side="left", padx=(0, 6))
            self.buttons.append(button)
        self.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

    def apply_theme(self, p, s):
        font = s["font_family"]
        for button in self.buttons:
            button.configure(text_color=p["text"], hover_color=p["border"],
                             border_color=p["border"], corner_radius=s["widget_radius"])
        bold, italic, code, link = self.buttons
        bold.configure(font=(font, 13, "bold"))
        italic.configure(font=(font, 13, "italic"))
        code.configure(font=("Courier", 13))
        link.configure(font=(font, 13, "underline"))