# Cafeteria Management System
> Developed by Arjun Adhikari

![Cafeteria Management System](https://i.ibb.co/s30DcmB/cafems.png)

This project helps to manage a single point cafeteria system. 
The features of this system are:

1. Add / Remove Cafeteria managers.
2. Add / Remove customers.
3. Automatically update daily balances(accounting).
4. Manage the daily spending/expenses of cafeteria.
5. Manage the sales/income of cafeteria.
6. Provide discount / add service tax to individual sale.
7. Manage the items available for sale/in-cafe-use with respective prices.
8. Increase/decrease stocks of items automatically.
9. Issue penalties if any entities are responsible to be penalized.
10. Record the transactions performed in cafeteria.
11. View the log entries of the cafeteria manager.
12. Provide role and permissions to the cafeteria manager.


## Installation Instructions
Run the following instructions on your system.
```
python3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Then access the server with created credentials.


> If you feel like improving this project, send a PR or create issue.
