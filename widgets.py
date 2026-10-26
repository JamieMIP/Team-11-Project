import customtkinter as ctk
from base import Page



class Dashboard(ctk.CTkFrame): # top bar of the app, contains the dashboard label and the add button
    def __init__(self, master):
        super().__init__(master)
        
        
        """
        self.Dashboardlabel = ctk.CTkLabel(self, text="Dashboard Label")
        self.Dashboardlabel.pack(side="left", fill="x", pady=0, padx=0)
        self.Dashboardlabel2 = ctk.CTkLabel(self, text="Dashboard Label2")
        self.Dashboardlabel2.pack(side="left",
            fill="x", pady=30,
            padx=20)
        """

        size = 50
        self.circle_btn = ctk.CTkButton(
            self,
            text="+",
            width=size,
            height=size,
            corner_radius=size // 2)
        self.circle_btn.pack(side="right",
                    padx=20,
                    pady=10,)

        self.label = ctk.CTkLabel(self, text="Name McNameson")
        self.label.pack(side="right", pady=2, padx=10)

class SidePanel(ctk.CTkFrame): # frame for the side panel
    def __init__(self, master, command=None):
        super().__init__(master)
        
        sections = {
            "Personal To-do List": ["List 1", "List 2", "..."],
            "Team To-do List": ["Team 1", "Team 2", "..."],
        }
        for title, items in sections.items():
            Dropdown(self, title, items, command=command).pack(   
                fill="x", padx=(10, 40), pady=10)

        NavButton(self, "Knowledge Base", command=command).pack(
            fill="x", padx=(10, 40), pady=10)

class NavButton(ctk.CTkFrame): # class for buttons in side panel, currently only knowledge base button uses this class
    """A sidebar entry that goes straight to a page (no dropdown)."""
    def __init__(self, master, title, command=None, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkButton(self, text=f"   {title}", anchor="w", fg_color="transparent",
                      command=lambda: command(title) if command else None
                      ).pack(fill="x")

class Dropdown(ctk.CTkFrame): # class for the dropdown menus in the side panel
    def __init__(self, master, title, items, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        self.open = False
        self.command = command

        self.header = ctk.CTkButton(self, text=f"▶ {title}", anchor="w",
                                    fg_color="transparent", command=self.toggle)
        self.header.pack(fill="x")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        for item in items:
            ctk.CTkButton(self.body, text=item, anchor="w",
                          command=lambda i=item: self._clicked(i)).pack(fill="x", padx=(20, 0), pady=1)

    def _clicked(self, item):
        if self.command:
            self.command(item)

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.body.pack(fill="x")
            self.header.configure(text=f"▼ {self.title}")
        else:
            self.body.pack_forget()
            self.header.configure(text=f"▶ {self.title}")


class PostCard(ctk.CTkFrame):
    def __init__(self, master, post, size=300):
        super().__init__(master, width=size, height=size,
                         corner_radius=12, border_width=2,
                         border_color="gray40")
        self.pack_propagate(False)
        self.post = post

        ctk.CTkLabel(self, text=post["title"], anchor="w", justify="left",
                     wraplength=size - 30,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(fill="x", padx=12, pady=(12, 0))
        ctk.CTkLabel(self, text=f"by {post['author']}", anchor="w",
                     text_color="gray").pack(fill="x", padx=12)
        ctk.CTkLabel(self, text=post["body"], anchor="nw", justify="left",
                     wraplength=size - 30).pack(fill="both", expand=True, padx=12, pady=(6, 12))

        
        
        ctk.CTkButton(self, text="Expand", width=80, height=30, command=self.expand_post).pack(side="right", padx=10, pady=10)
        ctk.CTkButton(self, text="Reply", width=80, height=30, command=self.reply_post).pack(side="right", padx=10, pady=10)

    def expand_post(self):
        """Expand the post to show full content in a new window."""
        top = ctk.CTkToplevel(self)
        top.title(self.post["title"])
        top.geometry("400x400")

        top.transient(self.winfo_toplevel())   
        top.after(100, top.lift)               
        top.after(100, top.focus)

        ctk.CTkLabel(top, text=self.post["title"], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 0))
        ctk.CTkLabel(top, text=f"by {self.post['author']}", text_color="gray").pack()
        ctk.CTkLabel(top, text=self.post["body"], wraplength=380).pack(pady=10, padx=10)

    def reply_post(self):
        """Open a reply window to allow the user to reply to the post."""
        top = ctk.CTkToplevel(self)
        top.title(f"Reply to {self.post['title']}")
        top.geometry("600x450")

        top.transient(self.winfo_toplevel())   
        top.after(100, top.lift)               
        top.after(100, top.focus)

        ctk.CTkLabel(top, text=f"Replying to: {self.post['title']}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 0))
        reply_entry = ctk.CTkEntry(top, placeholder_text="Type your reply here...")
        reply_entry.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top, text="Submit Reply", command=lambda: self.submit_reply(reply_entry.get(), top)).pack(pady=10)
        

