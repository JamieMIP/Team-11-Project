import customtkinter as ctk
from base import Page

class KnowledgePage(Page):
    """Layout for knowledge base pages: title, search bar, post area."""
    title = "Knowledge Base"

    def __init__(self, master, app):
        super().__init__(master, app)
        ctk.CTkLabel(self, text=self.title,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 10))

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search = ctk.CTkEntry(top_bar, placeholder_text="Search posts...")
        self.search.pack(side="left", fill="x", expand=True)

        self.add_new_post_button = ctk.CTkButton(top_bar, text="Add New Post", width=120,
                                                command=self.add_new_post)
        self.add_new_post_button.pack(side="left", padx=(10, 0))

        self.post_area = ctk.CTkScrollableFrame(self)
        self.post_area.pack(fill="both", expand=True)

        self.post = []

    def add_new_post(self):
        top = ctk.CTkToplevel(self)
        top.title(f"Create new post")
        top.geometry("600x450")
        
        top.transient(self.winfo_toplevel())   
        top.after(100, top.lift)               
        top.after(100, top.focus)
        
        ctk.CTkLabel(top, text=f"Create new post", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 0))
        post_title = ctk.CTkEntry(top, placeholder_text="Post title...")
        post_title.pack(fill="x", padx=10, pady=10)

        author_entry = ctk.CTkEntry(top, placeholder_text="Author name here...")
        author_entry.pack(fill="x", padx=10, pady=10)

        file_entry = ctk.CTkEntry(top, placeholder_text="File additions here...")
        file_entry.pack(fill="x", padx=10, pady=10)

        post_entry = ctk.CTkTextbox(top, height=120)
        post_entry.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(top, text="Submit Post", command=lambda: self.submit_post(post_title.get(), post_entry.get("1.0", "end-1c"), author_entry.get(), file_entry.get(), top)).pack(pady=10)

    
