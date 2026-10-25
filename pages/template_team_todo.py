from asyncio import tasks

import customtkinter as ctk
from base import Page

class TeamTodoPage(Page):
    title = "Team To-do List"
    default_tasks = {"Task1": "Description of Task 1",
                     "Task2": "Description of Task 2",
                     "Task3": "Description of Task 3"}

    def __init__(self, master, app):
        super().__init__(master, app)
        ctk.CTkLabel(self, text=self.title,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 10))

        self.tasks = dict(self.default_tasks)   # per-page copy

        self.task_area = ctk.CTkScrollableFrame(self)
        self.task_area.pack(fill="both", expand=True)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", pady=(10, 0))
        self.entry = ctk.CTkEntry(bar, placeholder_text="New task...")
        self.entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(bar, text="Add", width=60, command=self.add_task).pack(side="left", padx=(10, 0))

        self.refresh()

    def refresh(self):
        for widget in self.task_area.winfo_children():
            widget.destroy()
        for name, description in self.tasks.items():
            task_frame = ctk.CTkFrame(self.task_area, fg_color="transparent")
            task_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(task_frame, text=name,
                         font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10)
            ctk.CTkLabel(task_frame, text=description,
                         wraplength=600).pack(anchor="w", padx=10, pady=(0, 5))

    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.tasks[text] = "No description yet"
        self.entry.delete(0, "end")
        self.refresh()