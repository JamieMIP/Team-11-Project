import customtkinter as ctk
from widgets import Dashboard, SidePanel, Dropdown
from base import PlaceholderPage
from pages.personal_todo_list import PersonalListPage
from pages.team_todo_list import TeamListPage

PAGES = {
    "List 1": PersonalListPage,
    "Team 1": TeamListPage,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My First App")
        self.geometry("1200x900")
        self.minsize(400, 300)

        self.columnconfigure(1, weight=1)   # content column stretches
        self.rowconfigure(1, weight=1)      # content row stretches

        self.dashboard = Dashboard(self)
        self.dashboard.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.sidePanel = SidePanel(self, command=self.show_page)
        self.sidePanel.grid(row=1, column=0, sticky="ns")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.pages = {}
        self.current = None

    def show_page(self, name):
        if self.current:
            self.current.pack_forget()

        if name not in self.pages:
            page_class = PAGES.get(name)
            if page_class:
                self.pages[name] = page_class(self.content, self)
            else:
                self.pages[name] = PlaceholderPage(self.content, self, name)

        self.current = self.pages[name]
        self.current.pack(fill="both", expand=True)
        self.current.on_show()


if __name__ == "__main__":
    app = App()
    app.mainloop()