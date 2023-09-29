import io
import csv
import os

from igsbill import db, create_app#, bcrypt
from werkzeug.security import generate_password_hash
from igsbill.models.users import *
from igsbill.models.services import *
from igsbill.models.bills import *
from igsbill.models.payments import *
from igsbill.models.withdrawals import *


app = create_app()

def ImportCSV(csv_file, delimiter):
	#stream = io.StringIO(csv_file.read().decode("UTF8"), newline=None)
	return csv.reader(open(csv_file), delimiter=delimiter)

def AddToDb(data):
	db.session.add(data)
	try:
		db.session.commit()
	except Exception as e:
		db.session.rollback()

def main():
	db.create_all()

	reader = ImportCSV("igsbill/static/database_csv/user_org.csv",";")
	next(reader, None)
	for organization in reader:
		user_organization = User_Org(organization=organization[0])
		AddToDb(user_organization)
	print("user organization, done.")

	reader = ImportCSV("igsbill/static/database_csv/user_cohort.csv",";")
	next(reader, None)
	for cohort in reader:
		user_cohort = User_Cohort(cohort=cohort[0])
		AddToDb(user_cohort)
	print("user cohort, done.")


	reader = ImportCSV("igsbill/static/database_csv/user_type.csv",";")
	next(reader, None)
	for user_type in reader:
		a_user_type = User_Type(user_type=user_type[0])
		AddToDb(a_user_type)
	print("user type, done.")


	reader = ImportCSV("igsbill/static/database_csv/users.csv",";")
	next(reader, None)
	for username, email, password, first_name, last_name, phone, bank_account, virtual_account_number_0, virtual_account_number_1, virtual_account_number_2, account_note, org_id, cohort_id, user_type_id in reader:
		strip_username = username.strip().lower()
		if password is None:
			password = os.environ.get('DEFAULT_PASSWORD_USER')
		clear_email = email.replace(" ", "").lower()
		hashed_password = generate_password_hash(password).decode('utf-8')
		user = User(username=strip_username, email=clear_email, password=hashed_password, first_name=first_name, last_name=last_name, phone=phone, bank_account=bank_account, virtual_account_number_0=virtual_account_number_0, virtual_account_number_1=virtual_account_number_1, virtual_account_number_2=virtual_account_number_2, account_note=account_note, org_id=org_id, cohort_id=cohort_id, user_type_id=user_type_id)
		AddToDb(user)
	print("users, done.")


	reader = ImportCSV("igsbill/static/database_csv/service_type.csv",";")
	next(reader, None)
	for service_type in reader:
		a_service_type = Service_Type(service_type=service_type[0])
		AddToDb(a_service_type)
	print("service type, done.")


	reader = ImportCSV("igsbill/static/database_csv/bill_type.csv",";")
	next(reader, None)
	for bill_type in reader:
		a_bill_type = Bill_Type(bill_type=bill_type[0])
		AddToDb(a_bill_type)
	print("bill type, done.")


	reader = ImportCSV("igsbill/static/database_csv/payment_type.csv",";")
	next(reader, None)
	for payment_type in reader:
		a_payment_type = Payment_Type(transaction_type=payment_type[0])
		AddToDb(a_payment_type)
	print("payment type, done.")


	reader = ImportCSV("igsbill/static/database_csv/payment_method.csv",";")
	next(reader, None)
	for payment_method in reader:
		a_payment_method = Payment_Method(method=payment_method[0])
		AddToDb(a_payment_method)
	print("payment method, done.")


	reader = ImportCSV("igsbill/static/database_csv/withdrawal_type.csv",";")
	next(reader, None)
	for withdrawal_type in reader:
		a_withdrawal_type = Withdrawal_Type(withdrawal_type=withdrawal_type[0])
		AddToDb(a_withdrawal_type)
	print("withdrawal type, done.")


	reader = ImportCSV("igsbill/static/database_csv/withdrawal_method.csv",";")
	next(reader, None)
	for withdrawal_method in reader:
		a_withdrawal_method = Withdrawal_Method(method=withdrawal_method[0])
		AddToDb(a_withdrawal_method)
	print("withdrawal method, done.")


	print("Finished.")

if __name__ == '__main__':
	with app.app_context():
		main()