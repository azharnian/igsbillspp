from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from igsbill import db#, bcrypt

from igsbill.models.users import User_Org, User_Cohort, User_Type, User_Cohort, User
from igsbill.models.bills import Bill
from igsbill.models.payments import Payment, Payment_Type, Payment_Method
from igsbill.models.services import Service
from igsbill.models.withdrawals import Withdrawal, Withdrawal_Type, Withdrawal_Method

from igsbill.users.forms import LoginForm, CreateOrganizationForm, CreateCohortForm, CreateUserTypeForm, CreateUserForm, UpdateUserForm, AccountForm, ResetPasswordForm, RequestResetPasswordForm, ResetPasswordByEmailForm, ReportBillUserCohort, ShowUsersCohort, ReportAllBillsPaymentsUserCohort
from igsbill.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)

from igsbill.users.filters import currency_format, datetime_format

@users.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and check_password_hash(user.password, form.password.data) and user.user_type_id <= 4:
			login_user(user, remember=form.remember.data)
			user.last_login = datetime.utcnow()
			user.last_ip = str(request.remote_addr)
			db.session.commit()
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Gagal masuk, Cek kembali nama pengguna dan kata sandi', 'danger')
	return render_template('users/login.html', form=form)

@users.route("/logout", methods=['GET', 'POST'])
def logout():
	logout_user()
	return redirect(url_for('main.home'))

@users.route("/request_reset_password", methods=['GET', 'POST'])
def request_reset_password():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('Tautan reset sudah di kirimkan ke email.', 'info')
		return redirect(url_for('users.login'))
	return render_template("users/request_reset_password.html", form=form)

@users.route("/request_reset_password/<token>", methods=['GET', 'POST'])
def request_reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('Invalid Token atau Token Telah Kadaluarsa', 'warning')
		return redirect(url_for('users.request_reset_password'))
	form = ResetPasswordByEmailForm()
	if form.validate_on_submit():
		hassed_password = generate_password_hash(form.new_password.data).decode('utf-8')
		user.password = hassed_password
		user.last_updated = datetime.utcnow()
		db.session.commit()
		flash(f'Kata sandi telah di-reset, silahkan masuk.', 'success')
		return redirect(url_for('users.login'))
	return render_template('users/request_reset_token.html', form=form)

#User_Org
@users.route("/users/organization")
@login_required
def user_organization():
	if current_user.user_type_id > 3:
		abort(403)
	organizations = User_Org.query.order_by(User_Org.added_on.asc())
	return render_template("users/user_orgs.html", title="Organisasi Pengguna", organizations=organizations)

@users.route("/users/organization/add", methods=['GET', 'POST'])
@login_required
def add_user_organization():
	if current_user.user_type_id > 3:
		abort(403)
	form = CreateOrganizationForm()
	if form.validate_on_submit():
		user_org = User_Org(organization=form.organization.data.title(), active=form.active.data)
		db.session.add(user_org)
		db.session.commit()
		flash('Organisasi Pengguna telah ditambahkan', 'success')
		return redirect(url_for('users.user_organization'))
	form.active.data = True
	return render_template('users/create_organization.html', title="Tambah Organisasi", legend="Tambah Organisasi", form=form)

@users.route("/users/organization/<int:user_org_id>", methods=['GET', 'POST'])
@login_required
def user_organization_detail(user_org_id):
	if current_user.user_type_id > 3:
		abort(403)
	user_org = User_Org.query.get_or_404(user_org_id)
	return render_template('users/user_org.html', title=user_org.organization, user_org=user_org)

@users.route("/users/organization/<int:user_org_id>/update", methods=['GET', 'POST'])
@login_required
def update_user_organization(user_org_id):
	if current_user.user_type_id > 3:
		abort(403)
	user_org = User_Org.query.get_or_404(user_org_id)
	form = CreateOrganizationForm()
	if form.validate_on_submit():
		user_org.organization = form.organization.data.title()
		user_org.active = form.active.data
		user_org.last_updated = datetime.utcnow()

		db.session.commit()
		flash('Organisasi Pengguna Telah Diperbarui!', 'success')
		return redirect(url_for('users.user_organization_detail', user_org_id=user_org_id))
	elif request.method == 'GET':
		form.organization.data = user_org.organization
		form.active.data = user_org.active
	return render_template('users/create_organization.html', title="Perbarui Organisasi", legend="Perbarui Organisasi", form=form)

@users.route("/users/organization/<int:user_org_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_user_organization(user_org_id):
	if current_user.user_type_id > 3:
		abort(403)
	user_org = User_Org.query.get_or_404(user_org_id)
	db.session.delete(user_org)
	db.session.commit()
	flash('Organisasi Pengguna Telah Dihapus', 'success')
	return redirect(url_for('users.user_organization'))


#User_Cohort
@users.route("/users/cohort")
@login_required
def user_cohort():
	if current_user.user_type_id > 3:
		abort(403)
	cohorts = User_Cohort.query.order_by(User_Cohort.added_on.asc())
	return render_template("users/user_cohorts.html", title="Kohort Pengguna", cohorts=cohorts)

@users.route("/users/cohort/add", methods=['GET', 'POST'])
@login_required
def add_user_cohort():
	if current_user.user_type_id > 3:
		abort(403)
	form = CreateCohortForm()
	if form.validate_on_submit():
		user_cohort = User_Cohort(cohort=form.cohort.data.upper(), active=form.active.data)
		db.session.add(user_cohort)
		db.session.commit()
		flash('Kohort Pengguna telah ditambahkan', 'success')
		return redirect(url_for('users.user_cohort'))
	form.active.data = True
	return render_template('users/create_cohort.html', title="Tambah Kohort", legend="Tambah Kohort", form=form)

@users.route("/users/cohort/<int:user_cohort_id>", methods=['GET', 'POST'])
@login_required
def user_cohort_detail(user_cohort_id):
	if current_user.user_type_id > 3:
		abort(403)
	user_cohort = User_Cohort.query.get_or_404(user_cohort_id)
	return render_template('users/user_cohort.html', title=user_cohort.cohort, user_cohort=user_cohort)

@users.route("/users/cohort/<int:user_cohort_id>/update", methods=['GET', 'POST'])
@login_required
def update_user_cohort(user_cohort_id):
	if current_user.user_type_id > 3:
		abort(403)
	user_cohort = User_Cohort.query.get_or_404(user_cohort_id)
	form = CreateCohortForm()
	if form.validate_on_submit():
		user_cohort.cohort = form.cohort.data.upper()
		user_cohort.active = form.active.data
		user_cohort.last_updated = datetime.utcnow()

		db.session.commit()
		flash('Kohort Pengguna Telah Diperbarui!', 'success')
		return redirect(url_for('users.user_cohort_detail', user_cohort_id=user_cohort_id))
	elif request.method == 'GET':
		form.cohort.data = user_cohort.cohort
		form.active.data = user_cohort.active
	return render_template('users/create_cohort.html', title="Perbarui Kohort", legend="Perbarui Kohort", form=form)

@users.route("/users/cohort/<int:user_cohort_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_user_cohort(user_cohort_id):
	if current_user.user_type_id > 3:
		abort(403)
	user_cohort = User_Cohort.query.get_or_404(user_cohort_id)
	db.session.delete(user_cohort)
	db.session.commit()
	flash('Kohort Pengguna Telah Dihapus', 'success')
	return redirect(url_for('users.user_cohort'))

#User_Type
@users.route("/users/type")
@login_required
def user_type():
	if current_user.user_type_id > 3:
		abort(403)
	user_types = User_Type.query.order_by(User_Type.added_on.asc())
	return render_template("users/user_types.html", title="Tipe Pengguna", user_types=user_types)

@users.route("/users/type/add", methods=['GET', 'POST'])
@login_required
def add_user_type():
	if current_user.user_type_id > 3:
		abort(403)
	form = CreateUserTypeForm()
	if form.validate_on_submit():
		a_user_type = User_Type(user_type=form.user_type.data.lower(), active=form.active.data)
		db.session.add(a_user_type)
		db.session.commit()
		flash('Tipe Pengguna telah ditambahkan', 'success')
		return redirect(url_for('users.user_type'))
	form.active.data = True
	return render_template('users/create_user_type.html', title="Tambah Tipe Pengguna", legend="Tambah Tipe Pengguna", form=form)

@users.route("/users/type/<int:user_type_id>", methods=['GET', 'POST'])
@login_required
def user_type_detail(user_type_id):
	if current_user.user_type_id > 3:
		abort(403)
	a_user_type = User_Type.query.get_or_404(user_type_id)
	return render_template('users/user_type.html', title=a_user_type.user_type, user_type=a_user_type)

@users.route("/users/type/<int:user_type_id>/update", methods=['GET', 'POST'])
@login_required
def update_user_type(user_type_id):
	if current_user.user_type_id > 3:
		abort(403)
	a_user_type = User_Type.query.get_or_404(user_type_id)
	form = CreateUserTypeForm()
	if form.validate_on_submit():
		a_user_type.user_type = form.user_type.data.lower()
		a_user_type.active = form.active.data
		a_user_type.last_updated = datetime.utcnow()

		db.session.commit()
		flash('Tipe Pengguna Telah Diperbarui!', 'success')
		return redirect(url_for('users.user_type_detail', user_type_id=user_type_id))
	elif request.method == 'GET':
		form.user_type.data = a_user_type.user_type
		form.active.data = a_user_type.active
	return render_template('users/create_user_type.html', title="Perbarui Tipe Pengguna", legend="Perbarui Tipe Pengguna", form=form)

@users.route("/users/type/<int:user_type_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_user_type(user_type_id):
	if current_user.user_type_id > 3:
		abort(403)
	a_user_type = User_Type.query.get_or_404(user_type_id)
	db.session.delete(a_user_type)
	db.session.commit()
	flash('Tipe Pengguna Telah Dihapus', 'success')
	return redirect(url_for('users.user_type'))

#User
@users.route("/users_list")
@login_required
def users_list():
	if current_user.user_type_id > 2:
		abort(403)
	page = request.args.get('page', 1, type=int)
	users = db.session.query(User, User_Org, User_Cohort).filter(User.org_id==User_Org.id, User.cohort_id==User_Cohort.id).order_by(User.added_on.asc()).paginate(page=page, per_page=10)
	return render_template("users/users.html", title="Daftar Pengguna", users=users, type="Pengguna", url="users.users_list")

@users.route("/users/students")
@login_required
def students_list():
	page = request.args.get('page', 1, type=int)
	users = db.session.query(User, User_Org, User_Cohort).filter(User.org_id==User_Org.id, User.cohort_id==User_Cohort.id, User.user_type_id==6).order_by(User.added_on.asc()).paginate(page=page, per_page=10)
	return render_template("users/users.html", title="Daftar Siswa", users=users, type="Siswa", url="users.students_list")

@users.route("/users/teachers")
@login_required
def teachers_list():
	page = request.args.get('page', 1, type=int)
	users = db.session.query(User, User_Org, User_Cohort).filter(User.org_id==User_Org.id, User.cohort_id==User_Cohort.id, User.user_type_id==5).order_by(User.added_on.asc()).paginate(page=page, per_page=10)
	return render_template("users/users.html", title="Daftar Pengajar", users=users, type="Pengajar", url="users.teachers_list")

@users.route("/users/admins")
@login_required
def admins_list():
	if current_user.user_type_id > 3:
		abort(403)
	page = request.args.get('page', 1, type=int)
	users = db.session.query(User, User_Org, User_Cohort).filter(User.org_id==User_Org.id, User.cohort_id==User_Cohort.id, User.user_type_id<=4).order_by(User.added_on.asc()).paginate(page=page, per_page=10)
	return render_template("users/users.html", title="Daftar Admin", users=users, type="Admin", url="users.admins_list")

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = AccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data.strip().replace(" ", "").lower()
		current_user.email = form.email.data.replace(" ", "").lower()
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.first_name = form.first_name.data
		current_user.last_name = form.last_name.data
		current_user.last_updated = datetime.utcnow()
		db.session.commit()
		flash('Data Pengguna Telah Diperbarui', 'success')
		return redirect(url_for('users.account'))
	form.username.data = current_user.username
	form.email.data = current_user.email
	form.first_name.data = current_user.first_name
	form.last_name.data = current_user.last_name
	return render_template('users/account.html', form=form)

@users.route("/reset_password", methods=['GET', 'POST'])
@login_required
def reset_password():
	form = ResetPasswordForm()
	if form.validate_on_submit():
		if bcrypt.check_password_hash(current_user.password, form.old_password.data):
			hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
			current_user.password = hashed_password
			current_user.last_updated = datetime.utcnow()
			db.session.commit()
			flash('Password berhasil di reset.', 'success')
			return redirect(url_for('users.account'))
		else:
			flash('Password Lama Tidak Sesuai', 'danger')
	return render_template("users/reset_password.html", form=form)

@users.route("/users/add", methods=['GET', 'POST'])
@login_required
def add_user():
	form = CreateUserForm()
	if form.validate_on_submit():
		strip_username = form.username.data.strip().replace(" ", "").lower()
		clear_email = form.email.data.replace(" ", "").lower()
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=strip_username, email=clear_email, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data, phone=form.phone.data, bank_account=form.bank_account.data, virtual_account_number_0=form.virtual_account_number_0.data, virtual_account_number_1=form.virtual_account_number_1.data, virtual_account_number_2=form.virtual_account_number_2.data, account_note=form.account_note.data, active=form.active.data, org_id=form.org_id.data.id, cohort_id=form.cohort_id.data.id, user_type_id=form.user_type_id.data.id)
		db.session.add(user)
		db.session.commit()
		flash('Pengguna telah ditambahkan', 'success')
		return redirect(url_for('users.students_list'))
	form.active.data = True
	return render_template('users/create_user.html', title="Tambah Pengguna", legend="Tambah Pengguna", form=form)

@users.route("/users/<string:username>", methods=['GET', 'POST'])
@login_required
def user_detail(username):
	user= User.query.filter(User.username == username).first()
	if user is None:
		abort(404)
	return render_template('users/user.html', title=user.username, user=user)

@users.route("/users/<string:username>/update", methods=['GET', 'POST'])
@login_required
def update_user(username):
	user= User.query.filter(User.username == username).first()
	if user is None:
		abort(404)
	if current_user.user_type_id > user.user_type_id:
		abort(403)
	user_org = User_Org.query.get(user.org_id)
	user_cohort = User_Cohort.query.get(user.cohort_id)
	user_type = User_Type.query.get(user.user_type_id)
	form = UpdateUserForm(org_id=user_org, cohort_id=user_cohort, user_type_id=user.user_type)
	if form.validate_on_submit():
		bills = Bill.query.filter_by(user_id=user.id).all()
		if bills and not form.active.data:
			flash('Pengguna memiliki tagihan aktif', 'danger')
			return redirect(url_for('users.update_user', username=user.username))
		user.username = form.username.data.strip().replace(" ", "").lower()
		user.email = form.email.data.replace(" ", "").lower()
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			user.image_file = picture_file
		user.first_name = form.first_name.data
		user.last_name = form.last_name.data
		user.phone = form.phone.data
		user.bank_account = form.bank_account.data
		user.virtual_account_number_0 = form.virtual_account_number_0.data
		user.virtual_account_number_1 = form.virtual_account_number_1.data
		user.virtual_account_number_2 = form.virtual_account_number_2.data
		user.account_note = form.account_note.data
		user.active = form.active.data
		user.org_id=form.org_id.data.id
		user.cohort_id=form.cohort_id.data.id
		user.user_type_id=form.user_type_id.data.id
		user.last_updated = datetime.utcnow()
		db.session.commit()
		flash('Data Pengguna Telah Diperbarui', 'success')
		return redirect(url_for('users.user_detail', username=user.username))
	elif request.method == 'GET':
		form.username.data = user.username
		form.email.data = user.email
		form.first_name.data = user.first_name
		form.last_name.data = user.last_name
		form.phone.data = user.phone
		form.bank_account.data = user.bank_account
		form.virtual_account_number_0.data = user.virtual_account_number_0
		form.virtual_account_number_1.data = user.virtual_account_number_1
		form.virtual_account_number_2.data = user.virtual_account_number_2
		form.account_note.data = user.account_note
		form.active.data = user.active
	image_file = url_for('static', filename=user.image_file)
	return render_template('users/user_update.html', title="Perbarui Data Pengguna", legend="Perbarui Data Pengguna", image_file=image_file, form=form)

@users.route("/users/<string:username>/delete", methods=['GET', 'POST'])
@login_required
def delete_user(username):
	user= User.query.filter(User.username == username).first()
	if user is None:
		abort(404)
	if user.active:
		flash('Pengguna masih terdata aktif dalam sistem', 'danger')
		return redirect(url_for('users.user_detail', username=user.username))
	payments = Payment.query.filter(Payment.user_id == user.id).all()
	if payments:
		flash('Pengguna memiliki riwayat pembayaran dalam sistem', 'danger')
		return redirect(url_for('users.user_detail', username=user.username))
	bills = Bill.query.filter(Bill.user_id == user.id).all()
	if bills:
		flash('Pengguna memiliki riwayat tagihan dalam sistem', 'danger')
		return redirect(url_for('users.user_detail', username=user.username))
	db.session.delete(user)
	db.session.commit()
	flash('Pengguna Telah Dihapus', 'success')
	return redirect(url_for('users.users_list'))

@users.route("/users/paybilldetail/<string:username>")
@login_required
def paybilldetail_user(username):
	user = db.session.query(User, User_Org, User_Cohort, User_Type).filter(User.org_id==User_Org.id, User.cohort_id==User_Cohort.id, User.user_type_id==User_Type.id, User.username==username, User_Type.id == 6).first()
	if user is None:
		abort(404)
	bills = db.session.query(Bill, User, Service).filter(Bill.user_id==User.id, Bill.service_id==Service.id, Bill.user_id==user.User.id).order_by(Service.service.asc()).all()
	payments = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service).filter(Payment.bill_id==Bill.id, Payment.payment_type_id==Payment_Type.id, Payment.payment_method_id==Payment_Method.id, Payment.user_id==User.id, Bill.service_id==Service.id, Payment.user_id==user.User.id).order_by(Payment.added_on.asc()).all()

	return render_template('users/paybilldetail_user.html', user=user, bills=bills, payments=payments, title=f"Detail Tagihan dan Pembayaran {user.User.full_name}")


@users.route("/users/withdrawaldetail/<string:username>")
@login_required
def withdrawaldetail_user(username):
	user = db.session.query(User, User_Org, User_Cohort, User_Type).filter(User.org_id==User_Org.id, User.cohort_id==User_Cohort.id, User.user_type_id==User_Type.id, User.username==username, User_Type.id == 5).first()
	if user is None:
		abort(404)
	services = db.session.query(Service).filter(Service.user_id == user.User.id).order_by(Service.id.asc()).all()

	withdrawals = db.session.query(Withdrawal, Service, Withdrawal_Type, Withdrawal_Method, User).filter(Withdrawal.service_id == Service.id, Withdrawal.withdrawal_type_id == Withdrawal_Type.id, Withdrawal.withdrawal_method_id == Withdrawal_Method.id, Service.user_id == User.id, User.id == user.User.id).order_by(Withdrawal.added_on.asc()).all()

	return render_template('users/withdrawaldetail_user.html', user=user, services=services, withdrawals=withdrawals, title=f"Detail Saldo dan Penarikan Tunai {user.User.full_name}")


@users.route("/user_cohort/reportstatus", methods=['GET', 'POST'])
@login_required
def report_status():
	if current_user.user_type_id > 4:
		abort(403)
	form = ReportBillUserCohort()
	bills = None
	if form.validate_on_submit():
		bills = db.session.query(Bill, User, User_Cohort, Service).filter(User.cohort_id == User_Cohort.id, Bill.user_id == User.id, Bill.service_id == Service.id, User_Cohort.id == form.cohort.data.id, Service.id == form.service.data.id, Bill.active == True).order_by(User.first_name.asc()).all()
	return render_template("users/report_status.html", form=form, title="Laporan Status", bills=bills, status=form.isDone.data)

@users.route("/user_cohort/changecohort", methods=['GET', 'POST'])
@login_required
def change_cohort():
	if current_user.user_type_id > 3:
		abort(403)
	form = None
	return render_template("users/change_cohort.html", form=form, title="Ubah Kohort Masal")


@users.route("/user_cohort/showuserspercohort", methods=['GET', 'POST'])
@login_required
def show_users_per_cohort():
	if current_user.user_type_id > 4:
		abort(403)
	form = ShowUsersCohort()
	users = None
	if form.validate_on_submit():
		users = db.session.query(User, User_Cohort).filter(User.cohort_id == User_Cohort.id, User_Cohort.id == form.cohort.data.id).order_by(User.first_name.asc()).all()
	return render_template("users/show_users_per_cohort.html", form=form, title="Daftar Siswa per Kelas", users=users)

@users.route("/user_cohort/reportallbillsandpaymentspercohort", methods=['GET', 'POST'])
@login_required
def report_all_bills_and_payments_per_cohort():
	if current_user.user_type_id > 4:
		abort(403)
	form = ReportAllBillsPaymentsUserCohort()
	bills = None
	payments = None
	services = None
	users = None
	if form.validate_on_submit():
		services = [form.service1.data, form.service2.data, form.service3.data, form.service4.data, form.service5.data, form.service6.data, form.service7.data, form.service8.data, form.service9.data, form.service10.data, form.service11.data, form.service12.data, form.service13.data, form.service14.data, form.service15.data]
		users = db.session.query(User, User_Cohort).filter(User.cohort_id == User_Cohort.id, User_Cohort.id == form.cohort.data.id).order_by(User.first_name.asc()).all()
		# print(users)
		return render_template("users/report_all_bills_and_payments_output.html", title="Laporan", services=services, users=users)
	return render_template("users/report_all_bills_and_payments_per_cohort.html", form=form, title="Laporan Per Kelas", payments=payments, bills=bills, users=users, services=services)
