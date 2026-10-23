import customtkinter as ctk

class Dashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        
        
        self.Dashboardlabel = ctk.CTkLabel(self, text="Dashboard Label")
        self.Dashboardlabel.pack(side="left", fill="x", pady=0, padx=0)
        self.Dashboardlabel2 = ctk.CTkLabel(self, text="Dashboard Label2")
        self.Dashboardlabel2.pack(side="left",
            fill="x", pady=30,
            padx=20)

        size = 50
        self.circle_btn = ctk.CTkButton(
            self,
            text="+",
            width=size,
            height=size,
            corner_radius=size // 2)
        self.circle_btn.pack(side="right",
                    padx=20,
                    pady=10,)

        self.label = ctk.CTkLabel(self, text="Name McNameson")
        self.label.pack(side="right", pady=2, padx=10)

class SidePanel(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master)
        
        sections = {
            "Personal To-do List": ["List 1", "List 2", "..."],
            "Team To-do List": ["Team 1", "Team 2", "..."],
            "Knowledge Base": ["Your Post 1", "Your Post 2", "Your Post 3", "..."],
        }
        for title, items in sections.items():
            Dropdown(self, title, items, command=command).pack(   # <- pass it down
                fill="x", padx=(10, 40), pady=10)



class Dropdown(ctk.CTkFrame):
    def __init__(self, master, title, items, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        self.open = False
        self.command = command

        self.header = ctk.CTkButton(self, text=f"▶ {title}", anchor="w",
                                    fg_color="transparent", command=self.toggle)
        self.header.pack(fill="x")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        for item in items:
            ctk.CTkButton(self.body, text=item, anchor="w",
                          command=lambda i=item: self._clicked(i)).pack(fill="x", padx=(20, 0), pady=1)

    def _clicked(self, item):
        if self.command:
            self.command(item)

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.body.pack(fill="x")
            self.header.configure(text=f"▼ {self.title}")
        else:
            self.body.pack_forget()
            self.header.configure(text=f"▶ {self.title}")




