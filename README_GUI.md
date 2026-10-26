Team 11 Project: GUI Frontend

This README is for whoever is connecting the GUI to the backend (login, database, etc.). The GUI is built with customtkinter. All the window layout and navigation is done. What's left is replacing the placeholder data with real data and calling the GUI from the login code.

1. Running it
bash
pip install customtkinter pillow
cd <project folder>
python gui_main.py

Run it from inside the project folder. The files use flat imports (from base import Page), which only work when that folder is the working directory or on sys.path.

2. File structure
Team-11-Project/
  gui_main.py            # App window, the PAGES registry, show_page()
  base.py                # Page base classes (Page, PlaceholderPage, TodoPage, KnowledgePage)
  widgets.py             # Reusable widgets (Dashboard, SidePanel, Dropdown, NavButton, PostCard)
  pages/
    __init__.py
    personal_todo_list.py
    team_todo_list.py
    knowledge_base.py
File	What's in it
gui_main.py	App (the main window), PAGES (sidebar text -> page class), show_page()
base.py	Page (every screen inherits from this), PlaceholderPage (shown for pages not built yet), TodoPage and KnowledgePage (shared layouts)
widgets.py	The top bar, the sidebar, and the post cards. Contains no backend logic.
pages/*.py	One file per screen. This is where backend calls go.
3. How navigation works
Sidebar button click
   -> Dropdown._clicked / NavButton   (widgets.py)
   -> App.show_page(button_text)      (gui_main.py)
   -> looks up button_text in PAGES
   -> creates the page (first visit only) and displays it
   -> calls page.on_show()
Pages are created once and cached, so they keep their state when you switch away and back.
on_show() runs every time a page is displayed. Load fresh data from the backend in on_show().
The key in PAGES must match the sidebar button text exactly. If a button shows "<name> (not built yet)", the key is missing or misspelled.
python
PAGES = {
    "List 1": PersonalListPage,
    "Team 1": TeamListPage,
    "Knowledge Base": KnowledgeBasePage,
}

Check that the class names in PAGES match the class names inside the page files.

4. Launching from the login code

gui_main.py only starts the window when run directly (if __name__ == "__main__":), so the login code can import it safely:

python
from gui_main import App

app = App()
app.mainloop()

Important: one root window only. customtkinter works best with a single CTk() window. If the login screen is also a CTk window, call login_window.destroy() before creating App(), or make the login a CTkToplevel instead. Having two CTk roots causes strange bugs.

Import paths. If the login code lives in a different folder, the flat imports (from base import Page) may fail. Either add the GUI folder to the path before importing:

python
import sys
sys.path.append("path/to/Team-11-Project")

or convert the files to a package and use relative imports.

5. Where to connect the backend

These are the placeholder spots. Everything else in the GUI is finished.

Location	Currently	What to do
pages/knowledge_base.py -> get_posts()	Returns a hard-coded list of dicts	Replace with a real function that returns posts (format below)
pages/knowledge_base.py -> add_new_post()	Stub / not implemented	Save the new post to the backend, then call self.on_show() to redraw
Knowledge base search bar (self.search)	Displayed but does nothing	Filter posts using self.search.get()
pages/team_todo_list.py -> self.tasks, add_task()	Hard-coded dict, in-memory only	Load tasks from the backend in on_show(), save in add_task()
pages/personal_todo_list.py	Stub page	Same pattern as the team to-do page
widgets.py -> SidePanel -> sections	Hard-coded list names ("List 1", "Team 1", ...)	Build this from the backend (the user's actual lists)
widgets.py -> Dashboard	"Name McNameson", "Dashboard Label", "Dashboard Label2"	Pass in the logged-in user's name; replace the placeholder labels
+ button in Dashboard	No command	Decide what it does and attach a function
Data format for posts

get_posts() must return a list of dictionaries, each with these keys:

python
[
    {"title": "Getting started", "author": "Alex", "body": "Welcome to the knowledge base."},
    {"title": "Team conventions", "author": "Sam",  "body": "How we name files and branches."},
]

Return plain data rather than GUI widgets. The page builds the PostCards itself, because a card needs a parent widget to exist. If you'd rather return something else, agree the format with the GUI author first.

Data format for tasks

Currently a dict of {task_name: description}. If the backend needs more fields (due date, assignee, done/not done), change this to a list of dicts and update refresh(), which is the one method that draws the task list.

6. Rules for editing the GUI code
Don't mix pack and grid in the same parent widget. It raises TclError: cannot use geometry manager "pack" inside ... grid is already managing.... The main App window uses grid. Inside each frame, either is fine, but only one per frame.
Every widget's first argument is its parent. Inside a class, that should be self (or self.some_frame). A widget created with the wrong parent ends up in the wrong place or triggers the error above.
.pack() / .grid() return None. Write w = Widget(...) on one line and w.pack() on the next if you need to keep a reference to w.
Pass functions without parentheses for command=: command=self.save, not command=self.save(). Use lambda only if you need to pass an argument.
widgets.py must not import from pages/. Pages import from widgets.py; the reverse creates a circular import.
Don't use time.sleep() or long-running backend calls on the GUI thread. The window freezes. For slow calls (network, large queries), run them in a threading.Thread and update the GUI with self.after(0, ...) when done.
7. Adding a new page
Create pages/my_page.py:
python
   import customtkinter as ctk
   from base import Page

   class MyPage(Page):
       def __init__(self, master, app):
           super().__init__(master, app)
           ctk.CTkLabel(self, text="Hello").pack(pady=20)

       def on_show(self):
           pass  # load data here

For to-do or knowledge-base style screens, subclass TodoPage or KnowledgePage from base.py instead, to get the standard layout.

Import it in gui_main.py and add one line to PAGES:
python
   "Sidebar Button Text": MyPage,
Make sure a sidebar button with exactly that text exists (see SidePanel in widgets.py).

self.app inside any page gives access to the main window if a page needs it.

8. Troubleshooting
Symptom	Likely cause
Nothing happens when running	Missing if __name__ == "__main__": block, an unsaved file, or an import error. Run from a terminal so the error stays visible.
Window opens but the middle is blank	Nothing has called show_page() yet. Click a sidebar button, or call self.show_page("...") at the end of App.__init__.
"<name> (not built yet)" appears	The button text isn't a key in PAGES.
TclError ... grid is already managing	pack and grid mixed in one parent, or a widget created with the wrong parent.
Popup windows open behind the main window	Use top.transient(self.winfo_toplevel()) and top.after(100, top.lift) (already done for post popups).
Button images show blank	Keep a reference to the CTkImage (self.icon = ...) so it isn't garbage collected.
ModuleNotFoundError for base/widgets	Run from the project folder, or add it to sys.path.
