"""Which role can do what.

Permissions are fixed per role in this prototype. (The client also
mentioned granting extra permissions to individuals, Q&A admin Q6; that
is planned for Part 2.)
"""

from .models import Employee, Permission, Role

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.EMPLOYEE: set(),
    Role.TEAM_LEADER: {
        Permission.VIEW_DASHBOARD,       # for the teams they lead
        Permission.MANAGE_TASKS,         # Q&A PM Q5: view, create, assign, edit, reassign
        Permission.APPROVE_TASKS,        # Q&A PM Q2: approve high-risk tasks
    },
    Role.MANAGER: set(Permission),       # managers can do everything
}


def has_permission(employee: Employee, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[employee.role]
