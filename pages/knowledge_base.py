from pages.template_knowledge_base import KnowledgePage
from pages.template_knowledge_base import KnowledgePage
from widgets import PostCard

from forums.post_search import search_posts
from organisation import Role, organisation



class KnowledgeBasePage(KnowledgePage):
    title = "Knowledge Base"

    def __init__(self, master, app):
        super().__init__(master, app)

        # Whoever logged in. Posts and replies are made as this person.
        self.user_email = app.current_user["email"]
        self.user_name = app.current_user["name"]

        # The Post objects currently on screen (the feed, or search results)
        self.posts = []

    # ----- WHO IS LOGGED IN -----

    def is_manager(self) -> bool:
        """True if the logged-in user is a Manager. Checked each time,
        because a role can be changed on the Manage Teams & Roles page."""
        return organisation.get_employee(self.user_email).role is Role.MANAGER

    def team_names(self) -> list[str]:
        """Names of the teams the logged-in user can see, for ranking the feed."""
        return [team.name for team in organisation.teams_for(self.user_email)]

    # ----- LOADING AND SHOWING POSTS -----

    def on_show(self):
        """Runs every time the page is opened: reload the feed and draw it."""
        self.load_feed()
        self.show_posts()

    def load_feed(self):
        """Fill self.posts with the logged-in user's ranked home feed."""
        feed = self.forum.get_home_feed(self.user_email, self.team_names())
        self.posts = [entry.post for entry in feed]

    def show_posts(self):
        """Clear the post area and draw a card for each post in self.posts."""
        for widget in self.post_area.winfo_children():
            widget.destroy()

        columns = 3
        for i, post in enumerate(self.posts):
            card = PostCard(self.post_area, self.card_data(post))
            card.grid(row=i // columns, column=i % columns, padx=10, pady=10)

    def card_data(self, post):
        """Turn a Post into the dict the old PostCard expects.
        Temporary: goes away when the new post card arrives in Section 2."""
        return {"title": post.title, "author": post.author_name,
                "body": post.preview(), "topic": post.topic.name}

    # ----- ACTIONS -----

    def topic_named(self, name):
        """Find the topic with this name (used by the topic drop-downs)."""
        return next(topic for topic in self.forum.get_topics() if topic.name == name)

    def submit_post(self, title, content, author, files, top):
        topic = self.topic_named(self.dropdown.get())
        self.forum.create_forum_post(self.user_email, self.user_name,
                                     topic.id, title, content)
        top.destroy()
        self.on_show()

    def on_search_posts(self, event):
        topic = self.topic_named(self.filter_topic.get())
        self.posts = search_posts(self.forum.get_all_posts(), self.search.get(), topic.id)
        self.show_posts()
        
    
        
