"""Dummy topics, posts and comments for the Part 1 prototype.

The forum doesn't manage users or teams, so SAMPLE_USERS stands in for
whoever is "logged in" during a demo: each has the email, name,
moderator flag and team names the GUI would normally get from the
roles and teams parts of the system.

Run from the repo root to print every sample user's home feed:

    python -m forums.forum_sample_data
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .forum_gui_service import ForumService
from .forum_models import Comment, Post, TopicCategory

SAMPLE_USERS: dict[str, dict] = {
    "priya": {"email": "priya.shah@make-it-all.co.uk", "name": "Priya Shah",
              "is_moderator": True, "teams": ["Management"]},
    "tom": {"email": "tom.okafor@make-it-all.co.uk", "name": "Tom Okafor",
            "is_moderator": True, "teams": ["Development"]},
    "lena": {"email": "lena.novak@make-it-all.co.uk", "name": "Lena Novak",
             "is_moderator": False, "teams": ["Development"]},
    "sam": {"email": "sam.price@make-it-all.co.uk", "name": "Sam Price",
            "is_moderator": False, "teams": ["Facilities"]},
    "jo": {"email": "jo.reed@make-it-all.co.uk", "name": "Jo Reed",
           "is_moderator": False, "teams": ["Development"]},
}



if __name__ == "__main__":
    sample_forum = build_sample_forum()
    for user in SAMPLE_USERS.values():
        print(f"\nHome feed for {user['name']}:")
        for entry in sample_forum.get_home_feed(user["email"], user["teams"], limit=6):
            print(f"  {entry.score:5.2f}  [{entry.post.type_label()}] "
                  f"{entry.post.title}  ({entry.reason})")
    print("\nTechnical questions still waiting for an answer:")
    for topic, count in sample_forum.unsolved_by_topic():
        print(f"  {topic.name}: {count}")