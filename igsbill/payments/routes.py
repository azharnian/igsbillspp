from datetime import datetime, timedelta

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, session
from flask_login import current_user, login_required

from sqlalchemy import and_

from igsbill import db, bcrypt
from igsbill.models.payments import Payment_Type, Payment_Method, Payment
from igsbill.models.bills import Bill
from igsbill.models.services import Service
from igsbill.models.users import User, User_Org, User_Cohort
from igsbill.payments.forms import CreatePaymentMethodForm, CreatePaymentForm, ConfirmationPaymentForm, ConfirmationAdminForm, MutasiForm, MutasiIntervalForm
from igsbill.payments.utils import generate_payment_code, generate_qr_code, save_picture

payments = Blueprint('payments', __name__)

from igsbill.payments.filters import currency_format, datetime_format

#Payment_Method
@payments.route("/payments/methods")
@login_required
def payment_methods():
	if current_user.user_type_id > 3:
		abort(403)
	payment_methods = Payment_Method.query.all()
	return render_template("payments/payment_methods.html", title="Daftar Metode Pembayaran", payment_methods=payment_methods)

@payments.route("/payments/methods/add", methods=['GET', 'POST'])
@login_required
def add_payment_method():
	if current_user.user_type_id > 3:
		abort(403)
	form = CreatePaymentMethodForm()
	if form.validate_on_submit():
		payment_method = Payment_Method(method=form.method.data, active=form.active.data)
		db.session.add(payment_method)
		db.session.commit()
		flash('Metode Pembayaran Telah Dibuat', 'success')
		return redirect(url_for('payments.payment_methods'))
	form.active.data = True
	return render_template('payments/create_payment_method.html', title="Tambah Metode Pembayaran", legend="Tambah Metode Pembayaran", form=form)

@payments.route("/payments/methods/<int:payment_method_id>", methods=['GET', 'POST'])
@login_required
def payment_method_detail(payment_method_id):
	if current_user.user_type_id > 3:
		abort(403)
	payment_method = Payment_Method.query.get_or_404(payment_method_id)
	return render_template('payments/payment_method.html', title=payment_method.method, payment_method=payment_method)

@payments.route("/payments/methods/<int:payment_method_id>/update", methods=['GET', 'POST'])
@login_required
def update_payment_method(payment_method_id):
	if current_user.user_type_id > 3:
		abort(403)
	payment_method = Payment_Method.query.get_or_404(payment_method_id)
	form = CreatePaymentMethodForm()
	if form.validate_on_submit():
		payment_method.method = form.method.data
		payment_method.active = form.active.data
		payment_method.last_updated = datetime.utcnow()
		db.session.commit()
		flash('Data Metode Pembayaran Telah Diperbarui', 'success')
		return redirect(url_for('payments.payment_methods'))
	form.method.data = payment_method.method
	form.active.data = payment_method.active
	return render_template('payments/create_payment_method.html', title="Perbarui Metode Pembayaran", legend="Perbarui Metode Pembayaran", form=form)

@payments.route("/payments/methods/<int:payment_method_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_payment_method(payment_method_id):
	if current_user.user_type_id > 3:
		abort(403)
	payment_method = Payment_Method.query.get_or_404(payment_method_id)
	db.session.delete(payment_method)
	db.session.commit()
	flash('Metode Pembayaran Telah Dihapus', 'success')
	return redirect(url_for('payments.payment_methods'))

@payments.route("/payments/add_payment/<string:bill_code>", methods=['GET', 'POST'])
@login_required
def add_payment(bill_code):
	if 'payment_confirmation_detail' in session:
		session.pop('payment_confirmation_detail')
	bill = db.session.query(Bill, User, Service).filter(Bill.code == bill_code, Bill.user_id==User.id, Bill.service_id==Service.id, Bill.active==True).first()
	if not bill:
		abort(404)
	form = CreatePaymentForm()
	payments = Payment.query.filter(Payment.bill_id == bill.Bill.id).all()
	total_payment = 0
	for payment in payments:
		if payment.active:
			total_payment += payment.amount
	status = "BELUM LUNAS"
	if total_payment == bill.Service.total_price:
		status = "LUNAS"
	elif total_payment > bill.Service.total_price:
		status = "LEBIH BAYAR"

	if form.validate_on_submit():
		if int(form.amount.data) > (bill.Service.total_price - total_payment):
			flash("Jumlah Pembayaran Melebihi Tagihan.", 'danger')
			return redirect(url_for('payments.add_payment', bill_code=bill.Bill.code))
		elif int(form.amount.data) < 0:
			flash("Jumlah Pembayaran Tidak Valid.", 'danger')
			return redirect(url_for('payments.add_payment', bill_code=bill.Bill.code))
		data = {
			'user_id' : bill.Bill.user_id,
			'user_username' : bill.User.username,
			'user_full_name' : bill.User.full_name,
			'service' : bill.Service.service,
			'bill_id' : bill.Bill.id,
			'bill_code' : form.bill_code.data,
			'amount' : int(form.amount.data),
			'payment_method' : form.payment_method.data.method,
			'payment_method_id' : form.payment_method.data.id,
			'reference' : form.reference.data,
			'note' : form.note.data,
			'confirmation' : True
		}
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			data['image_file'] = picture_file
		else:
			data['image_file'] = 'payments/default.jpg'
		session['payment_confirmation_detail'] = data
		return redirect(url_for('payments.confirmation_payment', bill_code=data['bill_code']))
	form.bill_code.data = bill.Bill.code
	form.confirmation.data = True
	return render_template('payments/create_payment.html', title=f"Pembayaran - {bill.Service.service} - {bill.Bill.code}",bill=bill, payments=payments, total_payment=total_payment, status=status, form=form)

@payments.route("/payments/confirmation_payment/<string:bill_code>", methods=['GET', 'POST'])
@login_required
def confirmation_payment(bill_code):
	if 'payment_confirmation_detail' not in session:
		return redirect(url_for('main.home'))
	if session['payment_confirmation_detail']['bill_code'] != bill_code:
		session.pop('payment_confirmation_detail')
		return redirect(url_for('main.home'))
	form = ConfirmationPaymentForm()
	payment_data = session['payment_confirmation_detail']
	if form.validate_on_submit():
		admin = User.query.filter_by(username=current_user.username).first()
		if bcrypt.check_password_hash(admin.password, form.password.data) and admin.user_type_id <= 4:
			code = generate_payment_code()
			payment = Payment(code=code, amount=payment_data['amount'], note=payment_data['note'], reference=payment_data['reference'], confirmation=payment_data['confirmation'], success=True, payment_type_id=1, payment_method_id=payment_data['payment_method_id'], bill_id=payment_data['bill_id'], user_id=payment_data['user_id'], image_file=payment_data['image_file'], admin_id=current_user.id)
			db.session.add(payment)
			db.session.commit()
			session.pop('payment_confirmation_detail')
			flash('Pembayaran Sukses di Proses', 'success')
			return render_template('payments/success_payment.html', payment_data=payment_data, code=code)
		else:
			flash('Kata sandi tidak cocok', 'danger')
	return render_template('payments/confirmation_payment.html', payment_data=payment_data, form=form, title="Konfirmasi Pembayaran")

@payments.route("/payments/print/<string:payment_code>")
@login_required
def print_payment(payment_code):
	payment = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service, User_Org, User_Cohort).filter(Payment.payment_type_id == Payment_Type.id, Payment.payment_method_id == Payment_Method.id, Payment.bill_id == Bill.id, Payment.user_id == User.id, Bill.service_id == Service.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, Payment.code == payment_code).first()
	if payment is None:
		abort(404)
	#url = str(request.host_url)+"payments/print/"+str(payment_code)
	url = "http://my.ignatiusglobal.sch.id/payments/print/"+str(payment_code)
	qr_code = generate_qr_code(url)
	return render_template('payments/kwitansi_payment.html', payment=payment, title=f"Kwitansi - {payment_code}", qr=qr_code.decode('utf-8'))

@payments.route("/payments/history/<string:bill_code>")
@login_required
def history_payment(bill_code):
	bill = db.session.query(Bill, User, User_Org, User_Cohort, Service, Payment, Payment_Method, Payment_Type).filter(Bill.user_id == User.id, User.org_id == User_Org.id, User.cohort_id == User_Cohort.id, Bill.service_id == Service.id, Bill.id == Payment.bill_id, Payment.payment_method_id == Payment_Method.id, Payment.payment_type_id == Payment_Type.id, Bill.code == bill_code).first()
	if bill is None:
		abort(404)
	url = str(request.host_url)+"payments/history/"+str(bill_code)
	qr_code = generate_qr_code(url)
	return render_template('payments/history_payments.html', bill=bill, title=f"Riwayat Pembayaran Tagihan - {bill_code}", qr=qr_code.decode('utf-8'))

@payments.route("/payments/cancel/<string:payment_code>", methods=['GET', 'POST'])
@login_required
def cancel_payment(payment_code):
	payment = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service, User_Org, User_Cohort).filter(Payment.payment_type_id == Payment_Type.id, Payment.payment_method_id == Payment_Method.id, Payment.bill_id == Bill.id, Payment.user_id == User.id, Bill.service_id == Service.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, Payment.code == payment_code).first()
	if payment is None:
		abort(404)
	if not payment.Bill.active:
		flash('Aktifkan tagihan untuk pembayaran ini terlebih dahulu.', 'danger')
		return redirect(url_for('users.paybilldetail_user', username=payment.User.username))
	form = ConfirmationAdminForm()
	if form.validate_on_submit():
		admin = User.query.filter_by(username=form.username.data).first()
		if bcrypt.check_password_hash(admin.password, form.password.data) and admin.user_type_id <= 3:
			payment.Payment.active = not payment.Payment.active
			payment.Payment.last_updated = datetime.utcnow()
			db.session.commit()
			if payment.Payment.active:
				flash('Pembayaran Telah Berhasil Diaktifkan', 'success')
			else:
				flash('Pembayaran Telah Berhasil Dibatalkan', 'success')
			return redirect(url_for('users.paybilldetail_user', username=payment.User.username))
		else:
			flash('Username admin dan kata sandi tidak cocok', 'danger')
	return render_template("payments/cancel_payment_confirmation.html", payment=payment,form=form)

@payments.route("/payments/view/<string:payment_code>", methods=['GET', 'POST'])
@login_required
def view_payment(payment_code):
	payment = Payment.query.filter_by(code=payment_code).first()
	if payment:
		return render_template("payments/view_payment_image.html", payment=payment)
	abort(404)

@payments.route("/payments/mutasi", methods=['GET', 'POST'])
@login_required
def mutasi_payment():
	form = MutasiForm()
	payments = None
	payment_method_summary = {}
	if form.validate_on_submit():
		start_time = datetime.strptime(str(form.datepicker.data), '%Y-%m-%d') - timedelta(hours = 7)
		end_time = datetime.strptime(str(form.datepicker.data), '%Y-%m-%d') + timedelta(days = 1) - timedelta(hours = 7)
		if form.service.data:
			payments = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service, User_Org, User_Cohort).filter(Payment.payment_type_id == Payment_Type.id, Payment.payment_method_id == Payment_Method.id, Payment.bill_id == Bill.id, Payment.user_id == User.id, Bill.service_id == Service.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, and_(Payment.added_on >= start_time, Payment.added_on <= end_time), Service.id == form.service.data.id, Payment.active == True).order_by(Payment.added_on.asc()).all()
		else:
			payments = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service, User_Org, User_Cohort).filter(Payment.payment_type_id == Payment_Type.id, Payment.payment_method_id == Payment_Method.id, Payment.bill_id == Bill.id, Payment.user_id == User.id, Bill.service_id == Service.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, and_(Payment.added_on >= start_time, Payment.added_on <= end_time), Payment.active == True).order_by(Payment.added_on.asc()).all()
		payment_method_list = []
		for payment in payments:
			payment_method_list.append(payment.Payment_Method.method)
		payment_method_list = list(set(payment_method_list))
		for payment in payment_method_list:
			payment_method_summary[payment] = 0
		for payment in payments:
			payment_method_summary[payment.Payment_Method.method] += payment.Payment.amount
	return render_template("payments/mutasi_payment.html", form=form, title="Mutasi Pembayaran", payments=payments, payment_method_summary=payment_method_summary)


@payments.route("/payments/mutasi_interval", methods=['GET', 'POST'])
@login_required
def mutasi_interval_payment():
	if current_user.user_type_id > 3:
		abort(403)
	form = MutasiIntervalForm()
	payments = None
	payment_method_summary = {}
	if form.validate_on_submit():
		start_time = datetime.strptime(str(form.from_date.data), '%Y-%m-%d') - timedelta(hours = 7)
		end_time = datetime.strptime(str(form.to_date.data), '%Y-%m-%d') + timedelta(days = 1) - timedelta(hours = 7)
		if end_time <= start_time:
			flash("Rentang Waktu Tidak Valid", "danger")
			return render_template("payments/mutasi_interval_payment.html", form=form, title="Mutasi Pembayaran", payments=payments, payment_method_summary=payment_method_summary)
		if form.service.data:
			payments = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service, User_Org, User_Cohort).filter(Payment.payment_type_id == Payment_Type.id, Payment.payment_method_id == Payment_Method.id, Payment.bill_id == Bill.id, Payment.user_id == User.id, Bill.service_id == Service.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, and_(Payment.added_on >= start_time, Payment.added_on <= end_time), Service.id == form.service.data.id, Payment.active == True).order_by(Payment.added_on.asc()).all()
		else:
			payments = db.session.query(Payment, Payment_Type, Payment_Method, Bill, User, Service, User_Org, User_Cohort).filter(Payment.payment_type_id == Payment_Type.id, Payment.payment_method_id == Payment_Method.id, Payment.bill_id == Bill.id, Payment.user_id == User.id, Bill.service_id == Service.id, Service.org_id == User_Org.id, Service.cohort_id == User_Cohort.id, and_(Payment.added_on >= start_time, Payment.added_on <= end_time), Payment.active == True).order_by(Payment.added_on.asc()).all()
		payment_method_list = []
		for payment in payments:
			payment_method_list.append(payment.Payment_Method.method)
		payment_method_list = list(set(payment_method_list))
		for payment in payment_method_list:
			payment_method_summary[payment] = 0
		for payment in payments:
			payment_method_summary[payment.Payment_Method.method] += payment.Payment.amount
	return render_template("payments/mutasi_interval_payment.html", form=form, title="Mutasi Interval Pembayaran", payments=payments, payment_method_summary=payment_method_summary)
