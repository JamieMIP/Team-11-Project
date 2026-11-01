# pages/themes_page.py
import customtkinter as ctk
from base import Page
import theme_config
from theme_config import ThemeManager


class ThemeSwatchCard(ctk.CTkFrame):
    """
    A single theme preview card in the gallery grid (miniature sidebar/UI preview + radio button).
    Marked with _skip_global_theme = True so its preview colours stay locked to its own palette.
    """
    _skip_global_theme = True

    def __init__(self, master, palette_name: str, palette_data: dict, variable: ctk.StringVar, on_select):
        super().__init__(master, fg_color="transparent")
        self.palette_name = palette_name
        self.palette_data = palette_data
        self.variable = variable
        self.on_select = on_select

        # Fallback safety tokens in case a palette definition is missing keys
        bg_col = palette_data.get("bg", "#1E1E2E")
        card_col = palette_data.get("card_bg", "#252538")
        border_col = palette_data.get("border", "#3E3E5E")
        primary_col = palette_data.get("primary", "#3B82F6")
        text_col = palette_data.get("text", "#FFFFFF")
        subtext_col = palette_data.get("subtext", "#A0A0B0")
        error_col = palette_data.get("error", "#EF4444")
        success_col = palette_data.get("success", primary_col)

        # 1. Miniature Preview Box (Models the Slack theme preview card)
        self.preview_box = ctk.CTkFrame(
            self,
            width=140,
            height=115,
            fg_color=bg_col,
            border_color=border_col,
            border_width=2,
            corner_radius=8
        )
        self.preview_box.pack_propagate(False)
        self.preview_box.pack(padx=8, pady=(6, 6))

        # Top header bar inside preview
        top_strip = ctk.CTkFrame(
            self.preview_box,
            height=24,
            fg_color=card_col,
            corner_radius=0
        )
        top_strip.pack(fill="x", side="top")
        top_strip.pack_propagate(False)

        ctk.CTkLabel(
            top_strip,
            text=palette_name[:18],
            text_color=text_col,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=6)

        # Subtext section label
        ctk.CTkLabel(
            self.preview_box,
            text="CHANNELS",
            text_color=subtext_col,
            font=("Segoe UI", 7, "bold")
        ).pack(anchor="w", padx=6, pady=(4, 1))

        # Active highlight bar across the middle
        active_bar = ctk.CTkFrame(
            self.preview_box,
            height=18,
            fg_color=primary_col,
            corner_radius=4
        )
        active_bar.pack(fill="x", padx=5, pady=1)
        active_bar.pack_propagate(False)

        bar_text_color = "#000000" if palette_name == "Cyber Neon" else "#FFFFFF"
        ctk.CTkLabel(
            active_bar,
            text="# dashboard",
            text_color=bar_text_color,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=5)

        badge = ctk.CTkFrame(
            active_bar,
            width=10,
            height=10,
            fg_color=error_col,
            corner_radius=5
        )
        badge.pack(side="right", padx=4)

        # Secondary item rows
        row2 = ctk.CTkFrame(self.preview_box, height=16, fg_color="transparent")
        row2.pack(fill="x", padx=6, pady=1)

        ctk.CTkLabel(
            row2,
            text="● team-tasks",
            text_color=success_col,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            self.preview_box,
            text="○ knowledge-base",
            text_color=subtext_col,
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=6, pady=0)

        # 2. Radio Button underneath the preview box
        self.radio = ctk.CTkRadioButton(
            self,
            text=palette_name,
            variable=self.variable,
            value=palette_name,
            command=self._handle_click,
            radiobutton_width=16,
            radiobutton_height=16,
            font=("Segoe UI", 12)
        )
        self.radio.pack(pady=(2, 8))

        # Allow clicking directly on the preview image to select the theme
        self._bind_click_recursively(self.preview_box)

    def _bind_click_recursively(self, widget):
        widget.bind("<Button-1>", lambda e: self._handle_click())
        for child in widget.winfo_children():
            self._bind_click_recursively(child)

    def _handle_click(self):
        self.variable.set(self.palette_name)
        self.on_select(self.palette_name)

    def update_chrome(self, active_p, active_s):
        """Updates the selection outline and radio button text to match the active theme."""
        is_selected = (self.variable.get() == self.palette_name)
        default_border = self.palette_data.get("border", active_p["border"])
        self.preview_box.configure(
            border_color=active_p["primary"] if is_selected else default_border,
            border_width=3 if is_selected else 1,
            corner_radius=active_s.get("card_radius", 8)
        )
        self.radio.configure(
            text_color=active_p["text"],
            fg_color=active_p["primary"],
            hover_color=active_p["primary_hover"],
            border_color=active_p["subtext"],
            font=(active_s.get("font_family", "Segoe UI"), 12, "bold" if is_selected else "normal")
        )


class ThemesPage(Page):
    title = "Themes"

    def __init__(self, master, app):
        super().__init__(master, app)

        self.selected_palette_var = ctk.StringVar(value=getattr(ThemeManager, "current_palette_name", "Midnight Slate"))
        self.swatch_cards = []

        # Central Showcase Card (Matches the Slack gallery container)
        self.showcase_card = ctk.CTkFrame(self, border_width=1)
        self.showcase_card.pack(fill="both", expand=True, padx=16, pady=12)

        # ---- Top Header Bar ----
        self.top_bar = ctk.CTkFrame(self.showcase_card, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=24, pady=(18, 10))

        self.header_title = ctk.CTkLabel(
            self.top_bar,
            text="SELECT A THEME TO PREVIEW",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.header_title.pack(side="left")

        # Geometry Preset Selector on the right of the header
        style_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        style_frame.pack(side="right")

        ctk.CTkLabel(
            style_frame,
            text="Geometry Preset:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 8))

        style_names = self._get_all_styles_list()
        self.style_menu = ctk.CTkOptionMenu(
            style_frame,
            values=style_names,
            command=self._on_style_selected,
            width=170
        )
        curr_style = getattr(ThemeManager, "current_style_name", style_names[0] if style_names else "Default")
        self.style_menu.set(curr_style)
        self.style_menu.pack(side="left")

        # ---- Scrollable Grid of Theme Swatches ----
        self.grid_scroll = ctk.CTkScrollableFrame(self.showcase_card, fg_color="transparent")
        self.grid_scroll.pack(fill="both", expand=True, padx=16, pady=4)

        self._build_swatch_grid()

        # ---- Bottom Footer Bar (Current Selection + Copy Button) ----
        self.footer = ctk.CTkFrame(self.showcase_card, height=76, border_width=1)
        self.footer.pack(fill="x", side="bottom", padx=0, pady=0)
        self.footer.pack_propagate(False)

        footer_left = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_left.pack(side="left", padx=24, pady=12)

        self.curr_label_title = ctk.CTkLabel(
            footer_left,
            text="Current selection",
            font=ctk.CTkFont(size=12)
        )
        self.curr_label_title.pack(anchor="w")

        self.curr_selection_label = ctk.CTkLabel(
            footer_left,
            text=getattr(ThemeManager, "current_palette_name", "Default"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.curr_selection_label.pack(anchor="w")

        self.copy_btn = ctk.CTkButton(
            self.footer,
            text="Copy theme to clipboard",
            width=260,
            height=40,
            command=self._copy_theme_to_clipboard
        )
        self.copy_btn.pack(side="right", padx=24, pady=16)

    def _get_all_palettes(self) -> dict:
        """Inspects theme_config and ThemeManager to locate the complete palette collection."""
        # 1. Check module-level dictionaries in theme_config
        for attr in ("PALETTES", "THEMES", "COLOR_PALETTES", "ALL_PALETTES"):
            val = getattr(theme_config, attr, None)
            if isinstance(val, dict) and len(val) > 1:
                return val

        # 2. Check class-level dictionaries on ThemeManager
        for attr in ("PALETTES", "THEMES", "COLOR_PALETTES", "_palettes"):
            val = getattr(ThemeManager, attr, None)
            if isinstance(val, dict) and len(val) > 1:
                return val

        # 3. Check methods on ThemeManager
        if hasattr(ThemeManager, "get_palette_names"):
            names = ThemeManager.get_palette_names()
            res = {}
            for n in names:
                if hasattr(ThemeManager, "get_palette"):
                    res[n] = ThemeManager.get_palette(n)
            if len(res) > 1:
                return res

        # 4. Fallback to active theme
        return {getattr(ThemeManager, "current_palette_name", "Default"): ThemeManager.get_palette()}

    def _get_all_styles_list(self) -> list:
        if hasattr(ThemeManager, "get_style_names"):
            return ThemeManager.get_style_names()
        for attr in ("GEOMETRY_PRESETS", "STYLES", "GEOMETRY_STYLES"):
            val = getattr(theme_config, attr, None) or getattr(ThemeManager, attr, None)
            if isinstance(val, dict):
                return list(val.keys())
        return ["Modern Rounded", "Sharp Enterprise", "Compact Density"]

    def _build_swatch_grid(self):
        for w in self.grid_scroll.winfo_children():
            w.destroy()
        self.swatch_cards.clear()

        palettes = self._get_all_palettes()
        columns = 4

        for col in range(columns):
            self.grid_scroll.columnconfigure(col, weight=1)

        for idx, (p_name, p_data) in enumerate(palettes.items()):
            r = idx // columns
            c = idx % columns
            swatch = ThemeSwatchCard(
                self.grid_scroll,
                palette_name=p_name,
                palette_data=p_data,
                variable=self.selected_palette_var,
                on_select=self._on_palette_selected
            )
            swatch.grid(row=r, column=c, padx=10, pady=12)
            self.swatch_cards.append(swatch)

    def _on_palette_selected(self, palette_name: str):
        if hasattr(ThemeManager, "set_palette"):
            ThemeManager.set_palette(palette_name)
        elif hasattr(ThemeManager, "apply_palette"):
            ThemeManager.apply_palette(palette_name)
        else:
            ThemeManager.current_palette_name = palette_name
            if hasattr(ThemeManager, "_notify"):
                ThemeManager._notify()

    def _on_style_selected(self, style_name: str):
        if hasattr(ThemeManager, "set_style"):
            ThemeManager.set_style(style_name)
        elif hasattr(ThemeManager, "apply_style"):
            ThemeManager.apply_style(style_name)
        else:
            ThemeManager.current_style_name = style_name
            if hasattr(ThemeManager, "_notify"):
                ThemeManager._notify()

    def _copy_theme_to_clipboard(self):
        p = ThemeManager.get_palette()
        summary = f"{getattr(ThemeManager, 'current_palette_name', 'Theme')}: {p}"
        self.clipboard_clear()
        self.clipboard_append(summary)
        self.copy_btn.configure(text="✓ Copied to clipboard!")
        self.after(1800, lambda: self.copy_btn.configure(text="Copy theme to clipboard"))

    def apply_theme(self, p=None, s=None):
        super().apply_theme(p, s)
        if p is None:
            p = ThemeManager.get_palette()
        if s is None:
            s = ThemeManager.get_style()

        curr_p = getattr(ThemeManager, "current_palette_name", "Theme")
        curr_s = getattr(ThemeManager, "current_style_name", "")
        self.curr_selection_label.configure(
            text=f"{curr_p}  •  {curr_s}" if curr_s else curr_p
        )
        self.curr_label_title.configure(text_color=p["subtext"])

        for swatch in self.swatch_cards:
            swatch.update_chrome(p, s)