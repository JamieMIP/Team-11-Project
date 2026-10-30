from pages.template_knowledge_base import KnowledgePage
from widgets import PostCard

from forums.sample_data import SAMPLE_USERS, build_sample_forum
from forums import ForumPost
from forums.post_search import search_posts




class KnowledgeBasePage(KnowledgePage):
    title = "Knowledge Base"

    def __init__(self, master, app):
        super().__init__(master, app)

        self.posts = []

        self.forum = build_sample_forum()
        self.user = SAMPLE_USERS["lena"]


        for entry in self.forum.get_home_feed(self.user["email"], self.user["name"]):
            post = entry.post
            print(post.type_label(), post.title, post.author_name, post.preview(), entry.reason)
            self.posts.append({"title" : post.title, "author" : post.author_name, "body" : post.preview(), "topics" : post.topic})
            
            if isinstance(post, ForumPost):
                print(post.comment_count(), "comments", "Solved" if post.is_solved() else "")

        #self.posts = [
        #            {"title": "Getting started", "author": "Alex",
        #             "body": "Welcome to the knowledge base. Start here to learn how the team shares information.", "topic": "introduction, start"},
        #            {"title": "Team conventions", "author": "Sam",
        #             "body": "How we name files and branches, and how pull requests get reviewed.", "topic" : "standerds"},
        #            {"title": "Setting up your environment", "author": "Priya",
        #             "body": "Install Python, then run pip install customtkinter. Open the GUI files folder in VS Code.", "topic": "pip, gui"},
        #           {"title": "Meeting notes: week 3", "author": "Jordan",
        #            "body": "Agreed on the page system for the GUI. Login will launch the main window after authentication. "
        #                     "Database schema to be finalised by Friday. This one is long on purpose so you can check that the text wraps.", "topic" : "database"},
        #            {"title": "Useful links", "author": "Alex",
        #             "body": "Links to the project board, the shared drive and the design mockups.", "topic" : ""},
        #            {"title": "Troubleshooting", "author": "Sam",
        #             "body": "If the window doesn't appear, run from a terminal so any error stays visible.", "topic" : ""},
        #        ]

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
            self.forum.create_forum_post(self.user["email"], self.user["name"], new_post["topic"].id, new_post["title"], new_post["body"], tags=None)
            print("all posts: ", self.forum.get_all_posts)

    def submit_post(self, title, content, author, files, top):
        selected_name = self.dropdown.get()
        topics = self.forum.get_topics()

        selected_topic = next(
            topic for topic in topics
            if topic.name == selected_name
        )

        post = {"title": title, "author" : author, "body" : content, "topic" : selected_topic}
        self.add_post(post)
        print(self.posts)

        self.on_show()

        top.destroy()

    def on_search_posts(self, event):
        print(event)
        selected_name = self.filter_topic.get()
        topics = self.forum.get_topics()
        
        selected_topic = next(
            topic for topic in topics
            if topic.name == selected_name
        )

        results = search_posts(self.forum.get_all_posts(), self.search.get(), selected_topic.id)
        #print("all posts: ", self.forum.get_all_posts())
        #print("search query: ", self.search.get())
        #print("topic name/id: ", selected_topic.name, selected_topic.id)
        #print("search results: ", results)

        for post in results:
                #print(post.type_label(), post.title, post.author_name, post.preview(), entry.reason)
                self.posts = []
                self.posts.append({"title" : post.title, "author" : post.author_name, "body" : post.preview(), "topics" : post.topic})
                
                    
                #if isinstance(post, ForumPost):
                    #print(post.comment_count(), "comments", "Solved" if post.is_solved() else "")
        print("some posts: ", self.forum.get_all_posts)
        self.on_show()
        
    
        
