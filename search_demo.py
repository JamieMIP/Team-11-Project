import tkinter as tk

import customtkinter as ctk

from forums.forum_models import TopicCategory
from forums.post_search import search_posts
from forums.sample_data import build_sample_forum


class SearchDemo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Post Search Demo")
        self.geometry("850x700")

        self.forum = build_sample_forum()
        self.search_text = tk.StringVar(master=self)

        # Display names map to the values used by the search function.
        self.topic_options = {"All topics": None}
        self.topic_options.update({
            topic.name: topic.id
            for topic in self.forum.get_topics()
        })

        self.category_options = {
            "All categories": None,
            "Technical": TopicCategory.TECHNICAL,
            "Non-technical": TopicCategory.NON_TECHNICAL,
        }

        ctk.CTkLabel(
            self,
            text="Search posts",
            font=("", 24),
        ).pack(padx=20, pady=(20, 5), anchor="w")

        ctk.CTkLabel(
            self,
            text="Search titles and content as you type.",
        ).pack(padx=20, anchor="w")

        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_text,
            height=40,
        )
        self.search_entry.pack(fill="x", padx=20, pady=15)

        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            filters_frame,
            text="Topic:",
        ).grid(row=0, column=0, padx=(0, 8))

        self.topic_menu = ctk.CTkOptionMenu(
            filters_frame,
            values=list(self.topic_options),
            command=self.refresh_results,
            width=210,
        )
        self.topic_menu.grid(row=0, column=1, padx=(0, 20))
        self.topic_menu.set("All topics")

        ctk.CTkLabel(
            filters_frame,
            text="Category:",
        ).grid(row=0, column=2, padx=(0, 8))

        self.category_menu = ctk.CTkOptionMenu(
            filters_frame,
            values=list(self.category_options),
            command=self.refresh_results,
            width=170,
        )
        self.category_menu.grid(row=0, column=3)
        self.category_menu.set("All categories")

        ctk.CTkButton(
            self,
            text="Clear search and filters",
            command=self.clear_search,
        ).pack(padx=20, pady=(0, 10), anchor="w")

        self.result_count = ctk.CTkLabel(self, text="")
        self.result_count.pack(padx=20, anchor="w")

        self.results_frame = ctk.CTkScrollableFrame(self)
        self.results_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(5, 20),
        )

        self.search_text.trace_add("write", self.refresh_results)
        self.forum.on_change(self.refresh_results)

        self.refresh_results()
        self.search_entry.focus_set()

    def refresh_results(self, *_):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        topic_id = self.topic_options[self.topic_menu.get()]
        category = self.category_options[self.category_menu.get()]

        matches = search_posts(
            self.forum.get_all_posts(),
            query=self.search_text.get(),
            topic_id=topic_id,
            category=category,
        )

        noun = "post" if len(matches) == 1 else "posts"
        self.result_count.configure(
            text=f"{len(matches)} {noun} found"
        )

        if not matches:
            ctk.CTkLabel(
                self.results_frame,
                text="No matching posts. Try changing the text or filters.",
                wraplength=650,
            ).pack(pady=20)
            return

        for post in matches:
            card = ctk.CTkFrame(self.results_frame)
            card.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                card,
                text=post.title,
                font=("", 16, "bold"),
                anchor="w",
                wraplength=700,
                justify="left",
            ).pack(fill="x", padx=12, pady=(10, 3))

            ctk.CTkLabel(
                card,
                text=(
                    f"{post.topic.name} | "
                    f"Posted by {post.author_name} | "
                    f"{post.created_at:%d %b %Y}"
                ),
                anchor="w",
                wraplength=700,
                justify="left",
            ).pack(fill="x", padx=12)

            ctk.CTkLabel(
                card,
                text=post.preview(),
                anchor="w",
                wraplength=700,
                justify="left",
            ).pack(fill="x", padx=12, pady=(3, 10))

    def clear_search(self):
        self.topic_menu.set("All topics")
        self.category_menu.set("All categories")
        self.search_text.set("")
        self.search_entry.focus_set()


if __name__ == "__main__":
    app = SearchDemo()
    app.mainloop()