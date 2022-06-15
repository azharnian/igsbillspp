from flask import Blueprint, render_template, flash, abort
from flask_login import current_user, login_required

from igsbill import db, bcrypt
from igsbill.models.users import User_Org, User_Cohort, User_Type, User, Service_Type, Service, Bill_Type, Payment_Type, Payment_Method, Withdrawal_Type, Withdrawal_Method
from igsbill.admin.forms import ImportOrganizationForm, ImportCohortForm, ImportUserTypeForm, ImportUsersForm, ImportServiceTypeForm, ImportServicesForm, ImportBillTypeForm, ImportPaymentTypeForm, ImportPaymentMethodForm, ImportWithdrawalTypeForm, ImportWithdrawalMethodForm
from igsbill.admin.utils import ImportCSV, AddToDb

admin = Blueprint('admin', __name__)


@admin.route("/admin")
@login_required
def home():
	return render_template("admin.html")

@admin.route("/admin/import_organization", methods=['GET', 'POST'])
@login_required
def import_organization():
	if current_user.user_type_id > 3:
		abort(403)
	form = ImportOrganizationForm()
	if form.validate_on_submit():
		if form.csv.data:
			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
			results = {}
			next(reader, None)
			for organization in reader:
				user_organization = User_Org(organization=organization[0])
				results[user_organization] = AddToDb(user_organization)
			flash(f'Impor data organisasi telah selesai!', 'info')
			return render_template("import_form_result.html", title="Hasil Impor Organisasi", results=results)

	return render_template("import_form.html", title="Impor Organisasi", form=form)

@admin.route("/admin/import_cohort", methods=['GET', 'POST'])
@login_required
def import_cohort():
	if current_user.user_type_id > 3:
		abort(403)
	form = ImportCohortForm()
	if form.validate_on_submit():
		if form.csv.data:
			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
			results = {}
			next(reader, None)
			for cohort in reader:
				user_cohort = User_Cohort(cohort=cohort[0])
				results[user_cohort] = AddToDb(user_cohort)
			flash(f'Impor data kohort telah selesai!', 'info')
			return render_template("import_form_result.html", title="Hasil Impor Kohort", results=results)

	return render_template("import_form.html", title="Impor Kohort", form=form)

# @admin.route("/admin/import_user_type", methods=['GET', 'POST'])
# @login_required
# def import_user_type():
# 	if current_user.user_type_id > 3:
# 		abort(403)
# 	form = ImportUserTypeForm()
# 	if form.validate_on_submit():
# 		if form.csv.data:
# 			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
# 			results = {}
# 			next(reader, None)
# 			for user_type in reader:
# 				a_user_type = User_Type(user_type=user_type[0])
# 				results[a_user_type] = AddToDb(a_user_type)
# 			flash(f'Impor data tipe pengguna telah selesai!', 'info')
# 			return render_template("import_form_result.html", title="Hasil Impor Tipe Pengguna", results=results)

# 	return render_template("import_form.html", title="Impor Tipe Pengguna", form=form)

@admin.route("/admin/import_users", methods=['GET', 'POST'])
@login_required
def import_users():
	if current_user.user_type_id > 3:
		abort(403)
	form = ImportUsersForm()
	if form.validate_on_submit():
		if form.csv.data:
			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
			results = {}
			next(reader, None)
			for username, email, password, first_name, last_name, phone, bank_account, virtual_account_number_0, virtual_account_number_1, virtual_account_number_2, account_note, org_id, cohort_id, user_type_id in reader:
				strip_username = username.strip().lower()
				clear_email = email.replace(" ", "").lower()
				if password is None or password == "":
					password = '12345'
				hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
				user = User(username=strip_username, email=clear_email, password=hashed_password, first_name=first_name, last_name=last_name, phone=phone, bank_account=bank_account, virtual_account_number_0=virtual_account_number_0, virtual_account_number_1=virtual_account_number_1, virtual_account_number_2=virtual_account_number_2, account_note=account_note, org_id=org_id, cohort_id=cohort_id, user_type_id=user_type_id)
				results[user] = AddToDb(user)
			flash(f'Impor data pengguna telah selesai!', 'info')
			return render_template("import_form_result.html", title="Hasil Impor Pengguna", results=results)
	return render_template("import_form.html", title="Impor Pengguna", form=form)

# @admin.route("/admin/import_service_type", methods=['GET', 'POST'])
# @login_required
# def import_service_type():
# 	if current_user.user_type_id > 3:
# 		abort(403)
# 	form = ImportServiceTypeForm()
# 	if form.validate_on_submit():
# 		if form.csv.data:
# 			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
# 			results = {}
# 			next(reader, None)
# 			for service_type in reader:
# 				a_service_type = Service_Type(service_type=service_type[0])
# 				results[a_service_type] = AddToDb(a_service_type)
# 			flash(f'Impor data tipe layanan telah selesai!', 'info')
# 			return render_template("import_form_result.html", title="Hasil Impor Tipe Layanan", results=results)

# 	return render_template("import_form.html", title="Impor Tipe Layanan", form=form)

@admin.route("/admin/import_services", methods=['GET', 'POST'])
@login_required
def import_services():
	if current_user.user_type_id > 3:
		abort(403)
	form = ImportServicesForm()
	if form.validate_on_submit():
		if form.csv.data:
			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
			results = {}
			next(reader, None)
			for service, price, additional, tax, sharing_percentage, user_id, org_id, cohort_id, service_type_id in reader:
				a_service = Service(service=service, price=price, additional=additional, tax=tax, sharing_percentage=sharing_percentage, user_id=user_id, org_id=org_id, cohort_id=cohort_id, service_type_id=service_type_id)
				results[a_service] = AddToDb(a_service)
			flash(f'Impor data layanan telah selesai!', 'info')
			return render_template("import_form_result.html", title="Hasil Impor Layanan", results=results)

	return render_template("import_form.html", title="Impor Layanan", form=form)

# @admin.route("/admin/import_bill_type", methods=['GET', 'POST'])
# @login_required
# def import_bill_type():
# 	if current_user.user_type_id > 3:
# 		abort(403)
# 	form = ImportBillTypeForm()
# 	if form.validate_on_submit():
# 		if form.csv.data:
# 			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
# 			results = {}
# 			next(reader, None)
# 			for bill_type in reader:
# 				a_bill_type = Bill_Type(bill_type=bill_type[0])
# 				results[a_bill_type] = AddToDb(a_bill_type)
# 			flash(f'Impor data Tipe Tagihan telah selesai!', 'info')
# 			return render_template("import_form_result.html", title="Hasil Impor Tipe Tagihan", results=results)

# 	return render_template("import_form.html", title="Impor Tipe Tagihan", form=form)

# @admin.route("/admin/import_payment_type", methods=['GET', 'POST'])
# @login_required
# def import_payment_type():
# 	if current_user.user_type_id > 3:
# 		abort(403)
# 	form = ImportPaymentTypeForm()
# 	if form.validate_on_submit():
# 		if form.csv.data:
# 			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
# 			results = {}
# 			next(reader, None)
# 			for payment_type in reader:
# 				a_payment_type = Payment_Type(transaction_type=payment_type[0])
# 				results[a_payment_type] = AddToDb(a_payment_type)
# 			flash(f'Impor data Tipe Pembayaran telah selesai!', 'info')
# 			return render_template("import_form_result.html", title="Hasil Impor Tipe Pembayaran", results=results)

# 	return render_template("import_form.html", title="Impor Tipe Pembayaran", form=form)


@admin.route("/admin/import_payment_method", methods=['GET', 'POST'])
@login_required
def import_payment_method():
	if current_user.user_type_id > 3:
		abort(403)
	form = ImportPaymentMethodForm()
	if form.validate_on_submit():
		if form.csv.data:
			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
			results = {}
			next(reader, None)
			for payment_method in reader:
				a_payment_method = Payment_Method(method=payment_method[0])
				results[a_payment_method] = AddToDb(a_payment_method)
			flash(f'Impor data Metode Pembayaran telah selesai!', 'info')
			return render_template("import_form_result.html", title="Hasil Impor Metode Pembayaran", results=results)

	return render_template("import_form.html", title="Impor Metode Pembayaran", form=form)

# @admin.route("/admin/import_withdrawal_type", methods=['GET', 'POST'])
# @login_required
# def import_withdrawal_type():
# 	if current_user.user_type_id > 3:
# 		abort(403)
# 	form = ImportWithdrawalTypeForm()
# 	if form.validate_on_submit():
# 		if form.csv.data:
# 			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
# 			results = {}
# 			next(reader, None)
# 			for withdrawal_type in reader:
# 				a_withdrawal_type = Withdrawal_Type(withdrawal_type=withdrawal_type[0])
# 				results[a_withdrawal_type] = AddToDb(a_withdrawal_type)
# 			flash(f'Impor data Tipe Penarikan Tunai telah selesai!', 'info')
# 			return render_template("import_form_result.html", title="Hasil Impor Tipe Penarikan Tunai", results=results)

# 	return render_template("import_form.html", title="Impor Tipe Penarikan Tunai", form=form)


@admin.route("/admin/import_withdrawal_method", methods=['GET', 'POST'])
@login_required
def import_withdrawal_method():
	if current_user.user_type_id > 3:
		abort(403)
	form = ImportWithdrawalMethodForm()
	if form.validate_on_submit():
		if form.csv.data:
			reader = ImportCSV(form.csv.data, form.delimiter.data[0])
			results = {}
			next(reader, None)
			for withdrawal_method in reader:
				a_withdrawal_method = Withdrawal_Method(method=withdrawal_method[0])
				results[a_withdrawal_method] = AddToDb(a_withdrawal_method)
			flash(f'Impor data Metode Penarikan Tunai telah selesai!', 'info')
			return render_template("import_form_result.html", title="Hasil Impor Metode Penarikan Tunai", results=results)

	return render_template("import_form.html", title="Impor Metode Penarikan Tunai", form=form)
