# theme_config.py
import customtkinter as ctk

# =====================================================================
# 20 WORKSPACE & FORUM COLOR PALETTES
# =====================================================================

COLOR_PALETTES = {
    # 1. Default Workspace
    "Midnight Slate": {
        "mode": "Dark",
        "bg": "#0F172A",
        "card_bg": "#1E293B",
        "text": "#F8FAFC",
        "subtext": "#94A3B8",
        "entry_bg": "#0F172A",
        "border": "#334155",
        "primary": "#2D4B73",
        "primary_hover": "#3B82F6",
        "secondary": "#475569",
        "secondary_hover": "#334155",
        "error": "#EF4444"
    },

    # 2. Microsoft Teams (Classic Dark Workspace)
    "Microsoft Teams": {
        "mode": "Dark",
        "bg": "#1F1F1F",
        "card_bg": "#292929",
        "text": "#F5F5F5",
        "subtext": "#ADADAD",
        "entry_bg": "#141414",
        "border": "#3D3D3D",
        "primary": "#6264A7",
        "primary_hover": "#7F85F5",
        "secondary": "#444791",
        "secondary_hover": "#363870",
        "error": "#C4314B"
    },

    # 3. Slack Aubergine (Iconic Slack Purple & Clean Workspace)
    "Slack Aubergine": {
        "mode": "Light",
        "bg": "#F8F8FA",
        "card_bg": "#FFFFFF",
        "text": "#1D1C1D",
        "subtext": "#616061",
        "entry_bg": "#F0EFF1",
        "border": "#E0DEE1",
        "primary": "#4A154B",
        "primary_hover": "#611F69",
        "secondary": "#1264A3",
        "secondary_hover": "#0B4C8C",
        "error": "#E01E5A"
    },

    # 4. Discord Blurple (Gamer & Community Forum)
    "Discord Dark": {
        "mode": "Dark",
        "bg": "#1E1F22",
        "card_bg": "#2B2D31",
        "text": "#F2F3F5",
        "subtext": "#949BA4",
        "entry_bg": "#111214",
        "border": "#35373C",
        "primary": "#5865F2",
        "primary_hover": "#4752C4",
        "secondary": "#3BA55D",
        "secondary_hover": "#2D7D46",
        "error": "#ED4245"
    },

    # 5. Linear Dark (Minimalist Issue Tracker)
    "Linear Charcoal": {
        "mode": "Dark",
        "bg": "#101114",
        "card_bg": "#191B20",
        "text": "#EEEEF0",
        "subtext": "#8A8F98",
        "entry_bg": "#141519",
        "border": "#282B33",
        "primary": "#5E6AD2",
        "primary_hover": "#717EE8",
        "secondary": "#2C313D",
        "secondary_hover": "#232731",
        "error": "#E5484D"
    },

    # 6. GitHub Dark Dimmed (Developer Standard)
    "GitHub Dimmed": {
        "mode": "Dark",
        "bg": "#1C2128",
        "card_bg": "#22272E",
        "text": "#CDD9E5",
        "subtext": "#768390",
        "entry_bg": "#1C2128",
        "border": "#444C56",
        "primary": "#316DCA",
        "primary_hover": "#539BF5",
        "secondary": "#373E47",
        "secondary_hover": "#2D333B",
        "error": "#F47067"
    },

    # 7. GitHub Light (Clean Enterprise White)
    "GitHub Light": {
        "mode": "Light",
        "bg": "#F6F8FA",
        "card_bg": "#FFFFFF",
        "text": "#1F2328",
        "subtext": "#656D76",
        "entry_bg": "#FFFFFF",
        "border": "#D0D7DE",
        "primary": "#0969DA",
        "primary_hover": "#0550AE",
        "secondary": "#2DA44E",
        "secondary_hover": "#2C974B",
        "error": "#CF222E"
    },

    # 8. Atlassian Jira (Agile Sprint Board Blue)
    "Jira Blue": {
        "mode": "Light",
        "bg": "#F4F5F7",
        "card_bg": "#FFFFFF",
        "text": "#172B4D",
        "subtext": "#5E6C84",
        "entry_bg": "#FAFBFC",
        "border": "#DFE1E6",
        "primary": "#0052CC",
        "primary_hover": "#0747A6",
        "secondary": "#4C9AFF",
        "secondary_hover": "#2684FF",
        "error": "#DE350B"
    },

    # 9. Notion Cream (Document & Knowledge Base)
    "Notion Minimal": {
        "mode": "Light",
        "bg": "#F7F6F3",
        "card_bg": "#FFFFFF",
        "text": "#37352F",
        "subtext": "#787774",
        "entry_bg": "#FFFFFF",
        "border": "#E3E2DE",
        "primary": "#2EAADC",
        "primary_hover": "#1D8AB5",
        "secondary": "#4D4B47",
        "secondary_hover": "#37352F",
        "error": "#EB5757"
    },

    # 10. Asana Coral (Warm Task Board)
    "Asana Warm": {
        "mode": "Light",
        "bg": "#F9F8F8",
        "card_bg": "#FFFFFF",
        "text": "#2A2B2D",
        "subtext": "#6D6E71",
        "entry_bg": "#F2F1F1",
        "border": "#E5E4E4",
        "primary": "#F06A6A",
        "primary_hover": "#D95252",
        "secondary": "#4573D2",
        "secondary_hover": "#335EBE",
        "error": "#E8384F"
    },

    # 11. Monday.com (High-Energy Dark Navy & Electric Blue)
    "Monday Neon": {
        "mode": "Dark",
        "bg": "#181B34",
        "card_bg": "#22264B",
        "text": "#FFFFFF",
        "subtext": "#9699B0",
        "entry_bg": "#121427",
        "border": "#363A6E",
        "primary": "#6161FF",
        "primary_hover": "#4E4EEB",
        "secondary": "#00CA72",
        "secondary_hover": "#00A35C",
        "error": "#FB275D"
    },

    # 12. Trello Board (Kanban Classic)
    "Trello Blue": {
        "mode": "Dark",
        "bg": "#0C2340",
        "card_bg": "#173B63",
        "text": "#E6F0FA",
        "subtext": "#8CB4DE",
        "entry_bg": "#08172B",
        "border": "#245287",
        "primary": "#0079BF",
        "primary_hover": "#026AA7",
        "secondary": "#61BD4F",
        "secondary_hover": "#519839",
        "error": "#EB5A46"
    },

    # 13. Reddit Forum (Modern Discussion Orange)
    "Reddit Night": {
        "mode": "Dark",
        "bg": "#0E1113",
        "card_bg": "#1A1A1B",
        "text": "#D7DADC",
        "subtext": "#818384",
        "entry_bg": "#131518",
        "border": "#343536",
        "primary": "#FF4500",
        "primary_hover": "#E03D00",
        "secondary": "#272729",
        "secondary_hover": "#343536",
        "error": "#EA0027"
    },

    # 14. Dracula Pro (Vibrant Developer Purple)
    "Dracula Pro": {
        "mode": "Dark",
        "bg": "#21222C",
        "card_bg": "#282A36",
        "text": "#F8F8F2",
        "subtext": "#6272A4",
        "entry_bg": "#191A21",
        "border": "#44475A",
        "primary": "#BD93F9",
        "primary_hover": "#A775F4",
        "secondary": "#50FA7B",
        "secondary_hover": "#40CA63",
        "error": "#FF5555"
    },

    # 15. Catppuccin Mocha (Soft Pastel Dark)
    "Catppuccin Mocha": {
        "mode": "Dark",
        "bg": "#181825",
        "card_bg": "#1E1E2E",
        "text": "#CDD6F4",
        "subtext": "#9399B2",
        "entry_bg": "#11111B",
        "border": "#313244",
        "primary": "#89B4FA",
        "primary_hover": "#B4BEFE",
        "secondary": "#CBA6F7",
        "secondary_hover": "#A67CF0",
        "error": "#F38BA8"
    },

    # 16. Cyber Neon (Matrix Terminal Contrast)
    "Cyber Neon": {
        "mode": "Dark",
        "bg": "#0A0E0D",
        "card_bg": "#121A17",
        "text": "#00FF66",
        "subtext": "#4E9A70",
        "entry_bg": "#060A08",
        "border": "#00AA44",
        "primary": "#00FF66",
        "primary_hover": "#26FF7C",
        "secondary": "#0D542E",
        "secondary_hover": "#093D21",
        "error": "#FF0055"
    },

    # 17. Nordic Green (Clean Mint)
    "Nordic Green": {
        "mode": "Light",
        "bg": "#ECEFF4",
        "card_bg": "#FFFFFF",
        "text": "#2E3440",
        "subtext": "#4C566A",
        "entry_bg": "#F8FAFC",
        "border": "#D8DEE9",
        "primary": "#15800B",
        "primary_hover": "#084811",
        "secondary": "#0D3C1A",
        "secondary_hover": "#0C5A17",
        "error": "#BF616A"
    },

    # 18. Nordic Frost (Cold Arctic Blue)
    "Nordic Frost": {
        "mode": "Light",
        "bg": "#ECEFF4",
        "card_bg": "#FFFFFF",
        "text": "#2E3440",
        "subtext": "#4C566A",
        "entry_bg": "#F8FAFC",
        "border": "#D8DEE9",
        "primary": "#5E81AC",
        "primary_hover": "#4C6A92",
        "secondary": "#88C0D0",
        "secondary_hover": "#6CA6B8",
        "error": "#BF616A"
    },

    # 19. Sunset Ember (Deep Earth & Warm Amber)
    "Sunset Ember": {
        "mode": "Dark",
        "bg": "#1C1917",
        "card_bg": "#292524",
        "text": "#FAFAF9",
        "subtext": "#A8A29E",
        "entry_bg": "#1C1917",
        "border": "#44403C",
        "primary": "#F97316",
        "primary_hover": "#EA580C",
        "secondary": "#57534E",
        "secondary_hover": "#44403C",
        "error": "#F43F5E"
    },

    # 20. Alex Theme (Vibrant Neon Rose)
    "Alex Theme": {
        "mode": "Dark",
        "bg": "#180714",
        "card_bg": "#290D23",
        "text": "#FFF0F8",
        "subtext": "#E8A7D5",
        "entry_bg": "#140411",
        "border": "#F472B6",
        "primary": "#FF2A93",
        "primary_hover": "#FF5BB0",
        "secondary": "#D946EF",
        "secondary_hover": "#C026D3",
        "error": "#FF1744"
    }
}

DESIGN_STYLES = {
    "Modern Rounded": {
        "card_radius": 16,
        "widget_radius": 8,
        "border_width": 1,
        "font_family": "Helvetica",
        "btn_height": 38
    },
    "Sharp Industrial": {
        "card_radius": 0,
        "widget_radius": 0,
        "border_width": 2,
        "font_family": "Courier",
        "btn_height": 40
    },
    "Soft Pill": {
        "card_radius": 28,
        "widget_radius": 20,
        "border_width": 1,
        "font_family": "Arial",
        "btn_height": 40
    }
}

# =====================================================================
# GLOBAL THEME MANAGER (Single source of truth)
# =====================================================================

class ThemeManager:
    _listeners = []
    current_palette_name = "Midnight Slate"
    current_style_name = "Modern Rounded"
    custom_radius = None
    custom_border = None

    # Expose dictionaries directly on class for backwards compatibility
    PALETTES = COLOR_PALETTES
    STYLES = DESIGN_STYLES

    @classmethod
    def subscribe(cls, callback):
        """Any window or page registers a callback here to get notified of styling changes."""
        if callback not in cls._listeners:
            cls._listeners.append(callback)
        # Trigger immediately upon registering so the widget matches the current theme
        callback(cls.get_palette(), cls.get_style())

    @classmethod
    def unsubscribe(cls, callback):
        if callback in cls._listeners:
            cls._listeners.remove(callback)

    @classmethod
    def notify(cls):
        """Broadcast changes to every subscribed window and page."""
        palette = cls.get_palette()
        style = cls.get_style()
        try:
            ctk.set_appearance_mode(palette["mode"])
        except Exception:
            pass

        # Call callbacks, dropping dead references if windows were closed
        for callback in list(cls._listeners):
            try:
                callback(palette, style)
            except Exception:
                cls._listeners.remove(callback)

    @classmethod
    def get_palette_names(cls):
        return list(COLOR_PALETTES.keys())

    @classmethod
    def get_style_names(cls):
        return list(DESIGN_STYLES.keys())

    @classmethod
    def get_palette(cls, name=None):
        target = name or cls.current_palette_name
        return COLOR_PALETTES.get(target, COLOR_PALETTES["Midnight Slate"])

    @classmethod
    def get_style(cls):
        style = DESIGN_STYLES.get(cls.current_style_name, DESIGN_STYLES["Modern Rounded"]).copy()
        if cls.custom_radius is not None:
            style["widget_radius"] = cls.custom_radius
        if cls.custom_border is not None:
            style["border_width"] = cls.custom_border
        return style

    @classmethod
    def set_palette(cls, name):
        if name in COLOR_PALETTES:
            cls.current_palette_name = name
            cls.notify()

    @classmethod
    def set_style(cls, name):
        if name in DESIGN_STYLES:
            cls.current_style_name = name
            cls.custom_radius = None
            cls.custom_border = None
            cls.notify()

    @classmethod
    def set_overrides(cls, radius=None, border=None):
        if radius is not None:
            cls.custom_radius = int(radius)
        if border is not None:
            cls.custom_border = int(border)
        cls.notify()


def apply_theme_to_tree(root, p=None, s=None):
    """
    Globally styles any widget and all of its descendants recursively.
    Penetrates CTkScrollableFrame canvas wrappers and dynamic card layouts.
    """
    if p is None:
        p = ThemeManager.get_palette()
    if s is None:
        s = ThemeManager.get_style()

    font_fam = s["font_family"]
    w_radius = s["widget_radius"]
    b_width = s["border_width"]
    btn_text = "#000000" if ThemeManager.current_palette_name == "Cyber Neon" else "#FFFFFF"

    def _style(w):
        try:
            # 1. Buttons
            if isinstance(w, ctk.CTkButton):
                txt = str(w.cget("text")).strip()
                fg = w.cget("fg_color")

                if fg == "transparent":
                    w.configure(
                        text_color=p["text"],
                        hover_color=p["secondary_hover"],
                        font=(font_fam, 13)
                    )
                elif txt in ("+25% Progress", "Reopen"):
                    w.configure(
                        fg_color=p["secondary"],
                        hover_color=p["secondary_hover"],
                        text_color="#FFFFFF",
                        corner_radius=w_radius,
                        border_width=b_width,
                        border_color=p["border"],
                        font=(font_fam, 12, "bold")
                    )
                else:
                    w.configure(
                        fg_color=p["primary"],
                        hover_color=p["primary_hover"],
                        text_color=btn_text,
                        corner_radius=w_radius,
                        border_width=b_width,
                        border_color=p["border"],
                        font=(font_fam, 13, "bold")
                    )

            # 2. Text Entries & Textboxes
            elif isinstance(w, (ctk.CTkEntry, ctk.CTkTextbox)):
                w.configure(
                    fg_color=p["entry_bg"],
                    text_color=p["text"],
                    border_color=p["border"],
                    corner_radius=w_radius,
                    border_width=b_width,
                    font=(font_fam, 13)
                )

            # 3. Dropdowns / Selectors
            elif isinstance(w, (ctk.CTkOptionMenu, ctk.CTkComboBox)):
                w.configure(
                    fg_color=p["secondary"],
                    button_color=p["primary"],
                    button_hover_color=p["primary_hover"],
                    text_color="#FFFFFF",
                    corner_radius=w_radius,
                    font=(font_fam, 13)
                )

            # 4. Checkboxes & Switches
            elif isinstance(w, (ctk.CTkCheckBox, ctk.CTkSwitch, ctk.CTkRadioButton)):
                w.configure(
                    fg_color=p["primary"],
                    hover_color=p["primary_hover"],
                    text_color=p["text"],
                    border_color=p["border"],
                    font=(font_fam, 13)
                )

            # 5. Progress Bars
            elif isinstance(w, ctk.CTkProgressBar):
                w.configure(
                    progress_color=p["primary"],
                    fg_color=p["entry_bg"],
                    border_color=p["border"],
                    border_width=max(0, b_width - 1),
                    corner_radius=w_radius
                )

            # 6. Labels
            elif isinstance(w, ctk.CTkLabel):
                txt = str(w.cget("text")).strip()
                if "[OVERDUE" in txt or "[OVERLOADED]" in txt or "[ACCESS ENDED]" in txt:
                    w.configure(text_color=p["error"], font=(font_fam, 14, "bold"))
                elif txt.startswith("[DONE]"):
                    w.configure(text_color=p["subtext"], font=(font_fam, 13))
                elif "Overall Project Progress" in txt or "Logged in:" in txt or "Current selection" in txt:
                    w.configure(text_color=p["subtext"], font=(font_fam, 12, "bold"))
                else:
                    w.configure(text_color=p["text"])

            # 7. Scrollable Frames
            elif isinstance(w, ctk.CTkScrollableFrame):
                w.configure(
                    fg_color="transparent",
                    scrollbar_button_color=p["secondary"],
                    scrollbar_button_hover_color=p["primary"]
                )

            # 8. Frames & Cards
            elif isinstance(w, ctk.CTkFrame):
                if w.cget("fg_color") != "transparent":
                    if not hasattr(w, "_orig_border"):
                        w._orig_border = w.cget("border_width")
                    orig_b = w._orig_border

                    if orig_b == 0:
                        w.configure(
                            fg_color=p["card_bg"],
                            corner_radius=s["card_radius"],
                            border_width=0
                        )
                    elif orig_b >= 2:
                        w.configure(
                            fg_color=p["card_bg"],
                            border_color=p["error"],
                            corner_radius=s["card_radius"],
                            border_width=max(2, b_width)
                        )
                    else:
                        w.configure(
                            fg_color=p["card_bg"],
                            border_color=p["border"],
                            corner_radius=s["card_radius"],
                            border_width=b_width
                        )
        except Exception:
            pass

        # CRITICAL: Always recurse into all children (penetrating CTkScrollableFrame canvas)
        for child in w.winfo_children():
            _style(child)

    _style(root)