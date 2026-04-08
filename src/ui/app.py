import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.ingestion.email_fetcher import fetch_emails
from src.parser.email_parser import Email
from src.parser.categorizer import EmailCategorizer
from src.storage.storage import save_emails, export_to_excel
from src.parser.file_parser import parse_file

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class EmailApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Email Parser Organizer")
        self.geometry("1300x750")

        self.categorizer = EmailCategorizer()
        self.parsed_emails = []
        self.uploaded_files = []  # Track uploaded files

        # HEADER
        header = ctk.CTkFrame(self, height=60, fg_color="#4f46e5")
        header.pack(side="top", fill="x")
        ctk.CTkLabel(
            header, text="Email Parser Organizer", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # SIDEBAR
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#111827")
        sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(
            sidebar, text="MENU", font=ctk.CTkFont(size=14, weight="bold"), text_color="#9ca3af"
        ).pack(pady=20)

        ctk.CTkButton(sidebar, text="Fetch Emails", command=self.fetch_emails).pack(
            pady=5, padx=10, fill="x"
        )
        ctk.CTkButton(sidebar, text="Upload File", command=self.upload_file).pack(
            pady=5, padx=10, fill="x"
        )
        ctk.CTkButton(sidebar, text="Save Emails", command=self.save_emails).pack(
            pady=5, padx=10, fill="x"
        )
        ctk.CTkButton(sidebar, text="Export to Excel", command=self.export_excel).pack(
            pady=5, padx=10, fill="x"
        )

        # MAIN CONTENT
        self.main = ctk.CTkFrame(self, fg_color="#1e293b")
        self.main.pack(side="left", fill="both", expand=True)

        # DASHBOARD CARDS
        cards_frame = ctk.CTkFrame(self.main, fg_color="#1e293b")
        cards_frame.pack(pady=15, padx=20, fill="x")

        self.total_card = self.create_card(cards_frame, "Total Emails", 0)
        self.work_card = self.create_card(cards_frame, "Work", 0)
        self.personal_card = self.create_card(cards_frame, "Personal", 0)
        self.other_card = self.create_card(cards_frame, "Other", 0)

        # TABS
        self.tabs = ctk.CTkTabview(self.main)
        self.tabs.pack(expand=True, fill="both", padx=20, pady=10)
        self.tabs.add("Add/Search")
        self.tabs.add("Email Table")

        # ADD / SEARCH EMAILS TAB
        self.add_tab_widgets()
        # EMAIL TABLE TAB
        self.table_tab_widgets()

        # STATUS BAR
        self.status = ctk.CTkLabel(self, text="Ready", anchor="w", fg_color="#4f46e5")
        self.status.pack(side="bottom", fill="x")

    # -------------------- WIDGETS --------------------
    def create_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, width=220, height=100)
        card.pack(side="left", padx=10, fill="both", expand=True)
        ctk.CTkLabel(card, text=title, text_color="#cbd5e1").pack(pady=5)
        label = ctk.CTkLabel(
            card, text=str(value), font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack()
        return label

    def add_tab_widgets(self):
        tab = self.tabs.tab("Add/Search")

        # INPUT FORM
        form_frame = ctk.CTkFrame(tab, fg_color="#334155")
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="Sender:").grid(row=0, column=0, padx=5, pady=5)
        self.sender_entry = ctk.CTkEntry(form_frame, width=250)
        self.sender_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Subject:").grid(row=1, column=0, padx=5, pady=5)
        self.subject_entry = ctk.CTkEntry(form_frame, width=250)
        self.subject_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Body:").grid(row=2, column=0, padx=5, pady=5)
        self.body_entry = ctk.CTkEntry(form_frame, width=250)
        self.body_entry.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkButton(form_frame, text="Add Email", command=self.add_email).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        # SEARCH
        search_frame = ctk.CTkFrame(tab, fg_color="#334155")
        search_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=250)
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Search", command=self.search_emails).pack(
            side="left", padx=5
        )
        ctk.CTkButton(search_frame, text="Show All", command=self.display_emails).pack(
            side="left", padx=5
        )

        # UPLOADED FILES DISPLAY
        self.files_frame = ctk.CTkFrame(tab, fg_color="#334155")
        self.files_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(self.files_frame, text="Uploaded Files:", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w"
        )
        self.file_labels = []

    def table_tab_widgets(self):
        tab = self.tabs.tab("Email Table")
        table_frame = ctk.CTkFrame(tab, fg_color="#1e293b")
        table_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.tree = ctk.CTkScrollableFrame(table_frame)
        self.tree.pack(expand=True, fill="both")
        self.tree_inner = []

    # -------------------- LOGIC --------------------
    def update_dashboard(self):
        total = len(self.parsed_emails)
        work = sum(1 for e in self.parsed_emails if e.category == "Work")
        personal = sum(1 for e in self.parsed_emails if e.category == "Personal")
        other = sum(1 for e in self.parsed_emails if e.category == "Other")
        self.total_card.configure(text=str(total))
        self.work_card.configure(text=str(work))
        self.personal_card.configure(text=str(personal))
        self.other_card.configure(text=str(other))

    def add_email(self):
        sender = self.sender_entry.get()
        subject = self.subject_entry.get()
        body = self.body_entry.get()

        if not sender or not subject:
            messagebox.showwarning("Warning", "Sender & Subject required")
            return

        email_obj = Email(sender, subject, body)
        email_obj.extract_data()
        self.categorizer.categorize(email_obj)
        self.parsed_emails.append(email_obj)

        self.display_emails()
        self.update_dashboard()

        self.sender_entry.delete(0, "end")
        self.subject_entry.delete(0, "end")
        self.body_entry.delete(0, "end")

    def display_emails(self):
        # Clear old widgets
        for widget in self.tree_inner:
            widget.destroy()
        self.tree_inner.clear()

        for email in self.parsed_emails:
            text = f"{email.sender} | {email.subject} | {email.category} | {self.format_extracted(email.extracted_data)}"
            lbl = ctk.CTkLabel(
                self.tree, text=text, fg_color="#475569", corner_radius=5, pady=5
            )
            lbl.pack(fill="x", padx=5, pady=2)
            self.tree_inner.append(lbl)

    def format_extracted(self, data):
        parts = []
        if data["phones"]:
            parts.append("Phone: " + ", ".join(data["phones"]))
        if data["emails"]:
            parts.append("Email: " + ", ".join(data["emails"]))
        if data["dates"]:
            parts.append("Date: " + ", ".join(data["dates"]))
        return " | ".join(parts) if parts else "No data"

    def search_emails(self):
        keyword = self.search_entry.get().lower()
        filtered = [
            e
            for e in self.parsed_emails
            if keyword in e.sender.lower()
            or keyword in e.subject.lower()
            or keyword in e.category.lower()
        ]
        self.parsed_emails = filtered
        self.display_emails()

    def fetch_emails(self):
        self.parsed_emails.clear()
        emails = fetch_emails()
        for email in emails:
            email_obj = Email(email["sender"], email["subject"], email["body"])
            email_obj.extract_data()
            self.categorizer.categorize(email_obj)
            self.parsed_emails.append(email_obj)
        self.display_emails()
        self.update_dashboard()

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.uploaded_files.append(file_path)
            emails = parse_file(file_path)
            for email in emails:
                email_obj = Email(email["sender"], email["subject"], email["body"])
                email_obj.extract_data()
                self.categorizer.categorize(email_obj)
                self.parsed_emails.append(email_obj)
            self.display_emails()
            self.update_dashboard()
            self.show_uploaded_files()

    def show_uploaded_files(self):
        # Clear old file labels
        for lbl, btn in self.file_labels:
            lbl.destroy()
            btn.destroy()
        self.file_labels.clear()

        for file_path in self.uploaded_files:
            file_frame = ctk.CTkFrame(self.files_frame, fg_color="#475569", corner_radius=5)
            file_frame.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(file_frame, text=file_path)
            lbl.pack(side="left", padx=5)
            btn = ctk.CTkButton(file_frame, text="Delete", width=60, command=lambda f=file_path: self.delete_file(f))
            btn.pack(side="right", padx=5)
            self.file_labels.append((lbl, btn))

    def delete_file(self, file_path):
        if file_path in self.uploaded_files:
            self.uploaded_files.remove(file_path)
            self.show_uploaded_files()
            # Remove emails from this file
            self.parsed_emails = [e for e in self.parsed_emails if getattr(e, "source_file", None) != file_path]
            self.display_emails()
            self.update_dashboard()

    def save_emails(self):
        save_emails(self.parsed_emails)
        messagebox.showinfo("Saved", "Emails saved")

    def export_excel(self):
        export_to_excel(self.parsed_emails)
        messagebox.showinfo("Exported", "Excel file created")


if __name__ == "__main__":
    app = EmailApp()
    app.mainloop()