"""
Banking Information System - Python Internship Project
A beginner-friendly command-line banking demo backed by SQLite.

Run:
    python main.py

This is an educational prototype, not production banking software.
"""
import hashlib
import os
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation

DB_PATH = os.path.join(os.path.dirname(__file__), "banking.db")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_pin(pin: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 200_000)
    return salt.hex(), digest.hex()


def verify_pin(pin: str, salt_hex: str, digest_hex: str) -> bool:
    _, candidate = hash_pin(pin, bytes.fromhex(salt_hex))
    return candidate == digest_hex


def initialize_database():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_no INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            salt TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            balance_cents INTEGER NOT NULL DEFAULT 0 CHECK(balance_cents >= 0),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
            note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(account_no) REFERENCES accounts(account_no)
        );
        """)


def money_to_cents(raw: str) -> int:
    try:
        amount = Decimal(raw.strip())
    except InvalidOperation:
        raise ValueError("Enter a valid amount, such as 250 or 99.50.")
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be positive and have no more than 2 decimal places.")
    return int(amount * 100)


def format_money(cents: int) -> str:
    return f"₹{cents / 100:,.2f}"


def timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def create_account():
    print("\n--- Create Account ---")
    name = input("Full name: ").strip()
    phone = input("Phone number: ").strip()
    pin = input("Create a 4-8 digit PIN: ").strip()
    if not name or not phone:
        print("Name and phone number are required.")
        return
    if not pin.isdigit() or not 4 <= len(pin) <= 8:
        print("PIN must contain 4 to 8 digits.")
        return
    salt, digest = hash_pin(pin)
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO accounts(full_name, phone, salt, pin_hash, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (name, phone, salt, digest, timestamp()),
        )
        account_no = cur.lastrowid
    print(f"Account created successfully. Your account number is: {account_no}")
    print("Keep your account number private and remember your PIN.")


def authenticate():
    try:
        account_no = int(input("Account number: ").strip())
    except ValueError:
        print("Account number must be a number.")
        return None
    pin = input("PIN: ").strip()
    with connect() as conn:
        account = conn.execute(
            "SELECT * FROM accounts WHERE account_no = ?", (account_no,)
        ).fetchone()
    if account is None or not verify_pin(pin, account["salt"], account["pin_hash"]):
        print("Invalid account number or PIN.")
        return None
    return account


def check_balance(account_no: int):
    with connect() as conn:
        row = conn.execute(
            "SELECT full_name, balance_cents FROM accounts WHERE account_no = ?",
            (account_no,),
        ).fetchone()
    if row:
        print(f"\nAccount holder: {row['full_name']}")
        print(f"Available balance: {format_money(row['balance_cents'])}")


def add_transaction(conn, account_no, kind, cents, note):
    conn.execute(
        """INSERT INTO transactions(account_no, transaction_type, amount_cents, note, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (account_no, kind, cents, note, timestamp()),
    )


def deposit(account_no: int):
    try:
        cents = money_to_cents(input("Amount to deposit (₹): "))
    except ValueError as exc:
        print(exc)
        return
    with connect() as conn:
        conn.execute(
            "UPDATE accounts SET balance_cents = balance_cents + ? WHERE account_no = ?",
            (cents, account_no),
        )
        add_transaction(conn, account_no, "DEPOSIT", cents, "Cash deposit")
    print(f"Deposit successful: {format_money(cents)}")


def withdraw(account_no: int):
    try:
        cents = money_to_cents(input("Amount to withdraw (₹): "))
    except ValueError as exc:
        print(exc)
        return
    with connect() as conn:
        row = conn.execute(
            "SELECT balance_cents FROM accounts WHERE account_no = ?", (account_no,)
        ).fetchone()
        if row is None or row["balance_cents"] < cents:
            print("Transaction declined: insufficient balance.")
            return
        conn.execute(
            "UPDATE accounts SET balance_cents = balance_cents - ? WHERE account_no = ?",
            (cents, account_no),
        )
        add_transaction(conn, account_no, "WITHDRAWAL", cents, "Cash withdrawal")
    print(f"Withdrawal successful: {format_money(cents)}")


def transfer(account_no: int):
    try:
        target_no = int(input("Recipient account number: ").strip())
        cents = money_to_cents(input("Amount to transfer (₹): "))
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        return
    if target_no == account_no:
        print("You cannot transfer money to the same account.")
        return
    with connect() as conn:
        sender = conn.execute(
            "SELECT balance_cents FROM accounts WHERE account_no = ?", (account_no,)
        ).fetchone()
        recipient = conn.execute(
            "SELECT account_no FROM accounts WHERE account_no = ?", (target_no,)
        ).fetchone()
        if recipient is None:
            print("Recipient account was not found.")
            return
        if sender["balance_cents"] < cents:
            print("Transfer declined: insufficient balance.")
            return
        conn.execute(
            "UPDATE accounts SET balance_cents = balance_cents - ? WHERE account_no = ?",
            (cents, account_no),
        )
        conn.execute(
            "UPDATE accounts SET balance_cents = balance_cents + ? WHERE account_no = ?",
            (cents, target_no),
        )
        add_transaction(conn, account_no, "TRANSFER_OUT", cents, f"To account {target_no}")
        add_transaction(conn, target_no, "TRANSFER_IN", cents, f"From account {account_no}")
    print(f"Transfer successful: {format_money(cents)} to account {target_no}")


def transaction_history(account_no: int):
    with connect() as conn:
        rows = conn.execute(
            """SELECT transaction_type, amount_cents, note, created_at
               FROM transactions WHERE account_no = ?
               ORDER BY transaction_id DESC LIMIT 20""",
            (account_no,),
        ).fetchall()
    print("\n--- Recent Transactions (latest 20) ---")
    if not rows:
        print("No transactions found.")
        return
    for row in rows:
        print(f"{row['created_at']} | {row['transaction_type']:<12} | "
              f"{format_money(row['amount_cents']):>12} | {row['note']}")


def account_menu(account_no: int):
    while True:
        print("""
--- Account Menu ---
1. Check balance
2. Deposit money
3. Withdraw money
4. Transfer money
5. View transaction history
6. Logout
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            check_balance(account_no)
        elif choice == "2":
            deposit(account_no)
        elif choice == "3":
            withdraw(account_no)
        elif choice == "4":
            transfer(account_no)
        elif choice == "5":
            transaction_history(account_no)
        elif choice == "6":
            print("Logged out.")
            return
        else:
            print("Choose a number from 1 to 6.")


def main():
    initialize_database()
    while True:
        print("""
====================================
   BANKING INFORMATION SYSTEM
====================================
1. Create account
2. Login to account
3. Exit
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            create_account()
        elif choice == "2":
            account = authenticate()
            if account:
                account_menu(account["account_no"])
        elif choice == "3":
            print("Thank you for trying the Banking Information System.")
            break
        else:
            print("Choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
