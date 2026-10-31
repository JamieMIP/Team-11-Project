# pages/new_project.py
"""New Project page (Managers only): the client flow in three steps.

  Step 1  Create the project (name, description, deadline)
          ...or pick a project that has not been given to a team yet.
  Step 2  See every team ranked by spare capacity before the deadline,
          with the reasons, and assign the project to one of them.
          Changing the deadline here re-ranks the teams.
  Step 3  Add tasks. Overloaded people are marked in the dropdown and a
          warning appears if a new task overloads someone.
"""

import customtkinter as ctk

from organisation import Priority, organisation
from pages.org_common import (PRIORITY_NAMES, OrgPage, clear, name_of, parse_date,
                              people_menu_values, show_date)

NEW_PROJECT = "+ New project"
STEP_NAMES = ["1. Create", "2. Choose Team", "3. Add Tasks"]


class NewProjectPage(OrgPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.project_id = None
        self.step = 1

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="New Project",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", anchor="w")
        ctk.CTkLabel(header_frame, text=f"Logged in: {self.user.name} ({self.user.role.value})",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="right", padx=6)

        # Step indicator, styled like the progress frame on the team page
        steps_frame = ctk.CTkFrame(self)
        steps_frame.pack(fill="x", pady=(0, 10), padx=2)
        self.steps_label = ctk.CTkLabel(steps_frame, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.steps_label.pack(anchor="w", padx=12, pady=8)

        self.add_message_label()

        self.body = ctk.CTkScrollableFrame(self)
        self.body.pack(fill="both", expand=True)
        self.refresh()

    def on_show(self):
        if self.project_id is None:
            self.refresh()

    def refresh(self):
        """Redraw whichever step we are on."""
        [self.draw_step_1, self.draw_step_2, self.draw_step_3][self.step - 1]()

    def start_card(self, title):
        """Clear the page and return a card to build this step in."""
        self.steps_label.configure(text="   >   ".join(
            f"[{name}]" if number == self.step else name
            for number, name in enumerate(STEP_NAMES, start=1)))
        clear(self.body)
        card = ctk.CTkFrame(self.body, border_width=1)
        card.pack(fill="x", pady=6, padx=4)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(8, 6))
        return card

    # ------------------------------------------------------------------
    # Step 1: create, or continue an unassigned project
    # ------------------------------------------------------------------

    def draw_step_1(self):
        card = self.start_card("Project Details")
        unassigned = organisation.unassigned_projects()
        self.unassigned_lookup = {project.name: project.id for project in unassigned}
        self.start_menu = None
        if unassigned:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=(0, 6))
            ctk.CTkLabel(row, text="Start from:").pack(side="left")
            self.start_menu = ctk.CTkOptionMenu(row, width=300,
                                                values=[NEW_PROJECT, *self.unassigned_lookup])
            self.start_menu.pack(side="left", padx=8)
            ctk.CTkLabel(row, text="(projects waiting for a team are listed here)",
                         font=ctk.CTkFont(size=12)).pack(side="left")

        self.name_entry = ctk.CTkEntry(card, placeholder_text="Project name...")
        self.name_entry.pack(fill="x", padx=12, pady=4)
        self.description_entry = ctk.CTkEntry(card, placeholder_text="Short description (optional)...")
        self.description_entry.pack(fill="x", padx=12, pady=4)
        self.deadline_entry = ctk.CTkEntry(card, placeholder_text="Deadline (YYYY-MM-DD)")
        self.deadline_entry.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(card, text="Next: Choose Team", width=150,
                      command=self.finish_step_1).pack(anchor="e", padx=12, pady=(6, 10))
        self.redraw_theme()

    def finish_step_1(self):
        if self.start_menu is not None and self.start_menu.get() != NEW_PROJECT:
            self.project_id = self.unassigned_lookup[self.start_menu.get()]
            self.go_to(2)
            return
        try:
            deadline = parse_date(self.deadline_entry.get())
        except ValueError as error:
            self.show_message(str(error))
            return
        if deadline is None:
            self.show_message("Please give the project a deadline.")
            return
        project = self.run_service(organisation.create_project, self.name_entry.get(),
                                   self.description_entry.get(), deadline)
        if project is not None:
            self.project_id = project.id
            self.go_to(2)

    def go_to(self, step):
        self.step = step
        self.refresh()

    # ------------------------------------------------------------------
    # Step 2: suggested teams, ranked by spare capacity
    # ------------------------------------------------------------------

    def draw_step_2(self):
        project = organisation.get_project(self.project_id)
        card = self.start_card(f"Choose a Team for '{project.name}'")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 4))
        ctk.CTkLabel(row, text="Project deadline:").pack(side="left")
        self.step2_deadline = ctk.CTkEntry(row, width=130)
        self.step2_deadline.insert(0, show_date(project.deadline) if project.deadline else "")
        self.step2_deadline.pack(side="left", padx=6)
        ctk.CTkButton(row, text="Update Ranking", width=130,
                      command=self.change_deadline).pack(side="left")
        ctk.CTkLabel(card, anchor="w", justify="left", wraplength=850, font=ctk.CTkFont(size=12),
                     text="Teams are ranked by spare capacity before the deadline: the work each "
                          "person still has due by then (weighted by priority and how far through "
                          "it they are), spread over the weeks available. 100 = completely free. "
                          "You make the final choice.").pack(fill="x", padx=12, pady=(0, 10))

        for rank, suggestion in enumerate(organisation.suggest_teams(self.project_id), start=1):
            team = suggestion.team
            team_card = ctk.CTkFrame(self.body, border_width=2 if rank == 1 else 1)
            team_card.pack(fill="x", pady=6, padx=4)
            top_row = ctk.CTkFrame(team_card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(8, 2))
            best = "  [SUGGESTED]" if rank == 1 else ""
            ctk.CTkLabel(top_row, text=f"{rank}. {team.name}{best}",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            ctk.CTkLabel(top_row, text=f"Capacity Score: {suggestion.score}/100",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")
            bar = ctk.CTkProgressBar(team_card)
            bar.set(suggestion.score / 100)
            bar.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(team_card, anchor="w", justify="left", font=ctk.CTkFont(size=12),
                         text="  |  ".join(suggestion.reasons)).pack(fill="x", padx=12)
            bottom_row = ctk.CTkFrame(team_card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=12, pady=(2, 8))
            people = ", ".join(name_of(email) for email in team.everyone())
            ctk.CTkLabel(bottom_row, font=ctk.CTkFont(size=12),
                         text=f"Team Leader: {name_of(team.leader_email)}  |  People: {people}"
                         ).pack(side="left")
            ctk.CTkButton(bottom_row, text=f"Assign to {team.name}", width=140, height=28,
                          command=lambda team_id=team.id: self.assign(team_id)).pack(side="right")

        ctk.CTkButton(self.body, text="Back", width=90, command=self.back_to_start).pack(
            anchor="w", padx=4, pady=10)
        self.redraw_theme()

    def back_to_start(self):
        self.project_id = None
        self.go_to(1)

    def change_deadline(self):
        try:
            deadline = parse_date(self.step2_deadline.get())
        except ValueError as error:
            self.show_message(str(error))
            return
        if deadline is None:
            self.show_message("Please give the project a deadline.")
            return
        self.run_service(organisation.set_project_deadline, self.project_id, deadline)

    def assign(self, team_id):
        self.step = 3            # so run_service redraws step 3 if it works
        if self.run_service(organisation.assign_project, self.project_id, team_id) is None:
            self.step = 2

    # ------------------------------------------------------------------
    # Step 3: add tasks
    # ------------------------------------------------------------------

    def draw_step_3(self):
        project = organisation.get_project(self.project_id)
        team = organisation.team_of(project)
        card = self.start_card(f"Add Tasks to '{project.name}' ({team.name})")
        ctk.CTkLabel(card, anchor="w", font=ctk.CTkFont(size=12),
                     text=f"Project due: {show_date(project.deadline)}. Task deadlines must be on "
                          f"or before this date.").pack(fill="x", padx=12, pady=(0, 6))

        bar = ctk.CTkFrame(card, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=(0, 10))
        self.task_entry = ctk.CTkEntry(bar, placeholder_text="New task title...")
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        active = [email for email in team.everyone() if organisation.get_employee(email).is_active()]
        labels, self.assignee_lookup = people_menu_values(active)
        self.assignee_menu = ctk.CTkOptionMenu(bar, values=labels, width=165)
        self.assignee_menu.pack(side="left", padx=4)
        self.task_deadline = ctk.CTkEntry(bar, placeholder_text="Due (YYYY-MM-DD)", width=135)
        self.task_deadline.pack(side="left", padx=4)
        self.task_priority = ctk.CTkOptionMenu(bar, values=PRIORITY_NAMES, width=110)
        self.task_priority.set("Medium")
        self.task_priority.pack(side="left", padx=4)
        self.risk_check = ctk.CTkCheckBox(bar, text="High Risk", width=90)
        self.risk_check.pack(side="left", padx=6)
        ctk.CTkButton(bar, text="Add Task", width=90, command=self.add_task).pack(side="left")

        for task in project.tasks:
            task_card = ctk.CTkFrame(self.body, border_width=1)
            task_card.pack(fill="x", pady=6, padx=4)
            row = ctk.CTkFrame(task_card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=8)
            risk = " [HIGH RISK]" if task.high_risk else ""
            ctk.CTkLabel(row, text=f"{task.title}{risk}",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            ctk.CTkLabel(row, font=ctk.CTkFont(size=12, weight="bold"),
                         text=f"Assigned to: {name_of(task.assignee_email)}  |  "
                              f"Priority: {task.priority.value}  |  Due: {show_date(task.deadline)}"
                         ).pack(side="right")

        ctk.CTkButton(self.body, text="Finish", width=90, command=self.finish).pack(
            anchor="e", padx=4, pady=10)
        self.redraw_theme()

    def add_task(self):
        try:
            deadline = parse_date(self.task_deadline.get())
        except ValueError as error:
            self.show_message(str(error))
            return
        task = self.run_service(
            organisation.add_task, self.project_id, self.task_entry.get(),
            self.assignee_lookup.get(self.assignee_menu.get()), "", deadline,
            Priority(self.task_priority.get()), bool(self.risk_check.get()))
        if task is not None and organisation.is_overloaded(task.assignee_email):
            self.show_message(f"Task added. Warning: {name_of(task.assignee_email)} now has "
                              f"{organisation.active_task_count(task.assignee_email)} "
                              f"unfinished tasks (overloaded).")

    def finish(self):
        project = organisation.get_project(self.project_id)
        team = organisation.team_of(project)
        self.project_id = None
        self.go_to(1)
        self.show_message(f"'{project.name}' is set up. Open {team.name} under "
                          f"Team To-do List to manage it.")
