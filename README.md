💰 Personal Finance Manager + Insights

A command-line Personal Finance Manager built with Python that helps users record, manage, search, filter, and analyze their financial transactions.

This project was developed as part of a Python Programming Internship while applying software engineering principles such as modular architecture, separation of concerns, reusable components, and robust input validation.

⸻

🚀 Features

Transaction Management

* Add new transactions
* Update existing transactions
* Delete transactions
* View all transactions

Transaction Search

Search transactions by:

* Category
* Description
* Transaction Type
* Year
* Month

Transaction Filtering

Filter transactions by:

* Income
* Expense
* Date Range
* Amount Range

Financial Reports

Generate:

* Monthly Financial Reports
* Yearly Financial Reports

Each report includes:

* Total Income
* Total Expenses
* Balance
* Transaction Count
* Financial Status (Surplus, Overspending, Break Even)

Financial Summary

View an overall summary including:

* Total Income
* Total Expenses
* Current Balance
* Number of Transactions

User Experience

* Paginated transaction display
* Numbered transaction listings
* Consistent transaction formatting
* Robust input validation
* Friendly error messages

⸻

🏗️ Project Structure

personal_finance_manager/
│
├── main.py
├── README.md
├── .gitignore
│
├── menus/
│   ├── menu_helpers.py
│   └── transaction_menu.py
│
├── models/
│   ├── financial_summary.py
│   ├── transaction.py
│   └── user.py
│
├── services/
│   └── transaction_service.py
│
├── storage/
│   ├── json_storage.py
│   └── files/
│       ├── transactions.json
│       └── users.json
│
└── utils/
    ├── constants.py
    ├── enums.py
    └── validators.py

⸻

🛠️ Technologies Used

* Python 3
* Pandas
* JSON File Storage
* Object-Oriented Programming (OOP)

⸻

🏛️ Software Architecture

The project follows a layered architecture:

User
   ↓
Menus
   ↓
Services
   ↓
Storage
   ↓
JSON Files

Each layer has a single responsibility:

* Menus — User interaction and input collection
* Services — Business logic and data processing
* Storage — Reading and writing JSON files
* Models — Data representation
* Utilities — Shared constants, validators, and enumerations

⸻

▶️ Running the Project

Clone the repository:

git clone <repository-url>

Navigate into the project:

cd personal_finance_manager

Install dependencies:

pip install pandas

Run the application:

python main.py

⸻

📷 Screenshots & Demo

Screenshots and a demonstration video will be added in future updates.

⸻

🔮 Future Improvements

Planned enhancements include:

* Transaction sorting
* Spending insights and analytics
* Category-wise spending reports
* Monthly spending trends
* Largest income and expense analysis
* Average income and expense calculations
* Charts and visualizations
* Database support (SQLite/PostgreSQL)
* User authentication and multi-user login
* Export reports (CSV/PDF)

⸻

📚 Learning Outcomes

This project provided practical experience in:

* Object-Oriented Programming
* Layered Software Architecture
* Separation of Concerns
* JSON File Handling
* Data Analysis with Pandas
* Input Validation
* Exception Handling
* Modular Software Design
* Code Reusability
* Command-Line Application Development

⸻

👨‍💻 Author

Jubilent Shonhayi

Computer Science Student

Developed as part of a Python Programming Internship.