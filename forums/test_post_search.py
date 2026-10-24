import unittest

from .post_search import search_posts
from .sample_data import build_sample_forum
from .forum_models import TopicCategory


class PostSearchTests(unittest.TestCase):
    def setUp(self):
        self.forum = build_sample_forum()
        self.posts = self.forum.get_all_posts()

    def test_finds_title_match(self):
        results = search_posts(self.posts, "vpn")

        self.assertEqual(len(results), 1)
        self.assertIn("VPN", results[0].title)

    def test_ignores_capitalisation(self):
        lowercase = search_posts(self.posts, "vpn")
        uppercase = search_posts(self.posts, "VPN")

        self.assertEqual(lowercase, uppercase)

    def test_empty_query_returns_all_posts(self):
        self.assertEqual(search_posts(self.posts, ""), self.posts)

    def test_ignores_extra_spaces(self):
        normal = search_posts(self.posts, "vpn")
        spaced = search_posts(self.posts, "   vpn   ")

        self.assertEqual(normal, spaced)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(
            search_posts(self.posts, "zzznomatchingpostzzz"),
            [],
        )

    def test_finds_word_in_body(self):
        post = self.forum.create_forum_post(
            "owen@example.com",
            "Owen",
            self.forum.get_topics()[0].id,
            "Example question",
            "The unusualkeyword appears only in this body.",
        )

        results = search_posts(
            self.forum.get_all_posts(),
            "unusualkeyword",
        )

        self.assertEqual(results, [post])

    def test_requires_all_words(self):
        results = search_posts(self.posts, "vpn zzznomatchingpostzzz")

        self.assertEqual(results, [])

    def test_filters_by_topic(self):
        topic = next(
            topic for topic in self.forum.get_topics()
            if topic.name == "Printing"
        )

        results = search_posts(self.posts, topic_id=topic.id)
        expected = [
            post for post in self.posts
            if post.topic.id == topic.id
        ]

        self.assertTrue(results)
        self.assertEqual(results, expected)

    def test_filters_by_category(self):
        category = TopicCategory.NON_TECHNICAL

        results = search_posts(self.posts, category=category)
        expected = [
            post for post in self.posts
            if post.topic.category == category
        ]

        self.assertTrue(results)
        self.assertEqual(results, expected)

    def test_combines_keywords_and_filters(self):
        topic = next(
            topic for topic in self.forum.get_topics()
            if topic.name == "Printing"
        )

        matching_post = self.forum.create_forum_post(
            "owen@example.com",
            "Owen",
            topic.id,
            "Search test",
            "uniquefilterword",
        )

        self.forum.create_forum_post(
            "owen@example.com",
            "Owen",
            topic.id,
            "Another search test",
            "Different content without the search term.",
        )

        results = search_posts(
            self.forum.get_all_posts(),
            query="uniquefilterword",
            topic_id=topic.id,
            category=TopicCategory.TECHNICAL,
        )

        self.assertEqual(results, [matching_post])

        incompatible_results = search_posts(
            self.forum.get_all_posts(),
            query="uniquefilterword",
            topic_id=topic.id,
            category=TopicCategory.NON_TECHNICAL,
        )

        self.assertEqual(incompatible_results, [])


if __name__ == "__main__":
    unittest.main()