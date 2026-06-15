
from tkinter import *
from tkinter import messagebox
import sqlite3
from cryptography.fernet import Fernet

# ==========================
# Generate Encryption Key
# ==========================

try:
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

cipher = Fernet(key)

# ==========================
# Database Setup
# ==========================

conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password BLOB
)
""")

conn.commit()

# ==========================
# Functions
# ==========================

def save_password():
    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if website == "" or username == "" or password == "":
        messagebox.showerror("Error", "Please fill all fields")
        return

    encrypted_password = cipher.encrypt(password.encode())

    cursor.execute(
        "INSERT INTO passwords(website, username, password) VALUES (?, ?, ?)",
        (website, username, encrypted_password)
    )

    conn.commit()

    website_entry.delete(0, END)
    username_entry.delete(0, END)
    password_entry.delete(0, END)

    load_passwords()

    messagebox.showinfo("Success", "Password Saved Successfully")


def load_passwords():
    password_list.delete(0, END)

    cursor.execute("SELECT * FROM passwords")

    rows = cursor.fetchall()

    for row in rows:
        decrypted = cipher.decrypt(row[3]).decode()

        display = (
            f"ID:{row[0]} | "
            f"{row[1]} | "
            f"{row[2]} | "
            f"{decrypted}"
        )

        password_list.insert(END, display)


def delete_password():
    selected = password_list.curselection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Select a record first"
        )
        return

    item = password_list.get(selected[0])

    record_id = item.split("|")[0].replace("ID:", "").strip()

    cursor.execute(
        "DELETE FROM passwords WHERE id=?",
        (record_id,)
    )

    conn.commit()

    load_passwords()

    messagebox.showinfo("Deleted", "Record Deleted")


# ==========================
# GUI
# ==========================

root = Tk()
root.title("Secure Password Manager")
root.geometry("750x550")
root.resizable(False, False)

title = Label(
    root,
    text="Secure Password Manager",
    font=("Arial", 20, "bold")
)
title.pack(pady=10)

website_label = Label(root, text="Website")
website_label.pack()

website_entry = Entry(root, width=50)
website_entry.pack(pady=5)

username_label = Label(root, text="Username")
username_label.pack()

username_entry = Entry(root, width=50)
username_entry.pack(pady=5)

password_label = Label(root, text="Password")
password_label.pack()

password_entry = Entry(root, width=50, show="*")
password_entry.pack(pady=5)

save_btn = Button(
    root,
    text="Save Password",
    bg="green",
    fg="white",
    width=20,
    command=save_password
)
save_btn.pack(pady=10)

password_list = Listbox(
    root,
    width=100,
    height=15
)
password_list.pack(pady=10)

delete_btn = Button(
    root,
    text="Delete Selected",
    bg="red",
    fg="white",
    width=20,
    command=delete_password
)
delete_btn.pack()

load_passwords()

root.mainloop()

conn.close()
