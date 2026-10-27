# Banking Information System (Python)

A command-line banking application built with **Python 3** and **SQLite** for the UpSkill Campus Python internship project.

## Features

- Create an account with a unique account number
- Login with account number and PIN
- PIN hashing using PBKDF2-HMAC-SHA256 (PINs are not stored as plain text)
- Check account balance
- Deposit and withdraw money
- Transfer money between accounts
- View the latest 20 transactions
- SQLite persistence, input validation, and prevention of negative balances
- Parameterized SQL queries to reduce SQL injection risk

> **Educational prototype only:** This project is not production-ready banking software. It has no bank integration, identity verification, rate limiting, encryption-at-rest strategy, or professional security audit. Use fictional data only.

## Requirements

- Python 3.10 or newer
- No third-party packages required

## Run locally

1. Install Python from https://www.python.org/downloads/ if it is not installed.
2. Download or clone this repository.
3. Open a terminal in this folder.
4. Run:

   ```bash
   python main.py
   ```

   On some Windows installations, use `py main.py`.

The program creates `banking.db` automatically on first run. This local database is intentionally excluded from GitHub.

## Quick demo

1. Choose `1` to create an account.
2. Enter a fictional name, phone number, and a 4–8 digit PIN.
3. Note the account number printed by the program.
4. Choose `2` to log in.
5. Try a deposit, balance check, withdrawal, transfer to a second account, and transaction history.

## Project structure

```text
upskillcampus/
├── main.py
├── test_main.py
├── requirements.txt
├── .gitignore
├── README.md
└── report/
    └── BankingInformationSystem_Report.md
```

## Tests

Run:

```bash
python -m unittest -v
```

The automated tests cover money input validation and PIN hashing/verification.

## GitHub submission

Create a public repository named **`upskillcampus`**, then upload the contents of this project folder. Do not upload `banking.db`, personal information, or real account data.

Suggested code link after uploading:

`https://github.com/YOUR-USERNAME/upskillcampus/blob/main/main.py`

Suggested report link after uploading:

`https://github.com/YOUR-USERNAME/upskillcampus/blob/main/report/BankingInformationSystem_Report.md`

Replace `YOUR-USERNAME` with your GitHub username. These are templates; they become valid only after the repository and files have been uploaded.
