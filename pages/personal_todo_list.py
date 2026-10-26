import customtkinter as ctk
from base import Page
from personal_todo.models import TodoItem

class TaskButton(ctk.CTkButton):
    def __init__(self, parent, task: TodoItem):
        self.task = task

        super().__init__(parent,
            text=task.title,
            command=self.on_click
        )

    def on_click(self):
        self.app.show_page(ExpandedTaskPage, self.task)

class PersonalListPage(Page):
    def __init__(self, master, app, todo_list):
        super().__init__(master, app)

        ctk.CTkLabel(self, text="Personal To-do List").pack(pady=20)

        for task in todo_list.items:
            TaskButton(self, task).pack(pady=5)

class ExpandedTaskPage(Page):
    def __init__(self, master, app, task):
        super().__init__(master, app)

        ctk.CTkLabel(
            self,
            text=f"Title: {task.title}"
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"Description: {task.description}"
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"Deadline: {task.deadline}"
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"Priority: {task.priority}"
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"Status: {task.status}"
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"Created: {task.created_at}"
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"Completed: {task.completed_at}"
        ).pack(pady=10)