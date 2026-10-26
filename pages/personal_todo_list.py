import customtkinter as ctk
from base import Page

class PersonalListPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        ctk.CTkLabel(self, text="Personal To-do List").pack(pady=20)