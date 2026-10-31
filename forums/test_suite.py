"""Tests for the forums component.

Run from the repo root with:  python -m unittest -v
"""

import unittest
from datetime import datetime, timedelta

from forums import (AccessDeniedError, Announcement, CommentNotFoundError,
                    ForumPost, ForumService, Post, PostNotFoundError,
                    TopicCategory, TopicNotFoundError, ValidationError)
from sample_data import LIVE_USERS, build_sample_forum

PRIYA = "priya@make-it-all.co.uk"   # a moderator
SAM = "sam@make-it-all.co.uk"       # writes the forum post in every test
LENA = "lena@make-it-all.co.uk"     # someone else


class ForumTestCase(unittest.TestCase):
    """Builds a small forum before every test."""

    def setUp(self) -> None:
        self.forum = ForumService()
        self.refreshes = 0
        self.forum.on_change(self._count_refresh)
        self.printing = self.forum.create_topic(PRIYA, "Printing", is_moderator=True)
        self.admin = self.forum.create_topic(PRIYA, "Admin Processes",
                                             category=TopicCategory.NON_TECHNICAL,
                                             is_moderator=True)
        self.post = self.forum.create_forum_post(
            SAM, "Sam Price", self.printing.id, "Printer jams on tray 2",
            "Paper gets **stuck**, see [the guide](https://x)", ["#Printer", "printer"])

    def _count_refresh(self) -> None:
        self.refreshes += 1

    def _announce(self, title: str = "New printers on Monday") -> Announcement:
        return self.forum.create_announcement(PRIYA, "Priya Shah", self.printing.id,
                                              title, "Collect printing by Friday.",
                                              is_moderator=True)


class TestPostTypes(ForumTestCase):

    def test_post_cannot_be_created_directly(self):
        with self.assertRaises(TypeError):
            Post("Title", "Body", SAM, "Sam Price", self.printing)

    def test_both_kinds_are_posts(self):
        notice = self._announce()
        self.assertIsInstance(self.post, Post)
        self.assertIsInstance(notice, Post)
        self.assertNotIsInstance(notice, ForumPost)

    def test_each_kind_has_its_own_label(self):
        self.assertEqual(self.post.type_label(), "Forum post")
        self.assertEqual(self._announce().type_label(), "Announcement")

    def test_only_moderators_can_post_announcements(self):
        with self.assertRaises(AccessDeniedError):
            self.forum.create_announcement(SAM, "Sam Price", self.printing.id,
                                           "Free cake", "In the kitchen")

    def test_announcements_cannot_be_commented_on(self):
        notice = self._announce()
        self.assertFalse(notice.allows_comments())
        with self.assertRaises(ValidationError):
            self.forum.add_comment(LENA, "Lena Novak", notice.id, "Thanks!")

    def test_announcements_cannot_have_a_solution(self):
        notice = self._announce()
        with self.assertRaises(ValidationError):
            self.forum.mark_solution(PRIYA, notice.id, "any-id")

    def test_announcements_never_need_an_answer(self):
        self.assertFalse(self._announce().needs_answer())


class TestCreatingPosts(ForumTestCase):

    def test_blank_title_is_refused(self):
        with self.assertRaises(ValidationError):
            self.forum.create_forum_post(SAM, "Sam Price", self.printing.id, "  ", "Body")

    def test_blank_body_is_refused(self):
        with self.assertRaises(ValidationError):
            self.forum.create_forum_post(SAM, "Sam Price", self.printing.id, "Title", "   ")

    def test_blank_announcement_description_is_refused(self):
        with self.assertRaises(ValidationError):
            self.forum.create_announcement(PRIYA, "Priya Shah", self.printing.id,
                                           "Title", " ", is_moderator=True)

    def test_author_name_is_required(self):
        with self.assertRaises(ValidationError):
            self.forum.create_forum_post(SAM, " ", self.printing.id, "Title", "Body")

    def test_unknown_topic_is_refused(self):
        with self.assertRaises(TopicNotFoundError):
            self.forum.create_forum_post(SAM, "Sam Price", "no-such-id", "Title", "Body")

    def test_tags_are_tidied(self):
        self.assertEqual(self.post.tags, ["printer"])

    def test_markdown_is_stripped_for_search_and_previews(self):
        self.assertEqual(self.post.plain_text(), "Paper gets stuck, see the guide")


class TestTopics(ForumTestCase):

    def test_only_moderators_can_create_topics(self):
        with self.assertRaises(AccessDeniedError):
            self.forum.create_topic(SAM, "Networking")

    def test_duplicate_topic_names_are_refused(self):
        with self.assertRaises(ValidationError):
            self.forum.create_topic(PRIYA, "printing", is_moderator=True)

    def test_topics_are_listed_a_to_z(self):
        names = [topic.name for topic in self.forum.get_topics()]
        self.assertEqual(names, ["Admin Processes", "Printing"])

    def test_following_ignores_capitals_and_repeats(self):
        self.forum.follow_topic("SAM@make-it-all.co.uk", self.printing.id)
        self.forum.follow_topic(SAM, self.printing.id)
        self.assertEqual(self.forum.get_followed_topics(SAM), [self.printing])
        self.forum.unfollow_topic(SAM, self.printing.id)
        self.assertFalse(self.forum.is_following(SAM, self.printing.id))


class TestCommentsAndSolutions(ForumTestCase):

    def setUp(self):
        super().setUp()
        self.comment = self.forum.add_comment(LENA, "Lena Novak", self.post.id,
                                              "Try tray 1")

    def test_author_can_mark_a_solution(self):
        marked = self.forum.mark_solution(SAM, self.post.id, self.comment.id)
        self.assertIs(marked, self.comment)
        self.assertTrue(self.post.is_solved())
        self.assertFalse(self.post.needs_answer())

    def test_others_cannot_mark_a_solution(self):
        with self.assertRaises(AccessDeniedError):
            self.forum.mark_solution(LENA, self.post.id, self.comment.id)

    def test_unknown_comment_is_refused(self):
        with self.assertRaises(CommentNotFoundError):
            self.forum.mark_solution(SAM, self.post.id, "no-such-id")

    def test_comment_counts_as_activity(self):
        self.assertEqual(self.post.last_activity(), self.comment.created_at)


class TestRemovingPosts(ForumTestCase):

    def test_author_can_remove_their_own_post(self):
        self.forum.remove_post(SAM, self.post.id)
        self.assertTrue(self.post.is_removed)

    def test_others_cannot_remove_a_post(self):
        self.assertFalse(self.post.can_be_removed_by(LENA))
        with self.assertRaises(AccessDeniedError):
            self.forum.remove_post(LENA, self.post.id)

    def test_moderators_can_remove_any_post(self):
        self.forum.remove_post(PRIYA, self.post.id, is_moderator=True)
        self.assertEqual(self.post.removed_by, PRIYA)

    def test_removed_posts_are_hidden_everywhere(self):
        self.forum.remove_post(SAM, self.post.id)
        with self.assertRaises(PostNotFoundError):
            self.forum.get_post(self.post.id)
        self.assertEqual(self.forum.get_all_posts(), [])
        self.assertEqual(self.forum.get_home_feed(LENA), [])


class TestFeed(ForumTestCase):

    def test_followed_topics_come_first_with_a_reason(self):
        self.forum.create_forum_post(PRIYA, "Priya Shah", self.admin.id,
                                     "Expenses", "By the 25th")
        self.forum.follow_topic(SAM, self.printing.id)
        feed = self.forum.get_home_feed(SAM)
        self.assertEqual([entry.post for entry in feed], [self.post])
        self.assertEqual(feed[0].reason, "From a topic you follow")

    def test_feed_mixes_both_kinds_of_post(self):
        notice = self._announce()
        feed_posts = [entry.post for entry in self.forum.get_home_feed(LENA)]
        self.assertIn(notice, feed_posts)
        self.assertIn(self.post, feed_posts)

    def test_unsolved_questions_rank_above_equal_announcements(self):
        notice = self._announce()
        notice.created_at = self.post.created_at
        feed_posts = [entry.post for entry in self.forum.get_home_feed(LENA)]
        self.assertEqual(feed_posts, [self.post, notice])

    def test_team_topics_are_included(self):
        expenses = self.forum.create_forum_post(PRIYA, "Priya Shah", self.admin.id,
                                                "Expenses", "By the 25th")
        self.forum.link_topic_to_team(self.admin.id, "Finance", is_moderator=True)
        self.forum.follow_topic(LENA, self.printing.id)
        with_team = [entry.post for entry in self.forum.get_home_feed(LENA, ["finance"])]
        without_team = [entry.post for entry in self.forum.get_home_feed(LENA)]
        self.assertIn(expenses, with_team)
        self.assertNotIn(expenses, without_team)

    def test_older_posts_sink(self):
        old = self.forum.create_forum_post(LENA, "Lena Novak", self.printing.id,
                                           "Old", "Old post")
        old.created_at = datetime.now() - timedelta(days=9)
        self.forum.follow_topic(SAM, self.printing.id)
        feed_posts = [entry.post for entry in self.forum.get_home_feed(SAM)]
        self.assertEqual(feed_posts, [self.post, old])

    def test_topic_feed_only_shows_that_topic(self):
        self.forum.create_forum_post(PRIYA, "Priya Shah", self.admin.id,
                                     "Expenses", "By the 25th")
        feed = self.forum.get_topic_feed(LENA, self.printing.id)
        self.assertEqual([entry.post for entry in feed], [self.post])


class TestRefreshAndInsight(ForumTestCase):

    def test_changes_trigger_a_refresh_but_failures_do_not(self):
        before = self.refreshes
        with self.assertRaises(AccessDeniedError):
            self.forum.create_topic(SAM, "Nope")
        self.assertEqual(self.refreshes, before)
        self.forum.add_comment(LENA, "Lena Novak", self.post.id, "Same here")
        self.assertEqual(self.refreshes, before + 1)

    def test_unsolved_questions_are_counted_per_topic(self):
        self._announce()
        self.assertEqual(self.forum.unsolved_by_topic(), [(self.printing, 1)])

    def test_solved_questions_are_not_counted(self):
        comment = self.forum.add_comment(LENA, "Lena Novak", self.post.id, "Fix")
        self.forum.mark_solution(SAM, self.post.id, comment.id)
        self.assertEqual(self.forum.unsolved_by_topic(), [])


class TestSampleData(unittest.TestCase):

    def test_every_sample_user_gets_a_feed(self):
        forum = build_sample_forum()
        for user in LIVE_USERS.values():
            self.assertTrue(forum.get_home_feed(user["email"]))

    def test_sample_data_has_both_kinds_of_post(self):
        kinds = {post.type_label() for post in build_sample_forum().get_all_posts()}
        self.assertEqual(kinds, {"Forum post", "Announcement"})


if __name__ == "__main__":
    unittest.main()