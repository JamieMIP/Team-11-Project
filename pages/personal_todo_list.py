"""Personal to-do list page.

Shows the logged-in employee's personal to-do lists and lets them add,
start, finish, reopen and delete items. All the rules (who owns what,
blank titles, archiving) live in personal_todo/service.py. This file
only draws the screen and passes button clicks to the service.
"""

from datetime import date, datetime, timedelta

import customtkinter as ctk

from base import Page
from personal_todo import PersonalTodoService, Priority, Status, TodoError
from theme_config import ThemeManager

# One shared service for the whole app, so items are kept when you switch
# to another page and back. When the team adds a database, this is the
# only line that needs to change.
todo_service = PersonalTodoService()

PRIORITY_CHOICES = {"Low": Priority.LOW, "Medium": Priority.MEDIUM, "High": Priority.HIGH}
STATUS_TEXT = {
    Status.NOT_STARTED: "Not started",
    Status.IN_PROGRESS: "In progress",
    Status.DONE: "Done",
}

_users_with_demo_items = set()


def add_demo_items(email):
    """Give each user a few example items the first time they open the page."""
    if email in _users_with_demo_items:
        return
    _users_with_demo_items.add(email)

    today = date.today()
    general = todo_service.get_general_list(email)
    todo_service.add_item(email, general.id, "Reply to client emails",
                          "Answer the two outstanding queries.",
                          today + timedelta(days=1), Priority.HIGH)
    todo_service.add_item(email, general.id, "Book annual leave",
                          deadline=today - timedelta(days=2), priority=Priority.LOW)

    training = todo_service.create_list(email, "Training")
    todo_service.add_item(email, training.id, "Finish security awareness course",
                          "Modules 3 and 4.", today + timedelta(days=7))


class PersonalListPage(Page):
    """The screen for one employee's personal to-do lists."""

    def __init__(self, master, app):
        super().__init__(master, app)

        user = getattr(app, "current_user", None) or {}
        self.email = user.get("email", "guest@company.co.uk")
        self.user_name = user.get("name", "Guest")

        add_demo_items(self.email)
        self.selected_list_id = todo_service.get_general_list(self.email).id
        self.label_to_id = {}

        # ----- header: page title, list picker, new list button -----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header, text=f"{self.user_name}'s To-do Lists",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="New List", width=90, command=self.create_list
        ).pack(side="right")

        self.list_menu = ctk.CTkOptionMenu(
            header, values=["General"], width=180, command=self.choose_list
        )
        self.list_menu.pack(side="right", padx=6)

        # ----- progress bar for the selected list -----
        progress_frame = ctk.CTkFrame(self)
        progress_frame.pack(fill="x", pady=(0, 10), padx=2)

        self.progress_label = ctk.CTkLabel(
            progress_frame, text="", font=ctk.CTkFont(size=13, weight="bold")
        )
        self.progress_label.pack(anchor="w", padx=12, pady=(8, 2))

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=12, pady=(0, 10))

        # ----- message line for mistakes like a blank title -----
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(anchor="w")

        # ----- the items themselves -----
        self.item_area = ctk.CTkScrollableFrame(self)
        self.item_area.pack(fill="both", expand=True)

        # ----- bar for adding a new item -----
        add_bar = ctk.CTkFrame(self, fg_color="transparent")
        add_bar.pack(fill="x", pady=(10, 0))

        self.title_entry = ctk.CTkEntry(add_bar, placeholder_text="New item title...")
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.title_entry.bind("<Return>", lambda event: self.add_item())

        self.deadline_entry = ctk.CTkEntry(
            add_bar, placeholder_text="Deadline (YYYY-MM-DD)", width=170
        )
        self.deadline_entry.pack(side="left", padx=4)

        self.priority_menu = ctk.CTkOptionMenu(
            add_bar, values=list(PRIORITY_CHOICES), width=110
        )
        self.priority_menu.set("Medium")
        self.priority_menu.pack(side="left", padx=4)

        ctk.CTkButton(
            add_bar, text="Add Item", width=90, command=self.add_item
        ).pack(side="left", padx=(6, 0))

        # Optional description, on its own row so there's room to type.
        self.description_entry = ctk.CTkEntry(
            self, placeholder_text="Description (optional)..."
        )
        self.description_entry.pack(fill="x", pady=(6, 0))
        self.description_entry.bind("<Return>", lambda event: self.add_item())

        self.refresh()

    def on_show(self):
        """Runs every time the page is opened from the sidebar."""
        self.refresh()

    # ----- drawing -----

    def refresh(self):
        """Redraw the list picker, progress bar and every item."""
        lists = todo_service.get_lists(self.email)
        self.label_to_id = {self.list_label(todo_list): todo_list.id for todo_list in lists}

        current = next((todo_list for todo_list in lists
                        if todo_list.id == self.selected_list_id), lists[0])
        self.selected_list_id = current.id

        self.list_menu.configure(values=list(self.label_to_id))
        self.list_menu.set(self.list_label(current))

        percent = current.progress()
        self.progress_label.configure(text=f"{current.name}: {percent:.0f}% done")
        self.progress_bar.set(percent / 100)

        for widget in self.item_area.winfo_children():
            widget.destroy()

        items = current.items()
        if not items:
            ctk.CTkLabel(
                self.item_area, text="Nothing here yet. Add your first item below."
            ).pack(pady=20)
        for item in items:
            self.draw_item(item)

        # New widgets need the team's colour theme applied to them.
        if hasattr(self.app, "apply_theme"):
            self.app.apply_theme(ThemeManager.get_palette(), ThemeManager.get_style())

        p = ThemeManager.get_palette()
        s = ThemeManager.get_style()
        font_fam = s["font_family"]
        w_radius = s["widget_radius"]
        b_width = s["border_width"]

    def draw_item(self, item):
        """Draw one item as a card with its details and buttons."""
        overdue = item.is_overdue()
        card = ctk.CTkFrame(self.item_area, border_width=2 if overdue else 1)
        card.pack(fill="x", pady=6, padx=4)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(8, 2))

        if item.is_done():
            prefix = "[DONE] "
        elif overdue:
            prefix = "[OVERDUE] "
        else:
            prefix = ""
        ctk.CTkLabel(
            top_row, text=f"{prefix}{item.title}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", anchor="w")

        due = item.deadline.strftime("%d %b %Y") if item.deadline else "No deadline"
        details = (f"Priority: {item.priority.value.title()}  |  "
                   f"Due: {due}  |  Status: {STATUS_TEXT[item.status]}")
        ctk.CTkLabel(
            top_row, text=details, font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")

        if item.description:
            ctk.CTkLabel(
                card, text=item.description, wraplength=750, justify="left"
            ).pack(anchor="w", padx=12, pady=(2, 6))

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.pack(fill="x", padx=12, pady=(0, 8))

        if item.is_done() and item.completed_at:
            ctk.CTkLabel(
                button_row,
                text=f"Completed: {item.completed_at.strftime('%d %b %Y %H:%M')}",
                font=ctk.CTkFont(size=12)
            ).pack(side="left")

        # item_id=item.id saves this item's ID now. Without it, every
        # button would act on the last item drawn.
        ctk.CTkButton(
            button_row, text="Delete", width=80, height=28,
            command=lambda item_id=item.id: self.delete_item(item_id)
        ).pack(side="right", padx=4)

        if item.is_done():
            ctk.CTkButton(
                button_row, text="Reopen", width=90, height=28,
                command=lambda item_id=item.id: self.set_status(item_id, Status.NOT_STARTED)
            ).pack(side="right", padx=4)
        else:
            ctk.CTkButton(
                button_row, text="Mark Done", width=100, height=28,
                command=lambda item_id=item.id: self.set_status(item_id, Status.DONE)
            ).pack(side="right", padx=4)
            if item.status is Status.NOT_STARTED:
                ctk.CTkButton(
                    button_row, text="Start", width=80, height=28,
                    command=lambda item_id=item.id: self.set_status(item_id, Status.IN_PROGRESS)
                ).pack(side="right", padx=4)

    @staticmethod
    def list_label(todo_list):
        """The text shown for a list in the list picker."""
        if todo_list.is_team_list():
            return f"{todo_list.name} (team)"
        return todo_list.name

    def show_message(self, text):
        """Show a short message above the items, or clear it with ""."""
        self.message_label.configure(text=text)

    # ----- button actions -----

    def run_service(self, action, *args):
        """Call a service method, show any error, and redraw if it worked."""
        try:
            result = action(self.email, *args)
        except TodoError as error:
            self.show_message(f"Couldn't do that: {error}")
            return None
        self.show_message("")
        self.refresh()
        return result

    def choose_list(self, label):
        """Runs when a different list is picked from the list picker."""
        self.selected_list_id = self.label_to_id[label]
        self.show_message("")
        self.refresh()

    def create_list(self):
        """Ask for a name, then make a new custom list and open it."""
        dialog = ctk.CTkInputDialog(text="Name of the new list:", title="New List")
        name = dialog.get_input()
        if name is None:  # the user pressed Cancel
            return
        new_list = self.run_service(todo_service.create_list, name)
        if new_list is not None:
            self.selected_list_id = new_list.id
            self.refresh()

    def add_item(self):
        """Add the item typed into the bar at the bottom."""
        title = self.title_entry.get().strip()
        if not title:
            self.show_message("Type a title for the item first.")
            return

        deadline = None
        deadline_text = self.deadline_entry.get().strip()
        if deadline_text:
            try:
                deadline = datetime.strptime(deadline_text, "%Y-%m-%d").date()
            except ValueError:
                self.show_message("The deadline must look like 2026-11-20.")
                return

        priority = PRIORITY_CHOICES[self.priority_menu.get()]
        description = self.description_entry.get().strip()
        item = self.run_service(todo_service.add_item, self.selected_list_id,
                                title, description, deadline, priority)
        if item is not None:
            self.title_entry.delete(0, "end")
            self.description_entry.delete(0, "end")
            self.deadline_entry.delete(0, "end")

    def set_status(self, item_id, status):
        """Start, finish or reopen an item."""
        self.run_service(todo_service.update_status, self.selected_list_id, item_id, status)

    def delete_item(self, item_id):
        """Delete an item from the selected list."""
        self.run_service(todo_service.delete_item, self.selected_list_id, item_id)