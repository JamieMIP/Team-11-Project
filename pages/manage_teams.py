# pages/manage_teams.py
"""Manage Teams & Roles page (Managers only).

Teams view:   create a team (a leader is required), change a team's
              leader, add and remove members. Removing someone lists their
              unfinished tasks so the leader can reassign them (Q&A PM Q8).
People view:  change anyone's role in either direction (admin Q4) and set
              an access end date for temporary staff (admin Q3).
"""

import customtkinter as ctk

from organisation import Role, organisation
from pages.org_common import OrgPage, clear, name_of, parse_date, show_date

ROLE_NAMES = [role.value for role in Role]


class ManageTeamsPage(OrgPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.view = "Teams"

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="Manage Teams & Roles",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", anchor="w")
        ctk.CTkLabel(header_frame, text=f"Logged in: {self.user.name} ({self.user.role.value})",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="right", padx=6)

        switch_frame = ctk.CTkFrame(self, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(0, 6))
        for view in ("Teams", "People & Roles"):
            ctk.CTkButton(switch_frame, text=view, width=140,
                          command=lambda v=view: self.switch(v)).pack(side="left", padx=(0, 6))

        self.add_message_label()
        self.body = ctk.CTkScrollableFrame(self)
        self.body.pack(fill="both", expand=True)
        self.refresh()

    def switch(self, view):
        self.view = view
        self.show_message("")
        self.refresh()

    def refresh(self):
        clear(self.body)
        if self.view == "Teams":
            self.draw_teams()
        else:
            self.draw_people()
        self.redraw_theme()

    def card(self, title):
        card = ctk.CTkFrame(self.body, border_width=1)
        card.pack(fill="x", pady=6, padx=4)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(8, 4))
        return card

    @staticmethod
    def active_people():
        return [person for person in organisation.all_employees() if person.is_active()]

    # ------------------------------------------------------------------
    # Teams view
    # ------------------------------------------------------------------

    def draw_teams(self):
        # ----- create a team -----
        card = self.card("Create a Team")
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 6))
        self.team_name_entry = ctk.CTkEntry(row, placeholder_text="Team name...")
        self.team_name_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(row, text="Team Leader:").pack(side="left", padx=4)
        people = self.active_people()
        self.people_lookup = {person.name: person.email for person in people}
        self.new_leader_menu = ctk.CTkOptionMenu(row, values=list(self.people_lookup), width=165)
        self.new_leader_menu.pack(side="left", padx=4)
        ctk.CTkButton(row, text="Create Team", width=110, command=self.create_team).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(card, text="Members (tick everyone who should join):",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12)
        boxes = ctk.CTkFrame(card, fg_color="transparent")
        boxes.pack(fill="x", padx=12, pady=(2, 10))
        self.member_boxes = {}
        for index, person in enumerate(people):
            box = ctk.CTkCheckBox(boxes, text=person.name, width=150)
            box.grid(row=index // 5, column=index % 5, sticky="w", pady=2)
            self.member_boxes[person.email] = box

        # ----- one card per team -----
        for team in organisation.all_teams():
            projects = organisation.projects_for_team(team.id)
            card = self.card(f"{team.name}  |  Team Leader: {name_of(team.leader_email)}  |  "
                             f"Projects: {len(projects)}")

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=(0, 4))
            ctk.CTkLabel(row, text="Change leader:").pack(side="left")
            leader_menu = ctk.CTkOptionMenu(row, values=list(self.people_lookup), width=165)
            leader_menu.set(name_of(team.leader_email))
            leader_menu.pack(side="left", padx=6)
            ctk.CTkButton(row, text="Set Leader", width=100, height=28,
                          command=lambda t=team.id, m=leader_menu: self.set_leader(t, m)
                          ).pack(side="left")

            outsiders = [person.name for person in people if person.email not in team.everyone()]
            if outsiders:
                add_menu = ctk.CTkOptionMenu(row, values=outsiders, width=165)
                add_menu.pack(side="left", padx=(24, 6))
                ctk.CTkButton(row, text="Add Member", width=110, height=28,
                              command=lambda t=team.id, m=add_menu: self.add_member(t, m)
                              ).pack(side="left")

            for email in team.everyone():
                person = organisation.get_employee(email)
                member_row = ctk.CTkFrame(card, fg_color="transparent")
                member_row.pack(fill="x", padx=12, pady=1)
                role = "Team Leader of this team" if email == team.leader_email else person.role.value
                overloaded = "  [OVERLOADED]" if organisation.is_overloaded(email) else ""
                ctk.CTkLabel(member_row, font=ctk.CTkFont(size=12),
                             text=f"{person.name}  ({email})  |  {role}  |  "
                                  f"Unfinished tasks: {organisation.active_task_count(email)}"
                                  f"{overloaded}").pack(side="left")
                if email != team.leader_email:
                    ctk.CTkButton(member_row, text="Remove", width=80, height=26,
                                  command=lambda t=team.id, e=email: self.remove_member(t, e)
                                  ).pack(side="right")
            ctk.CTkLabel(card, text="").pack(pady=1)

    def create_team(self):
        members = [email for email, box in self.member_boxes.items() if box.get()]
        team = self.run_service(organisation.create_team, self.team_name_entry.get(),
                                self.people_lookup.get(self.new_leader_menu.get()), members)
        if team is not None:
            self.show_message(f"{team.name} created. It now appears under Team To-do List.")

    def set_leader(self, team_id, menu):
        self.run_service(organisation.appoint_leader, team_id, self.people_lookup[menu.get()])

    def add_member(self, team_id, menu):
        self.run_service(organisation.add_member, team_id, self.people_lookup[menu.get()])

    def remove_member(self, team_id, email):
        leftover = self.run_service(organisation.remove_member, team_id, email)
        if leftover is None:
            return
        team = organisation.get_team(team_id)
        if leftover is True or not leftover:
            self.show_message(f"{name_of(email)} removed from {team.name}.")
        else:
            titles = ", ".join(task.title for task in leftover)
            self.show_message(f"{name_of(email)} removed from {team.name}. Their unfinished tasks "
                              f"still need a decision from the Team Leader: {titles}. "
                              f"Open {team.name} and use Edit to reassign them.")

    # ------------------------------------------------------------------
    # People & Roles view
    # ------------------------------------------------------------------

    def draw_people(self):
        card = self.card("People & Roles")
        ctk.CTkLabel(card, font=ctk.CTkFont(size=12), anchor="w", justify="left", wraplength=900, text=(
            "Roles can change in both directions. You cannot change your own role. "
            "For temporary staff, set the date their access ends; after it they "
            "cannot be given new tasks or added to teams. Leave it blank for permanent staff."
        )).pack(fill="x", padx=12, pady=(0, 6))

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=12, pady=(0, 10))
        for column, text in enumerate(["Name", "Email", "Role", "Access Ends", "", "Status"]):
            ctk.CTkLabel(table, text=text, font=ctk.CTkFont(size=13, weight="bold")).grid(
                row=0, column=column, sticky="w", padx=8, pady=4)

        for row_number, person in enumerate(organisation.all_employees(), start=1):
            ctk.CTkLabel(table, text=person.name, font=ctk.CTkFont(size=12)).grid(
                row=row_number, column=0, sticky="w", padx=8)
            ctk.CTkLabel(table, text=person.email, font=ctk.CTkFont(size=12)).grid(
                row=row_number, column=1, sticky="w", padx=8)
            role_menu = ctk.CTkOptionMenu(
                table, values=ROLE_NAMES, width=140,
                command=lambda value, e=person.email: self.change_role(e, value))
            role_menu.set(person.role.value)
            role_menu.grid(row=row_number, column=2, sticky="w", padx=8, pady=2)
            end_entry = ctk.CTkEntry(table, placeholder_text="YYYY-MM-DD", width=120)
            if person.access_ends:
                end_entry.insert(0, show_date(person.access_ends))
            end_entry.grid(row=row_number, column=3, sticky="w", padx=8)
            ctk.CTkButton(table, text="Save", width=60, height=26,
                          command=lambda e=person.email, box=end_entry: self.set_access_end(e, box)
                          ).grid(row=row_number, column=4, padx=4)
            status = "Active" if person.is_active() else "[ACCESS ENDED]"
            ctk.CTkLabel(table, text=status, font=ctk.CTkFont(size=12)).grid(
                row=row_number, column=5, sticky="w", padx=8)

    def change_role(self, email, value):
        if self.run_service(organisation.change_role, email, Role(value)) is not None:
            self.show_message(f"{name_of(email)} is now a {value}.")

    def set_access_end(self, email, entry):
        try:
            end_date = parse_date(entry.get())
        except ValueError as error:
            self.show_message(str(error))
            return
        if self.run_service(organisation.set_access_end, email, end_date) is not None:
            when = f"ends on {show_date(end_date)}" if end_date else "is permanent"
            self.show_message(f"{name_of(email)}'s access {when}.")
