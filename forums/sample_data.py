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


def build_sample_forum() -> ForumService:
    """Return a ForumService filled with realistic dummy data."""
    now = datetime.now()
    forum = ForumService()
    priya, tom, lena, sam = (SAMPLE_USERS[key] for key in ("priya", "tom", "lena", "sam"))

    # ----- topics and the teams they belong to -----

    dev = forum.create_topic(priya["email"], "Software Development",
                             "Coding standards, tools and how-tos.", is_moderator=True)
    issues = forum.create_topic(priya["email"], "Software Issues",
                                "Bugs, errors and their fixes.", is_moderator=True)
    printing = forum.create_topic(priya["email"], "Printing",
                                  "Printer setup, drivers and faults.", is_moderator=True)
    admin = forum.create_topic(priya["email"], "Admin Processes",
                               "Expenses, leave and other HR processes.",
                               TopicCategory.NON_TECHNICAL, is_moderator=True)
    forum.link_topic_to_team(dev.id, "Development", is_moderator=True)
    forum.link_topic_to_team(issues.id, "Development", is_moderator=True)
    forum.link_topic_to_team(printing.id, "Facilities", is_moderator=True)

    # ----- who follows what (Jo is new and follows nothing) -----

    forum.follow_topic(lena["email"], issues.id)
    forum.follow_topic(sam["email"], printing.id)
    forum.follow_topic(sam["email"], admin.id)
    forum.follow_topic(priya["email"], admin.id)
    forum.follow_topic(priya["email"], printing.id)

    # ----- helpers that backdate posts and comments -----

    def backdate(post: Post, days_ago: float) -> Post:
        post.created_at = now - timedelta(days=days_ago)
        return post

    def reply(target: Post, author: dict, body: str, days_ago: float) -> Comment:
        return target.add_comment(author["email"], author["name"], body,
                                  created_at=now - timedelta(days=days_ago))

    # ----- forum posts -----

    vpn = backdate(forum.create_forum_post(
        lena["email"], lena["name"], issues.id,
        "VPN drops every 20 minutes on Windows 11",
        "Since the last update my VPN disconnects roughly every **20 minutes**. "
        "Reconnecting works, but it kills long uploads. Anyone else?",
        ["vpn", "windows"]), days_ago=1.5)
    reply(vpn, tom, "Same here on two laptops in the dev team.", days_ago=1.2)
    fix = reply(vpn, sam, "Turn off *Allow the computer to turn off this device to save "
                "power* on the network adapter. Fixed it for me.", days_ago=0.8)
    vpn.mark_solution(lena["email"], fix.id)

    backdate(forum.create_forum_post(
        tom["email"], tom["name"], dev.id, "Branch naming for the Team 11 repo",
        "Please name branches `feature/<area>`, for example `feature/personal-todo`. "
        "See [PEP 8](https://peps.python.org/pep-0008/) for code style.",
        ["git", "standards"]), days_ago=3)

    jam = backdate(forum.create_forum_post(
        sam["email"], sam["name"], printing.id, "Second floor printer jams on tray 2",
        "Tray 2 jams with A4 80gsm paper. Tray 1 is fine. "
        "Is there a setting for paper weight?",
        ["printer", "hardware"]), days_ago=0.3)
    reply(jam, priya, "I've logged it with facilities as well.", days_ago=0.1)

    backdate(forum.create_forum_post(
        lena["email"], lena["name"], issues.id,
        "Excel crashes when opening shared workbooks",
        "Excel closes without an error when I open the shared budget workbook "
        "from the network drive.", ["excel", "office"]), days_ago=6)

    backdate(forum.create_forum_post(
        priya["email"], priya["name"], admin.id, "How to submit an expenses claim",
        "# Steps\nFill in the claim form, attach your receipts and send it to "
        "your manager by the **25th** of the month.", ["expenses", "finance"]), days_ago=2)

    old = backdate(forum.create_forum_post(
        sam["email"], sam["name"], printing.id, "Installing the old printer driver",
        "Download the driver from the IT portal and run it as administrator.",
        ["printer", "drivers"]), days_ago=30)
    forum.remove_post(sam["email"], old.id)

    # ----- announcements -----

    backdate(forum.create_announcement(
        priya["email"], priya["name"], printing.id, "New printers arrive on Monday",
        "The second floor printers are being replaced on **Monday**. "
        "Please collect any printing by Friday afternoon.",
        is_moderator=True), days_ago=0.5)

    backdate(forum.create_announcement(
        tom["email"], tom["name"], dev.id, "Code freeze before the demo",
        "No new features on `main` from Thursday. Bug fixes only.",
        is_moderator=True), days_ago=1)

    return forum


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