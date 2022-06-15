from datetime import datetime, timedelta

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, session
from flask_login import current_user, login_required

from sqlalchemy import and_

from igsbill import db, bcrypt
from igsbill.models.withdrawals import Withdrawal, Withdrawal_Method, Withdrawal_Type
from igsbill.models.payments import Payment_Type, Payment_Method, Payment
from igsbill.models.bills import Bill
from igsbill.models.services import Service
from igsbill.models.users import User, User_Org, User_Cohort
from igsbill.withdrawals.forms import CreateWithdrawalMethodForm, CreateWithdrawalForm, ConfirmationWithdrawalForm, ConfirmationAdminForm, MutasiIntervalForm
from igsbill.withdrawals.utils import generate_withdrawal_code, generate_qr_code, save_picture

withdrawals = Blueprint('withdrawals', __name__)

from igsbill.withdrawals.filters import currency_format, datetime_format

#Payment_Method
@withdrawals.route("/withdrawals/methods")
@login_required
def withdrawal_methods():
	if current_user.user_type_id > 3:
		abort(403)
	withdrawal_methods = Withdrawal_Method.query.all()
	return render_template("withdrawals/withdrawal_methods.html", title="Daftar Metode Tarik Tunai", withdrawal_methods=withdrawal_methods)

@withdrawals.route("/withdrawals/methods/add", methods=['GET', 'POST'])
@login_required
def add_withdrawal_method():
	if current_user.user_type_id > 3:
		abort(403)
	form = CreateWithdrawalMethodForm()
	if form.validate_on_submit():
		withdrawal_method = Withdrawal_Method(method=form.method.data, active=form.active.data)
		db.session.add(withdrawal_method)
		db.session.commit()
		flash('Metode Tarik Tunai Telah Dibuat', 'success')
		return redirect(url_for('withdrawals.withdrawal_methods'))
	form.active.data = True
	return render_template('withdrawals/create_withdrawal_method.html', title="Tambah Metode Tarik Tunai", legend="Tambah Metode Tarik Tunai", form=form)

@withdrawals.route("/withdrawals/methods/<int:withdrawal_method_id>", methods=['GET', 'POST'])
@login_required
def withdrawal_method_detail(withdrawal_method_id):
	if current_user.user_type_id > 3:
		abort(403)
	withdrawal_method = Withdrawal_Method.query.get_or_404(withdrawal_method_id)
	return render_template('withdrawals/withdrawal_method.html', title=withdrawal_method.method, withdrawal_method=withdrawal_method)


@withdrawals.route("/withdrawals/methods/<int:withdrawal_method_id>/update", methods=['GET', 'POST'])
@login_required
def update_withdrawal_method(withdrawal_method_id):
	if current_user.user_type_id > 3:
		abort(403)
	withdrawal_method = Withdrawal_Method.query.get_or_404(withdrawal_method_id)
	form = CreateWithdrawalMethodForm()
	if form.validate_on_submit():
		withdrawal_method.method = form.method.data
		withdrawal_method.active = form.active.data
		withdrawal_method.last_updated = datetime.utcnow()
		db.session.commit()
		flash('Data Metode Penarikan Telah Diperbarui', 'success')
		return redirect(url_for('withdrawals.withdrawal_methods'))
	form.method.data = withdrawal_method.method
	form.active.data = withdrawal_method.active
	return render_template('withdrawals/create_withdrawal_method.html', title="Perbarui Metode Penarikan", legend="Perbarui Metode Penarikan", form=form)

@withdrawals.route("/withdrawals/methods/<int:withdrawal_method_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_withdrawal_method(withdrawal_method_id):
	if current_user.user_type_id > 3:
		abort(403)
	withdrawal_method = Withdrawal_Method.query.get_or_404(withdrawal_method_id)
	db.session.delete(withdrawal_method)
	db.session.commit()
	flash('Metode Penarikan Telah Dihapus', 'success')
	return redirect(url_for('withdrawals.withdrawal_methods'))


@withdrawals.route("/withdrawals/add_withdrawal/<int:service_id>", methods=['GET', 'POST'])
@login_required
def add_withdrawal(service_id):
	if 'withdrawal_confirmation_detail' in session:
		session.pop('withdrawal_confirmation_detail')
	service = db.session.query(Service, User, User_Org, User_Cohort).filter(Service.user_id == User.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, Service.id == service_id).first()
	if not service:
		abort(404)
	form = CreateWithdrawalForm()

	total_withdrawal_paid = 0
	if service.Service.withdrawals :
		for withdrawal in service.Service.withdrawals:
			if withdrawal.active:
				total_withdrawal_paid += withdrawal.amount

	total_bill_paid = 0
	if service.Service.bills:
		for bill in service.Service.bills:
			bill_paid =0
			if bill.payments:
				for payment in bill.payments:
					bill_paid += payment.amount
				bill_paid = (bill_paid - service.Service.tax - service.Service.additional) * (service.Service.sharing_percentage/100)
			total_bill_paid += bill_paid

	left = total_bill_paid - total_withdrawal_paid
	status = "BELUM LUNAS"
	if total_bill_paid == total_withdrawal_paid:
		status = "LUNAS"
	elif total_bill_paid < total_withdrawal_paid:
		status = "LEBIH BAYAR"

	if form.validate_on_submit():
		if int(form.amount.data) > left:
			flash("Jumlah Saldo Tidak Mencukupi untuk Melakukan Penarikan.", 'danger')
			return redirect(url_for('withdrawals.add_withdrawal', service_id=service.Service.id))
		elif int(form.amount.data) < 0:
			flash("Jumlah Penarikan Tidak Valid.", 'danger')
			return redirect(url_for('withdrawals.add_withdrawal', service_id=service.Service.id))
		data = {
			'user_id' : service.Service.user_id,
			'user_username' : service.User.username,
			'user_full_name' : service.User.full_name,
			'service' : service.Service.service,
			'service_id' : service.Service.id,
			'amount' : int(form.amount.data),
			'withdrawal_method' : form.withdrawal_method.data.method,
			'withdrawal_method_id' : form.withdrawal_method.data.id,
			'reference' : form.reference.data,
			'note' : form.note.data,
			'confirmation' : True
		}
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			data['image_file'] = picture_file
		else:
			data['image_file'] = 'withdrawals/default.jpg'
		print(data)
		session['withdrawal_confirmation_detail'] = data
		return redirect(url_for('withdrawals.confirmation_withdrawal', service_id=data['service_id']))
	form.service_id.data = service.Service.id
	form.confirmation.data = True
	return render_template('withdrawals/create_withdrawal.html', title=f"Penarikan - {service.Service.service} - {service.User.full_name}", total_bill_paid=total_bill_paid, total_withdrawal_paid=total_withdrawal_paid, status=status, form=form, service=service)

@withdrawals.route("/withdrawals/confirmation_withdrawal/<int:service_id>", methods=['GET', 'POST'])
@login_required
def confirmation_withdrawal(service_id):
	if 'withdrawal_confirmation_detail' not in session:
		return redirect(url_for('main.withdrawal_check'))
	if session['withdrawal_confirmation_detail']['service_id'] != service_id:
		session.pop('withdrawal_confirmation_detail')
		return redirect(url_for('main.withdrawal_check'))
	form = ConfirmationWithdrawalForm()
	withdrawal_data = session['withdrawal_confirmation_detail']
	if form.validate_on_submit():
		admin = User.query.filter_by(username=current_user.username).first()
		if bcrypt.check_password_hash(admin.password, form.password.data) and admin.user_type_id <= 4:
			code = generate_withdrawal_code()
			withdrawal = Withdrawal(code=code, amount=withdrawal_data['amount'], note=withdrawal_data['note'], reference=withdrawal_data['reference'], confirmation=withdrawal_data['confirmation'], success=True, withdrawal_type_id=1, withdrawal_method_id=withdrawal_data['withdrawal_method_id'], service_id=withdrawal_data['service_id'], image_file=withdrawal_data['image_file'], admin_id=current_user.id)
			db.session.add(withdrawal)
			db.session.commit()
			session.pop('withdrawal_confirmation_detail')
			flash('Penarikan Sukses di Proses', 'success')
			return render_template('withdrawals/success_withdrawal.html', withdrawal_data=withdrawal_data, code=code)
		else:
			flash('Kata sandi tidak cocok', 'danger')
	return render_template('withdrawals/confirmation_withdrawal.html', withdrawal_data=withdrawal_data, form=form, title="Konfirmasi Penarikan")


@withdrawals.route("/withdrawals/print/<string:withdrawal_code>")
@login_required
def print_withdrawal(withdrawal_code):
	withdrawal = db.session.query(Withdrawal, Withdrawal_Type, Withdrawal_Method, Service, User).filter(Withdrawal.withdrawal_type_id == Withdrawal_Type.id, Withdrawal.withdrawal_method_id == Withdrawal_Method.id, Withdrawal.service_id == Service.id, Service.user_id == User.id, Withdrawal.code == withdrawal_code).first()
	if withdrawal is None:
		abort(404)
	#url = str(request.host_url)+"withdrawals/print/"+str(withdrawal_code)
	url = "http://my.ignatiusglobal.sch.id/withdrawals/print/"+str(withdrawal_code)
	qr_code = generate_qr_code(url)
	return render_template('withdrawals/kwitansi_withdrawal.html', withdrawal=withdrawal, title=f"Kwitansi - {withdrawal_code}", qr=qr_code.decode('utf-8'))


@withdrawals.route("/withdrawals/history/<int:service_id>")
@login_required
def history_withdrawal(service_id):
	service = db.session.query(Service, User, User_Org, User_Cohort).filter(Service.user_id == User.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, Service.id == service_id).first()
	if not service:
		abort(404)
	url = str(request.host_url)+"withdrawals/history/"+str(service_id)
	qr_code = generate_qr_code(url)
	return render_template('withdrawals/history_withdrawals.html', service=service, title=f"Riwayat Penarikan Saldo Layanan - {service_id}", qr=qr_code.decode('utf-8'))


@withdrawals.route("/withdrawals/cancel/<string:withdrawal_code>", methods=['GET', 'POST'])
@login_required
def cancel_withdrawal(withdrawal_code):
	withdrawal = db.session.query(Withdrawal, Withdrawal_Type, Withdrawal_Method, Service, User).filter(Withdrawal.withdrawal_type_id == Withdrawal_Type.id, Withdrawal.withdrawal_method_id == Withdrawal_Method.id, Withdrawal.service_id == Service.id, Service.user_id == User.id, Withdrawal.code == withdrawal_code).first()
	if withdrawal is None:
		abort(404)
	if not withdrawal.Service.active:
		flash('Aktifkan Layanan untuk pembayaran ini terlebih dahulu.', 'danger')
		return redirect(url_for('users.withdrawaldetail_user', username=withdrawal.User.username))
	form = ConfirmationAdminForm()
	if form.validate_on_submit():
		admin = User.query.filter_by(username=form.username.data).first()
		if bcrypt.check_password_hash(admin.password, form.password.data) and admin.user_type_id <= 3:
			withdrawal.Withdrawal.active = not withdrawal.Withdrawal.active
			withdrawal.Withdrawal.last_updated = datetime.utcnow()
			db.session.commit()
			if withdrawal.Withdrawal.active:
				flash('Penarikan Telah Berhasil Diaktifkan', 'success')
			else:
				flash('Penarikan Telah Berhasil Dibatalkan', 'success')
			return redirect(url_for('users.withdrawaldetail_user', username=withdrawal.User.username))
		else:
			flash('Username admin dan kata sandi tidak cocok', 'danger')
	return render_template("withdrawals/cancel_withdrawal_confirmation.html", withdrawal=withdrawal,form=form)


@withdrawals.route("/withdrawals/view/<string:withdrawal_code>", methods=['GET', 'POST'])
@login_required
def view_withdrawal(withdrawal_code):
	withdrawal = Withdrawal.query.filter_by(code=withdrawal_code).first()
	if withdrawal:
		return render_template("withdrawals/view_withdrawal_image.html", withdrawal=withdrawal)
	abort(404)


@withdrawals.route("/withdrawals/mutasi_interval", methods=['GET', 'POST'])
@login_required
def mutasi_interval_withdrawal():
	if current_user.user_type_id > 3:
		abort(403)
	form = MutasiIntervalForm()
	withdrawals = None
	withdrawal_method_summary = {}
	if form.validate_on_submit():
		start_time = datetime.strptime(str(form.from_date.data), '%Y-%m-%d') + timedelta(hours = 7)
		end_time = datetime.strptime(str(form.to_date.data), '%Y-%m-%d') + timedelta(days = 1, hours = 7)
		if end_time <= start_time:
			flash("Rentang Waktu Tidak Valid", "danger")
			return render_template("withdrawals/mutasi_interval_withdrawal.html", form=form, title="Mutasi Penarikan", withdrawals=withdrawals, withdrawal_method_summary=withdrawal_method_summary)
		if form.service.data:
			withdrawals = db.session.query(Withdrawal, Withdrawal_Type, Withdrawal_Method, User, Service, User_Org, User_Cohort).filter(Withdrawal.withdrawal_type_id == Withdrawal_Type.id, Withdrawal.withdrawal_method_id == Withdrawal_Method.id, Withdrawal.service_id == Service.id, Service.user_id == User.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, and_(Withdrawal.added_on >= start_time, Withdrawal.added_on <= end_time), Service.id == form.service.data.id, Withdrawal.active == True).order_by(Withdrawal.added_on.asc()).all()
		else:
			withdrawals = db.session.query(Withdrawal, Withdrawal_Type, Withdrawal_Method, User, Service, User_Org, User_Cohort).filter(Withdrawal.withdrawal_type_id == Withdrawal_Type.id, Withdrawal.withdrawal_method_id == Withdrawal_Method.id, Withdrawal.service_id == Service.id, Service.user_id == User.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, and_(Withdrawal.added_on >= start_time, Withdrawal.added_on <= end_time), Withdrawal.active == True).order_by(Withdrawal.added_on.asc()).all()
		withdrawal_method_list = []
		for withdrawal in withdrawals:
			withdrawal_method_list.append(withdrawal.Withdrawal_Method.method)
		withdrawal_method_list = list(set(withdrawal_method_list))
		for withdrawal in withdrawal_method_list:
			withdrawal_method_summary[withdrawal] = 0
		for withdrawal in withdrawals:
			withdrawal_method_summary[withdrawal.Withdrawal_Method.method] += withdrawal.Withdrawal.amount
	return render_template("withdrawals/mutasi_interval_withdrawal.html", form=form, title="Mutasi Interval Penarikan", withdrawals=withdrawals, withdrawal_method_summary=withdrawal_method_summary)
