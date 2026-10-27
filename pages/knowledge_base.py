from pages.template_knowledge_base import KnowledgePage
from widgets import PostCard

class KnowledgeBasePage(KnowledgePage):
    title = "Knowledge Base"

    

    def on_show(self):
        print("on_show running, posts:", len(self.get_posts()))        
        for widget in self.post_area.winfo_children():
            widget.destroy()

        columns = 3
        for i, post in enumerate(self.get_posts()):
            card = PostCard(self.post_area, post)
            card.grid(row=i // columns, column=i % columns, padx=10, pady=10)

    def get_posts(self):
        # TEMPORARY: replace with real get_posts() function
        return [
            {"title": "Getting started", "author": "Alex",
             "body": "Welcome to the knowledge base. Start here to learn how the team shares information."},
            {"title": "Team conventions", "author": "Sam",
             "body": "How we name files and branches, and how pull requests get reviewed."},
            {"title": "Setting up your environment", "author": "Priya",
             "body": "Install Python, then run pip install customtkinter. Open the GUI files folder in VS Code."},
            {"title": "Meeting notes: week 3", "author": "Jordan",
             "body": "Agreed on the page system for the GUI. Login will launch the main window after authentication. "
                     "Database schema to be finalised by Friday. This one is long on purpose so you can check that the text wraps."},
            {"title": "Useful links", "author": "Alex",
             "body": "Links to the project board, the shared drive and the design mockups."},
            {"title": "Troubleshooting", "author": "Sam",
             "body": "If the window doesn't appear, run from a terminal so any error stays visible."},
        ]