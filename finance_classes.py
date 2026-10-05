import csv
from enum import Enum


class TransactionType(Enum):
    INCOME = "Доход"
    EXPENSE = "Расход"


class Category:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class Transaction:
    def __init__(self, amount, category, date, description=""):
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description


class FinanceManager:
    def __init__(self, filename="transactions.csv"):
        self.filename = filename
        self.transactions = []
        self.categories = [
            Category("Зарплата", TransactionType.INCOME),
            Category("Инвестиции", TransactionType.INCOME),
            Category("Продукты", TransactionType.EXPENSE),
            Category("Транспорт", TransactionType.EXPENSE),
            Category("Развлечения", TransactionType.EXPENSE)
        ]
        self.load_from_file()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.save_to_file()

    def delete_transaction(self, index):
        if 0 <= index < len(self.transactions):
            del self.transactions[index]
            self.save_to_file()

    def get_balance(self):
        income = 0
        expenses = 0
        for t in self.transactions:
            if t.category.type == TransactionType.INCOME:
                income = income + t.amount
            else:
                expenses = expenses + t.amount
        return income - expenses

    def get_category_summary(self):
        summary = {}
        for t in self.transactions:
            name = t.category.name
            if name not in summary:
                summary[name] = 0
            if t.category.type == TransactionType.INCOME:
                summary[name] = summary[name] + t.amount
            else:
                summary[name] = summary[name] - t.amount
        return summary

    def save_to_file(self):
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Amount", "Category", "Type", "Date", "Description"])
            for t in self.transactions:
                writer.writerow([
                    t.amount,
                    t.category.name,
                    t.category.type.value,
                    t.date,
                    t.description
                ])

    def load_from_file(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cat = None
                    for c in self.categories:
                        if c.name == row["Category"]:
                            cat = c
                            break
                    if cat:
                        t = Transaction(
                            float(row["Amount"]),
                            cat,
                            row["Date"],
                            row["Description"]
                        )
                        self.transactions.append(t)
        except FileNotFoundError:
            self.transactions = []
        except Exception:
            self.transactions = []
