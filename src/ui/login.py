# src/ui/login.py
import sys
import os

# Add project root to path so src imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import customtkinter as ctk
from tkinter import messagebox
from src.ui.app import EmailApp  # Import your main app

# Dummy credentials (you can change these)
USERNAME = "admin"
PASSWORD = "1234"

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Email Parser Organizer")
        self.geometry("400x250")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Username
        ctk.CTkLabel(self, text="Username:").pack(pady=10)
        self.username_entry = ctk.CTkEntry(self, width=200)
        self.username_entry.pack()

        # Password
        ctk.CTkLabel(self, text="Password:").pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, show="*", width=200)
        self.password_entry.pack()

        # Login button
        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=20)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == USERNAME and password == PASSWORD:
            messagebox.showinfo("Success", "Login Successful!")
            self.destroy()
            # Open main Email app
            app = EmailApp()
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")

if __name__ == "__main__":
    login = LoginApp()
    login.mainloop()