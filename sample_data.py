# sample_data.py

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