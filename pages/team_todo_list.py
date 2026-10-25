import customtkinter as ctk
from pages.template_team_todo import TeamTodoPage
from base import Page

class TeamListPage(TeamTodoPage):
    def __init__(self, master, app):
        super().__init__(master, app)