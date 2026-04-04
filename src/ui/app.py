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
        self.root.title("Email Dashboard")
        self.root.geometry("1100x750")
        self.root.configure(bg="#eef1f5")

        self.categorizer = EmailCategorizer()
        self.parsed_emails = []

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        # ================= SIDEBAR =================
        self.sidebar = tk.Frame(root, bg="#1f2937", width=220)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar,
            text="EMAIL APP",
            bg="#1f2937",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)

        ttk.Button(self.sidebar, text="Fetch Emails", command=self.fetch_emails).pack(fill="x", padx=15, pady=5)
        ttk.Button(self.sidebar, text="Upload File", command=self.upload_file).pack(fill="x", padx=15, pady=5)
        ttk.Button(self.sidebar, text="Save Emails", command=self.save_emails).pack(fill="x", padx=15, pady=5)
        ttk.Button(self.sidebar, text="Export to Excel", command=self.export_excel).pack(fill="x", padx=15, pady=5)

        # ================= MAIN =================
        self.main = tk.Frame(root, bg="#eef1f5")
        self.main.pack(side="right", fill="both", expand=True)

        # ================= CARDS =================
        self.cards_frame = tk.Frame(self.main, bg="#eef1f5")
        self.cards_frame.pack(fill="x", padx=20, pady=15)

        self.total_card = self.create_card(self.cards_frame, "Total Emails", "0", 0)
        self.work_card = self.create_card(self.cards_frame, "Work", "0", 1)
        self.personal_card = self.create_card(self.cards_frame, "Personal", "0", 2)
        self.other_card = self.create_card(self.cards_frame, "Other", "0", 3)

        # ================= INPUT =================
        input_frame = tk.Frame(self.main, bg="white")
        input_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(input_frame, text="Sender", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.sender_entry = tk.Entry(input_frame, width=35)
        self.sender_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Subject", bg="white").grid(row=1, column=0, padx=5, pady=5)
        self.subject_entry = tk.Entry(input_frame, width=35)
        self.subject_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Body", bg="white").grid(row=2, column=0, padx=5, pady=5)
        self.body_entry = tk.Entry(input_frame, width=35)
        self.body_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Email", command=self.add_email)\
            .grid(row=3, column=0, columnspan=2, pady=10)

        # ================= SEARCH =================
        search_frame = tk.Frame(self.main, bg="#eef1f5")
        search_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(search_frame, text="Search:", bg="#eef1f5").pack(side="left")

        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="Search", command=self.search_emails).pack(side="left")
        ttk.Button(search_frame, text="Show All", command=self.display_emails).pack(side="left", padx=5)

        # ================= TABLE =================
        table_frame = tk.Frame(self.main)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Sender", "Subject", "Category", "Extracted", "Action"),
            show="headings"
        )

        self.tree.heading("Sender", text="Sender")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Extracted", text="Extracted")
        self.tree.heading("Action", text="Action")

        self.tree.column("Sender", width=180)
        self.tree.column("Subject", width=180)
        self.tree.column("Category", width=120)
        self.tree.column("Extracted", width=300)
        self.tree.column("Action", width=100)

        self.tree.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")

        # Row colors
        self.tree.tag_configure("odd", background="#f9fafb")
        self.tree.tag_configure("even", background="white")

        self.tree.bind("<ButtonRelease-1>", self.handle_click)

        # ================= STATUS =================
        self.status = tk.Label(root, text="Ready", bg="#d1d5db", anchor="w")
        self.status.pack(side="bottom", fill="x")

    # ================= CARD =================
    def create_card(self, parent, title, value, col):
        frame = tk.Frame(parent, bg="white", width=220, height=100)
        frame.grid(row=0, column=col, padx=10)
        frame.pack_propagate(False)

        tk.Label(frame, text=title, bg="white", fg="#6b7280",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=5)

        label = tk.Label(frame, text=value, bg="white", fg="#111827",
                         font=("Segoe UI", 20, "bold"))
        label.pack(anchor="w", padx=10)

        return label

    # ================= LOGIC =================
    def update_dashboard(self):
        total = len(self.parsed_emails)
        work = sum(1 for e in self.parsed_emails if e.category == "Work")
        personal = sum(1 for e in self.parsed_emails if e.category == "Personal")
        other = sum(1 for e in self.parsed_emails if e.category == "Other")

        self.total_card.config(text=str(total))
        self.work_card.config(text=str(work))
        self.personal_card.config(text=str(personal))
        self.other_card.config(text=str(other))

    def update_status(self, msg):
        self.status.config(text=msg)

    def add_email(self):
        sender = self.sender_entry.get()
        subject = self.subject_entry.get()
        body = self.body_entry.get()

        if not sender or not subject:
            messagebox.showwarning("Warning", "Sender and Subject required")
            return

        email_obj = Email(sender, subject, body)
        email_obj.extract_data()
        self.categorizer.categorize(email_obj)

        self.parsed_emails.append(email_obj)

        self.display_emails()
        self.update_dashboard()
        self.update_status("Email added")

        self.sender_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.body_entry.delete(0, tk.END)

    def handle_click(self, event):
        selected = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if column == "#5":
            values = self.tree.item(selected, "values")

            if messagebox.askyesno("Confirm", "Delete this email?"):
                self.parsed_emails = [
                    e for e in self.parsed_emails
                    if not (e.sender == values[0] and e.subject == values[1])
                ]

                self.display_emails()
                self.update_dashboard()

    def display_emails(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, email in enumerate(self.parsed_emails):
            tag = "even" if i % 2 == 0 else "odd"
            extracted = self.format_extracted(email.extracted_data)

            self.tree.insert("", "end", values=(
                email.sender,
                email.subject,
                email.category,
                extracted,
                "Delete"
            ), tags=(tag,))

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
            e for e in self.parsed_emails
            if keyword in e.sender.lower()
            or keyword in e.subject.lower()
            or keyword in e.category.lower()
        ]

        self.display_filtered(filtered)

    def display_filtered(self, emails):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, email in enumerate(emails):
            tag = "even" if i % 2 == 0 else "odd"
            extracted = self.format_extracted(email.extracted_data)

            self.tree.insert("", "end", values=(
                email.sender,
                email.subject,
                email.category,
                extracted,
                "Delete"
            ), tags=(tag,))

    def save_emails(self):
        save_emails(self.parsed_emails)
        messagebox.showinfo("Success", "Saved successfully")

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("XML files", "*.xml"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            emails = parse_file(file_path)

            for email in emails:
                email_obj = Email(email["sender"], email["subject"], email["body"])
                email_obj.extract_data()
                self.categorizer.categorize(email_obj)
                self.parsed_emails.append(email_obj)

            self.display_emails()
            self.update_dashboard()

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

    def export_excel(self):
        if not self.parsed_emails:
            messagebox.showwarning("Warning", "No emails to export")
            return

        export_to_excel(self.parsed_emails)
        messagebox.showinfo("Success", "Excel exported!")


def main():
    root = tk.Tk()
    app = EmailApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()