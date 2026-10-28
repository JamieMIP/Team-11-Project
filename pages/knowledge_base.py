from pages.template_knowledge_base import KnowledgePage
from widgets import PostCard

class KnowledgeBasePage(KnowledgePage):
    title = "Knowledge Base"

    def __init__(self, master, app):
        super().__init__(master, app)

        self.posts = [
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

    def get_posts(self):
        return self.posts

    def on_show(self):
        print("on_show running, posts:", len(self.get_posts()))        
        for widget in self.post_area.winfo_children():
            widget.destroy()

        columns = 3
        for i, post in enumerate(self.get_posts()):
            card = PostCard(self.post_area, post)
            card.grid(row=i // columns, column=i % columns, padx=10, pady=10)

    def add_post(self, new_post):
            self.posts.append(new_post) 

    def submit_post(self, title, content, author, files, top):
        post = {"title": title, "author" : author, "body" : content}
        self.add_post(post)
        print(self.posts)

        self.on_show()
    
        top.destroy()