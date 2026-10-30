# pages/manager_dashboard.py
"""Dashboard page for Managers (every team) and Team Leaders (the teams
they lead). Answers the client letter: track project progress, see how
many tasks each person is working on, and spot overdue work.

Team Leaders only see people in their own teams (data protection).
"""

from datetime import date

import customtkinter as ctk

from organisation import OVERLOAD_THRESHOLD, organisation
from pages.org_common import OrgPage, clear, name_of, show_date


class DashboardPage(OrgPage):
    def __init__(self, master, app):
        super().__init__(master, app)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        title = "Manager Dashboard" if self.user.role.value == "Manager" else "Team Leader Dashboard"
        ctk.CTkLabel(header_frame, text=title,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", anchor="w")
        ctk.CTkLabel(header_frame, text=f"Logged in: {self.user.name} ({self.user.role.value})",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="right", padx=6)

        self.summary = ctk.CTkFrame(self, fg_color="transparent")
        self.summary.pack(fill="x", pady=(0, 10))
        self.body = ctk.CTkScrollableFrame(self)
        self.body.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        teams = organisation.dashboard_teams(self.email)
        projects = organisation.dashboard_projects(self.email)
        people = organisation.dashboard_people(self.email)
        overdue = organisation.overdue_tasks(self.email)
        overloaded = [person for person in people if organisation.is_overloaded(person.email)]

        # ----- summary tiles -----
        clear(self.summary)
        for value, label in [(len(teams), "Teams"), (len(projects), "Projects"),
                             (len(overdue), "Overdue Tasks"), (len(overloaded), "Overloaded People")]:
            tile = ctk.CTkFrame(self.summary)
            tile.pack(side="left", expand=True, fill="x", padx=2)
            ctk.CTkLabel(tile, text=str(value), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(8, 0))
            ctk.CTkLabel(tile, text=label, font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(0, 8))

        clear(self.body)

        # ----- project progress -----
        self.section("Project Progress")
        for project in projects:
            team = organisation.team_of(project)
            late = len(project.overdue_tasks())
            card = ctk.CTkFrame(self.body, border_width=2 if late else 1)
            card.pack(fill="x", pady=6, padx=4)
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(8, 2))
            prefix = "[OVERDUE TASKS] " if late else ""
            ctk.CTkLabel(top_row, text=f"{prefix}{project.name}",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            done = sum(1 for task in project.tasks if task.is_done())
            ctk.CTkLabel(top_row, font=ctk.CTkFont(size=12, weight="bold"), text=(
                f"Team: {team.name if team else 'NOT ASSIGNED'}  |  Due: {show_date(project.deadline)}  |  "
                f"Tasks Done: {done}/{len(project.tasks)}  |  Overdue: {late}  |  "
                f"Progress: {project.progress()}%")).pack(side="right")
            bar = ctk.CTkProgressBar(card)
            bar.set(project.progress() / 100)
            bar.pack(fill="x", padx=12, pady=(4, 10))

        # ----- workload (client letter: how many tasks each person has) -----
        self.section(f"Workload  (overloaded = {OVERLOAD_THRESHOLD} or more unfinished tasks)")
        table = ctk.CTkFrame(self.body, border_width=1)
        table.pack(fill="x", pady=6, padx=4)
        headers = ["Name", "Role", "Teams", "Unfinished Tasks", "Projects", "Status"]
        for column, text in enumerate(headers):
            ctk.CTkLabel(table, text=text, font=ctk.CTkFont(size=13, weight="bold")).grid(
                row=0, column=column, sticky="w", padx=12, pady=(8, 4))
        for row_number, person in enumerate(people, start=1):
            team_names = ", ".join(team.name for team in organisation.all_teams()
                                   if person.email in team.everyone())
            status = []
            if organisation.is_overloaded(person.email):
                status.append("[OVERLOADED]")
            if person.access_ends:
                status.append(f"Access ends {show_date(person.access_ends)}"
                              if person.is_active() else "[ACCESS ENDED]")
            values = [person.name, person.role.value, team_names,
                      str(organisation.active_task_count(person.email)),
                      str(organisation.active_project_count(person.email)),
                      "  ".join(status) or "OK"]
            for column, text in enumerate(values):
                ctk.CTkLabel(table, text=text, font=ctk.CTkFont(size=12)).grid(
                    row=row_number, column=column, sticky="w", padx=12, pady=2)
        ctk.CTkLabel(table, text="").grid(row=len(people) + 1, column=0, pady=2)

        # ----- overdue tasks -----
        self.section("Overdue Tasks")
        if not overdue:
            card = ctk.CTkFrame(self.body, border_width=1)
            card.pack(fill="x", pady=6, padx=4)
            ctk.CTkLabel(card, text="Nothing overdue.").pack(anchor="w", padx=12, pady=10)
        today = date.today()
        for project, task in sorted(overdue, key=lambda pair: pair[1].deadline):
            days = (today - task.deadline).days
            card = ctk.CTkFrame(self.body, border_width=2)
            card.pack(fill="x", pady=6, padx=4)
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=8)
            ctk.CTkLabel(top_row, text=f"[OVERDUE {days} DAY{'S' if days != 1 else ''}] {task.title}",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            ctk.CTkLabel(top_row, font=ctk.CTkFont(size=12, weight="bold"), text=(
                f"Project: {project.name}  |  Assigned to: {name_of(task.assignee_email)}  |  "
                f"Priority: {task.priority.value}  |  Due: {show_date(task.deadline)} "
                f"({task.progress}%)")).pack(side="right")

        self.redraw_theme()

    def section(self, title):
        """A section heading, in a card like everything else in the list."""
        holder = ctk.CTkFrame(self.body, border_width=0)
        holder.pack(fill="x", padx=4, pady=(12, 0))
        ctk.CTkLabel(holder, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w", padx=8, pady=6)
