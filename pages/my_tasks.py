# pages/my_tasks.py
"""My Tasks page (everyone): every project task assigned to the logged-in
user, across ALL their teams and projects, unfinished and soonest first.
This is the demo plan's "showcase all of the tasks one person has".

Employees can update progress and complete their own tasks here; high-
risk tasks go to the Team Leader for approval (Q&A PM Q1, Q2).
"""

import customtkinter as ctk

from organisation import TaskStatus, organisation
from pages.org_common import OrgPage, show_date


class MyTasksPage(OrgPage):
    def __init__(self, master, app):
        super().__init__(master, app)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="My Tasks",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", anchor="w")
        ctk.CTkLabel(header_frame, text=f"Logged in: {self.user.name} ({self.user.role.value})",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="right", padx=6)

        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.pack(fill="x", pady=(0, 10), padx=2)
        self.summary_label = ctk.CTkLabel(self.summary_frame, text="",
                                          font=ctk.CTkFont(size=13, weight="bold"))
        self.summary_label.pack(anchor="w", padx=12, pady=10)

        self.add_message_label()
        self.task_area = ctk.CTkScrollableFrame(self)
        self.task_area.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        rows = organisation.tasks_for_employee(self.email)
        unfinished = organisation.active_task_count(self.email)
        overdue = sum(1 for _, task in rows if task.is_overdue())
        warning = "  |  You are overloaded: talk to your Team Leader" \
            if organisation.is_overloaded(self.email) else ""
        self.summary_label.configure(
            text=f"Unfinished Tasks: {unfinished}  |  Projects: "
                 f"{organisation.active_project_count(self.email)}  |  Overdue: {overdue}{warning}")

        for widget in self.task_area.winfo_children():
            widget.destroy()
        if not rows:
            card = ctk.CTkFrame(self.task_area, border_width=1)
            card.pack(fill="x", pady=6, padx=4)
            ctk.CTkLabel(card, text="No project tasks are assigned to you.").pack(pady=12)

        for project, task in rows:
            team = organisation.team_of(project)
            overdue_task = task.is_overdue()
            card = ctk.CTkFrame(self.task_area, border_width=2 if overdue_task else 1)
            card.pack(fill="x", pady=6, padx=4)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(8, 2))
            prefix = "[OVERDUE] " if overdue_task else ""
            risk = " [HIGH RISK]" if task.high_risk else ""
            ctk.CTkLabel(top_row, text=f"{prefix}{task.title}{risk}",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            ctk.CTkLabel(top_row, font=ctk.CTkFont(size=12, weight="bold"), text=(
                f"Priority: {task.priority.value}  |  Due: {show_date(task.deadline)}  |  "
                f"Status: {task.status.value} ({task.progress}%)")).pack(side="right")

            if task.description:
                ctk.CTkLabel(card, text=task.description, wraplength=750,
                             justify="left").pack(anchor="w", padx=12, pady=(2, 6))

            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=12, pady=(0, 8))
            ctk.CTkLabel(bottom_row, font=ctk.CTkFont(size=12),
                         text=f"Team: {team.name if team else '-'}  |  Project: {project.name}"
                         ).pack(side="left")

            if task.is_done() or task.status is TaskStatus.PENDING_APPROVAL:
                continue
            # p=p, t=t saves THIS task's IDs now. Without it, every button
            # would act on the last task drawn.
            p, t = project.id, task.id
            label = "Request Approval" if task.high_risk else "Mark Complete"
            ctk.CTkButton(bottom_row, text=label, width=140, height=28,
                          command=lambda p=p, t=t: self.run_service(organisation.complete_task, p, t)
                          ).pack(side="right", padx=4)
            if task.progress < 100:
                ctk.CTkButton(bottom_row, text="+25% Progress", width=110, height=28,
                              command=lambda p=p, t=t, now=task.progress: self.run_service(
                                  organisation.update_progress, p, t, min(100, now + 25))
                              ).pack(side="right", padx=4)
        self.redraw_theme()
