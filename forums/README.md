# Forums and Knowledge Base

**Author:** Dominic Stachura · **Team:** Team 11 · **Status:** ready for review

Lets employees share technical knowledge (configs, bugs, fixes) and non-technical knowledge (admin processes) as **posts** filed under **topics** such as *Software Issues* or *Printing*. There are two kinds of post:

- **Forum posts:** questions and discussions. Anyone can write one, anyone can comment, and the author can mark a comment as the accepted solution.
- **Announcements:** a title and description only, with no comments. Only moderators (Managers and Team Leaders) can post them.

Employees can follow topics and remove their own posts. Moderators can remove any post and manage topics.

The **ranked posts feed is the default home page**. It orders posts by how relevant their topic is to the user, how much discussion they have, whether they are unsolved technical questions, and how recently they were active.

This folder is **logic only**: no screens and no GUI imports. The GUI talks to one class, `ForumService`.

## Tech stack

- **Language:** Python
- **GUI:** CustomTkinter
- **Editor:** VS Code
- **Data:** held in memory for Part 1 (no database or login)

## How it works

### Building the feed

```mermaid
flowchart TD
    A(["User opens the app"]) --> B["GUI passes email and team names"]
    B --> C{"Follows any topics?"}
    C -- Yes --> D["Gather posts from followed<br/>and team topics"]
    C -- No --> E["Gather posts active in<br/>the last 14 days"]
    D --> F["Score each post<br/>(topic match, activity, unsolved, freshness)"]
    E --> F
    F --> G["Sort by score,<br/>most recently active first on ties"]
    G --> H(["Show the feed with a reason label on each post"])
```

### What a user can do from the feed

```mermaid
flowchart TD
    S(["Posts feed displayed"]) --> ACT{"User action?"}

    ACT -- New post --> K{"Which kind?"}
    K -- Forum post --> F1["Select topic, write title,<br/>body, links and tags"]
    K -- Announcement --> AM{"Moderator?"}
    AM -- No --> AE["Show permission message"]
    AE --> K
    AM -- Yes --> A1["Select topic, write<br/>title and description"]
    F1 --> CV{"Post valid?"}
    A1 --> CV
    CV -- No --> CE["Show error message"]
    CV -- Yes --> C3["Save post with author name"]
    C3 --> CR(["Return to posts feed"])

    ACT -- Open post --> O1["Show post<br/>(and comments if allowed)"]
    O1 --> OD{"Action on post?"}
    OD -- Back --> OB(["Return to posts feed"])
    OD -- Comment --> OCA{"Forum post?"}
    OCA -- Yes --> OC["Add comment"]
    OC --> O1
    OCA -- No --> OE["Show message"]
    OD -- Mark solution --> OS{"Forum post and<br/>viewer is the author?"}
    OS -- Yes --> OSY["Mark comment as solution"]
    OSY --> O1
    OS -- No --> OE
    OD -- Delete --> OM{"Author or moderator?"}
    OM -- No --> OE
    OE --> OD
    OM -- Yes --> OR["Hide post (soft delete)"]
    OR --> OEND(["Return to posts feed"])

    ACT -- Browse topic --> T1["Choose a topic"]
    T1 --> T2["Rank that topic's posts<br/>with the same scoring"]
    T2 --> T3(["Topic feed displayed"])
```

The GUI shows the comment box only when `post.allows_comments()` is True, and the "Mark as solution" button only on forum posts the viewer wrote. The logic refuses these actions anyway if a button is shown by mistake.

Search is built by another team member. It searches the posts returned by `get_all_posts()`.

### How a post is scored

```
score = (1 + topic + activity + unsolved) x freshness

topic     = 3.0 if the user follows the topic, 2.0 if it's one of their team's topics, else 0
activity  = 0.5 x log(1 + number of comments)
unsolved  = 1.0 if post.needs_answer(): a technical forum post with no accepted solution, else 0
freshness = 0.5 ^ (days since last activity / 3)
```

The reason label shown on each post is whichever part added the most, for example *From a topic you follow* or *Unsolved in Printing*. The weights are settings at the top of `FeedRanker` in `forum_feed.py`.

## How to plug it into the GUI

**1. Create one service when the app starts** and share it with every screen:

```python
from forums import ForumService, ForumError

forum = ForumService()
```

For demos, use the sample data instead:

```python
from forums.forum_sample_data import SAMPLE_USERS, build_sample_forum

forum = build_sample_forum()
user = SAMPLE_USERS["lena"]   # pretend Lena is logged in
```

**2. Tell it how to refresh your screen.** It calls this after every change:

```python
forum.on_change(refresh_forum_screen)   # your own function, no arguments
```

**3. Draw the home feed** using the logged-in user's email and team names. Both kinds of post appear in the same feed:

```python
from forums import ForumPost

for entry in forum.get_home_feed(user_email, team_names):
    post = entry.post
    print(post.type_label(), post.title, post.author_name, post.preview(), entry.reason)
    if isinstance(post, ForumPost):
        print(post.comment_count(), "comments", "Solved" if post.is_solved() else "")
```

**4. Wire up buttons**, catching `ForumError` to show a friendly message:

```python
try:
    forum.create_forum_post(user_email, user_name, topic_id, title, body, tags)
    forum.create_announcement(user_email, user_name, topic_id, title, description,
                              is_moderator=is_moderator)
    forum.add_comment(user_email, user_name, post_id, "Try restarting the router")
    forum.mark_solution(user_email, post_id, comment_id)
    forum.remove_post(user_email, post_id, is_moderator=is_moderator)
except ForumError as error:
    show_error_popup(str(error))   # your GUI's own pop-up
```

**5. Hide buttons the user can't use:**

```python
show_delete = post.can_be_removed_by(user_email, is_moderator)
show_comment_box = post.allows_comments()
show_mark_solution = isinstance(post, ForumPost) and post.is_author(user_email)
follow_text = "Unfollow" if forum.is_following(user_email, topic_id) else "Follow"
```

**6. Showing post bodies.** Bodies are Markdown text: `**bold**`, `*italic*`, `[link text](https://...)` and `# Heading`. CustomTkinter's `CTkTextbox` doesn't allow fonts on text tags, so use a plain `tkinter.Text` widget to display a post. Use tags for bold and headings, and `tag_bind` with `webbrowser.open` for clickable links.

## What you can call on `ForumService`

Methods that act for someone take the logged-in user's email first.

| Method | What it does |
|--------|--------------|
| `get_home_feed(email, team_names, limit)` | Ranked home page posts, as `FeedEntry` objects |
| `get_topic_feed(email, topic_id, team_names, limit)` | Ranked posts in one topic (browse by topic) |
| `get_topics()` | Every topic, A to Z |
| `get_topic(topic_id)` | One topic |
| `create_topic(email, name, description, category, is_moderator)` | New topic (moderators only) |
| `link_topic_to_team(topic_id, team, is_moderator)` | Show a topic's posts to a team in their feed (moderators only) |
| `follow_topic(email, topic_id)` / `unfollow_topic(email, topic_id)` | Follow or stop following a topic |
| `is_following(email, topic_id)` | Whether to show Follow or Unfollow |
| `get_followed_topics(email)` | The user's followed topics, A to Z |
| `create_forum_post(email, name, topic_id, title, body, tags)` | Publish a forum post; the logged-in user is always the author |
| `create_announcement(email, name, topic_id, title, description, is_moderator)` | Publish an announcement (moderators only) |
| `get_post(post_id)` | Open a post (removed posts count as not found) |
| `get_all_posts()` | Every visible post, newest first (used by search) |
| `remove_post(email, post_id, is_moderator)` | Author removes their own, moderators any (soft delete) |
| `add_comment(email, name, post_id, body)` | Reply to a forum post (announcements refuse comments) |
| `mark_solution(email, post_id, comment_id)` | Accept a comment as the solution (forum post author only) |
| `clear_solution(email, post_id)` | Remove the accepted solution (forum post author only) |
| `unsolved_by_topic()` | Technical forum posts still needing an answer, per topic, most first, for managers |
| `on_change(function)` | Runs your function after every change |

**Useful on each `FeedEntry`:** `post`, `score`, `reason`

**Useful on every post:** `id`, `title`, `body`, `author_name`, `author_email`, `topic`, `tags`, `created_at`, `type_label()`, `allows_comments()`, `needs_answer()`, `comments()`, `comment_count()`, `is_author()`, `can_be_removed_by()`, `preview()`, `plain_text()`, `last_activity()`

**Only on forum posts:** `accepted_solution`, `is_solved()`, `mark_solution()`, `clear_solution()`

**Useful on each topic:** `id`, `name`, `description`, `category`, `is_technical()`, `teams()`

**Useful on each comment:** `id`, `author_name`, `author_email`, `body`, `created_at`

## Errors

All errors inherit from `ForumError`, so `except ForumError` catches everything.

| Error | When |
|-------|------|
| `ValidationError` | Blank title, body, description, comment, name or topic name, a bad email, a duplicate topic name, commenting on an announcement, or marking a solution on one |
| `TopicNotFoundError` | No topic with that ID |
| `PostNotFoundError` | No post with that ID, or it has been removed |
| `CommentNotFoundError` | No comment with that ID on the post |
| `AccessDeniedError` | Not allowed, e.g. removing someone else's post, or a non-moderator creating a topic or announcement |

## What the forum needs from other parts of the system

The forum doesn't create or manage users, roles or teams. The GUI passes in:

| Value | Comes from | Used for |
|-------|-----------|----------|
| `user_email` | Login | Who is acting; staff email is the unique identifier |
| `user_name` | Login | Shown as the author of posts and comments |
| `is_moderator` | Roles and permissions | True for Managers and Team Leaders (and anyone given moderation rights) |
| `team_names` | Teams | Posts in a team's topics get the team boost in the feed |

## Class diagram

```mermaid
classDiagram
    direction TB

    class TopicCategory {
        <<enumeration>>
        TECHNICAL
        NON_TECHNICAL
    }

    class Topic {
        +id: str
        +name: str
        +created_by: str
        +description: str
        +category: TopicCategory
        -_teams: list~str~
        +is_technical() bool
        +teams() list~str~
        +link_team(team: str) None
        +unlink_team(team: str) None
        +is_linked_to(team_names: list~str~) bool
    }

    class Comment {
        +id: str
        +author_email: str
        +author_name: str
        +body: str
        +created_at: datetime
        +plain_text() str
    }

    class Post {
        <<abstract>>
        +ALLOWS_COMMENTS: bool = True
        +id: str
        +title: str
        +body: str
        +author_email: str
        +author_name: str
        +topic: Topic
        +tags: list~str~
        +created_at: datetime
        +is_removed: bool
        +removed_by: str
        +removed_at: datetime
        -_comments: list~Comment~
        +type_label()* str
        +needs_answer()* bool
        +allows_comments() bool
        +add_comment(author_email, author_name, body) Comment
        +get_comment(comment_id: str) Comment
        +comments() list~Comment~
        +comment_count() int
        +is_author(user_email: str) bool
        +can_be_removed_by(user_email, is_moderator) bool
        +remove(user_email, is_moderator) None
        +last_activity() datetime
        +plain_text() str
        +preview(length: int) str
    }

    class ForumPost {
        +accepted_solution: Comment
        +type_label() str
        +needs_answer() bool
        +mark_solution(user_email, comment_id) Comment
        +clear_solution(user_email: str) None
        +is_solved() bool
    }

    class Announcement {
        +ALLOWS_COMMENTS: bool = False
        +type_label() str
        +needs_answer() bool
    }

    class FeedEntry {
        +post: Post
        +score: float
        +reason: str
    }

    class FeedRanker {
        +FOLLOWED_WEIGHT: float = 3.0
        +TEAM_WEIGHT: float = 2.0
        +ACTIVITY_WEIGHT: float = 0.5
        +UNSOLVED_BOOST: float = 1.0
        +RECENCY_HALF_LIFE_DAYS: float = 3.0
        +COLD_START_DAYS: int = 14
        +build_feed(posts, followed_topic_ids, team_names, limit) list~FeedEntry~
        +rank(posts, followed_topic_ids, team_names, limit) list~FeedEntry~
        -_gather_candidates(posts, followed_topic_ids, team_names, now) list~Post~
        -_score(post, followed_topic_ids, team_names, now) FeedEntry
    }

    class ForumService {
        -_topics: dict~str, Topic~
        -_posts: dict~str, Post~
        -_followed: dict~str, set~
        -_ranker: FeedRanker
        -_listeners: list
        +on_change(callback) None
        +get_home_feed(user_email, team_names, limit) list~FeedEntry~
        +get_topic_feed(user_email, topic_id, team_names, limit) list~FeedEntry~
        +get_topics() list~Topic~
        +get_topic(topic_id) Topic
        +create_topic(user_email, name, description, category, is_moderator) Topic
        +link_topic_to_team(topic_id, team, is_moderator) Topic
        +follow_topic(user_email, topic_id) None
        +unfollow_topic(user_email, topic_id) None
        +is_following(user_email, topic_id) bool
        +get_followed_topics(user_email) list~Topic~
        +create_forum_post(email, name, topic_id, title, body, tags) ForumPost
        +create_announcement(email, name, topic_id, title, desc, mod) Announcement
        +get_post(post_id) Post
        +get_all_posts() list~Post~
        +remove_post(user_email, post_id, is_moderator) None
        +add_comment(user_email, user_name, post_id, body) Comment
        +mark_solution(user_email, post_id, comment_id) Comment
        +clear_solution(user_email, post_id) None
        +unsolved_by_topic() list
        -_add_post(post: Post) None
        -_get_forum_post(post_id) ForumPost
    }

    Post <|-- ForumPost
    Post <|-- Announcement
    Topic --> "1" TopicCategory
    Post --> "1" Topic : filed under
    Post "1" *-- "0..*" Comment : comments
    ForumPost --> "0..1" Comment : accepted solution
    FeedEntry --> "1" Post
    FeedRanker ..> FeedEntry : creates
    ForumService "1" o-- "0..*" Topic
    ForumService "1" o-- "0..*" Post
    ForumService --> "1" FeedRanker
```

Parameter names are shortened in the diagram (`mod` is `is_moderator`). `Post` is abstract: it can't be created on its own, and every subclass must write `type_label()` and `needs_answer()` (marked `*`). The feed only ever calls methods that `Post` defines, so a new kind of post can be added without changing the feed or the service's storage.

## Design decisions

- **Post types through inheritance.** `Post` is an abstract base class holding everything posts share. `ForumPost` adds accepted solutions; `Announcement` turns comments off with one class setting (`ALLOWS_COMMENTS = False`). Each answers `needs_answer()` in its own way, so the feed boosts open questions without checking which kind of post it has (polymorphism).
- **Users identified by email.** As the client asked, and matching the personal to-do list. The forum stores the author's email and name on each post and comment, so posts are never anonymous.
- **Moderation.** The client has no Admin role. Managers and Team Leaders moderate by default, and anyone else can be given moderation rights by the roles system. The GUI passes `is_moderator`, which defaults to `False` so forgetting it is always safe. Moderators can also create topics, which stops near-duplicates like "Printer" and "Printers" splitting posts up, and post announcements.
- **Soft delete.** Removing a post hides it from the feed and `get_all_posts()`, but keeps it with who removed it and when, in case a removal is questioned.
- **Markdown bodies.** The client requires formatting and links. Markdown is plain text, so it's simple to store and search, and the post screen formats it.
- **Cold start.** A user who follows nothing, or whose topics have no posts yet, sees everything active in the last 14 days, so the home page is never empty.
- **Ranking uses last activity.** A new comment brings an older post back up the feed.
- **Unsolved boost.** Open technical forum posts are pushed up so they get answered faster. Announcements never get it.
- **Topic-level insight only.** `unsolved_by_topic()` counts per topic, never per person, so it can't be used to target individuals. It helps managers see where training might be needed, which the original brief asks for.

## Files

## What you can call on `ForumService`

Methods that act for someone take the logged-in user's email first. Every ID is a string (`str`), so store `post.id`, `topic.id` or `comment.id` on your widget and pass it back in.

### Feed

| Method | What it does | Returns | Can raise |
|--------|--------------|---------|-----------|
| `get_home_feed(email, team_names=None, limit=20)` | Ranked posts for the home page | `list[FeedEntry]`, best first. Never empty if any posts exist | Nothing |
| `get_topic_feed(email, topic_id, team_names=None, limit=20)` | Ranked posts in one topic (browse by topic) | `list[FeedEntry]`, best first. Empty if the topic has no posts | `TopicNotFoundError` |

### Topics

| Method | What it does | Returns | Can raise |
|--------|--------------|---------|-----------|
| `get_topics()` | Every topic, for drop-downs and topic lists | `list[Topic]`, A to Z | Nothing |
| `get_topic(topic_id)` | One topic | `Topic` | `TopicNotFoundError` |
| `create_topic(email, name, description="", category=TopicCategory.TECHNICAL, is_moderator=False)` | New topic (moderators only) | The new `Topic` | `AccessDeniedError`, `ValidationError` |
| `link_topic_to_team(topic_id, team, is_moderator=False)` | Show a topic's posts to a team in their feed (moderators only) | The updated `Topic` | `AccessDeniedError`, `TopicNotFoundError`, `ValidationError` |
| `follow_topic(email, topic_id)` | Follow a topic | Nothing (`None`) | `TopicNotFoundError` |
| `unfollow_topic(email, topic_id)` | Stop following a topic | Nothing (`None`) | Nothing |
| `is_following(email, topic_id)` | Whether to show Follow or Unfollow | `bool` | Nothing |
| `get_followed_topics(email)` | The user's followed topics | `list[Topic]`, A to Z | Nothing |

### Posts

| Method | What it does | Returns | Can raise |
|--------|--------------|---------|-----------|
| `create_forum_post(email, name, topic_id, title, body, tags=None)` | Publish a forum post; the logged-in user is always the author | The new `ForumPost` | `TopicNotFoundError`, `ValidationError` |
| `create_announcement(email, name, topic_id, title, description, is_moderator=False)` | Publish an announcement (moderators only) | The new `Announcement` | `AccessDeniedError`, `TopicNotFoundError`, `ValidationError` |
| `get_post(post_id)` | Open a post | `ForumPost` or `Announcement` (check with `isinstance`) | `PostNotFoundError` (also if removed) |
| `get_all_posts()` | Every visible post (used by search) | `list[Post]`, newest first, both kinds mixed | Nothing |
| `remove_post(email, post_id, is_moderator=False)` | Author removes their own, moderators any (soft delete) | Nothing (`None`) | `PostNotFoundError`, `AccessDeniedError` |

### Comments and solutions

| Method | What it does | Returns | Can raise |
|--------|--------------|---------|-----------|
| `add_comment(email, name, post_id, body)` | Reply to a forum post | The new `Comment` | `PostNotFoundError`, `ValidationError` (blank, or the post is an announcement) |
| `mark_solution(email, post_id, comment_id)` | Accept a comment as the solution (forum post author only) | The `Comment` now marked as the solution | `PostNotFoundError`, `CommentNotFoundError`, `AccessDeniedError`, `ValidationError` (announcement) |
| `clear_solution(email, post_id)` | Remove the accepted solution (forum post author only) | Nothing (`None`) | `PostNotFoundError`, `AccessDeniedError`, `ValidationError` (announcement) |

### Other

| Method | What it does | Returns | Can raise |
|--------|--------------|---------|-----------|
| `unsolved_by_topic()` | Technical forum posts still needing an answer, for managers | `list[tuple[Topic, int]]`, most first, e.g. `[(printing, 3), (issues, 1)]`. Topics with none are left out | Nothing |
| `on_change(function)` | Runs your function (no arguments) after every successful change | Nothing (`None`) | Nothing |

### Parameter types

| Parameter | Type | Notes |
|-----------|------|-------|
| `email` | `str` | Logged-in user's staff email; capitals and spaces don't matter |
| `name` | `str` | Logged-in user's display name, saved as the author |
| `topic_id`, `post_id`, `comment_id` | `str` | From `topic.id`, `post.id`, `comment.id` |
| `team_names` | `list[str]`, optional | The user's team names, e.g. `["Development"]` |
| `limit` | `int`, default 20 | Most posts a feed returns |
| `title`, `description` | `str` | Can't be blank |
| `body` | `str` | Markdown text; can't be blank |
| `tags` | `list[str]`, optional | Tidied automatically: `"#Printer"` becomes `"printer"`, repeats removed |
| `category` | `TopicCategory` | `TopicCategory.TECHNICAL` or `TopicCategory.NON_TECHNICAL` |
| `is_moderator` | `bool`, default `False` | From the roles system |

## What you get back

### `FeedEntry` (from the feeds)

| Attribute | Type | Use it for |
|-----------|------|-----------|
| `post` | `ForumPost` or `Announcement` | Everything shown on the card (see below) |
| `score` | `float` | How well it ranked; mainly for testing |
| `reason` | `str` | Small label on the card, e.g. `"From a topic you follow"` or `"Unsolved in Printing"` |

### Every post (`ForumPost` and `Announcement`)

| Attribute or method | Type | Use it for |
|---------------------|------|-----------|
| `id` | `str` | Store on the widget; pass to `get_post`, `add_comment` etc. |
| `title` | `str` | Card and page heading |
| `body` | `str` | Full Markdown text for the post page (an announcement's description) |
| `author_name` | `str` | "Posted by" |
| `author_email` | `str` | Comparing with the logged-in user |
| `topic` | `Topic` | `post.topic.name` for the topic label |
| `tags` | `list[str]` | Tag chips (always empty for announcements) |
| `created_at` | `datetime` | "Posted on" date, e.g. `post.created_at.strftime("%d %b %Y")` |
| `type_label()` | `str` | Badge: `"Forum post"` or `"Announcement"` |
| `allows_comments()` | `bool` | Whether to show the comment box |
| `needs_answer()` | `bool` | Whether to show an "Unanswered" badge |
| `comments()` | `list[Comment]` | The comment thread, oldest first (always empty for announcements) |
| `comment_count()` | `int` | "3 comments" on the card |
| `is_author(email)` | `bool` | Whether the logged-in user wrote it |
| `can_be_removed_by(email, is_moderator)` | `bool` | Whether to show the delete button |
| `preview(length=150)` | `str` | Short plain-text snippet for the card, cut at a whole word with `...` |
| `plain_text()` | `str` | Body with Markdown symbols removed |
| `last_activity()` | `datetime` | When it was posted or last commented on |

### Only on `ForumPost`

| Attribute or method | Type | Use it for |
|---------------------|------|-----------|
| `accepted_solution` | `Comment` or `None` | Highlight that comment in the thread |
| `is_solved()` | `bool` | "Solved" badge |

### `Topic`

| Attribute or method | Type | Use it for |
|---------------------|------|-----------|
| `id` | `str` | Store on the drop-down or list item |
| `name` | `str` | Display name, e.g. `"Printing"` |
| `description` | `str` | Shown under the name (may be empty) |
| `category` | `TopicCategory` | `topic.category.value` gives `"technical"` or `"non-technical"` |
| `is_technical()` | `bool` | Technical or not |
| `teams()` | `list[str]` | Names of the teams it's linked to |
| `created_by` | `str` | Email of the moderator who made it |

### `Comment`

| Attribute or method | Type | Use it for |
|---------------------|------|-----------|
| `id` | `str` | Pass to `mark_solution` |
| `author_name` | `str` | "Reply from" |
| `author_email` | `str` | Comparing with the logged-in user |
| `body` | `str` | Markdown text of the reply |
| `created_at` | `datetime` | When it was posted |
| `plain_text()` | `str` | Body with Markdown symbols removed |

## Running

From the repo root:

```
python -m forums.forum_sample_data   # print every sample user's home feed
python -m unittest -v                # run the tests
```

## Notes

- Data is held in memory for the Part 1 prototype and resets when the app closes. Only the storage inside `forum_gui_service.py` would need changing for a database in Part 2.
- Search, users, roles and teams are built by other team members. See "What the forum needs from other parts of the system" above.
