

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import mysql.connector as ms
import pandas as pd
import matplotlib.pyplot as plt

LOW_STOCK = 10


class Pharmacy:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1400x750")

        self.bill = 0
        self.sales_cache = []

        self.header()
        self.frames()
        self.table()
        self.low_stock_alert()

    # ---------------- DB ----------------
    def db(self):
        self.con = ms.connect(
            host="localhost",
            user="root",
            password="YOUR MYSQL PASSWORD",
            database="rec"
        )
        self.cur = self.con.cursor()

    # ---------------- HEADER ----------------
    def header(self):
        tk.Label(
            self.root,
            text="Pharmacy Management System",
            font=("Arial", 28, "bold"),
            bg="#3949AB",
            fg="white",
            pady=6
        ).pack(fill="x")

    # ---------------- FRAMES ----------------
    def frames(self):
        self.left = tk.Frame(self.root, bd=3, relief="ridge")
        self.left.place(x=10, y=60, width=360, height=670)

        self.center = tk.Frame(self.root, bd=3, relief="ridge")
        self.center.place(x=380, y=60, width=680, height=670)

        self.right = tk.Frame(self.root, bd=3, relief="ridge")
        self.right.place(x=1070, y=60, width=310, height=670)

        self.add_medicine_ui()
        self.buttons()

    # ---------------- ADD MEDICINE ----------------
    def add_medicine_ui(self):
        tk.Label(self.left, text="Add Medicine", font=("Arial", 18, "bold")).pack(pady=10)

        self.ent = {}
        fields = ["Name", "Price", "Quantity", "Expiry (YYYY-MM-DD)"]

        for f in fields:
            tk.Label(self.left, text=f).pack(anchor="w", padx=20)
            e = tk.Entry(self.left)
            e.pack(fill="x", padx=20, pady=4)
            self.ent[f] = e

        tk.Button(
            self.left, text="Add Medicine",
            font=("Arial", 14),
            command=self.add_medicine
        ).pack(pady=15)

    def add_medicine(self):
        try:
            self.db()
            self.cur.execute(
                "INSERT INTO pharmacy VALUES (%s,%s,%s,%s)",
                (
                    self.ent["Name"].get(),
                    int(self.ent["Price"].get()),
                    int(self.ent["Quantity"].get()),
                    datetime.strptime(self.ent["Expiry (YYYY-MM-DD)"].get(), "%Y-%m-%d").date()
                )
            )
            self.con.commit()
            self.con.close()
            self.show_all()
            messagebox.showinfo("Success", "Medicine Added Successfully")
            for e in self.ent.values():
                e.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- TABLE ----------------
    def table(self):
        self.tree = ttk.Treeview(
            self.center,
            columns=("name", "price", "qty", "exp"),
            show="headings"
        )
        for c in ("name", "price", "qty", "exp"):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=160)
        self.tree.pack(fill="both", expand=True)

    def show_all(self):
        self.tree.delete(*self.tree.get_children())
        self.db()
        self.cur.execute("SELECT * FROM pharmacy")
        for r in self.cur.fetchall():
            self.tree.insert("", "end", values=r)
        self.con.close()

    # ---------------- BUTTONS ----------------
    def buttons(self):
        actions = [
            ("Show All", self.show_all),
            ("Search Medicine", self.search_window),
            ("Add Quantity", self.add_qty_window),
            ("Billing", self.billing_window),
            ("Transaction Log", self.transaction_log_window),
            ("Sales Report", self.sales_report),
            ("Suppliers", self.supplier_menu),
            ("Exit", self.root.destroy)
        ]

        for t, c in actions:
            tk.Button(
                self.right, text=t,
                font=("Arial", 14),
                command=c
            ).pack(fill="x", padx=20, pady=7)

    # ---------------- NICE WINDOW ----------------
    def nice_window(self, title, size):
        w = tk.Toplevel(self.root)
        w.title(title)
        w.geometry(size)
        w.resizable(False, False)
        tk.Label(w, text=title, font=("Arial", 18, "bold")).pack(pady=10)
        return w

    # ---------------- SEARCH ----------------
    def search_window(self):
        w = self.nice_window("Search Medicine", "420x260")
        tk.Label(w, text="Medicine Name").pack()
        name = tk.Entry(w)
        name.pack()

        def search():
            self.tree.delete(*self.tree.get_children())
            self.db()
            self.cur.execute("SELECT * FROM pharmacy WHERE name=%s", (name.get(),))
            row = self.cur.fetchone()
            self.con.close()
            if row:
                self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("Info", "Medicine Not Found")
            w.destroy()

        tk.Button(w, text="Search", command=search).pack(pady=10)
        tk.Button(w, text="Exit", command=w.destroy).pack()

    # ---------------- ADD QUANTITY ----------------
    def add_qty_window(self):
        w = self.nice_window("Add Quantity", "420x300")
        tk.Label(w, text="Medicine Name").pack()
        name = tk.Entry(w)
        name.pack()
        tk.Label(w, text="Quantity").pack()
        q = tk.Entry(w)
        q.pack()

        def add():
            try:
                self.db()
                self.cur.execute("SELECT quant FROM pharmacy WHERE name=%s", (name.get(),))
                old = self.cur.fetchone()[0]
                self.cur.execute(
                    "UPDATE pharmacy SET quant=%s WHERE name=%s",
                    (old + int(q.get()), name.get())
                )
                self.con.commit()
                self.con.close()
                self.show_all()
                w.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(w, text="Add Quantity", command=add).pack(pady=10)
        tk.Button(w, text="Exit", command=w.destroy).pack()

    # ---------------- BILLING ----------------
    def billing_window(self):
        self.bill = 0
        self.bill_win = self.nice_window("Billing", "500x420")
        self.lb = tk.Listbox(self.bill_win, font=("Arial", 13))
        self.lb.pack(fill="both", expand=True, pady=10)

        tk.Button(self.bill_win, text="Purchase", command=self.purchase_window).pack(side="left", padx=10)
        tk.Button(self.bill_win, text="Print Bill", command=self.print_bill).pack(side="left")
        tk.Button(self.bill_win, text="Exit", command=self.bill_win.destroy).pack(side="right", padx=10)

    def purchase_window(self):
        w = self.nice_window("Purchase Medicine", "420x300")
        tk.Label(w, text="Medicine Name").pack()
        name = tk.Entry(w)
        name.pack()
        tk.Label(w, text="Quantity").pack()
        q = tk.Entry(w)
        q.pack()

        def buy():
            try:
                qty = int(q.get())
                self.db()
                self.cur.execute(
                    "SELECT price, quant FROM pharmacy WHERE name=%s",
                    (name.get(),)
                )
                price, stock = self.cur.fetchone()

                if stock < qty:
                    messagebox.showerror("Error", "Out of stock")
                    return

                amt = price * qty
                self.bill += amt
                self.lb.insert(tk.END, f"{name.get()}  x{qty}  = {amt}")

                self.cur.execute(
                    "UPDATE pharmacy SET quant=%s WHERE name=%s",
                    (stock - qty, name.get())
                )

                self.cur.execute(
                    "INSERT INTO sales_history VALUES (%s,%s,%s,%s)",
                    (name.get(), qty, amt, datetime.now())
                )

                self.con.commit()
                self.con.close()
                w.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(w, text="Purchase", command=buy).pack(pady=10)
        tk.Button(w, text="Exit", command=w.destroy).pack()

    def print_bill(self):
        self.lb.insert(tk.END, "------------------")
        self.lb.insert(tk.END, f"TOTAL = {self.bill}")

    # ---------------- TRANSACTION LOG ----------------
    def transaction_log_window(self):
        w = self.nice_window("Transaction Log", "750x420")
        tree = ttk.Treeview(
            w,
            columns=("med", "qty", "amt", "time"),
            show="headings"
        )
        for c in ("med", "qty", "amt", "time"):
            tree.heading(c, text=c.upper())
            tree.column(c, width=170)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.db()
        self.cur.execute("SELECT * FROM sales_history ORDER BY sale_time DESC")
        for r in self.cur.fetchall():
            tree.insert("", "end", values=r)
        self.con.close()

        tk.Button(w, text="Exit", command=w.destroy).pack()

    # ---------------- SALES REPORT ----------------
    def sales_report(self):
        self.db()
        self.cur.execute("SELECT amount FROM sales_history")
        data = self.cur.fetchall()
        self.con.close()

        if not data:
            messagebox.showinfo("Info", "No sales data")
            return

        df = pd.DataFrame(data, columns=["Amount"])
        plt.plot(df["Amount"], marker="o")
        plt.title("Sales Trend")
        plt.xlabel("Transaction")
        plt.ylabel("Amount")
        plt.show()

    # ---------------- SUPPLIERS ----------------
    def supplier_menu(self):
        w = self.nice_window("Supplier Module", "420x280")
        tk.Button(w, text="Add Supplier", command=self.add_supplier_window).pack(pady=10)
        tk.Button(w, text="View Suppliers", command=self.view_suppliers_window).pack(pady=10)
        tk.Button(w, text="Exit", command=w.destroy).pack(pady=10)

    def add_supplier_window(self):
        w = self.nice_window("Add Supplier", "420x360")
        ent = {}

        for f in ["Name", "Company", "Phone", "Email"]:
            tk.Label(w, text=f).pack()
            e = tk.Entry(w)
            e.pack(pady=4)
            ent[f] = e

        def save():
            self.db()
            self.cur.execute(
                "INSERT INTO supplier VALUES (%s,%s,%s,%s)",
                (ent["Name"].get(), ent["Company"].get(), ent["Phone"].get(), ent["Email"].get())
            )
            self.con.commit()
            self.con.close()
            messagebox.showinfo("Success", "Supplier Added")
            w.destroy()

        tk.Button(w, text="Save Supplier", command=save).pack(pady=10)
        tk.Button(w, text="Exit", command=w.destroy).pack()

    def view_suppliers_window(self):
        w = self.nice_window("Supplier List", "600x400")
        tree = ttk.Treeview(
            w,
            columns=("name", "company", "phone", "email"),
            show="headings"
        )
        for c in ("name", "company", "phone", "email"):
            tree.heading(c, text=c.upper())
            tree.column(c, width=140)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.db()
        self.cur.execute("SELECT * FROM supplier")
        for r in self.cur.fetchall():
            tree.insert("", "end", values=r)
        self.con.close()

        tk.Button(w, text="Exit", command=w.destroy).pack()

    # ---------------- LOW STOCK ----------------
    def low_stock_alert(self):
        try:
            self.db()
            self.cur.execute(
                "SELECT name, quant FROM pharmacy WHERE quant<=%s",
                (LOW_STOCK,)
            )
            for n, q in self.cur.fetchall():
                messagebox.showwarning("Low Stock", f"{n} only {q} left")
            self.con.close()
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    Pharmacy(root)
    root.mainloop()
