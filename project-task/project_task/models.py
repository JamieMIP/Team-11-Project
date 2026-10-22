from __future__ import annotations

from datetime import date
from enum import Enum


# ---------------------------------------------------------------------------
# Enumerations, constants and errors
# ---------------------------------------------------------------------------

class TaskStatus(Enum):
    TO_DO: str = "To do"
    IN_PROGRESS: str = "In progress"
    DONE: str = "Done"
    OVERDUE: str = "Overdue"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# Warning level only. Employees have no fixed limit on their workload.
OVERLOAD_THRESHOLD = 3


class TaskError(Exception):
    """Base class for errors that should be shown to the user."""


class PermissionDenied(TaskError):
    """Raised when someone acts outside their role or area of responsibility."""


class InvalidAction(TaskError):
    """Raised when an action is not valid for the task's current state."""


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class Task:
    _nextId = 1

    def __init__(self, title: str, deadline: date, priority: Priority,
                 isHighRisk: bool, createdBy: TeamLeader):
        if not title or not title.strip():
            raise InvalidAction("A task needs a title.")
        if not isinstance(deadline, date):
            raise InvalidAction("A task needs a valid deadline.")
        self.taskId = f"T{Task._nextId:03d}"
        Task._nextId += 1
        self.title = title.strip()
        self.deadline = deadline
        self.status = TaskStatus.TO_DO
        self.priority = priority
        self.isHighRisk = isHighRisk
        self.isApproved = False
        self.createdBy = createdBy
        self.assignee: Employee | None = None
        self.assignedBy: TeamLeader | None = None

    def setPriority(self, priority: Priority) -> None:
        if not isinstance(priority, Priority):
            raise InvalidAction("Choose a valid priority.")
        self.priority = priority

    def makeOverdue(self) -> bool:
        """Mark the task overdue if its deadline has passed. The task stays open."""
        if self.status != TaskStatus.DONE and date.today() > self.deadline:
            self.status = TaskStatus.OVERDUE
        return self.status == TaskStatus.OVERDUE

    def isComplete(self) -> bool:
        """Routine tasks are complete when done; high-risk tasks also need approval."""
        return self.status == TaskStatus.DONE and (not self.isHighRisk or self.isApproved)

    def isAwaitingApproval(self) -> bool:
        return self.status == TaskStatus.DONE and self.isHighRisk and not self.isApproved

    def statusText(self) -> str:
        """Status as shown to users, including approval state."""
        if self.isAwaitingApproval():
            return "Awaiting approval"
        if self.isHighRisk and self.isComplete():
            return "Done (approved)"
        return self.status.value

    def __str__(self) -> str:
        risk = "High-risk" if self.isHighRisk else "Routine"
        who = self.assignee.name if self.assignee else "Unassigned"
        return (f"{self.taskId}: {self.title}\n"
                f"Assigned to: {who}\n"
                f"Priority: {self.priority.name.title()}\n"
                f"Deadline: {self.deadline.isoformat()}\n"
                f"Risk: {risk}\n"
                f"Status: {self.statusText()}")


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class Project:
    allProjects: list[Project] = []
    _nextId = 1

    def __init__(self, name: str):
        if not name or not name.strip():
            raise InvalidAction("A project needs a name.")
        self.projectId = f"P{Project._nextId:03d}"
        Project._nextId += 1
        self.name = name.strip()
        self.tasks: list[Task] = []
        Project.allProjects.append(self)

    def addTask(self, task: Task) -> None:
        self.tasks.append(task)

    def showProgress(self) -> float:
        """Progress of the project's tasks as a percentage (0-100)."""
        if not self.tasks:
            return 0.0
        completed = sum(1 for task in self.tasks if task.isComplete())
        return completed / len(self.tasks) * 100

    def completedCount(self) -> int:
        return sum(1 for task in self.tasks if task.isComplete())

    @staticmethod
    def allTasks() -> list[Task]:
        return [task for project in Project.allProjects for task in project.tasks]

    @staticmethod
    def projectOf(task: Task) -> Project | None:
        for project in Project.allProjects:
            if task in project.tasks:
                return project
        return None

    @classmethod
    def clearAll(cls) -> None:
        """Remove all projects (used when loading data and in tests)."""
        cls.allProjects.clear()


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------

class Employee:
    role = "Employee"

    def __init__(self, employeeId: str, name: str, email: str):
        self.employeeId = employeeId
        self.name = name
        self.email = email
        self.dashboard = Dashboard(self)

    def _checkOwnTask(self, task: Task) -> None:
        if task.assignee is not self:
            raise PermissionDenied(
                "You can only update tasks assigned to you.")
        if task.isHighRisk and task.isApproved:
            raise InvalidAction("This task has been approved. Only a team leader "
                                "or manager can reopen it.")

    def markToDo(self, task: Task) -> Task:
        self._checkOwnTask(task)
        if task.status != TaskStatus.OVERDUE:      # overdue tasks stay highlighted
            task.status = TaskStatus.TO_DO
        return task

    def markProgressing(self, task: Task) -> Task:
        self._checkOwnTask(task)
        if task.status != TaskStatus.OVERDUE:      # overdue tasks stay highlighted
            task.status = TaskStatus.IN_PROGRESS
        return task

    def markDone(self, task: Task) -> bool:
        """Mark a task done. Returns True if it now needs approval."""
        self._checkOwnTask(task)
        if task.status == TaskStatus.DONE:
            raise InvalidAction("This task is already done.")
        task.status = TaskStatus.DONE
        task.isApproved = False
        return task.isHighRisk

    def canSee(self, task: Task) -> bool:
        """Employees see only the tasks assigned to them."""
        return task.assignee is self

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"


# ---------------------------------------------------------------------------
# Team leader
# ---------------------------------------------------------------------------

class TeamLeader(Employee):
    role = "Team Leader"

    def __init__(self, employeeId: str, name: str, email: str):
        super().__init__(employeeId, name, email)
        self.teamsLed: list[Team] = []

    # --- permissions -------------------------------------------------------

    def canManage(self, employee: Employee) -> bool:
        """Team leaders can act only on members of the teams they lead."""
        return any(employee in team.members for team in self.teamsLed)

    def _inScope(self, task: Task) -> bool:
        return task.createdBy is self or (
            task.assignee is not None and self.canManage(task.assignee))

    def _requireScope(self, task: Task) -> None:
        if not self._inScope(task):
            raise PermissionDenied(
                f"{task.taskId} is outside your area of responsibility.")

    def canSee(self, task: Task) -> bool:
        return super().canSee(task) or self._inScope(task)

    # --- task management ---------------------------------------------------

    def createTask(self, project: Project, title: str, deadline: date,
                   priority: Priority = Priority.MEDIUM,
                   isHighRisk: bool = False) -> Task:
        task = Task(title, deadline, priority, isHighRisk, createdBy=self)
        project.addTask(task)
        return task

    def editTask(self, task: Task, title: str | None = None,
                 isHighRisk: bool | None = None) -> Task:
        self._requireScope(task)
        if title is not None:
            if not title.strip():
                raise InvalidAction("A task needs a title.")
            task.title = title.strip()
        if isHighRisk is not None:
            task.isHighRisk = isHighRisk
        return task

    def assignTask(self, task: Task, employee: Employee) -> bool:
        """Assign a task. Returns True if the employee may be overloaded
        (a warning only; the assignment still happens)."""
        self._requireScope(task)
        if not self.canManage(employee):
            raise PermissionDenied(
                f"{employee.name} is outside your area of responsibility.")
        overloaded = self.dashboard.highlightOverload(employee)
        task.assignee = employee
        task.assignedBy = self
        return overloaded

    def reassignTask(self, task: Task, newEmployee: Employee) -> bool:
        self._requireScope(task)
        if task.assignee is newEmployee:
            raise InvalidAction(
                f"{task.taskId} is already assigned to {newEmployee.name}.")
        return self.assignTask(task, newEmployee)

    def reviewTask(self, task: Task) -> str:
        """Return the task details for review."""
        self._requireScope(task)
        return str(task)

    def approveTask(self, task: Task) -> Task:
        self._requireScope(task)
        if not task.isHighRisk:
            raise InvalidAction("Routine tasks do not need approval.")
        if task.status != TaskStatus.DONE:
            raise InvalidAction(
                "A task can only be approved once it is marked done.")
        task.isApproved = True
        return task

    def reopenTask(self, task: Task) -> Task:
        self._requireScope(task)
        if task.status != TaskStatus.DONE:
            raise InvalidAction("Only tasks that are done can be reopened.")
        task.isApproved = False
        task.status = TaskStatus.IN_PROGRESS
        task.makeOverdue()                     # back to overdue if the deadline has passed
        return task

    def changeDeadline(self, task: Task, newDeadline: date) -> Task:
        self._requireScope(task)
        if not isinstance(newDeadline, date):
            raise InvalidAction("Enter a valid date.")
        task.deadline = newDeadline
        if task.status == TaskStatus.OVERDUE and newDeadline >= date.today():
            task.status = TaskStatus.IN_PROGRESS   # no longer overdue
        return task

    def changePriority(self, task: Task, newPriority: Priority) -> Task:
        self._requireScope(task)
        task.setPriority(newPriority)
        return task


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class Manager(TeamLeader):
    role = "Manager"

    def __init__(self, employeeId: str, name: str, email: str):
        super().__init__(employeeId, name, email)
        self.managedTeams: list[Team] = []

    def canManage(self, employee: Employee) -> bool:
        """Managers can act on anyone in the teams they manage, including the leaders."""
        return any(employee in team.members or employee is team.leader
                   for team in self.managedTeams)

    def _inScope(self, task: Task) -> bool:
        return task.createdBy is self or any(
            person is not None and self.canManage(person)
            for person in (task.assignee, task.createdBy))

    def createTeam(self, name: str) -> Team:
        team = Team(name)
        self.managedTeams.append(team)
        return team

    def appointTeamLeader(self, team: Team, leader: TeamLeader) -> Team:
        if team not in self.managedTeams:
            raise PermissionDenied(
                f"You do not manage the team '{team.name}'.")
        if not isinstance(leader, TeamLeader):
            raise InvalidAction(f"{leader.name} is not a team leader.")
        if team.leader is leader:
            raise InvalidAction(f"{leader.name} already leads '{team.name}'.")
        if team.leader is not None:                  # each team has only one leader
            team.leader.teamsLed.remove(team)
        team.leader = leader
        # a leader may lead many teams
        leader.teamsLed.append(team)
        return team


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

class Team:
    _nextId = 1

    def __init__(self, name: str):
        if not name or not name.strip():
            raise InvalidAction("A team needs a name.")
        self.teamId = f"TM{Team._nextId:02d}"
        Team._nextId += 1
        self.name = name.strip()
        self.leader: TeamLeader | None = None
        self.members: list[Employee] = []

    def addMember(self, employee: Employee) -> None:
        if employee in self.members:
            raise InvalidAction(
                f"{employee.name} is already in '{self.name}'.")
        self.members.append(employee)

    def removeMember(self, employee: Employee) -> list[Task]:
        """Remove a member and return their unfinished tasks.
        Tasks are NOT reassigned automatically: the team leader decides case by case."""
        if employee not in self.members:
            raise InvalidAction(f"{employee.name} is not in '{self.name}'.")
        self.members.remove(employee)
        return [task for task in Project.allTasks()
                if task.assignee is employee and task.status != TaskStatus.DONE]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class Dashboard:
    def __init__(self, owner: Employee):
        self.owner = owner

    def visibleTasks(self) -> list[Task]:
        return [task for task in Project.allTasks() if self.owner.canSee(task)]

    def highlightOverdueTask(self) -> list[Task]:
        """Update overdue statuses and return the overdue tasks this user can see."""
        return [task for task in self.visibleTasks() if task.makeOverdue()]

    @staticmethod
    def activeTaskCount(employee: Employee) -> int:
        return sum(1 for task in Project.allTasks()
                   if task.assignee is employee and task.status != TaskStatus.DONE)

    def highlightOverload(self, employee: Employee) -> bool:
        """True if the employee already has OVERLOAD_THRESHOLD or more active tasks."""
        return self.activeTaskCount(employee) >= OVERLOAD_THRESHOLD

    def show(self) -> dict[str, list[Task]]:
        """Visible tasks grouped by who assigned them, so manager-assigned and
        team-leader-assigned tasks can be handled separately."""
        groups: dict[str, list[Task]] = {"manager": [], "teamLeader": []}
        for task in self.visibleTasks():
            task.makeOverdue()
            source = task.assignedBy or task.createdBy
            key = "manager" if isinstance(source, Manager) else "teamLeader"
            groups[key].append(task)
        return groups
