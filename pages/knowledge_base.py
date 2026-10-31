from pages.template_knowledge_base import ALL_TOPICS, KnowledgePage
from forums import ForumError
from pages.knowledge_base_widgets import ANNOUNCEMENT, FORUM_POST, NewPostDialog

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

        # Why each post is in the feed, e.g. "From a topic you follow" (post ID -> reason)
        self.reasons = {}

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
        """Runs every time the page is opened: back to the full feed, all topics."""
        self.clear_search()
        self.load_feed()
        self.show_posts()

    def clear_search(self):
        """Empty the search box and go back to All topics."""
        if self.search.get():               # clear old search text, keeping the placeholder
            self.search.delete(0, "end")
        self.filter_topic.set(ALL_TOPICS)
        self.update_follow_button()

    def load_feed(self):
        """Fill self.posts with the logged-in user's ranked home feed."""
        feed = self.forum.get_home_feed(self.user_email, self.team_names())
        self.posts = [entry.post for entry in feed]
        self.reasons = {entry.post.id: entry.reason for entry in feed}

    def show_posts(self):
        """Draw a card for each post in self.posts."""
        self.post_area.show(self.posts, self.reasons)

    # ----- ACTIONS -----

    def topic_named(self, name):
        """Find the topic with this name (used by the topic drop-downs)."""
        return next(topic for topic in self.forum.get_topics() if topic.name == name)

    def post_kinds(self) -> list[str]:
        """The kinds of post the logged-in user can make. Everyone can write
        forum posts; only Managers can post announcements."""
        kinds = [FORUM_POST]
        if self.is_manager():
            kinds.append(ANNOUNCEMENT)
        return kinds

    def add_new_post(self):
        """The Add New Post button. The dialog starts on the topic being
        filtered, if there is one."""
        topic_names = [topic.name for topic in self.forum.get_topics()]
        chosen = self.filter_topic.get()
        NewPostDialog(self, topic_names,
                      post_kinds=self.post_kinds(),
                      on_submit=self.create_post,
                      start_topic=None if chosen == ALL_TOPICS else chosen)

    def create_post(self, kind, title, topic_name, body, tags):
        """Make the post as the logged-in user. Returns an error message for
        the dialog to show (e.g. a blank title), or None if it worked."""
        topic = self.topic_named(topic_name)
        try:
            if kind == ANNOUNCEMENT:
                post = self.forum.create_announcement(self.user_email, self.user_name,
                                                      topic.id, title, body,
                                                      is_moderator=self.is_manager())
            else:
                post = self.forum.create_forum_post(self.user_email, self.user_name,
                                                    topic.id, title, body, tags)
        except ForumError as error:
            return str(error)

        # Back to the full feed, with the new post at the top so you can see it went up
        self.clear_search()
        self.load_feed()
        self.posts = [post] + [other for other in self.posts if other is not post]
        self.reasons[post.id] = "You just posted this"
        self.show_posts()
        return None

    def send_reply(self, post, text):
        """Save a reply to a post, as the logged-in user."""
        self.forum.add_comment(self.user_email, self.user_name, post.id, text)

    def toggle_solution(self, post, comment):
        """Mark a reply as the accepted solution, or unmark it if it already is.
        The forum only lets the post's author do this."""
        if post.accepted_solution is comment:
            self.forum.clear_solution(self.user_email, post.id)
        else:
            self.forum.mark_solution(self.user_email, post.id, comment.id)
            
    def on_search_posts(self, event):
        """Search when Enter is pressed or a topic is picked.
        With nothing typed and All topics picked, go back to the feed."""
        query = self.search.get().strip()
        topic_name = self.filter_topic.get()

        if not query and topic_name == ALL_TOPICS:
            self.load_feed()
        else:
            topic_id = None if topic_name == ALL_TOPICS else self.topic_named(topic_name).id
            self.posts = search_posts(self.forum.get_all_posts(), query, topic_id)
            self.reasons = {}
        self.show_posts()
        self.update_follow_button()

    # ----- FOLLOWING TOPICS -----

    def selected_topic(self):
        """The topic picked in the filter, or None for All topics."""
        name = self.filter_topic.get()
        return None if name == ALL_TOPICS else self.topic_named(name)

    def update_follow_button(self):
        """Show Follow topic / Unfollow topic while one topic is picked.
        Hide it for All topics, because there's nothing to follow."""
        topic = self.selected_topic()
        if topic is None:
            self.follow_button.pack_forget()
            return
        following = self.forum.is_following(self.user_email, topic.id)
        self.follow_button.configure(text="Unfollow topic" if following else "Follow topic")
        self.follow_button.pack(side="left", padx=(10, 0), before=self.add_new_post_button)

    def toggle_follow(self):
        """Follow the picked topic, or unfollow it if already following.
        Followed topics rank higher in the user's feed."""
        topic = self.selected_topic()
        if self.forum.is_following(self.user_email, topic.id):
            self.forum.unfollow_topic(self.user_email, topic.id)
        else:
            self.forum.follow_topic(self.user_email, topic.id)
        self.update_follow_button()
        
    
        
