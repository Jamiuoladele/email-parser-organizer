import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.ingestion.email_fetcher import fetch_emails
from src.parser.email_parser import Email
from src.parser.categorizer import EmailCategorizer
from src.storage.storage import save_emails, export_to_excel
from src.parser.file_parser import parse_file


class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Parser Organizer")
        self.root.geometry("1300x750")
        self.root.configure(bg="#f5f7fb")

        self.categorizer = EmailCategorizer()
        self.parsed_emails = []

        # HEADER 
        header = tk.Frame(root, bg="#4f46e5", height=60)
        header.pack(side="top", fill="x")

        tk.Label(
            header,
            text="📧 Email Parser Organizer",
            bg="#4f46e5",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        # SIDEBAR 
        sidebar = tk.Frame(root, bg="#111827", width=220)
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar,
            text="MENU",
            bg="#111827",
            fg="#9ca3af",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=20)

        def create_btn(text, cmd):
            btn = tk.Button(
                sidebar,
                text=text,
                command=cmd,
                bg="#1f2937",
                fg="white",
                bd=0,
                padx=10,
                pady=10,
                anchor="w"
            )
            btn.pack(fill="x", padx=10, pady=5)

        create_btn("Fetch Emails", self.fetch_emails)
        create_btn("Upload File", self.upload_file)
        create_btn("Save Emails", self.save_emails)
        create_btn("Export to Excel", self.export_excel)

        # MAIN
        self.main = tk.Frame(root, bg="#f5f7fb")
        self.main.pack(side="left", fill="both", expand=True)

        #  CARDS
        cards = tk.Frame(self.main, bg="#f5f7fb")
        cards.pack(fill="x", padx=20, pady=15)

        self.total_card = self.create_card(cards, "Total Emails", 0, 0)
        self.work_card = self.create_card(cards, "Work", 0, 1)
        self.personal_card = self.create_card(cards, "Personal", 0, 2)
        self.other_card = self.create_card(cards, "Other", 0, 3)

        # INPUT 
        form = tk.Frame(self.main, bg="white")
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Sender", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.sender_entry = tk.Entry(form, width=30)
        self.sender_entry.grid(row=0, column=1)

        tk.Label(form, text="Subject", bg="white").grid(row=1, column=0, padx=5, pady=5)
        self.subject_entry = tk.Entry(form, width=30)
        self.subject_entry.grid(row=1, column=1)

        tk.Label(form, text="Body", bg="white").grid(row=2, column=0, padx=5, pady=5)
        self.body_entry = tk.Entry(form, width=30)
        self.body_entry.grid(row=2, column=1)

        ttk.Button(form, text="Add Email", command=self.add_email)\
            .grid(row=3, column=0, columnspan=2, pady=10)

        #  SEARCH
        search = tk.Frame(self.main, bg="#f5f7fb")
        search.pack(fill="x", padx=20, pady=10)

        tk.Label(search, text="Search:", bg="#f5f7fb").pack(side="left")
        self.search_entry = tk.Entry(search, width=30)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search, text="Search", command=self.search_emails).pack(side="left")
        ttk.Button(search, text="Show All", command=self.display_emails).pack(side="left", padx=5)

        # TABLE 
        table_frame = tk.Frame(self.main)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Sender", "Subject", "Category", "Extracted", "Action"),
            show="headings"
        )

        for col in ("Sender", "Subject", "Category", "Extracted", "Action"):
            self.tree.heading(col, text=col)

        self.tree.column("Sender", width=180)
        self.tree.column("Subject", width=200)
        self.tree.column("Category", width=120)
        self.tree.column("Extracted", width=450)
        self.tree.column("Action", width=80)

        self.tree.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self.handle_click)

        # STATUS
        self.status = tk.Label(root, text="Ready", bg="#4f46e5", fg="white", anchor="w")
        self.status.pack(side="bottom", fill="x")

    # ==CARDS
    def create_card(self, parent, title, value, col):
        frame = tk.Frame(parent, bg="white", width=220, height=100)
        frame.grid(row=0, column=col, padx=10)

        tk.Label(frame, text=title, bg="white", fg="#6b7280").pack(pady=5)
        label = tk.Label(frame, text=value, bg="white", font=("Segoe UI", 16, "bold"))
        label.pack()

        return label

    # LOGIC 
    def update_dashboard(self):
        total = len(self.parsed_emails)
        work = sum(1 for e in self.parsed_emails if e.category == "Work")
        personal = sum(1 for e in self.parsed_emails if e.category == "Personal")
        other = sum(1 for e in self.parsed_emails if e.category == "Other")

        self.total_card.config(text=total)
        self.work_card.config(text=work)
        self.personal_card.config(text=personal)
        self.other_card.config(text=other)

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

        self.sender_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.body_entry.delete(0, tk.END)

    def display_emails(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for email in self.parsed_emails:
            extracted = self.format_extracted(email.extracted_data)

            self.tree.insert("", "end", values=(
                email.sender,
                email.subject,
                email.category,
                extracted,
                "Delete"
            ))

    def format_extracted(self, data):
        parts = []
        if data["phones"]:
            parts.append("Phone: " + ", ".join(data["phones"]))
        if data["emails"]:
            parts.append("Email: " + ", ".join(data["emails"]))
        if data["dates"]:
            parts.append("Date: " + ", ".join(data["dates"]))
        return " | ".join(parts) if parts else "No data"

    def handle_click(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if col == "#5":
            values = self.tree.item(row, "values")

            if messagebox.askyesno("Confirm", "Delete email?"):
                self.parsed_emails = [
                    e for e in self.parsed_emails
                    if not (e.sender == values[0] and e.subject == values[1])
                ]

                self.display_emails()
                self.update_dashboard()

    def search_emails(self):
        keyword = self.search_entry.get().lower()

        filtered = [
            e for e in self.parsed_emails
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
            emails = parse_file(file_path)

            for email in emails:
                email_obj = Email(email["sender"], email["subject"], email["body"])
                email_obj.extract_data()
                self.categorizer.categorize(email_obj)
                self.parsed_emails.append(email_obj)

            self.display_emails()
            self.update_dashboard()

    def save_emails(self):
        save_emails(self.parsed_emails)
        messagebox.showinfo("Saved", "Emails saved")

    def export_excel(self):
        export_to_excel(self.parsed_emails)
        messagebox.showinfo("Exported", "Excel file created")


def main():
    root = tk.Tk()
    app = EmailApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()