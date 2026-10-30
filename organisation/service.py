"""OrganisationService: the ONE class the GUI talks to for teams,
projects, project tasks, roles and the manager's dashboard.

Every method that changes something takes `actor` first: the email of
the logged-in user. The method checks that person is allowed to do it
and raises PermissionDenied if not. This keeps all the access rules in
one place instead of scattered through the screens.

Rules come from the client Q&A (16 Oct):
  * Three roles: Employee, Team Leader, Manager (admin Q2)
  * Roles can change in both directions (admin Q4)
  * Temporary staff lose access when they leave (admin Q3)
  * Managers create teams and appoint leaders (PM Q10)
  * One leader per team, but one person can lead many teams (PM Q9)
  * Managers and Team Leaders assign tasks in their own teams (PM Q4, Q5)
  * Employees update and complete their own tasks; high-risk tasks need
    approval (PM Q1, Q2)
  * Deadlines and priority can change (PM Q3)
  * No limit on workload, but overload is highlighted (PM Q11)
  * Overdue tasks stay open and show on dashboards (PM Q6)
  * When someone leaves a team, the leader decides what happens to their
    unfinished tasks (PM Q8)
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date

from .exceptions import InvalidAction, NotFound, PermissionDenied
from .models import (DEFAULT_PROJECT_WEEKS, FULL_WEEKLY_LOAD, OVERLOAD_THRESHOLD,
                     Employee, Permission, Priority, Project, ProjectTask, Role,
                     TaskStatus, Team, TeamSuggestion)
from .permissions import has_permission


class OrganisationService:
    def __init__(self) -> None:
        self._employees: dict[str, Employee] = {}
        self._teams: dict[str, Team] = {}
        self._projects: dict[str, Project] = {}
        self._listeners: list[Callable[[], None]] = []

    # ------------------------------------------------------------------
    # Change notifications: screens call on_change(self.refresh) so they
    # redraw whenever any data changes.
    # ------------------------------------------------------------------

    def on_change(self, callback: Callable[[], None]) -> None:
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[], None]) -> None:
        """Stop calling a screen that has closed (e.g. after logging out)."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self) -> None:
        for callback in list(self._listeners):
            try:
                callback()
            except Exception:       # a closed screen must not break the others
                pass

    # ------------------------------------------------------------------
    # People, roles and staff access
    # ------------------------------------------------------------------

    def add_employee(self, employee: Employee) -> Employee:
        """Used when loading data. One account per email (client letter)."""
        if employee.email in self._employees:
            raise InvalidAction(f"{employee.email} already has an account.")
        self._employees[employee.email] = employee
        return employee

    def get_employee(self, email: str) -> Employee:
        try:
            return self._employees[email]
        except KeyError:
            raise NotFound(f"No employee with email {email}.") from None

    def get_employee_by_login(self, login_id: int) -> Employee:
        for person in self._employees.values():
            if person.login_id == login_id:
                return person
        raise NotFound(f"No employee with login {login_id}.")

    def all_employees(self) -> list[Employee]:
        return sorted(self._employees.values(), key=lambda person: person.name)

    def can(self, actor: str, permission: Permission) -> bool:
        """Handy for the GUI: show a button only if this is True."""
        return has_permission(self.get_employee(actor), permission)

    def _require(self, actor: str, permission: Permission) -> Employee:
        person = self.get_employee(actor)
        if not has_permission(person, permission):
            raise PermissionDenied(f"Your role cannot do this ({permission.value}).")
        return person

    def _require_active(self, email: str) -> Employee:
        person = self.get_employee(email)
        if not person.is_active():
            raise InvalidAction(f"{person.name}'s access has ended.")
        return person

    def change_role(self, actor: str, email: str, new_role: Role) -> Employee:
        """Promote or demote someone, in either direction (admin Q4)."""
        self._require(actor, Permission.CHANGE_ROLES)
        if actor == email:
            raise InvalidAction("You cannot change your own role. Ask another manager.")
        person = self.get_employee(email)
        if new_role is Role.EMPLOYEE and self.teams_led_by(email):
            names = ", ".join(team.name for team in self.teams_led_by(email))
            raise InvalidAction(f"{person.name} still leads {names}. Appoint a new leader first.")
        person.role = new_role
        self._notify()
        return person

    def set_access_end(self, actor: str, email: str, end_date: date | None) -> Employee:
        """Temporary staff: access stops after end_date. None = permanent
        (admin Q3: access removed when they leave)."""
        self._require(actor, Permission.CHANGE_ROLES)
        person = self.get_employee(email)
        person.access_ends = end_date
        self._notify()
        return person

    # ------------------------------------------------------------------
    # Teams
    # ------------------------------------------------------------------

    def create_team(self, actor: str, name: str, leader_email: str,
                    member_emails: Iterable[str] = ()) -> Team:
        """Every team must have a leader from the start."""
        self._require(actor, Permission.CREATE_TEAMS)
        if not leader_email:
            raise InvalidAction("Choose a leader for the team.")
        if any(team.name.lower() == (name or "").strip().lower() for team in self._teams.values()):
            raise InvalidAction(f"A team called '{name.strip()}' already exists.")
        for email in [leader_email, *member_emails]:
            self._require_active(email)
        team = Team(name, leader_email)
        for email in member_emails:
            if email not in team.member_emails:
                team.member_emails.append(email)
        self._set_leader(team, leader_email)
        self._teams[team.id] = team
        self._notify()
        return team

    def appoint_leader(self, actor: str, team_id: str, email: str) -> Team:
        """Replace a team's leader. Each team has exactly one (Q9)."""
        self._require(actor, Permission.CREATE_TEAMS)
        self._require_active(email)
        team = self.get_team(team_id)
        self._set_leader(team, email)
        self._notify()
        return team

    def _set_leader(self, team: Team, email: str) -> None:
        """Appointing an employee as leader promotes them to Team Leader.
        (Only managers can call this, and managers may change roles.)"""
        person = self.get_employee(email)
        if person.role is Role.EMPLOYEE:
            person.role = Role.TEAM_LEADER
        team.leader_email = email
        if email not in team.member_emails:
            team.member_emails.append(email)

    def add_member(self, actor: str, team_id: str, email: str) -> Team:
        self._require(actor, Permission.MANAGE_MEMBERS)
        team = self.get_team(team_id)
        person = self._require_active(email)
        if email in team.member_emails:
            raise InvalidAction(f"{person.name} is already in {team.name}.")
        team.member_emails.append(email)
        self._notify()
        return team

    def remove_member(self, actor: str, team_id: str, email: str) -> list[ProjectTask]:
        """Remove someone and return their unfinished tasks in this team's
        projects. The tasks are NOT moved automatically: the leader decides
        case by case (Q8), using reassign_task."""
        self._require(actor, Permission.MANAGE_MEMBERS)
        team = self.get_team(team_id)
        if email == team.leader_email:
            raise InvalidAction("Appoint a new leader before removing the current one.")
        if email not in team.member_emails:
            raise InvalidAction(f"{self.get_employee(email).name} is not in {team.name}.")
        team.member_emails.remove(email)
        self._notify()
        return [task for project in self.projects_for_team(team_id) for task in project.tasks
                if task.assignee_email == email and not task.is_done()]

    def get_team(self, team_id: str) -> Team:
        try:
            return self._teams[team_id]
        except KeyError:
            raise NotFound(f"No team with ID {team_id}.") from None

    def all_teams(self) -> list[Team]:
        return sorted(self._teams.values(), key=lambda team: team.name)

    def teams_led_by(self, email: str) -> list[Team]:
        return [team for team in self.all_teams() if team.leader_email == email]

    def teams_for(self, email: str) -> list[Team]:
        """Teams this person can open: managers see all, everyone else sees
        the teams they lead or belong to."""
        if self.get_employee(email).role is Role.MANAGER:
            return self.all_teams()
        return [team for team in self.all_teams() if email in team.everyone()]

    def can_manage_team(self, actor: str, team_id: str) -> bool:
        """Managers manage every team; Team Leaders manage the teams they lead."""
        person = self.get_employee(actor)
        if person.role is Role.MANAGER:
            return True
        return (person.role is Role.TEAM_LEADER
                and self.get_team(team_id).leader_email == actor)

    def _require_team_manager(self, actor: str, team_id: str | None) -> Team:
        if team_id is None:
            raise InvalidAction("Assign this project to a team before adding tasks.")
        if not self.can_manage_team(actor, team_id):
            raise PermissionDenied("Only this team's leader or a manager can do that.")
        return self.get_team(team_id)

    # ------------------------------------------------------------------
    # Projects: create -> suggest team -> assign -> add tasks
    # ------------------------------------------------------------------

    def create_project(self, actor: str, name: str, description: str = "",
                       deadline: date | None = None) -> Project:
        self._require(actor, Permission.CREATE_PROJECTS)
        project = Project(name=name, created_by=actor, description=description.strip(),
                          deadline=deadline)
        self._projects[project.id] = project
        self._notify()
        return project

    def set_project_deadline(self, actor: str, project_id: str, deadline: date) -> Project:
        self._require(actor, Permission.CREATE_PROJECTS)
        project = self.get_project(project_id)
        late = [task.title for task in project.tasks if task.deadline and task.deadline > deadline]
        if late:
            raise InvalidAction("These tasks are due after that date: " + ", ".join(late))
        project.deadline = deadline
        self._notify()
        return project

    def team_weekly_load(self, team: Team, deadline: date | None,
                         today: date | None = None) -> tuple[float, int]:
        """How busy a team is during a new project's lifetime.

        For each person in the team, add up the remaining work
        (weighted by priority) of their unfinished tasks in ANY project that:
          * are due on or before the project deadline,
          * are overdue (still open, so still taking their time), or
          * have no deadline (we cannot tell when they end, so we assume busy).
        Divide by the number of people, then by the weeks until the deadline.

        Returns (work per person per week, number of tasks counted).
        """
        today = today or date.today()
        if deadline is None:
            weeks = DEFAULT_PROJECT_WEEKS
        else:
            weeks = max(1.0, (deadline - today).days / 7)

        people = team.everyone()
        total_work = 0.0
        tasks_counted = 0
        for project in self._projects.values():
            for task in project.tasks:
                if task.assignee_email not in people or task.is_done():
                    continue
                if deadline is None or task.deadline is None or task.deadline <= deadline:
                    total_work += task.remaining_work()
                    tasks_counted += 1
        return total_work / len(people) / weeks, tasks_counted

    def suggest_teams(self, project_id: str, today: date | None = None) -> list[TeamSuggestion]:
        """Rank teams by spare capacity before this project's deadline, best first.

        score = 100 x (1 - work per person per week / FULL_WEEKLY_LOAD), never below 0.
        So a team with nothing to do before the deadline scores 100, and a
        team at FULL_WEEKLY_LOAD or more scores 0. The manager makes the
        final choice; this only suggests.
        """
        project = self.get_project(project_id)
        due_text = project.deadline.strftime("%d %b") if project.deadline else "the project ends"
        suggestions = []
        for team in self.all_teams():
            weekly_load, counted = self.team_weekly_load(team, project.deadline, today)
            score = round(100 * max(0.0, 1 - weekly_load / FULL_WEEKLY_LOAD))
            reasons = [
                f"{counted} unfinished task{'s' if counted != 1 else ''} due before {due_text}",
                f"{weekly_load:.2f} tasks' worth of work per person per week",
            ]
            busy = [self.get_employee(email).name for email in team.everyone()
                    if self.is_overloaded(email)]
            if busy:
                reasons.append("Overloaded: " + ", ".join(busy))
            inactive = [self.get_employee(email).name for email in team.everyone()
                        if not self.get_employee(email).is_active(today)]
            if inactive:
                reasons.append("Access ended: " + ", ".join(inactive))
            suggestions.append(TeamSuggestion(team=team, score=score, tasks_counted=counted,
                                              weekly_load=round(weekly_load, 2),
                                              reasons=reasons))
        suggestions.sort(key=lambda row: (-row.score, row.weekly_load, row.team.name))
        return suggestions

    def assign_project(self, actor: str, project_id: str, team_id: str) -> Project:
        """Give a project to a team. Teams can hold many projects.
        A project can only move team before any tasks are added."""
        self._require(actor, Permission.ASSIGN_PROJECTS)
        project = self.get_project(project_id)
        self.get_team(team_id)
        if project.team_id not in (None, team_id) and project.tasks:
            raise InvalidAction("This project already has tasks, so it cannot change team.")
        project.team_id = team_id
        self._notify()
        return project

    def get_project(self, project_id: str) -> Project:
        try:
            return self._projects[project_id]
        except KeyError:
            raise NotFound(f"No project with ID {project_id}.") from None

    def all_projects(self) -> list[Project]:
        return sorted(self._projects.values(), key=lambda project: project.name)

    def projects_for_team(self, team_id: str) -> list[Project]:
        return [project for project in self.all_projects() if project.team_id == team_id]

    def unassigned_projects(self) -> list[Project]:
        return [project for project in self.all_projects() if project.team_id is None]

    def team_of(self, project: Project) -> Team | None:
        return self._teams.get(project.team_id) if project.team_id else None

    # ------------------------------------------------------------------
    # Project tasks
    # ------------------------------------------------------------------

    def _check_assignee(self, team: Team, email: str | None) -> None:
        if email is None:
            return
        person = self._require_active(email)
        if email not in team.everyone():
            raise InvalidAction(f"{person.name} is not in {team.name}.")

    @staticmethod
    def _check_deadline(project: Project, deadline: date | None) -> None:
        if deadline and project.deadline and deadline > project.deadline:
            raise InvalidAction(
                f"The task deadline cannot be after the project deadline "
                f"({project.deadline.strftime('%d %b %Y')}).")

    def add_task(self, actor: str, project_id: str, title: str,
                 assignee_email: str | None = None, description: str = "",
                 deadline: date | None = None, priority: Priority = Priority.MEDIUM,
                 high_risk: bool = False) -> ProjectTask:
        project = self.get_project(project_id)
        team = self._require_team_manager(actor, project.team_id)
        self._check_assignee(team, assignee_email)
        self._check_deadline(project, deadline)
        task = ProjectTask(title=title, project_id=project_id, created_by=actor,
                           assignee_email=assignee_email, description=description.strip(),
                           deadline=deadline, priority=priority, high_risk=high_risk)
        project.tasks.append(task)
        self._notify()
        return task

    def edit_task(self, actor: str, project_id: str, task_id: str, *,
                  title: str | None = None, description: str | None = None,
                  deadline: date | None = None, priority: Priority | None = None,
                  high_risk: bool | None = None) -> ProjectTask:
        """Change details. Deadlines and priority can change (PM Q3)."""
        project = self.get_project(project_id)
        self._require_team_manager(actor, project.team_id)
        task = project.get_task(task_id)
        if title is not None and not title.strip():
            raise InvalidAction("Task title cannot be blank.")
        self._check_deadline(project, deadline)
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()
        if deadline is not None:
            task.deadline = deadline
        if priority is not None:
            task.priority = priority
        if high_risk is not None:
            task.high_risk = high_risk
        self._notify()
        return task

    def reassign_task(self, actor: str, project_id: str, task_id: str,
                      new_assignee: str) -> ProjectTask:
        project = self.get_project(project_id)
        team = self._require_team_manager(actor, project.team_id)
        self._check_assignee(team, new_assignee)
        task = project.get_task(task_id)
        task.assignee_email = new_assignee
        self._notify()
        return task

    def _require_assignee_or_manager(self, actor: str, project: Project,
                                     task: ProjectTask) -> bool:
        """Returns True if the actor manages the team (not just the assignee)."""
        manages = project.team_id is not None and self.can_manage_team(actor, project.team_id)
        if not manages and task.assignee_email != actor:
            raise PermissionDenied("You can only update tasks assigned to you.")
        return manages

    def update_progress(self, actor: str, project_id: str, task_id: str,
                        progress: int) -> ProjectTask:
        """Employees update their own tasks (PM Q1)."""
        project = self.get_project(project_id)
        task = project.get_task(task_id)
        self._require_assignee_or_manager(actor, project, task)
        if task.is_done():
            raise InvalidAction("This task is complete. Reopen it first.")
        if not 0 <= progress <= 100:
            raise InvalidAction("Progress must be between 0 and 100.")
        task.progress = progress
        if task.status is not TaskStatus.PENDING_APPROVAL:
            task.status = TaskStatus.IN_PROGRESS if progress > 0 else TaskStatus.NOT_STARTED
        self._notify()
        return task

    def complete_task(self, actor: str, project_id: str, task_id: str) -> ProjectTask:
        """Routine tasks: the assignee finishes them. High-risk tasks go to
        Pending Approval until the leader or a manager completes them (PM Q2)."""
        project = self.get_project(project_id)
        task = project.get_task(task_id)
        manages = self._require_assignee_or_manager(actor, project, task)
        can_approve = manages and self.can(actor, Permission.APPROVE_TASKS)
        task.progress = 100
        if task.high_risk and not can_approve:
            task.status = TaskStatus.PENDING_APPROVAL
        else:
            task.status = TaskStatus.DONE
        self._notify()
        return task

    def reopen_task(self, actor: str, project_id: str, task_id: str) -> ProjectTask:
        """Leaders and managers can review and reopen tasks (PM Q2)."""
        project = self.get_project(project_id)
        self._require_team_manager(actor, project.team_id)
        task = project.get_task(task_id)
        task.status = TaskStatus.IN_PROGRESS
        task.progress = min(task.progress, 90)
        self._notify()
        return task

    def delete_task(self, actor: str, project_id: str, task_id: str) -> None:
        """Our decision for PM Q5: only leaders/managers delete, and the GUI
        asks 'Are you sure?' first."""
        project = self.get_project(project_id)
        self._require_team_manager(actor, project.team_id)
        project.tasks.remove(project.get_task(task_id))
        self._notify()

    def tasks_for_employee(self, email: str) -> list[tuple[Project, ProjectTask]]:
        """Every project task assigned to one person ('My Tasks'), unfinished
        first, then soonest deadline first."""
        rows = [(project, task) for project in self.all_projects()
                for task in project.tasks if task.assignee_email == email]
        rows.sort(key=lambda row: (row[1].is_done(), row[1].deadline or date.max))
        return rows

    # ------------------------------------------------------------------
    # Workload and dashboard
    # ------------------------------------------------------------------

    def active_task_count(self, email: str) -> int:
        """Unfinished tasks assigned to this person, across every project.
        This plain count is what the dashboard shows (client letter)."""
        return sum(1 for project in self._projects.values() for task in project.tasks
                   if task.assignee_email == email and not task.is_done())

    def active_project_count(self, email: str) -> int:
        """Projects where this person has at least one unfinished task."""
        return sum(1 for project in self._projects.values()
                   if any(task.assignee_email == email and not task.is_done()
                          for task in project.tasks))

    def is_overloaded(self, email: str) -> bool:
        return self.active_task_count(email) >= OVERLOAD_THRESHOLD

    def dashboard_teams(self, actor: str) -> list[Team]:
        """Managers see every team; Team Leaders see the teams they lead."""
        self._require(actor, Permission.VIEW_DASHBOARD)
        return [team for team in self.all_teams() if self.can_manage_team(actor, team.id)]

    def dashboard_projects(self, actor: str) -> list[Project]:
        team_ids = {team.id for team in self.dashboard_teams(actor)}
        projects = [project for project in self.all_projects() if project.team_id in team_ids]
        if self.get_employee(actor).role is Role.MANAGER:
            projects += self.unassigned_projects()
        return projects

    def dashboard_people(self, actor: str) -> list[Employee]:
        """Only people in the actor's own teams, so the workload view cannot
        be used to look up anyone in the company (client letter: data
        protection)."""
        emails = {email for team in self.dashboard_teams(actor) for email in team.everyone()}
        return [person for person in self.all_employees() if person.email in emails]

    def overdue_tasks(self, actor: str, today: date | None = None
                      ) -> list[tuple[Project, ProjectTask]]:
        return [(project, task) for project in self.dashboard_projects(actor)
                for task in project.overdue_tasks(today)]
