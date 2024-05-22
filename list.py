import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Initialize database connection
conn = sqlite3.connect('todo_list.db')
c = conn.cursor()

# Create tasks table
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT,
    priority INTEGER,
    completed BOOLEAN,
    category TEXT
)
''')
conn.commit()

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")

        self.create_widgets()
        self.populate_tasks()

    def create_widgets(self):
        # Task input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Title").grid(row=0, column=0)
        self.title_entry = tk.Entry(input_frame)
        self.title_entry.grid(row=0, column=1, padx=10)

        tk.Label(input_frame, text="Description").grid(row=1, column=0)
        self.description_entry = tk.Entry(input_frame)
        self.description_entry.grid(row=1, column=1, padx=10)

        tk.Label(input_frame, text="Due Date (YYYY-MM-DD)").grid(row=2, column=0)
        self.due_date_entry = tk.Entry(input_frame)
        self.due_date_entry.grid(row=2, column=1, padx=10)

        tk.Label(input_frame, text="Priority (1-5)").grid(row=3, column=0)
        self.priority_entry = tk.Entry(input_frame)
        self.priority_entry.grid(row=3, column=1, padx=10)

        tk.Label(input_frame, text="Category").grid(row=4, column=0)
        self.category_entry = tk.Entry(input_frame)
        self.category_entry.grid(row=4, column=1, padx=10)

        self.add_btn = tk.Button(input_frame, text="Add Task", command=self.add_task)
        self.add_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Task list frame
        self.task_list_frame = tk.Frame(self.root)
        self.task_list_frame.pack()

        self.tree = ttk.Treeview(self.task_list_frame, columns=('ID', 'Title', 'Description', 'Due Date', 'Priority', 'Completed', 'Category'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Title', text='Title')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Due Date', text='Due Date')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Completed', text='Completed')
        self.tree.heading('Category', text='Category')

        self.tree.column('ID', width=30)
        self.tree.column('Title', width=150)
        self.tree.column('Description', width=200)
        self.tree.column('Due Date', width=100)
        self.tree.column('Priority', width=70)
        self.tree.column('Completed', width=70)
        self.tree.column('Category', width=100)

        self.tree.pack()

        self.tree.bind('<Double-1>', self.on_task_select)

        # Task control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.update_btn = tk.Button(control_frame, text="Update Task", command=self.update_task)
        self.update_btn.grid(row=0, column=0, padx=10)

        self.delete_btn = tk.Button(control_frame, text="Delete Task", command=self.delete_task)
        self.delete_btn.grid(row=0, column=1, padx=10)

        self.mark_complete_btn = tk.Button(control_frame, text="Mark as Complete", command=self.mark_task_complete)
        self.mark_complete_btn.grid(row=0, column=2, padx=10)

        self.filter_frame = tk.Frame(self.root)
        self.filter_frame.pack(pady=10)

        tk.Label(self.filter_frame, text="Filter by Category").grid(row=0, column=0)
        self.filter_category_entry = tk.Entry(self.filter_frame)
        self.filter_category_entry.grid(row=0, column=1, padx=10)

        self.filter_btn = tk.Button(self.filter_frame, text="Filter", command=self.filter_tasks)
        self.filter_btn.grid(row=0, column=2, padx=10)

    def populate_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        c.execute("SELECT * FROM tasks")
        rows = c.fetchall()
        for row in rows:
            self.tree.insert('', tk.END, values=row)

    def add_task(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        due_date = self.due_date_entry.get()
        priority = self.priority_entry.get()
        category = self.category_entry.get()

        if title and priority.isdigit() and 1 <= int(priority) <= 5:
            c.execute("INSERT INTO tasks (title, description, due_date, priority, completed, category) VALUES (?, ?, ?, ?, ?, ?)",
                      (title, description, due_date, int(priority), False, category))
            conn.commit()
            self.populate_tasks()
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Invalid input. Ensure title and priority (1-5) are provided.")

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def on_task_select(self, event):
        selected_item = self.tree.selection()[0]
        task = self.tree.item(selected_item, 'values')

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, task[1])
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, task[2])
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, task[3])
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, task[4])
        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, task[6])

        self.selected_task_id = task[0]

    def update_task(self):
        if hasattr(self, 'selected_task_id'):
            title = self.title_entry.get()
            description = self.description_entry.get()
            due_date = self.due_date_entry.get()
            priority = self.priority_entry.get()
            category = self.category_entry.get()

            if title and priority.isdigit() and 1 <= int(priority) <= 5:
                c.execute("UPDATE tasks SET title=?, description=?, due_date=?, priority=?, category=? WHERE id=?",
                          (title, description, due_date, int(priority), category, self.selected_task_id))
                conn.commit()
                self.populate_tasks()
                self.clear_entries()
                delattr(self, 'selected_task_id')
            else:
                messagebox.showerror("Error", "Invalid input. Ensure title and priority (1-5) are provided.")
        else:
            messagebox.showerror("Error", "No task selected for updating.")

    def delete_task(self):
        if hasattr(self, 'selected_task_id'):
            c.execute("DELETE FROM tasks WHERE id=?", (self.selected_task_id,))
            conn.commit()
            self.populate_tasks()
            self.clear_entries()
            delattr(self, 'selected_task_id')
        else:
            messagebox.showerror("Error", "No task selected for deletion.")

    def mark_task_complete(self):
        if hasattr(self, 'selected_task_id'):
            c.execute("UPDATE tasks SET completed=? WHERE id=?", (True, self.selected_task_id))
            conn.commit()
            self.populate_tasks()
            self.clear_entries()
            delattr(self, 'selected_task_id')
        else:
            messagebox.showerror("Error", "No task selected for marking as complete.")

    def filter_tasks(self):
        category = self.filter_category_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)

        c.execute("SELECT * FROM tasks WHERE category LIKE ?", (f"%{category}%",))
        rows = c.fetchall()
        for row in rows:
            self.tree.insert('', tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
    conn.close()
