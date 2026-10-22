"""
Tkinter interface for the task management feature.

- TaskManagementView is a ttk.Frame. Embed it in any window of the main
  management system by passing the logged-in user and the list of people.
- TaskManagementApp is a standalone window with a simple user picker,
  used to run this feature on its own.

All rules live in models.py. This file only displays data and turns
TaskError exceptions into message boxes.
"""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk
from typing import Callable

from .models import (
    Dashboard,
    Employee,
    InvalidAction,
    Manager,
    Priority,
    Project,
    Task,
    TaskError,
    TaskStatus,
    Team,
    TeamLeader,
)

DATE_FORMAT_HINT = "YYYY-MM-DD"

COLOURS = {
    "overdue_bg": "#f8d7da",
    "overdue_fg": "#721c24",
    "approval_bg": "#fff3cd",
    "approval_fg": "#664d03",
    "done_fg": "#6c757d",
    "ok_fg": "#0f5132",
    "warn_fg": "#842029",
}


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text.strip())
    except ValueError:
        raise InvalidAction(f"'{text}' is not a valid date. Use {DATE_FORMAT_HINT}.") from None


# ---------------------------------------------------------------------------
# Dialogs
# ---------------------------------------------------------------------------

class _Dialog(tk.Toplevel):
    """Base class for small modal dialogs."""

    def __init__(self, parent: tk.Misc, title: str):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.result = None
        self.body = ttk.Frame(self, padding=16)
        self.body.pack(fill="both", expand=True)
        self.bind("<Escape>", lambda _event: self.destroy())

    def add_buttons(self, row: int, ok_text: str = "OK") -> None:
        buttons = ttk.Frame(self.body)
        buttons.grid(row=row, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=ok_text, command=self.on_ok).pack(side="right", padx=(0, 8))
        self.bind("<Return>", lambda _event: self.on_ok())

    def run(self):
        self.grab_set()
        self.wait_window()
        return self.result

    def on_ok(self) -> None:
        raise NotImplementedError


class TaskFormDialog(_Dialog):
    """Form for creating a new task, or editing an existing task's title and risk level."""

    def __init__(self, parent: tk.Misc, projects: list[Project], task: Task | None = None):
        super().__init__(parent, "Edit task" if task else "New task")
        self.projects = projects
        self.editing = task is not None

        ttk.Label(self.body, text="Title").grid(row=0, column=0, sticky="w", pady=4)
        self.title_var = tk.StringVar(value=task.title if task else "")
        title_entry = ttk.Entry(self.body, textvariable=self.title_var, width=36)
        title_entry.grid(row=0, column=1, sticky="ew", pady=4)
        title_entry.focus_set()

        row = 1
        if not self.editing:
            ttk.Label(self.body, text="Project").grid(row=row, column=0, sticky="w", pady=4)
            self.project_box = ttk.Combobox(self.body, state="readonly", width=34,
                                            values=[p.name for p in projects])
            if projects:
                self.project_box.current(0)
            self.project_box.grid(row=row, column=1, sticky="ew", pady=4)
            row += 1

            ttk.Label(self.body, text=f"Deadline ({DATE_FORMAT_HINT})").grid(
                row=row, column=0, sticky="w", pady=4)
            self.deadline_var = tk.StringVar(value=date.today().isoformat())
            ttk.Entry(self.body, textvariable=self.deadline_var, width=36).grid(
                row=row, column=1, sticky="ew", pady=4)
            row += 1

            ttk.Label(self.body, text="Priority").grid(row=row, column=0, sticky="w", pady=4)
            self.priority_box = ttk.Combobox(self.body, state="readonly", width=34,
                                             values=[p.name.title() for p in Priority])
            self.priority_box.current(1)
            self.priority_box.grid(row=row, column=1, sticky="ew", pady=4)
            row += 1

        self.risk_var = tk.BooleanVar(value=task.isHighRisk if task else False)
        ttk.Checkbutton(self.body, text="High-risk task (needs approval when done)",
                        variable=self.risk_var).grid(row=row, column=1, sticky="w", pady=4)
        row += 1
        self.add_buttons(row, "Save" if self.editing else "Create")

    def on_ok(self) -> None:
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Missing title", "Enter a title for the task.", parent=self)
            return
        result = {"title": title, "isHighRisk": self.risk_var.get()}
        if not self.editing:
            if not self.projects:
                messagebox.showerror("No project", "Create a project first.", parent=self)
                return
            try:
                result["deadline"] = parse_date(self.deadline_var.get())
            except TaskError as error:
                messagebox.showerror("Invalid date", str(error), parent=self)
                return
            result["project"] = self.projects[self.project_box.current()]
            result["priority"] = list(Priority)[self.priority_box.current()]
        self.result = result
        self.destroy()


class ChoiceDialog(_Dialog):
    """Pick one item from a list."""

    def __init__(self, parent: tk.Misc, title: str, prompt: str,
                 options: list, labels: list[str], initial: int = 0):
        super().__init__(parent, title)
        self.options = options
        ttk.Label(self.body, text=prompt).grid(row=0, column=0, columnspan=2, sticky="w")
        self.box = ttk.Combobox(self.body, state="readonly", width=44, values=labels)
        if labels:
            self.box.current(min(initial, len(labels) - 1))
        self.box.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.box.focus_set()
        self.add_buttons(2)

    def on_ok(self) -> None:
        if self.box.current() < 0:
            return
        self.result = self.options[self.box.current()]
        self.destroy()


# ---------------------------------------------------------------------------
# Main feature view
# ---------------------------------------------------------------------------

class TaskManagementView(ttk.Frame):
    """The task management feature for one logged-in user.

    user:      the logged-in Employee, TeamLeader or Manager
    people:    everyone in the organisation (used for assigning and team membership)
    on_logout: optional callback; shows a "Switch user" button when given
    """

    def __init__(self, master: tk.Misc, user: Employee, people: list[Employee],
                 on_logout: Callable[[], None] | None = None):
        super().__init__(master, padding=12)
        self.user = user
        self.people = people
        self.on_logout = on_logout
        self.is_leader = isinstance(user, TeamLeader)     # true for managers too
        self.is_manager = isinstance(user, Manager)
        self._tasks_by_iid: dict[str, Task] = {}
        self._team_rows: dict[str, tuple[Team, Employee | None]] = {}

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, foreground="#555").pack(
            side="bottom", fill="x", pady=(8, 0))     # packed first so it is never cut off
        self._build_header()
        self._build_progress()
        self._build_notebook()
        self.refresh()

    # --- layout ------------------------------------------------------------

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="Task Management", font=("TkDefaultFont", 16, "bold")).pack(
            side="left")
        if self.on_logout:
            ttk.Button(header, text="Switch user", command=self.on_logout).pack(side="right")
        ttk.Label(header, text=f"Logged in as {self.user.name} ({self.user.role})").pack(
            side="right", padx=12)

        self.overdue_var = tk.StringVar()
        self.overdue_label = ttk.Label(self, textvariable=self.overdue_var,
                                       font=("TkDefaultFont", 10, "bold"))
        self.overdue_label.pack(fill="x", pady=(8, 0))
        self.overload_var = tk.StringVar()
        if self.is_leader:
            ttk.Label(self, textvariable=self.overload_var,
                      foreground=COLOURS["warn_fg"]).pack(fill="x")

    def _build_progress(self) -> None:
        frame = ttk.LabelFrame(self, text="Project progress", padding=8)
        frame.pack(fill="x", pady=(8, 8))
        self.project_box = ttk.Combobox(frame, state="readonly", width=28)
        self.project_box.pack(side="left")
        self.project_box.bind("<<ComboboxSelected>>", lambda _event: self._update_progress())
        self.progress = ttk.Progressbar(frame, length=300, maximum=100)
        self.progress.pack(side="left", padx=12, fill="x", expand=True)
        self.progress_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.progress_var, width=28).pack(side="left")
        if self.is_manager:
            ttk.Button(frame, text="New project", command=self.new_project).pack(
                side="left", padx=(8, 0))

    def _build_notebook(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        notebook.add(self._build_tasks_tab(notebook), text="Tasks")
        if self.is_leader:
            notebook.add(self._build_teams_tab(notebook),
                         text="Teams" if self.is_manager else "My teams")

    def _build_tasks_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        tab = ttk.Frame(parent, padding=8)
        columns = ("title", "project", "assignee", "priority", "deadline", "status", "risk")
        headings = ("Title", "Project", "Assigned to", "Priority", "Deadline", "Status", "Risk")
        widths = (220, 140, 100, 70, 90, 130, 80)

        # Button rows are packed at the bottom first, so on small screens the task
        # list shrinks instead of the buttons being cut off.
        if self.is_leader:
            manage = ttk.LabelFrame(tab, text="Manage tasks", padding=6)
            manage.pack(side="bottom", fill="x", pady=(8, 0))
            for text, command in (("New task", self.new_task),
                                  ("Edit", self.edit_task),
                                  ("Assign / reassign", self.assign_task),
                                  ("Change deadline", self.change_deadline),
                                  ("Change priority", self.change_priority),
                                  ("Review / approve", self.review_task),
                                  ("Reopen", self.reopen_task)):
                ttk.Button(manage, text=text, command=command).pack(side="left", padx=(0, 6))

        my_actions = ttk.LabelFrame(tab, text="My task", padding=6)
        my_actions.pack(side="bottom", fill="x", pady=(8, 0))
        for text, command in (("Mark to do", self.mark_todo),
                              ("Mark in progress", self.mark_progressing),
                              ("Mark done", self.mark_done)):
            ttk.Button(my_actions, text=text, command=command).pack(side="left", padx=(0, 6))

        legend = ttk.Frame(tab)
        legend.pack(side="bottom", fill="x", pady=(6, 0))
        tk.Label(legend, text=" Overdue ", bg=COLOURS["overdue_bg"],
                 fg=COLOURS["overdue_fg"]).pack(side="left")
        tk.Label(legend, text=" Awaiting approval ", bg=COLOURS["approval_bg"],
                 fg=COLOURS["approval_fg"]).pack(side="left", padx=6)
        tk.Label(legend, text=" Done ", fg=COLOURS["done_fg"]).pack(side="left")

        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill="both", expand=True)
        self.task_tree = ttk.Treeview(tree_frame, columns=columns, selectmode="browse")
        self.task_tree.heading("#0", text="ID")
        self.task_tree.column("#0", width=230, stretch=False)
        for column, heading, width in zip(columns, headings, widths):
            self.task_tree.heading(column, text=heading)
            self.task_tree.column(column, width=width, anchor="w")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        self.task_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.task_tree.tag_configure("group", font=("TkDefaultFont", 10, "bold"))
        self.task_tree.tag_configure("overdue", background=COLOURS["overdue_bg"],
                                     foreground=COLOURS["overdue_fg"])
        self.task_tree.tag_configure("approval", background=COLOURS["approval_bg"],
                                     foreground=COLOURS["approval_fg"])
        self.task_tree.tag_configure("done", foreground=COLOURS["done_fg"])

        return tab

    def _build_teams_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        tab = ttk.Frame(parent, padding=8)
        columns = ("role", "active", "workload")
        self.team_tree = ttk.Treeview(tab, columns=columns, selectmode="browse")
        self.team_tree.heading("#0", text="Team / member")
        self.team_tree.column("#0", width=260)
        for column, heading, width in zip(columns, ("Role", "Active tasks", "Workload"),
                                          (120, 100, 200)):
            self.team_tree.heading(column, text=heading)
            self.team_tree.column(column, width=width, anchor="w")
        self.team_tree.tag_configure("team", font=("TkDefaultFont", 10, "bold"))
        self.team_tree.tag_configure("overload", foreground=COLOURS["warn_fg"])

        if self.is_manager:
            actions = ttk.LabelFrame(tab, text="Manage teams", padding=6)
            actions.pack(side="bottom", fill="x", pady=(8, 0))
            for text, command in (("New team", self.new_team),
                                  ("Appoint team leader", self.appoint_leader),
                                  ("Add member", self.add_member),
                                  ("Remove member", self.remove_member)):
                ttk.Button(actions, text=text, command=command).pack(side="left", padx=(0, 6))
        else:
            ttk.Label(tab, text="Use active task counts to decide how to handle unfinished "
                               "tasks case by case.", foreground="#555").pack(
                side="bottom", fill="x", pady=(8, 0))
        self.team_tree.pack(fill="both", expand=True)
        return tab

    # --- refreshing ----------------------------------------------------------

    def refresh(self) -> None:
        self._refresh_overdue()
        self._refresh_tasks()
        self._refresh_projects()
        if self.is_leader:
            self._refresh_teams()
            self._refresh_overload()

    def _refresh_overdue(self) -> None:
        overdue = self.user.dashboard.highlightOverdueTask()
        if overdue:
            noun = "task is" if len(overdue) == 1 else "tasks are"
            self.overdue_var.set(f"{len(overdue)} {noun} overdue (highlighted in red below).")
            self.overdue_label.configure(foreground=COLOURS["overdue_fg"])
        else:
            self.overdue_var.set("No overdue tasks.")
            self.overdue_label.configure(foreground=COLOURS["ok_fg"])

    def _refresh_overload(self) -> None:
        managed = [p for p in self.people if self.user.canManage(p)]
        overloaded = [p for p in managed if self.user.dashboard.highlightOverload(p)]
        if overloaded:
            names = ", ".join(f"{p.name} ({Dashboard.activeTaskCount(p)} active tasks)"
                              for p in overloaded)
            self.overload_var.set(f"Potential overload: {names}")
        else:
            self.overload_var.set("")

    def _refresh_tasks(self) -> None:
        selected = self.task_tree.selection()
        self.task_tree.delete(*self.task_tree.get_children())
        self._tasks_by_iid.clear()
        groups = self.user.dashboard.show()
        for key, heading in (("manager", "Assigned by a manager"),
                             ("teamLeader", "Assigned by a team leader")):
            tasks = sorted(groups[key], key=lambda t: (t.status == TaskStatus.DONE, t.deadline))
            parent = self.task_tree.insert("", "end", text=f"{heading} ({len(tasks)})",
                                           open=True, tags=("group",))
            for task in tasks:
                project = Project.projectOf(task)
                values = (task.title,
                          project.name if project else "",
                          task.assignee.name if task.assignee else "Unassigned",
                          task.priority.name.title(),
                          task.deadline.isoformat(),
                          task.statusText(),
                          "High-risk" if task.isHighRisk else "Routine")
                self.task_tree.insert(parent, "end", iid=task.taskId, text=task.taskId,
                                      values=values, tags=(self._tag_for(task),))
                self._tasks_by_iid[task.taskId] = task
        for iid in selected:
            if self.task_tree.exists(iid):
                self.task_tree.selection_set(iid)

    @staticmethod
    def _tag_for(task: Task) -> str:
        if task.status == TaskStatus.OVERDUE:
            return "overdue"
        if task.isAwaitingApproval():
            return "approval"
        if task.isComplete():
            return "done"
        return ""

    def _refresh_projects(self) -> None:
        names = [p.name for p in Project.allProjects]
        current = self.project_box.get()
        self.project_box.configure(values=names)
        if names:
            self.project_box.set(current if current in names else names[0])
        self._update_progress()

    def _update_progress(self) -> None:
        project = self._selected_project()
        if project is None:
            self.progress["value"] = 0
            self.progress_var.set("No projects yet")
            return
        percent = project.showProgress()
        self.progress["value"] = percent
        self.progress_var.set(f"{project.completedCount()}/{len(project.tasks)} tasks "
                              f"complete ({percent:.0f}%)")

    def _refresh_teams(self) -> None:
        selected = self.team_tree.selection()
        self.team_tree.delete(*self.team_tree.get_children())
        self._team_rows.clear()
        teams = self.user.managedTeams if self.is_manager else self.user.teamsLed
        for team in teams:
            leader = team.leader.name if team.leader else "No leader"
            team_iid = f"team-{team.teamId}"
            self.team_tree.insert("", "end", iid=team_iid, text=team.name,
                                  values=(f"Leader: {leader}", "", ""),
                                  open=True, tags=("team",))
            self._team_rows[team_iid] = (team, None)
            for member in team.members:
                count = Dashboard.activeTaskCount(member)
                overloaded = self.user.dashboard.highlightOverload(member)
                member_iid = f"member-{team.teamId}-{member.employeeId}"
                self.team_tree.insert(team_iid, "end", iid=member_iid, text=member.name,
                                      values=(member.role, count,
                                              "Potential overload" if overloaded else "OK"),
                                      tags=("overload",) if overloaded else ())
                self._team_rows[member_iid] = (team, member)
        for iid in selected:
            if self.team_tree.exists(iid):
                self.team_tree.selection_set(iid)

    # --- helpers -------------------------------------------------------------

    def _selected_project(self) -> Project | None:
        name = self.project_box.get()
        return next((p for p in Project.allProjects if p.name == name), None)

    def _selected_task(self) -> Task | None:
        selection = self.task_tree.selection()
        task = self._tasks_by_iid.get(selection[0]) if selection else None
        if task is None:
            messagebox.showinfo("Select a task", "Select a task in the list first.", parent=self)
        return task

    def _selected_team_row(self) -> tuple[Team, Employee | None] | None:
        selection = self.team_tree.selection()
        row = self._team_rows.get(selection[0]) if selection else None
        if row is None:
            messagebox.showinfo("Select a team", "Select a team or member first.", parent=self)
        return row

    def _run(self, action: Callable[[], object],
             message: str | Callable[[], str] | None = None) -> bool:
        """Run an action, show any TaskError as a message box, then refresh.
        message is shown in the status bar afterwards; it may be a function so it
        can describe the task's new state. Returns True if the action succeeded."""
        try:
            result = action()
        except TaskError as error:
            messagebox.showerror("Not allowed", str(error), parent=self)
            return False
        if callable(message):
            message = message()
        elif message is None and isinstance(result, str):
            message = result
        if message:
            self.status_var.set(message)
        self.refresh()
        return True

    def _confirm_overload(self, employee: Employee) -> bool:
        if not self.user.dashboard.highlightOverload(employee):
            return True
        return messagebox.askyesno(
            "Potential overload",
            f"{employee.name} already has {Dashboard.activeTaskCount(employee)} active tasks "
            f"and may be overloaded.\n\nAssign anyway?", parent=self)

    # --- employee actions ----------------------------------------------------

    def mark_todo(self) -> None:
        task = self._selected_task()
        if task:
            self._run(lambda: self.user.markToDo(task),
                      lambda: f"{task.taskId} is now: {task.statusText()}")

    def mark_progressing(self) -> None:
        task = self._selected_task()
        if task:
            self._run(lambda: self.user.markProgressing(task),
                      lambda: f"{task.taskId} is now: {task.statusText()}")

    def mark_done(self) -> None:
        task = self._selected_task()
        if not task:
            return

        def action() -> str:
            needs_approval = self.user.markDone(task)
            if needs_approval:
                return f"{task.taskId} is done and has been sent for approval (high-risk)."
            return f"{task.taskId} is complete. Routine tasks need no approval."
        self._run(action)

    # --- team leader and manager actions ---------------------------------------

    def new_task(self) -> None:
        data = TaskFormDialog(self, list(Project.allProjects)).run()
        if not data:
            return
        created: list[Task] = []

        def action() -> str:
            task = self.user.createTask(data["project"], data["title"], data["deadline"],
                                        data["priority"], data["isHighRisk"])
            created.append(task)
            return f"Created {task.taskId} '{task.title}'."
        self._run(action)
        if created and messagebox.askyesno("Assign task", "Assign this task now?", parent=self):
            self.task_tree.selection_set(created[0].taskId)
            self.assign_task()

    def edit_task(self) -> None:
        task = self._selected_task()
        if not task:
            return
        data = TaskFormDialog(self, [], task).run()
        if data:
            self._run(lambda: self.user.editTask(task, data["title"], data["isHighRisk"]),
                      lambda: f"Updated {task.taskId}.")

    def assign_task(self) -> None:
        task = self._selected_task()
        if not task:
            return
        candidates = [p for p in self.people if self.user.canManage(p) and p is not task.assignee]
        if not candidates:
            messagebox.showinfo("No one to assign",
                                "There is no one else in your area of responsibility.",
                                parent=self)
            return
        labels = [f"{p.name} ({p.role}) - {Dashboard.activeTaskCount(p)} active tasks"
                  for p in candidates]
        verb = "Reassign" if task.assignee else "Assign"
        employee = ChoiceDialog(self, f"{verb} task", f"{verb} {task.taskId} '{task.title}' to:",
                                candidates, labels).run()
        if not employee or not self._confirm_overload(employee):
            return
        if task.assignee:
            self._run(lambda: self.user.reassignTask(task, employee),
                      lambda: f"Reassigned {task.taskId} to {employee.name}.")
        else:
            self._run(lambda: self.user.assignTask(task, employee),
                      lambda: f"Assigned {task.taskId} to {employee.name}.")

    def change_deadline(self) -> None:
        task = self._selected_task()
        if not task:
            return
        text = simpledialog.askstring("Change deadline",
                                      f"New deadline for {task.taskId} ({DATE_FORMAT_HINT}):",
                                      initialvalue=task.deadline.isoformat(), parent=self)
        if text:
            self._run(lambda: self.user.changeDeadline(task, parse_date(text)),
                      lambda: f"{task.taskId} deadline changed to {task.deadline}.")

    def change_priority(self) -> None:
        task = self._selected_task()
        if not task:
            return
        priorities = list(Priority)
        priority = ChoiceDialog(self, "Change priority", f"Priority for {task.taskId}:",
                                priorities, [p.name.title() for p in priorities],
                                initial=priorities.index(task.priority)).run()
        if priority:
            self._run(lambda: self.user.changePriority(task, priority),
                      lambda: f"{task.taskId} priority changed to {priority.name.title()}.")

    def review_task(self) -> None:
        task = self._selected_task()
        if not task:
            return
        try:
            details = self.user.reviewTask(task)
        except TaskError as error:
            messagebox.showerror("Not allowed", str(error), parent=self)
            return
        if not task.isAwaitingApproval():
            messagebox.showinfo("Review task", details, parent=self)
            return
        acceptable = messagebox.askyesnocancel(
            "Review high-risk task",
            f"{details}\n\nIs the work acceptable?\n\n"
            "Yes: approve the task\nNo: reopen it for more work", parent=self)
        if acceptable is True:
            self._run(lambda: self.user.approveTask(task),
                      lambda: f"Approved {task.taskId}.")
        elif acceptable is False:
            self._run(lambda: self.user.reopenTask(task),
                      lambda: f"Reopened {task.taskId}: {task.statusText()}.")

    def reopen_task(self) -> None:
        task = self._selected_task()
        if task and messagebox.askyesno("Reopen task", f"Reopen {task.taskId} '{task.title}'?",
                                        parent=self):
            self._run(lambda: self.user.reopenTask(task),
                      lambda: f"Reopened {task.taskId}: {task.statusText()}.")

    # --- manager actions -------------------------------------------------------

    def new_project(self) -> None:
        name = simpledialog.askstring("New project", "Project name:", parent=self)
        if name is None:
            return

        def action() -> str:
            project = Project(name)
            self.project_box.set(project.name)
            return f"Created project '{project.name}'."
        self._run(action)

    def new_team(self) -> None:
        name = simpledialog.askstring("New team", "Team name:", parent=self)
        if name is not None:
            self._run(lambda: f"Created team '{self.user.createTeam(name).name}'. "
                              "Appoint a team leader next.")

    def appoint_leader(self) -> None:
        row = self._selected_team_row()
        if not row:
            return
        team = row[0]
        leaders = [p for p in self.people if isinstance(p, TeamLeader) and p is not team.leader]
        labels = [f"{p.name} ({p.role}) - leads {len(p.teamsLed)} team(s)" for p in leaders]
        leader = ChoiceDialog(self, "Appoint team leader",
                              f"Choose the leader of '{team.name}':", leaders, labels).run()
        if leader:
            self._run(lambda: self.user.appointTeamLeader(team, leader),
                      lambda: f"{leader.name} now leads '{team.name}'.")

    def add_member(self) -> None:
        row = self._selected_team_row()
        if not row:
            return
        team = row[0]
        candidates = [p for p in self.people
                      if p not in team.members and p is not team.leader
                      and not isinstance(p, Manager)]
        if not candidates:
            messagebox.showinfo("No one to add", "Everyone is already in this team.", parent=self)
            return
        employee = ChoiceDialog(self, "Add member", f"Add to '{team.name}':", candidates,
                                [f"{p.name} ({p.role})" for p in candidates]).run()
        if employee:
            self._run(lambda: team.addMember(employee),
                      lambda: f"{employee.name} joined '{team.name}'.")

    def remove_member(self) -> None:
        row = self._selected_team_row()
        if not row:
            return
        team, member = row
        if member is None:
            messagebox.showinfo("Select a member", "Select a member of the team, not the team.",
                                parent=self)
            return
        if not messagebox.askyesno("Remove member",
                                   f"Remove {member.name} from '{team.name}'?", parent=self):
            return
        unfinished: list[Task] = []

        def action() -> str:
            unfinished.extend(team.removeMember(member))
            return f"{member.name} left '{team.name}'."
        self._run(action)
        if unfinished:
            listing = "\n".join(f"- {t.taskId}: {t.title}" for t in unfinished)
            messagebox.showinfo(
                "Unfinished tasks",
                f"{member.name} still has unfinished tasks:\n\n{listing}\n\n"
                "They have not been reassigned automatically. Decide case by case "
                "whether to reassign them or change their deadlines.", parent=self)


# ---------------------------------------------------------------------------
# Standalone application
# ---------------------------------------------------------------------------

class TaskManagementApp(tk.Tk):
    """Runs the feature on its own, with a simple user picker instead of a real login."""

    def __init__(self, people: list[Employee]):
        super().__init__()
        self.title("Task Management")
        self.geometry("1150x720")
        self.minsize(900, 560)
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")        # consistent look, and row colours work on all OSes
        style.configure("Treeview", rowheight=24)
        self.people = people
        self._current: ttk.Frame | None = None
        self.show_login()

    def _replace(self, frame: ttk.Frame) -> None:
        if self._current is not None:
            self._current.destroy()
        self._current = frame
        frame.pack(fill="both", expand=True)

    def show_login(self) -> None:
        frame = ttk.Frame(self, padding=40)
        ttk.Label(frame, text="Task Management", font=("TkDefaultFont", 18, "bold")).pack(
            pady=(40, 4))
        ttk.Label(frame, text="Choose who to log in as. In the full system, this "
                             "comes from your login screen.", foreground="#555").pack()
        box = ttk.Combobox(frame, state="readonly", width=36,
                           values=[f"{p.name} - {p.role}" for p in self.people])
        box.current(0)
        box.pack(pady=16)

        def log_in(_event=None) -> None:
            user = self.people[box.current()]
            self._replace(TaskManagementView(self, user, self.people,
                                             on_logout=self.show_login))
        ttk.Button(frame, text="Log in", command=log_in).pack()
        box.bind("<Return>", log_in)
        self._replace(frame)
