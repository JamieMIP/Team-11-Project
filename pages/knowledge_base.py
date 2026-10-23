import customtkinter as ctk
from base import Page

class KnowledgeBasePage(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        ctk.CTkLabel(self, text="Knowledge Base").pack(pady=20)