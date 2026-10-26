import customtkinter as ctk
from theme_config import ThemeManager, COLOR_PALETTES, DESIGN_STYLES

class ThemeStudioWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Theme Studio")
        self.geometry("280x370+720+200")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Global Design Studio", font=("Arial", 16, "bold")).pack(pady=(16, 12))

        # Palette Selector
        ctk.CTkLabel(self, text="Color Palette:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.palette_menu = ctk.CTkOptionMenu(
            self,
            values=list(COLOR_PALETTES.keys()),
            command=self._on_palette_change,
            width=230
        )
        self.palette_menu.set(ThemeManager.current_palette_name)
        self.palette_menu.pack(pady=(2, 12))

        # Design Preset Selector
        ctk.CTkLabel(self, text="Geometry Preset:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.style_menu = ctk.CTkOptionMenu(
            self,
            values=list(DESIGN_STYLES.keys()),
            command=self._on_style_change,
            width=230
        )
        self.style_menu.set(ThemeManager.current_style_name)
        self.style_menu.pack(pady=(2, 12))

        # Corner Radius Slider
        ctk.CTkLabel(self, text="Override Corner Radius:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.radius_slider = ctk.CTkSlider(
            self, from_=0, to=25, number_of_steps=25, width=230, command=self._on_radius_slide
        )
        self.radius_slider.set(ThemeManager.get_style()["widget_radius"])
        self.radius_slider.pack(pady=(2, 12))

        # Border Width Slider
        ctk.CTkLabel(self, text="Override Border Width:", font=("Arial", 12)).pack(anchor="w", padx=25)
        self.border_slider = ctk.CTkSlider(
            self, from_=0, to=5, number_of_steps=5, width=230, command=self._on_border_slide
        )
        self.border_slider.set(ThemeManager.get_style()["border_width"])
        self.border_slider.pack(pady=(2, 12))

    def _on_palette_change(self, choice):
        ThemeManager.set_palette(choice)

    def _on_style_change(self, choice):
        ThemeManager.set_style(choice)
        style = ThemeManager.get_style()
        self.radius_slider.set(style["widget_radius"])
        self.border_slider.set(style["border_width"])

    def _on_radius_slide(self, val):
        ThemeManager.set_overrides(radius=val)

    def _on_border_slide(self, val):
        ThemeManager.set_overrides(border=val)