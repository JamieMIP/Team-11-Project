"""Data classes for employees, teams, projects and project tasks.

These classes only hold data and small helper methods. All the rules
about WHO may do WHAT live in service.py, so this file stays simple.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from .exceptions import InvalidAction, NotFound

# ----------------------------------------------------------------------
# Settings. Kept together so they are easy to find and change.
# ----------------------------------------------------------------------

# Dashboard: a person with this many unfinished tasks or more is flagged
# as overloaded. A warning, never a hard limit (Q&A PM Q11).
OVERLOAD_THRESHOLD = 5

# Team suggestion: how much each task "blocks" someone, by priority.
# High-priority work cannot be put aside for a new project; low can.
PRIORITY_WEIGHTS = {
    "Low": 0.5,
    "Medium": 1.0,
    "High": 1.5,
    "Critical": 2.0,
}

# Team suggestion: weighted work per person per week that counts as
# completely full (capacity score 0).
FULL_WEEKLY_LOAD = 3.0

# Team suggestion: if a project has no deadline, assume it lasts this long.
DEFAULT_PROJECT_WEEKS = 4

_id_counter = itertools.count(1)


def _new_id(prefix: str) -> str:
    """Make a short readable ID such as 'PRJ-7'."""
    return f"{prefix}-{next(_id_counter)}"


def _clean(text: str, what: str) -> str:
    """Strip spaces and refuse blank text."""
    text = (text or "").strip()
    if not text:
        raise InvalidAction(f"{what} cannot be blank.")
    return text


class Role(Enum):
    """The client's three roles (Q&A admin Q2: no separate admin role)."""
    EMPLOYEE = "Employee"
    TEAM_LEADER = "Team Leader"
    MANAGER = "Manager"


class Permission(Enum):
    """Actions that depend on role. See permissions.py for who gets what."""
    VIEW_DASHBOARD = "View dashboard"
    CREATE_TEAMS = "Create teams"
    MANAGE_MEMBERS = "Add and remove team members"
    CREATE_PROJECTS = "Create projects"
    ASSIGN_PROJECTS = "Assign projects to teams"
    MANAGE_TASKS = "Create, assign and edit tasks"
    APPROVE_TASKS = "Approve high-risk tasks"
    CHANGE_ROLES = "Change roles and staff access"


class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    PENDING_APPROVAL = "Pending Approval"
    DONE = "Completed"


class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

    @property
    def weight(self) -> float:
        return PRIORITY_WEIGHTS[self.value]


@dataclass
class Employee:
    """One member of staff. The email is their unique ID (Q&A admin Q5)."""
    email: str
    name: str
    role: Role = Role.EMPLOYEE
    login_id: int | None = None        # the number typed on the demo login screen
    access_ends: date | None = None    # temporary staff only (Q&A admin Q3)

    def is_active(self, today: date | None = None) -> bool:
        """False once a temporary member of staff's access has ended."""
        today = today or date.today()
        return self.access_ends is None or today <= self.access_ends


@dataclass
class Team:
    """A team has exactly ONE leader (Q9), any number of members, and any
    number of projects. One employee can be in many teams."""
    name: str
    leader_email: str
    member_emails: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: _new_id("TEAM"))

    def __post_init__(self) -> None:
        self.name = _clean(self.name, "Team name")
        if not self.leader_email:
            raise InvalidAction("A team must have a leader.")

    def everyone(self) -> list[str]:
        """Leader plus members, with no duplicates."""
        people = list(self.member_emails)
        if self.leader_email not in people:
            people.insert(0, self.leader_email)
        return people


@dataclass
class ProjectTask:
    """A task inside a project, assigned to one employee."""
    title: str
    project_id: str
    created_by: str
    assignee_email: str | None = None
    description: str = ""
    deadline: date | None = None
    priority: Priority = Priority.MEDIUM
    high_risk: bool = False
    progress: int = 0                   # 0 to 100
    status: TaskStatus = TaskStatus.NOT_STARTED
    id: str = field(default_factory=lambda: _new_id("TASK"))

    def __post_init__(self) -> None:
        self.title = _clean(self.title, "Task title")

    def is_done(self) -> bool:
        return self.status is TaskStatus.DONE

    def is_overdue(self, today: date | None = None) -> bool:
        """Past its deadline and not finished. It stays open (Q&A PM Q6)."""
        today = today or date.today()
        return self.deadline is not None and self.deadline < today and not self.is_done()

    def remaining_work(self) -> float:
        """How much of this task is left, weighted by priority.
        e.g. a High task at 40% -> 0.6 left x 1.5 = 0.9"""
        if self.is_done():
            return 0.0
        return (100 - self.progress) / 100 * self.priority.weight


@dataclass
class Project:
    """A piece of work given to one team. Flow: create -> assign team -> add tasks."""
    name: str
    created_by: str
    description: str = ""
    deadline: date | None = None
    team_id: str | None = None          # None until a manager assigns it
    tasks: list[ProjectTask] = field(default_factory=list)
    id: str = field(default_factory=lambda: _new_id("PRJ"))

    def __post_init__(self) -> None:
        self.name = _clean(self.name, "Project name")

    def progress(self) -> int:
        """Average progress of its tasks, 0-100 (Q&A PM Q1: project progress
        reflects its tasks). A project with no tasks is 0%."""
        if not self.tasks:
            return 0
        return round(sum(task.progress for task in self.tasks) / len(self.tasks))

    def overdue_tasks(self, today: date | None = None) -> list[ProjectTask]:
        return [task for task in self.tasks if task.is_overdue(today)]

    def get_task(self, task_id: str) -> ProjectTask:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise NotFound(f"No task with ID {task_id}.")


@dataclass
class TeamSuggestion:
    """One row of the 'which team has room for this project?' ranking."""
    team: Team
    score: int                  # 0-100, higher means more spare capacity
    tasks_counted: int          # unfinished tasks due before the project deadline
    weekly_load: float          # weighted work per person per week
    reasons: list[str]
