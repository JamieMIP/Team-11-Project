import customtkinter as ctk

"""
app = ctk.CTk()
app.title("My First App")
app.geometry("400x300")




button = ctk.CTkButton(app, text="Button", command=button_pressed)
#button.pack(pady=10)

comboBox = ctk.CTkComboBox(app, values=["1", "2", "3"])
#comboBox.pack(pady=10)


ctk.CTkLabel(app, text="Name:").grid(row=0, column=0, padx=10, pady=10)
ctk.CTkEntry(app).grid(row=0, column=1, padx=10, pady=10)
ctk.CTkLabel(app, text="Email:").grid(row=1, column=0, padx=10, pady=10)
ctk.CTkEntry(app).grid(row=1, column=1, padx=10, pady=10)


frame = ctk.CTkFrame(app)
frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")


ctk.CTkLabel(frame, text="Inside the frame").pack(pady=10)
ctk.CTkButton(frame, text="Also inside").pack(pady=10)

#CTkLabel, CTkButton, CTkEntry, CTkCheckBox, CTkSwitch, CTkSlider, CTkOptionMenu, CTkComboBox, CTkTextbox, CTkProgressBar, CTkFrame

"""


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My First App")
        self.geometry("400x300")
        self.minsize(400, 300)

        self.dashboard = Dashboard(self)             # create it, parent is the window
        self.dashboard.pack(fill="x", padx=10, pady=10)

        self.button = ctk.CTkButton(self, text="Click Me", command=self.button_pressed)
        self.button.pack(pady=10)

    def button_pressed(self):
        print("Button pressed!")

class Dashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text="Dashboard")
        self.label.pack(side="right", pady=2)
        
        
        self.Dashboardlabel = ctk.CTkLabel(self, text="Dashboard Label")
        self.Dashboardlabel.pack(side="left", fill="x", pady=10, padx=10)
        self.Dashboardlabel2 = ctk.CTkLabel(self, text="Dashboard Label2")
        self.Dashboardlabel2.pack(side="left", fill="x", pady=30, padx=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()



