# Developer Guide: Teams, Sample Data & Personal To-Do Integration

This guide explains how authentication state, user identity, dynamic team rendering, and theming are passed through the application, and how to integrate the **Personal To-Do List** subsystem cleanly on top of this architecture.

---

## 1. Architecture & Execution Flow

```text
main.py 
   │
   ├──> run_login() (login_module.py)
   │       └── Returns: (user_id: int [0, 1, or 2], login_time: datetime)
   │
   └──> start_main_application(user_id, login_time) (GUI_main.py)
           │
           ├── Retrieves user profile: LIVE_USERS[user_id]
           ├── Filters visible teams: get_user_teams(user_id)
           ├── Updates Top Bar: Dashboard.set_user(current_user)
           ├── Injects teams into Sidebar: SidePanel(team_items=...)
           └── Subscribes to ThemeManager for live design styling
```

---

## 2. Sample Data Architecture (`sample_data.py`)

All demo data is held **in-memory**. Changes made during the runtime session (e.g., ticking off tasks, adding new tasks) will reset upon application restart.

### 2.1 Demo Accounts
The system recognizes 3 live access accounts passed directly from login:

| ID | User Name | Role | Access Scope |
| :--- | :--- | :--- | :--- |
| **`0`** | Alice | **Manager / Admin** | Full read/write access across all teams (`Team 1` – `Team 4`). |
| **`1`** | Dilip | **Team Leader** | Can create/reassign tasks, review, and approve high-risk tasks for teams led or joined (`Team 1`, `Team 2`, `Team 3`). |
| **`2`** | Liam | **Employee** | Can update own progress and complete routine tasks. Only sees teams they are an assigned member of (`Team 1`, `Team 2`). |

```python
from sample_data import LIVE_USERS, ALL_TEAMS, get_user_teams

# Example: Get full user dictionary
user = LIVE_USERS[0]
print(user["name"], user["role"], user["email"])

# Example: Get only the teams permitted for the current user
permitted_teams = get_user_teams(user_id=2)  # Returns dict containing Team 1 and Team 2 only
```

---

## 3. Dynamic Team System (`pages/team_todo_list.py`)

* Instead of hardcoded static pages, each team page is an instance of `TeamListPage(master, app, team_key="Team X")`.
* In `GUI_main.py`, `show_page(name)` dynamically catches any team key in `self.allowed_teams` and initializes its view:
  ```python
  if name in self.allowed_teams:
      self.pages[name] = TeamListPage(self.content, self, team_key=name)
  ```
* **Role Permissions Enforced in View:**
  * Only Managers (`0`) and the designated Team Leader for that team can view the **"Add Task"** panel.
  * Routine tasks can be marked complete by the assignee.
  * **High-Risk Tasks** require Manager or Team Leader sign-off before completion is finalized.
  * Past-deadline tasks automatically display the `[OVERDUE]` badge and highlighted border.

---

## 4. How to Integrate the Personal To-Do List

The team member responsible for `pages/personal_todo_list.py` can integrate their `PersonalTodoService` using either the **`app.current_user` object** or `sample_data.py`.

### Option A: The Recommended Approach (Direct App Context)

Because `App` already initializes with `self.current_user` and `self.current_user_id`, the Personal To-Do page can access the logged-in user's email directly through `self.app`:

```python
# pages/personal_todo_list.py
import customtkinter as ctk
from base import Page
from personal_todo import PersonalTodoService, Priority, Status, TodoError

class PersonalListPage(Page):
    title = "Personal To-do List"

    def __init__(self, master, app):
        super().__init__(master, app)

        # 1. Retrieve the authenticated user's email from the main App
        self.user_email = self.app.current_user.get("email", "user@company.co.uk")

        # 2. Instantiate or connect the service
        self.todo_service = PersonalTodoService()
        self.todo_service.on_change(self.refresh)

        # UI Layout
        self.title_label = ctk.CTkLabel(
            self, 
            text=f"My Tasks ({self.app.current_user['name']})", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 10))

        self.scroll_area = ctk.CTkScrollableFrame(self)
        self.scroll_area.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        # Clear existing items
        for widget in self.scroll_area.winfo_children():
            widget.destroy()

        # Render lists for the logged-in user's email
        for todo_list in self.todo_service.get_lists(self.user_email):
            header = ctk.CTkLabel(
                self.scroll_area, 
                text=f"{todo_list.name} ({todo_list.progress()}%)",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            header.pack(anchor="w", pady=(10, 4))

            for item in todo_list.items():
                item_card = ctk.CTkFrame(self.scroll_area)
                item_card.pack(fill="x", pady=2)
                
                status_text = "[DONE]" if item.status == Status.COMPLETED else "[OPEN]"
                ctk.CTkLabel(item_card, text=f"{status_text} {item.title}").pack(side="left", padx=10)

                if item.status != Status.COMPLETED:
                    ctk.CTkButton(
                        item_card, 
                        text="Done", 
                        width=60, 
                        command=lambda l=todo_list.id, i=item.id: self._tick(l, i)
                    ).pack(side="right", padx=6)

    def _tick(self, list_id, item_id):
        try:
            self.todo_service.tick_item(self.user_email, list_id, item_id)
        except TodoError as err:
            print(f"Error updating item: {err}")
```

### Option B: Dynamically Populating the Sidebar with Personal Lists

To have custom personal to-do lists appear inside the sidebar dropdown dynamically:
1. In `personal_todo_list.py` or `GUI_main.py`, fetch the list names:
   ```python
   user_lists = [l.name for l in todo_service.get_lists(app.current_user["email"])]
   ```
2. Update the sidebar dropdown via `widgets.py`:
   ```python
   self.sidePanel.dropdowns["personal"].set_items(user_lists)
   ```

---

## 5. Live Design Studio & Theme System

* Themes are handled entirely outside widget logic.
* You do **not** need to hardcode colors or corner radii in custom widgets.
* All elements inheriting from `CTkButton`, `CTkFrame`, `CTkEntry`, and `CTkOptionMenu` will automatically be restyled in real-time when testers adjust options in the **Theme Studio** window.