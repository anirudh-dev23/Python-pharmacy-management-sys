# Python-pharmacy-management-sys
A Python-based pharmacy management system with inventory, billing, suppliers, and transaction logs.
Pharmacy Management System

A desktop-based Pharmacy Management System built using **Python, Tkinter, and MySQL**.  
This project simulates a real-world pharmacy workflow including inventory management, billing, suppliers, and transaction logging.

FEATURES:

Medicine Management
- Add new medicines
- Update quantities
- View all medicines
- Low stock alerts

Billing System
- Purchase medicines
- Automatic stock deduction
- Bill generation
- Multiple items per bill
 ![Billing](https://github.com/anirudh-dev23/Python-pharmacy-management-sys/blob/main/Billing%20.jpg)

Transaction Log (Sales History)
- Records every sale
- Stores:
  - Medicine name
  - Quantity sold
  - Amount
  - Date & time
- Viewable inside the application

Supplier Management
- Add suppliers
- View supplier list
- Stores contact details and company info
![Suppliers list](https://github.com/user-attachments/assets/861a5775-155f-44b5-a6d1-0ea1c16e8fda)

Analytics
- Sales trend graph using Pandas & Matplotlib
 
Tech Stack

- **Language:** Python  
- **GUI:** Tkinter  
- **Database:** MySQL  
- **Data Analysis:** Pandas  
- **Visualization:** Matplotlib  

DATABASE SETUP:

Create the following tables in MySQL:

```sql
CREATE TABLE pharmacy (
    name VARCHAR(50),
    price INT,
    quant INT,
    exp DATE
);

CREATE TABLE supplier (
    name VARCHAR(50),
    company VARCHAR(50),
    phone VARCHAR(15),
    email VARCHAR(50)
);

CREATE TABLE sales_history (
    med_name VARCHAR(50),
    quantity INT,
    amount INT,
    sale_time DATETIME
);
