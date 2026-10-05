import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from finance_classes import Transaction, FinanceManager, TransactionType


class FinanceApp:
    def __init__(self, root):
        self.manager = FinanceManager()
        self.root = root
        self.root.title("Учет личных финансов")
        self.root.geometry("800x600")
        self.setup_ui()

    def setup_ui(self):
        # Форма ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавить операцию", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, state="readonly")
        names = []
        for cat in self.manager.categories:
            names.append(cat.name)
        self.category_combo["values"] = names
        self.category_combo.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=2, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Описание:").grid(row=3, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=3, column=1, padx=5, pady=2)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Добавить операцию", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить выбранную", command=self.delete_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Аналитика", command=self.show_analytics).pack(side=tk.LEFT, padx=5)

        # Баланс
        info_frame = ttk.LabelFrame(self.root, text="Финансовая информация", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.balance_label = ttk.Label(info_frame, text="", font=("Arial", 12, "bold"))
        self.balance_label.pack()
        self.update_balance()

        # Таблица
        table_frame = ttk.LabelFrame(self.root, text="История операций", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("date", "category", "type", "amount", "desc")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("type", text="Тип")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("desc", text="Описание")
        self.tree.column("date", width=100)
        self.tree.column("category", width=120)
        self.tree.column("type", width=80)
        self.tree.column("amount", width=100)
        self.tree.column("desc", width=200)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.update_table()

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category_name = self.category_var.get()
            date = self.date_entry.get()
            description = self.desc_entry.get()

            if not category_name or not date:
                messagebox.showwarning("Ошибка", "Заполните обязательные поля!")
                return

            category = None
            for cat in self.manager.categories:
                if cat.name == category_name:
                    category = cat
                    break

            if not category:
                messagebox.showwarning("Ошибка", "Выберите категорию!")
                return

            t = Transaction(amount, category, date, description)
            self.manager.add_transaction(t)
            self.update_table()
            self.update_balance()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")

    def delete_transaction(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            self.manager.delete_transaction(index)
            self.update_table()
            self.update_balance()
        else:
            messagebox.showwarning("Ошибка", "Выберите операцию!")

    def show_analytics(self):
        summary = self.manager.get_category_summary()
        win = tk.Toplevel(self.root)
        win.title("Аналитика по категориям")
        win.geometry("300x400")

        if not summary:
            ttk.Label(win, text="Нет данных").pack(padx=10, pady=10)
            return

        for name, amount in summary.items():
            color = "green" if amount >= 0 else "red"
            ttk.Label(win, text=f"{name}: {amount:.2f} руб.", foreground=color).pack(padx=10, pady=2, anchor=tk.W)

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.manager.transactions:
            self.tree.insert("", tk.END, values=(
                t.date,
                t.category.name,
                t.category.type.value,
                f"{t.amount:.2f}",
                t.description
            ))

    def update_balance(self):
        balance = self.manager.get_balance()
        color = "green" if balance >= 0 else "red"
        self.balance_label.config(
            text=f"Текущий баланс: {balance:.2f} руб.",
            foreground=color
        )

    def clear_inputs(self):
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.category_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
