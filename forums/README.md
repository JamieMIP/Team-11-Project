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
