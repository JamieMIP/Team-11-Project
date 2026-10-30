import customtkinter as ctk
from datetime import datetime
from base import Page
from sample_data import LIVE_USERS, ALL_TEAMS
from theme_config import ThemeManager


class TeamListPage(Page):
    def __init__(self, master, app, team_key="Team 1"):
        super().__init__(master, app)
        self.team_key = team_key

        # Keep the base page frame transparent so the main window background shows through
        self.configure(fg_color="transparent")

        team_bundle = ALL_TEAMS.get(team_key, ALL_TEAMS["Team 1"])
        self.team_info = dict(team_bundle.get("info", {}))
        self.tasks = {k: dict(v) for k, v in team_bundle.get("tasks", {}).items()}

        self.current_user_id = getattr(app, "current_user_id", 2)
        current_user = LIVE_USERS.get(self.current_user_id, LIVE_USERS[2])

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=f"{self.team_info.get('team_name', team_key)}: {self.team_info.get('project_name', '')}",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(side="left", anchor="w")

        self.user_badge = ctk.CTkLabel(
            self.header_frame,
            text=f"Logged in: {current_user['name']} ({current_user['role']})",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.user_badge.pack(side="right", anchor="e", padx=6)

        # Project Progress Bar Card
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", pady=(0, 10), padx=2)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Overall Project Progress: 0%",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.progress_label.pack(anchor="w", padx=12, pady=(8, 2))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=12, pady=(0, 10))

        # Scrollable Task List
        self.task_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.task_area.pack(fill="both", expand=True)

        # Task Creation Bar (Shown only if current user is Manager or this team's Leader)
        self.bar = ctk.CTkFrame(self, fg_color="transparent")
        self.bar.pack(fill="x", pady=(10, 0))

        self.entry = ctk.CTkEntry(self.bar, placeholder_text="New task title...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        member_ids = self.team_info.get("member_ids", [2])
        assignee_options = [
            f"{uid}: {LIVE_USERS[uid]['name']}" for uid in member_ids if uid in LIVE_USERS
        ] or [f"{uid}: {u['name']}" for uid, u in LIVE_USERS.items()]

        self.assignee_menu = ctk.CTkOptionMenu(self.bar, values=assignee_options, width=165)
        self.assignee_menu.set(assignee_options[-1])
        self.assignee_menu.pack(side="left", padx=4)

        self.priority_menu = ctk.CTkOptionMenu(
            self.bar, values=["Low", "Medium", "High", "Critical"], width=110
        )
        self.priority_menu.set("Medium")
        self.priority_menu.pack(side="left", padx=4)

        self.risk_check = ctk.CTkCheckBox(self.bar, text="High Risk", width=90)
        self.risk_check.pack(side="left", padx=6)

        self.add_btn = ctk.CTkButton(self.bar, text="Add Task", width=90, command=self.add_task)
        self.add_btn.pack(side="left", padx=(6, 0))

        # Subscribe to ThemeManager (automatically triggers apply_theme & refresh immediately)
        ThemeManager.subscribe(self.apply_theme)

    def destroy(self):
        ThemeManager.unsubscribe(self.apply_theme)
        super().destroy()

    def on_show(self):
        self.apply_theme()

    def apply_theme(self, p=None, s=None):
        """Styles static controls on this page and rebuilds dynamic task cards with active theme tokens."""
        if p is None:
            p = ThemeManager.get_palette()
        if s is None:
            s = ThemeManager.get_style()

        btn_text = "#000000" if ThemeManager.current_palette_name == "Cyber Neon" else "#FFFFFF"
        font_fam = s["font_family"]
        w_radius = s["widget_radius"]
        b_width = s["border_width"]

        # 1. Header Labels
        self.title_label.configure(text_color=p["text"], font=(font_fam, 22, "bold"))
        self.user_badge.configure(text_color=p["subtext"], font=(font_fam, 13, "bold"))

        # 2. Progress Bar Card
        self.progress_frame.configure(
            fg_color=p["card_bg"],
            border_color=p["border"],
            corner_radius=s["card_radius"],
            border_width=b_width
        )
        self.progress_label.configure(text_color=p["text"], font=(font_fam, 13, "bold"))
        self.progress_bar.configure(
            progress_color=p["primary"],
            fg_color=p["entry_bg"],
            border_color=p["border"],
            border_width=b_width,
            corner_radius=w_radius
        )

        # 3. Scrollable Area
        self.task_area.configure(
            fg_color="transparent",
            scrollbar_button_color=p["secondary"],
            scrollbar_button_hover_color=p["primary"]
        )

        # 4. Bottom Input Bar Controls
        self.entry.configure(
            fg_color=p["entry_bg"],
            text_color=p["text"],
            placeholder_text_color=p["subtext"],
            border_color=p["border"],
            corner_radius=w_radius,
            border_width=b_width,
            font=(font_fam, 13)
        )

        for menu in (self.assignee_menu, self.priority_menu):
            menu.configure(
                fg_color=p["secondary"],
                button_color=p["primary"],
                button_hover_color=p["primary_hover"],
                text_color="#FFFFFF",
                corner_radius=w_radius,
                font=(font_fam, 13)
            )

        self.risk_check.configure(
            fg_color=p["primary"],
            hover_color=p["primary_hover"],
            text_color=p["text"],
            border_color=p["border"],
            corner_radius=max(2, w_radius // 2),
            border_width=max(1, b_width),
            font=(font_fam, 13)
        )

        self.add_btn.configure(
            fg_color=p["primary"],
            hover_color=p["primary_hover"],
            text_color=btn_text,
            corner_radius=w_radius,
            border_width=b_width,
            border_color=p["border"],
            height=s["btn_height"],
            font=(font_fam, 13, "bold")
        )

        # 5. Re-render task cards so they use the updated palette and geometry
        self.refresh()

    def can_user_manage_team(self) -> bool:
        user = LIVE_USERS.get(self.current_user_id, LIVE_USERS[2])
        if user.get("role") == "Manager" or user.get("is_admin"):
            return True
        return self.current_user_id == self.team_info.get("leader_id")

    def is_overdue(self, task: dict) -> bool:
        if task.get("status") == "Completed":
            return False
        try:
            deadline_dt = datetime.strptime(task.get("deadline", ""), "%Y-%m-%d").date()
            return deadline_dt < datetime.now().date()
        except Exception:
            return False

    def calculate_project_progress(self) -> int:
        if not self.tasks:
            return 0
        try:
            total = sum(int(t.get("progress", 0)) for t in self.tasks.values())
            return int(total / len(self.tasks))
        except Exception:
            return 0

    def refresh(self):
        try:
            for widget in self.task_area.winfo_children():
                widget.destroy()

            can_manage = self.can_user_manage_team()

            if can_manage:
                self.bar.pack(fill="x", pady=(10, 0))
            else:
                self.bar.pack_forget()

            # Pull current theme tokens for all dynamically generated task cards
            p = ThemeManager.get_palette()
            s = ThemeManager.get_style()
            font_fam = s["font_family"]
            w_radius = s["widget_radius"]
            b_width = s["border_width"]
            btn_text = "#000000" if ThemeManager.current_palette_name == "Cyber Neon" else "#FFFFFF"

            pct = self.calculate_project_progress()
            leader_email = self.team_info.get("leader_email", "N/A")
            self.progress_label.configure(
                text=f"Overall Project Progress: {pct}%  |  Team Leader: {leader_email}"
            )
            self.progress_bar.set(pct / 100.0)

            for task_key, task in self.tasks.items():
                overdue = self.is_overdue(task)

                # Task Card Container
                card = ctk.CTkFrame(
                    self.task_area,
                    fg_color=p["card_bg"],
                    border_color=p["error"] if overdue else p["border"],
                    border_width=2 if overdue else b_width,
                    corner_radius=s["card_radius"]
                )
                card.pack(fill="x", pady=6, padx=4)

                # Top Row: Task Title & Metadata
                top_row = ctk.CTkFrame(card, fg_color="transparent")
                top_row.pack(fill="x", padx=12, pady=(8, 2))

                status_prefix = "[OVERDUE] " if overdue else ""
                risk_badge = " [HIGH RISK]" if task.get("is_high_risk") else ""
                title_text = f"{status_prefix}{task.get('title', 'Untitled')}{risk_badge}"

                ctk.CTkLabel(
                    top_row,
                    text=title_text,
                    text_color=p["error"] if overdue else p["text"],
                    font=(font_fam, 16, "bold")
                ).pack(side="left", anchor="w")

                meta_text = (
                    f"Priority: {task.get('priority', 'Medium')}  |  "
                    f"Due: {task.get('deadline', 'N/A')}  |  "
                    f"Status: {task.get('status', 'In Progress')} ({task.get('progress', 0)}%)"
                )
                ctk.CTkLabel(
                    top_row,
                    text=meta_text,
                    text_color=p["subtext"],
                    font=(font_fam, 12, "bold")
                ).pack(side="right")

                # Description
                ctk.CTkLabel(
                    card,
                    text=task.get("description", ""),
                    text_color=p["text"],
                    font=(font_fam, 13),
                    wraplength=750,
                    justify="left"
                ).pack(anchor="w", padx=12, pady=(2, 6))

                # Bottom Row: Assignee & Action Buttons
                bottom_row = ctk.CTkFrame(card, fg_color="transparent")
                bottom_row.pack(fill="x", padx=12, pady=(0, 8))

                ctk.CTkLabel(
                    bottom_row,
                    text=f"Assigned to: {task.get('assigned_user_name', 'Unassigned')} (ID: {task.get('assigned_user_id', '-')})",
                    text_color=p["subtext"],
                    font=(font_fam, 12)
                ).pack(side="left")

                is_assignee = (task.get("assigned_user_id") == self.current_user_id)

                if task.get("status") != "Completed":
                    if is_assignee or can_manage:
                        if task.get("progress", 0) < 100:
                            ctk.CTkButton(
                                bottom_row,
                                text="+25% Progress",
                                width=115,
                                height=28,
                                fg_color=p["secondary"],
                                hover_color=p["secondary_hover"],
                                text_color="#FFFFFF",
                                corner_radius=w_radius,
                                border_width=b_width,
                                border_color=p["border"],
                                font=(font_fam, 12, "bold"),
                                command=lambda k=task_key: self.bump_progress(k)
                            ).pack(side="right", padx=4)

                        if task.get("is_high_risk") and not can_manage:
                            if task.get("status") != "Pending Approval":
                                ctk.CTkButton(
                                    bottom_row,
                                    text="Request Approval",
                                    width=135,
                                    height=28,
                                    fg_color=p["primary"],
                                    hover_color=p["primary_hover"],
                                    text_color=btn_text,
                                    corner_radius=w_radius,
                                    border_width=b_width,
                                    border_color=p["border"],
                                    font=(font_fam, 12, "bold"),
                                    command=lambda k=task_key: self.request_approval(k)
                                ).pack(side="right", padx=4)
                        else:
                            btn_label = "Approve & Complete" if task.get("status") == "Pending Approval" else "Mark Complete"
                            ctk.CTkButton(
                                bottom_row,
                                text=btn_label,
                                width=145,
                                height=28,
                                fg_color=p["primary"],
                                hover_color=p["primary_hover"],
                                text_color=btn_text,
                                corner_radius=w_radius,
                                border_width=b_width,
                                border_color=p["border"],
                                font=(font_fam, 12, "bold"),
                                command=lambda k=task_key: self.complete_task(k)
                            ).pack(side="right", padx=4)
                else:
                    if can_manage:
                        ctk.CTkButton(
                            bottom_row,
                            text="Reopen",
                            width=90,
                            height=28,
                            fg_color=p["secondary"],
                            hover_color=p["secondary_hover"],
                            text_color="#FFFFFF",
                            corner_radius=w_radius,
                            border_width=b_width,
                            border_color=p["border"],
                            font=(font_fam, 12, "bold"),
                            command=lambda k=task_key: self.reopen_task(k)
                        ).pack(side="right", padx=4)
        except Exception:
            pass

    def bump_progress(self, key: str):
        try:
            task = self.tasks[key]
            task["progress"] = min(100, task.get("progress", 0) + 25)
            if task["progress"] < 100:
                task["status"] = "In Progress"
            self.refresh()
        except Exception:
            pass

    def request_approval(self, key: str):
        try:
            self.tasks[key]["progress"] = 100
            self.tasks[key]["status"] = "Pending Approval"
            self.refresh()
        except Exception:
            pass

    def complete_task(self, key: str):
        try:
            self.tasks[key]["progress"] = 100
            self.tasks[key]["status"] = "Completed"
            self.refresh()
        except Exception:
            pass

    def reopen_task(self, key: str):
        try:
            self.tasks[key]["progress"] = 75
            self.tasks[key]["status"] = "In Progress"
            self.refresh()
        except Exception:
            pass

    def add_task(self):
        try:
            title = self.entry.get().strip()
            if not title:
                return

            assignee_uid = int(self.assignee_menu.get().split(":")[0])
            assignee = LIVE_USERS.get(assignee_uid, LIVE_USERS[2])
            new_key = f"Task{len(self.tasks) + 1}"

            self.tasks[new_key] = {
                "title": title,
                "description": "Created during demo session.",
                "assigned_user_id": assignee["id"],
                "assigned_user_name": assignee["name"],
                "assigned_user_email": assignee["email"],
                "assigned_by_id": self.current_user_id,
                "deadline": "2026-11-20",
                "priority": self.priority_menu.get(),
                "status": "Not Started",
                "progress": 0,
                "is_high_risk": bool(self.risk_check.get()),
            }
            self.entry.delete(0, "end")
            self.refresh()
        except Exception:
            pass