"""Teams, projects, project tasks, roles and the manager's dashboard.

The GUI should only need these names:

    from organisation import organisation, OrgError, Priority, Role, TaskStatus
"""

from .demo_data import build_demo_organisation, organisation
from .exceptions import InvalidAction, NotFound, OrgError, PermissionDenied
from .models import (FULL_WEEKLY_LOAD, OVERLOAD_THRESHOLD, PRIORITY_WEIGHTS, Employee,
                     Permission, Priority, Project, ProjectTask, Role, TaskStatus, Team,
                     TeamSuggestion)
from .service import OrganisationService

__all__ = [
    "organisation", "build_demo_organisation", "OrganisationService",
    "OrgError", "InvalidAction", "NotFound", "PermissionDenied",
    "FULL_WEEKLY_LOAD", "OVERLOAD_THRESHOLD", "PRIORITY_WEIGHTS",
    "Employee", "Permission", "Priority", "Project", "ProjectTask", "Role",
    "TaskStatus", "Team", "TeamSuggestion",
]
