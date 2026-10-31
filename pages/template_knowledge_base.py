import customtkinter as ctk
from base import Page
from sample_data import forum
from pages.knowledge_base_widgets import PostFeed, centred_padding

ALL_TOPICS = "All topics"

class KnowledgePage(Page):
    """Layout for knowledge base pages: title, search bar, post area."""
    title = "Knowledge Base"

    def __init__(self, master, app):

        self.forum = forum      # the one shared forum, same as every other screen      
        
        super().__init__(master, app)
                # ----- header: stays put while the feed scrolls -----
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.header, text=self.title,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 10))

        top_bar = ctk.CTkFrame(self.header, fg_color="transparent")
        top_bar.pack(fill="x")

        self.search = ctk.CTkEntry(top_bar, placeholder_text="Search posts...")
        self.search.pack(side="left", fill="x", expand=True)
        self.search.bind("<Return>", self.on_search_posts)

        topic_names = [topic.name for topic in self.forum.get_topics()]
        self.filter_topic = ctk.CTkOptionMenu(
            top_bar,
            values=[ALL_TOPICS] + topic_names,
            width=180,
            command=lambda choice: self.on_search_posts(None)
        )
        self.filter_topic.set(ALL_TOPICS)
        self.filter_topic.pack(side="left", padx=(10, 0))
        
        # Only shown while one topic is picked (the page packs and hides it)
        self.follow_button = ctk.CTkButton(top_bar, text="Follow topic", width=130,
                                           command=self.toggle_follow)

        self.add_new_post_button = ctk.CTkButton(top_bar, text="Add New Post", width=130,
                                                command=self.add_new_post)
        self.add_new_post_button.pack(side="left", padx=(10, 0))

        # ----- feed: scrolls, centred, no wider than the cap -----
        self.post_area = PostFeed(self, page=self)
        self.post_area.pack(fill="both", expand=True)

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """Keep the header the same width as the feed column below it."""
        self.header.pack_configure(padx=centred_padding(self, event.width))

 
