# sample_data.py

"""Demo data for the whole app (Part 1 prototype, no database yet).

Delete this file once the real database is connected in Part 2.
"""

from datetime import datetime, timedelta

from forums import Comment, ForumService, Post, TopicCategory


LIVE_USERS = {
    0: {
        "id": 0,
        "name": "Alice",
        "email": "a.vance@company.co.uk",
        "role": "Manager",
        "is_admin": True,
    },
    1: {
        "id": 1,
        "name": "Dilip",
        "email": "m.sterling@company.co.uk",
        "role": "Team Leader",
        "is_admin": False,
    },
    2: {
        "id": 2,
        "name": "Liam",
        "email": "l.chen@company.co.uk",
        "role": "Employee",
        "is_admin": False,
    }
}

ALL_TEAMS = {
    "Team 1": {
        "info": {
            "team_id": "TEAM_01",
            "team_name": "Team 1",
            "project_name": "Cloud Auth & SSO Migration",
            "leader_id": 1,
            "leader_email": "m.sterling@company.co.uk",
            "member_ids": [1, 2],
        },
        "tasks": {
            "Task1": {
                "title": "Configure Passphrase Validator",
                "description": "Implement minimum length passphrase checking and common-password blacklisting.",
                "assigned_user_id": 2,
                "assigned_user_name": "Liam",
                "assigned_user_email": "l.chen@company.co.uk",
                "assigned_by_id": 1,
                "deadline": "2026-10-18",
                "priority": "Critical",
                "status": "In Progress",
                "progress": 65,
                "is_high_risk": True,
            },
            "Task2": {
                "title": "Build Multi-Device Session Handler",
                "description": "Ensure concurrent logins across desktop and laptop sessions track active tokens safely.",
                "assigned_user_id": 2,
                "assigned_user_name": "Liam",
                "assigned_user_email": "l.chen@company.co.uk",
                "assigned_by_id": 1,
                "deadline": "2026-11-05",
                "priority": "High",
                "status": "In Progress",
                "progress": 40,
                "is_high_risk": False,
            },
            "Task3": {
                "title": "Audit Contractor Offboarding Script",
                "description": "Verify that revoking contractor status terminates active sessions and task write access.",
                "assigned_user_id": 1,
                "assigned_user_name": "Dilip",
                "assigned_user_email": "m.sterling@company.co.uk",
                "assigned_by_id": 0,
                "deadline": "2026-11-12",
                "priority": "Medium",
                "status": "Pending Approval",
                "progress": 100,
                "is_high_risk": True,
            }
        }
    },
    "Team 2": {
        "info": {
            "team_id": "TEAM_02",
            "team_name": "Team 2",
            "project_name": "Internal Knowledge Base & Forum",
            "leader_id": 1,
            "leader_email": "m.sterling@company.co.uk",
            "member_ids": [1, 2],
        },
        "tasks": {
            "Task1": {
                "title": "Implement Rich Text & Hyperlink Parser",
                "description": "Allow employees to format technical posts with bolding, code blocks, and clickable URLs.",
                "assigned_user_id": 2,
                "assigned_user_name": "Liam",
                "assigned_user_email": "l.chen@company.co.uk",
                "assigned_by_id": 1,
                "deadline": "2026-11-02",
                "priority": "High",
                "status": "In Progress",
                "progress": 80,
                "is_high_risk": False,
            },
            "Task2": {
                "title": "Setup Content Moderation Overrides",
                "description": "Enable authorised users to remove inappropriate posts while keeping author attribution logs.",
                "assigned_user_id": 1,
                "assigned_user_name": "Dilip",
                "assigned_user_email": "m.sterling@company.co.uk",
                "assigned_by_id": 0,
                "deadline": "2026-10-20",
                "priority": "Medium",
                "status": "Not Started",
                "progress": 0,
                "is_high_risk": True,
            }
        }
    },
    "Team 3": {
        "info": {
            "team_id": "TEAM_03",
            "team_name": "Team 3",
            "project_name": "Q4 Security & Infrastructure Audit",
            "leader_id": 1,
            "leader_email": "m.sterling@company.co.uk",
            "member_ids": [1],  # User 2 is not in Team 3
        },
        "tasks": {
            "Task1": {
                "title": "Review Privileged Account Logs",
                "description": "Audit step-up authentication logs across all team leader and manager accounts.",
                "assigned_user_id": 1,
                "assigned_user_name": "Dilip",
                "assigned_user_email": "m.sterling@company.co.uk",
                "assigned_by_id": 0,
                "deadline": "2026-11-15",
                "priority": "High",
                "status": "In Progress",
                "progress": 50,
                "is_high_risk": True,
            }
        }
    },
    "Team 4": {
        "info": {
            "team_id": "TEAM_04",
            "team_name": "Team 4",
            "project_name": "Executive Resource Planning",
            "leader_id": 0,
            "leader_email": "a.vance@company.co.uk",
            "member_ids": [0],  # Only User 0 (Admin/Manager) is in Team 4
        },
        "tasks": {
            "Task1": {
                "title": "Q1 Department Capacity Forecast",
                "description": "Evaluate cross-team workload balancing and identify training budget allocations.",
                "assigned_user_id": 0,
                "assigned_user_name": "Alice",
                "assigned_user_email": "a.vance@company.co.uk",
                "assigned_by_id": 0,
                "deadline": "2026-11-25",
                "priority": "Medium",
                "status": "Not Started",
                "progress": 0,
                "is_high_risk": False,
            }
        }
    }
}

# ----- KNOWLEDGE BASE -----


def build_sample_forum() -> ForumService:

    """Return a ForumService filled with realistic dummy data."""
    now = datetime.now()
    forum = ForumService()
    alice, dilip, liam = LIVE_USERS[0], LIVE_USERS[1], LIVE_USERS[2]

    # ----- topics and the teams they belong to -----

    dev = forum.create_topic(alice["email"], "Software Development",
                             "Coding standards, tools and how-tos.", is_moderator=True)
    issues = forum.create_topic(alice["email"], "Software Issues",
                                "Bugs, errors and their fixes.", is_moderator=True)
    printing = forum.create_topic(alice["email"], "Printing",
                                  "Printer setup, drivers and faults.", is_moderator=True)
    admin = forum.create_topic(alice["email"], "Admin Processes",
                               "Expenses, leave and other HR processes.",
                               TopicCategory.NON_TECHNICAL, is_moderator=True)
    forum.link_topic_to_team(dev.id, "Team 1", is_moderator=True)
    forum.link_topic_to_team(issues.id, "Team 2", is_moderator=True)
    forum.link_topic_to_team(printing.id, "Team 3", is_moderator=True)

    # ----- who follows what -----.

    forum.follow_topic(liam["email"], issues.id)
    forum.follow_topic(dilip["email"], printing.id)
    forum.follow_topic(dilip["email"], admin.id)
    forum.follow_topic(alice["email"], admin.id)
    forum.follow_topic(alice["email"], printing.id)

    # ----- helpers that backdate posts and comments -----

    def backdate(post: Post, days_ago: float) -> Post:
        post.created_at = now - timedelta(days=days_ago)
        return post

    def reply(target: Post, author: dict, body: str, days_ago: float) -> Comment:
        return target.add_comment(author["email"], author["name"], body,
                                  created_at=now - timedelta(days=days_ago))

    # ----- forum posts -----

    vpn = backdate(forum.create_forum_post(
        liam["email"], liam["name"], issues.id,
        "VPN drops every 20 minutes on Windows 11",
        "Since the last update my VPN disconnects roughly every **20 minutes**. "
        "Reconnecting works, but it kills long uploads. Anyone else?",
        ["vpn", "windows"]), days_ago=1.5)
    reply(vpn, dilip, "Same here on two laptops in the dev team.", days_ago=1.2)
    fix = reply(vpn, alice, "Turn off *Allow the computer to turn off this device to save "
                "power* on the network adapter. Fixed it for me.", days_ago=0.8)
    vpn.mark_solution(liam["email"], fix.id)

    backdate(forum.create_forum_post(
        alice["email"], alice["name"], dev.id, "Branch naming for the Team 11 repo",
        "Please name branches `feature/<area>`, for example `feature/personal-todo`. "
        "See [PEP 8](https://peps.python.org/pep-0008/) for code style.",
        ["git", "standards"]), days_ago=3)

    jam = backdate(forum.create_forum_post(
        dilip["email"], dilip["name"], printing.id, "Second floor printer jams on tray 2",
        "Tray 2 jams with A4 80gsm paper. Tray 1 is fine. "
        "Is there a setting for paper weight?",
        ["printer", "hardware"]), days_ago=0.3)
    reply(jam, alice, "I've logged it with facilities as well.", days_ago=0.1)

    backdate(forum.create_forum_post(
        liam["email"], liam["name"], issues.id,
        "Excel crashes when opening shared workbooks",
        "Excel closes without an error when I open the shared budget workbook "
        "from the network drive.", ["excel", "office"]), days_ago=6)

    backdate(forum.create_forum_post(
        alice["email"], alice["name"], admin.id, "How to submit an expenses claim",
        "# Steps\nFill in the claim form, attach your receipts and send it to "
        "your manager by the **25th** of the month.", ["expenses", "finance"]), days_ago=2)

    old = backdate(forum.create_forum_post(
        dilip["email"], dilip["name"], printing.id, "Installing the old printer driver",
        "Download the driver from the IT portal and run it as administrator.",
        ["printer", "drivers"]), days_ago=30)
    forum.remove_post(dilip["email"], old.id)

    # ----- announcements -----

    backdate(forum.create_announcement(
        alice["email"], alice["name"], printing.id, "New printers arrive on Monday",
        "The second floor printers are being replaced on **Monday**. "
        "Please collect any printing by Friday afternoon.",
        is_moderator=True), days_ago=0.5)

    backdate(forum.create_announcement(
        dilip["email"], dilip["name"], dev.id, "Code freeze before the demo",
        "No new features on `main` from Thursday. Bug fixes only.",
        is_moderator=True), days_ago=1)

    return forum

forum = build_sample_forum()

def get_user_teams(user_id: int) -> dict:
    """Returns only the teams that the given user_id is permitted to view."""
    user = LIVE_USERS.get(user_id, LIVE_USERS[2])

    # Managers / Admins see every team
    if user.get("role") == "Manager" or user.get("is_admin"):
        return ALL_TEAMS

    # Team Leaders and Employees see teams they lead or are a member of
    permitted = {}
    for team_name, team_data in ALL_TEAMS.items():
        info = team_data.get("info", {})
        if user_id == info.get("leader_id") or user_id in info.get("member_ids", []):
            permitted[team_name] = team_data
    return permitted