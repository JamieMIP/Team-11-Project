import customtkinter as ctk
from datetime import datetime

# =====================================================================
# 1. PRESET DICTIONARIES (No hardcoded colors in the UI classes)
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
        "primary": "#3B82F6",
        "primary_hover": "#2563EB",
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
    },
    "Minimal Borderless": {
        "card_radius": 12,
        "widget_radius": 6,
        "border_width": 0,
        "font_family": "Segoe UI",
        "btn_height": 36
    }
}


# =====================================================================
# 2. SEPARATE THEME CONTROLLER WINDOW
# =====================================================================

class ThemeStudioWindow(ctk.CTkToplevel):
    """Separate small toolbox window to live-preview themes and geometry."""
    def __init__(self, master_login_window):
        super().__init__(master_login_window)
        self.login_win = master_login_window
        self.title("Theme Studio")
        self.geometry("280x360")
        self.resizable(False, False)
        
        # Position it right next to the login window
        self.geometry("+680+250")
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Live Design Studio", font=("Arial", 16, "bold")).pack(pady=(15, 10))

        # 1. Color Palette Selector
        ctk.CTkLabel(self, text="Color Palette:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.palette_menu = ctk.CTkOptionMenu(
            self,
            values=list(COLOR_PALETTES.keys()),
            command=self.update_palette,
            width=230
        )
        self.palette_menu.set(self.login_win.current_palette_name)
        self.palette_menu.pack(pady=(2, 12))

        # 2. Structural Style Selector (Corners, Borders, Fonts)
        ctk.CTkLabel(self, text="Design Preset (Geometry):", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.style_menu = ctk.CTkOptionMenu(
            self,
            values=list(DESIGN_STYLES.keys()),
            command=self.update_style,
            width=230
        )
        self.style_menu.set(self.login_win.current_style_name)
        self.style_menu.pack(pady=(2, 12))

        # 3. Fine-tune Corner Radius Slider
        ctk.CTkLabel(self, text="Override Corner Radius:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.radius_slider = ctk.CTkSlider(
            self, from_=0, to=25, number_of_steps=25, width=230, command=self.override_radius
        )
        self.radius_slider.pack(pady=(2, 12))

        # 4. Fine-tune Border Thickness Slider
        ctk.CTkLabel(self, text="Override Border Width:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.border_slider = ctk.CTkSlider(
            self, from_=0, to=5, number_of_steps=5, width=230, command=self.override_border
        )
        self.border_slider.pack(pady=(2, 15))

    def update_palette(self, choice):
        self.login_win.current_palette_name = choice
        self.login_win.apply_theme()

    def update_style(self, choice):
        self.login_win.current_style_name = choice
        style = DESIGN_STYLES[choice]
        self.radius_slider.set(style["widget_radius"])
        self.border_slider.set(style["border_width"])
        self.login_win.apply_theme()

    def override_radius(self, val):
        self.login_win.apply_theme(custom_radius=int(val))

    def override_border(self, val):
        self.login_win.apply_theme(custom_border=int(val))


# =====================================================================
# 3. MAIN LOGIN GUI
# =====================================================================

class LoginWindow(ctk.CTk):
    def __init__(self, enable_theme_studio=True):
        super().__init__()
        self.title("Authentication")
        self.geometry("360x440+300+250")
        self.resizable(False, False)

        # Output variables expected by main.py
        self.user_id = None
        self.login_time = None

        # Active theme state
        self.current_palette_name = "Midnight Slate"
        self.current_style_name = "Modern Rounded"

        # Build UI Layout (Colors/Styles are applied dynamically right after)
        self._build_widgets()
        self.apply_theme()

        # Launch the companion Theme Customizer window
        if enable_theme_studio:
            self.studio_win = ThemeStudioWindow(self)

    def _build_widgets(self):
        # Inner Card Container
        self.card = ctk.CTkFrame(self)
        self.card.pack(fill="both", expand=True, padx=25, pady=25)

        # Header
        self.title_label = ctk.CTkLabel(self.card, text="Welcome Back")
        self.title_label.pack(pady=(25, 4))

        self.subtitle_label = ctk.CTkLabel(self.card, text="Sign in to your account")
        self.subtitle_label.pack(pady=(0, 20))

        # Inputs
        self.username_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=240, height=38)
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(self.card, placeholder_text="Password", show="*", width=240, height=38)
        self.password_entry.pack(pady=8)

        # Feedback / Error Label
        self.status_label = ctk.CTkLabel(self.card, text="")
        self.status_label.pack(pady=4)

        # Primary Login Button
        self.login_btn = ctk.CTkButton(self.card, text="Login", width=240, command=self.standard_login)
        self.login_btn.pack(pady=(8, 6))

        # SSO Button
        self.sso_btn = ctk.CTkButton(self.card, text="Login with SSO", width=240, command=self.sso_login)
        self.sso_btn.pack(pady=6)

    def apply_theme(self, custom_radius=None, custom_border=None):
        """Dynamically re-skins every element based on the active dictionaries."""
        p = COLOR_PALETTES[self.current_palette_name]
        s = DESIGN_STYLES[self.current_style_name]

        w_radius = custom_radius if custom_radius is not None else s["widget_radius"]
        b_width = custom_border if custom_border is not None else s["border_width"]
        font_fam = s["font_family"]

        ctk.set_appearance_mode(p["mode"])

        # Window & Card background
        self.configure(fg_color=p["bg"])
        self.card.configure(
            fg_color=p["card_bg"],
            corner_radius=s["card_radius"],
            border_width=b_width,
            border_color=p["border"]
        )

        # Typography
        self.title_label.configure(
            text_color=p["text"],
            font=(font_fam, 22, "bold")
        )
        self.subtitle_label.configure(
            text_color=p["subtext"],
            font=(font_fam, 12)
        )
        self.status_label.configure(
            text_color=p["error"],
            font=(font_fam, 12)
        )

        # Entries
        for entry in (self.username_entry, self.password_entry):
            entry.configure(
                fg_color=p["entry_bg"],
                text_color=p["text"],
                placeholder_text_color=p["subtext"],
                border_color=p["border"],
                corner_radius=w_radius,
                border_width=b_width,
                font=(font_fam, 13)
            )

        # Buttons (Handles high-contrast text on bright buttons like Cyber Neon)
        primary_text_col = "#000000" if self.current_palette_name == "Cyber Neon" else "#FFFFFF"

        self.login_btn.configure(
            fg_color=p["primary"],
            hover_color=p["primary_hover"],
            text_color=primary_text_col,
            corner_radius=w_radius,
            height=s["btn_height"],
            font=(font_fam, 13, "bold")
        )

        self.sso_btn.configure(
            fg_color=p["secondary"],
            hover_color=p["secondary_hover"],
            text_color="#FFFFFF",
            border_color=p["border"],
            border_width=b_width,
            corner_radius=w_radius,
            height=s["btn_height"],
            font=(font_fam, 13)
        )

    # =================================================================
    # 4. AUTHENTICATION & EXIT HANDLERS
    # =================================================================

    def standard_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Replace with your authentication backend check
        if username == "0" and password == "":
            self.user_id = username
            self.login_time = datetime.now()
            self.destroy()
        elif username == "1" and password == "":
            self.user_id = username
            self.login_time = datetime.now()
            self.destroy()
        elif username == "2" and password == "":
            self.user_id = username
            self.login_time = datetime.now()
            self.destroy()

        else:
            self.status_label.configure(text="Invalid username or password")

    def sso_login(self):
        # Replace with your SSO authentication handler
        self.user_id = "0"
        self.login_time = datetime.now()
        self.destroy()


# =====================================================================
# 5. ENTRY POINT FOR MAIN.PY
# =====================================================================

def run_login(show_theme_studio: bool = True) -> tuple[str | None, datetime | None]:
    """
    Launches the Login GUI and blocks until closed or authenticated.
    Returns:
        tuple: (user_id, login_time)
    """
    app = LoginWindow(enable_theme_studio=show_theme_studio)
    app.mainloop()
    return app.user_id, app.login_time


# Standalone testing block (Only runs when you execute login_module.py directly)
if __name__ == "__main__":
    uid, timestamp = run_login(show_theme_studio=True)
    print(f"Returned to main -> User ID: {uid} | Login Time: {timestamp}")