# pages/team_projects.py
"""Team page: one team, ALL of its projects, and each project's tasks.

Same layout as the original TeamListPage (header, progress bar, task
cards, add-task bar), plus a project picker because a team can now have
several projects. Data and rules come from the organisation service.

What you can do depends on your role:
  * Employee:     +25% Progress / Mark Complete on YOUR OWN tasks
                  (high-risk tasks: Request Approval)
  * Team Leader:  for teams you lead, also add, edit, reassign, delete,
                  approve and reopen tasks
  * Manager:      the same as a leader, for every team
"""

import customtkinter as ctk

from organisation import Priority, TaskStatus, organisation
from pages.org_common import (PRIORITY_NAMES, OrgPage, ask_yes_no, clear, name_of,
                              parse_date, people_menu_values, show_date)


class TeamProjectsPage(OrgPage):
    def __init__(self, master, app, team_key):
        super().__init__(master, app)
        self.team_key = team_key                  # the team's name, as in the sidebar
        self.selected_project_id = None
        self.project_lookup = {}
        self.assignee_lookup = {}

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 4))
        self.title_label = ctk.CTkLabel(header_frame, text="",
                                        font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(side="left", anchor="w")
        self.user_badge = ctk.CTkLabel(
            header_frame, text=f"Logged in: {self.user.name} ({self.user.role.value})",
            font=ctk.CTkFont(size=13, weight="bold"))
        self.user_badge.pack(side="right", anchor="e", padx=6)

        # Project picker (a team can have several projects)
        picker_frame = ctk.CTkFrame(self, fg_color="transparent")
        picker_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(picker_frame, text="Project:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        self.project_menu = ctk.CTkOptionMenu(picker_frame, values=["-"], width=300,
                                              command=self.choose_project)
        self.project_menu.pack(side="left", padx=6)
        self.members_label = ctk.CTkLabel(picker_frame, text="", font=ctk.CTkFont(size=12))
        self.members_label.pack(side="right", padx=6)

        # Project Progress Bar
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", pady=(0, 10), padx=2)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="",
                                           font=ctk.CTkFont(size=13, weight="bold"))
        self.progress_label.pack(anchor="w", padx=12, pady=(8, 2))
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=12, pady=(0, 10))

        self.add_message_label()

        # Scrollable Task List
        self.task_area = ctk.CTkScrollableFrame(self)
        self.task_area.pack(fill="both", expand=True)

        # Task Creation Bar (shown only to a Manager or this team's Leader)
        self.bar = ctk.CTkFrame(self, fg_color="transparent")
        self.entry = ctk.CTkEntry(self.bar, placeholder_text="New task title...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.assignee_menu = ctk.CTkOptionMenu(self.bar, values=["-"], width=165)
        self.assignee_menu.pack(side="left", padx=4)
        self.deadline_entry = ctk.CTkEntry(self.bar, placeholder_text="Due (YYYY-MM-DD)", width=135)
        self.deadline_entry.pack(side="left", padx=4)
        self.priority_menu = ctk.CTkOptionMenu(self.bar, values=PRIORITY_NAMES, width=110)
        self.priority_menu.set("Medium")
        self.priority_menu.pack(side="left", padx=4)
        self.risk_check = ctk.CTkCheckBox(self.bar, text="High Risk", width=90)
        self.risk_check.pack(side="left", padx=6)
        self.add_btn = ctk.CTkButton(self.bar, text="Add Task", width=90, command=self.add_task)
        self.add_btn.pack(side="left", padx=(6, 0))

        self.refresh()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def team(self):
        return next(team for team in organisation.all_teams() if team.name == self.team_key)

    def refresh(self):
        team = self.team()
        can_manage = organisation.can_manage_team(self.email, team.id)

        members = [name_of(email) for email in team.member_emails if email != team.leader_email]
        self.members_label.configure(text=f"Members: {', '.join(members) or 'none yet'}")

        projects = organisation.projects_for_team(team.id)
        self.project_lookup = {project.name: project.id for project in projects}
        if self.selected_project_id not in self.project_lookup.values():
            self.selected_project_id = projects[0].id if projects else None
        self.project_menu.configure(values=list(self.project_lookup) or ["No projects yet"])

        for widget in self.task_area.winfo_children():
            widget.destroy()

        if self.selected_project_id is None:
            self.title_label.configure(text=team.name)
            self.project_menu.set("No projects yet")
            self.progress_label.configure(
                text=f"No projects yet  |  Team Leader: {name_of(team.leader_email)}")
            self.progress_bar.set(0)
            self.bar.pack_forget()
            self.redraw_theme()
            return

        project = organisation.get_project(self.selected_project_id)
        self.title_label.configure(text=f"{team.name}: {project.name}")
        self.project_menu.set(project.name)
        pct = project.progress()
        self.progress_label.configure(
            text=f"Overall Project Progress: {pct}%  |  Due: {show_date(project.deadline)}  |  "
                 f"Team Leader: {name_of(team.leader_email)}")
        self.progress_bar.set(pct / 100.0)

        if can_manage:
            active = [email for email in team.everyone()
                      if organisation.get_employee(email).is_active()]
            chosen = self.assignee_lookup.get(self.assignee_menu.get())
            labels, self.assignee_lookup = people_menu_values(active)
            self.assignee_menu.configure(values=labels)
            # keep the same person selected, even if "(overloaded)" was added to their name
            keep = next((label for label, email in self.assignee_lookup.items()
                         if email == chosen), labels[-1])
            self.assignee_menu.set(keep)
            self.bar.pack(fill="x", pady=(10, 0))
        else:
            self.bar.pack_forget()

        if not project.tasks:
            card = ctk.CTkFrame(self.task_area, border_width=1)
            card.pack(fill="x", pady=6, padx=4)
            ctk.CTkLabel(card, text="No tasks yet.").pack(pady=12)
        for task in project.tasks:
            self.draw_task(project, task, can_manage)
        self.redraw_theme()

    def draw_task(self, project, task, can_manage):
        overdue = task.is_overdue()
        card = ctk.CTkFrame(self.task_area, border_width=2 if overdue else 1)
        card.pack(fill="x", pady=6, padx=4)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(8, 2))
        status_prefix = "[OVERDUE] " if overdue else ""
        risk_badge = " [HIGH RISK]" if task.high_risk else ""
        ctk.CTkLabel(top_row, text=f"{status_prefix}{task.title}{risk_badge}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", anchor="w")
        meta_text = (f"Priority: {task.priority.value}  |  Due: {show_date(task.deadline)}  |  "
                     f"Status: {task.status.value} ({task.progress}%)")
        ctk.CTkLabel(top_row, text=meta_text,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")

        if task.description:
            ctk.CTkLabel(card, text=task.description, wraplength=750,
                         justify="left").pack(anchor="w", padx=12, pady=(2, 6))

        bottom_row = ctk.CTkFrame(card, fg_color="transparent")
        bottom_row.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(bottom_row, font=ctk.CTkFont(size=12),
                     text=f"Assigned to: {name_of(task.assignee_email)} "
                          f"({task.assignee_email or '-'})").pack(side="left")

        def button(text, command, width):
            ctk.CTkButton(bottom_row, text=text, width=width, height=28,
                          command=command).pack(side="right", padx=4)

        p, t = project.id, task.id
        is_assignee = task.assignee_email == self.email

        if can_manage:
            button("Delete", lambda: self.delete_task(p, t), 70)
            button("Edit", lambda: EditTaskWindow(self, p, t), 60)

        if task.is_done():
            if can_manage:
                button("Reopen", lambda: self.run_service(organisation.reopen_task, p, t), 90)
            return

        if is_assignee or can_manage:
            if task.status is TaskStatus.PENDING_APPROVAL:
                if can_manage:
                    button("Approve & Complete",
                           lambda: self.run_service(organisation.complete_task, p, t), 140)
            else:
                label = "Request Approval" if task.high_risk and not can_manage else "Mark Complete"
                button(label, lambda: self.run_service(organisation.complete_task, p, t), 140)
                if task.progress < 100:
                    button("+25% Progress", lambda: self.run_service(
                        organisation.update_progress, p, t, min(100, task.progress + 25)), 110)

    # ------------------------------------------------------------------
    # Button actions
    # ------------------------------------------------------------------

    def choose_project(self, name):
        self.selected_project_id = self.project_lookup.get(name)
        self.show_message("")
        self.refresh()

    def add_task(self):
        try:
            deadline = parse_date(self.deadline_entry.get())
        except ValueError as error:
            self.show_message(str(error))
            return
        task = self.run_service(
            organisation.add_task, self.selected_project_id, self.entry.get(),
            self.assignee_lookup.get(self.assignee_menu.get()), "", deadline,
            Priority(self.priority_menu.get()), bool(self.risk_check.get()))
        if task is None:
            return
        self.entry.delete(0, "end")
        self.deadline_entry.delete(0, "end")
        self.risk_check.deselect()
        if organisation.is_overloaded(task.assignee_email):
            self.show_message(f"Task added. Warning: {name_of(task.assignee_email)} now has "
                              f"{organisation.active_task_count(task.assignee_email)} "
                              f"unfinished tasks (overloaded).")

    def delete_task(self, project_id, task_id):
        if ask_yes_no(self, "Delete this task? This cannot be undone."):
            self.run_service(organisation.delete_task, project_id, task_id)


class EditTaskWindow(ctk.CTkToplevel):
    """Pop-up for a leader/manager to change the title, deadline, priority,
    risk or assignee of a task (Q&A PM Q3, Q5)."""

    def __init__(self, page, project_id, task_id):
        super().__init__(page)
        self.page = page
        self.project_id = project_id
        self.task = organisation.get_project(project_id).get_task(task_id)
        self.title(f"Edit: {self.task.title}")
        self.geometry("380x400")
        self.transient(page.winfo_toplevel())
        self.after(100, self.lift)
        self.after(100, self.focus)

        team = organisation.team_of(organisation.get_project(project_id))
        active = [email for email in team.everyone()
                  if organisation.get_employee(email).is_active()]
        labels, self.lookup = people_menu_values(active)

        def row(text):
            ctk.CTkLabel(self, text=text, anchor="w").pack(fill="x", padx=20, pady=(8, 0))

        row("Title")
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.insert(0, self.task.title)
        self.title_entry.pack(fill="x", padx=20)
        row("Deadline (YYYY-MM-DD)")
        self.deadline_entry = ctk.CTkEntry(self)
        if self.task.deadline:
            self.deadline_entry.insert(0, self.task.deadline.isoformat())
        self.deadline_entry.pack(fill="x", padx=20)
        row("Priority")
        self.priority_menu = ctk.CTkOptionMenu(self, values=PRIORITY_NAMES)
        self.priority_menu.set(self.task.priority.value)
        self.priority_menu.pack(fill="x", padx=20)
        row("Assigned to")
        self.assignee_menu = ctk.CTkOptionMenu(self, values=labels)
        self.assignee_menu.set(next((label for label, email in self.lookup.items()
                                     if email == self.task.assignee_email), labels[0]))
        self.assignee_menu.pack(fill="x", padx=20)
        self.risk_check = ctk.CTkCheckBox(self, text="High Risk (needs approval to complete)")
        if self.task.high_risk:
            self.risk_check.select()
        self.risk_check.pack(anchor="w", padx=20, pady=10)
        self.message_label = ctk.CTkLabel(self, text="", wraplength=340)
        self.message_label.pack()
        ctk.CTkButton(self, text="Save", command=self.save).pack(pady=6)

    def save(self):
        try:
            deadline = parse_date(self.deadline_entry.get())
            organisation.edit_task(self.page.email, self.project_id, self.task.id,
                                   title=self.title_entry.get(), deadline=deadline,
                                   priority=Priority(self.priority_menu.get()),
                                   high_risk=bool(self.risk_check.get()))
            new_assignee = self.lookup[self.assignee_menu.get()]
            if new_assignee != self.task.assignee_email:
                organisation.reassign_task(self.page.email, self.project_id,
                                           self.task.id, new_assignee)
        except Exception as error:          # OrgError or a bad date
            self.message_label.configure(text=f"Couldn't do that: {error}")
            return
        self.page.refresh()
        self.destroy()
