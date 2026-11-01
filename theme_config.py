import customtkinter as ctk

# =====================================================================
# PALETTES & GEOMETRY PRESETS
# =====================================================================

COLOR_PALETTES = {
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
    "Alex Theme": {
        "mode": "Dark",
        "bg": "#180714",             # Deep twilight plum (makes pinks pop)
        "card_bg": "#290D23",        # Rich sparkle velvet backdrop
        "text": "#FFF0F8",           # Diamond shimmer highlight white
        "subtext": "#E8A7D5",        # Iridescent rose petal
        "entry_bg": "#140411",       # Ultra-deep jewel base
        "border": "#F472B6",         # Sparkling pink rhinestone border
        "primary": "#FF2A93",        # Ultra-saturated glitter neon hot pink
        "primary_hover": "#FF5BB0",  # Light-catching sparkle burst
        "secondary": "#D946EF",      # Electric shimmer fuchsia
        "secondary_hover": "#C026D3",# Deep jewel gloss
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

    @classmethod
    def subscribe(cls, callback):
        """Any window registers a callback here to get notified of styling changes."""
        if callback not in cls._listeners:
            cls._listeners.append(callback)
        # Trigger immediately upon registering so window matches the current theme
        callback(cls.get_palette(), cls.get_style())

    @classmethod
    def unsubscribe(cls, callback):
        if callback in cls._listeners:
            cls._listeners.remove(callback)

    @classmethod
    def notify(cls):
        """Broadcast changes to every subscribed window."""
        palette = cls.get_palette()
        style = cls.get_style()
        ctk.set_appearance_mode(palette["mode"])

        # Call callbacks, dropping dead references if windows were closed
        for callback in list(cls._listeners):
            try:
                callback(palette, style)
            except Exception:
                cls._listeners.remove(callback)

    @classmethod
    def get_palette(cls):
        return COLOR_PALETTES[cls.current_palette_name]

    @classmethod
    def get_style(cls):
        style = DESIGN_STYLES[cls.current_style_name].copy()
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

            # 2. Text Entries
            elif isinstance(w, ctk.CTkEntry):
                w.configure(
                    fg_color=p["entry_bg"],
                    text_color=p["text"],
                    placeholder_text_color=p["subtext"],
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
                    border_width=b_width,
                    corner_radius=w_radius
                )

            # 6. Labels
            elif isinstance(w, ctk.CTkLabel):
                txt = str(w.cget("text")).strip()
                if txt.startswith("[OVERDUE]"):
                    w.configure(text_color=p["error"], font=(font_fam, 15, "bold"))
                elif txt.startswith("[DONE]"):
                    w.configure(text_color=p["subtext"], font=(font_fam, 13))
                elif "Overall Project Progress" in txt or "Logged in:" in txt or "Topic:" in txt:
                    w.configure(text_color=p["subtext"], font=(font_fam, 12, "bold"))
                else:
                    w.configure(text_color=p["text"])

            # 7. Frames & Cards
            elif isinstance(w, ctk.CTkScrollableFrame):
                w.configure(
                    fg_color="transparent",
                    scrollbar_button_color=p["secondary"],
                    scrollbar_button_hover_color=p["primary"]
                )
            elif isinstance(w, ctk.CTkFrame):
                if w.cget("fg_color") != "transparent":
                    # Keep error border on overdue cards if border_width is 2
                    is_overdue = (w.cget("border_width") == 2)
                    w.configure(
                        fg_color=p["card_bg"],
                        border_color=p["error"] if is_overdue else p["border"],
                        corner_radius=s["card_radius"],
                        border_width=2 if is_overdue else b_width
                    )
        except Exception:
            pass

        # CRITICAL: Traverse ALL children (including raw tkinter.Canvas) to reach nested cards
        for child in w.winfo_children():
            _style(child)

    _style(root)