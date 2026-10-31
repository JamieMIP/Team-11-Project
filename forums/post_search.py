"""Keyword searching and filtering for forum posts."""

from .forum_models import Post, TopicCategory


def search_posts(
    posts: list[Post],
    query: str = "",
    topic_id: str | None = None,
    category: TopicCategory | None = None,
) -> list[Post]:
    """Return posts matching the query and any selected filters.

    Matching ignores capitalisation and extra spaces.
    Every search word must appear in the title, body or tags.
    Results retain their original order.
    """
    search_words = query.casefold().split()
    matching_posts = []

    for post in posts:
        if topic_id is not None and post.topic.id != topic_id:
            continue

        if category is not None and post.topic.category != category:
            continue

        searchable_text = f"{post.title} {post.plain_text()} {' '.join(post.tags)}".casefold()

        if all(word in searchable_text for word in search_words):
            matching_posts.append(post)

    return matching_posts