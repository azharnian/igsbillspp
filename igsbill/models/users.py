from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import current_app
from flask_login import UserMixin

from igsbill import db, login_manager
from igsbill.models.services import *
from igsbill.models.bills import *
from igsbill.models.payments import *
from igsbill.models.withdrawals import *

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User_Org(db.Model):

	__tablename__ = "user_org"
	id = db.Column(db.Integer, primary_key=True)
	organization = db.Column(db.String(120), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	users = db.relationship('User', backref='user_org', lazy=True)
	services = db.relationship('Service', backref='service_org', lazy=True)

	def __repr__(self):
		return f"User Organization ('{self.organization}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

class User_Cohort(db.Model):

	__tablename__ = "user_cohort"
	id = db.Column(db.Integer, primary_key=True)
	cohort = db.Column(db.String(120), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	users = db.relationship('User', backref='user_cohort', lazy=True)
	services = db.relationship('Service', backref='service_cohort', lazy=True)

	def __repr__(self):
		return f"User Cohort ('{self.cohort}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

class User_Type(db.Model):

	__tablename__ = "user_type"
	id = db.Column(db.Integer, primary_key=True)
	user_type = db.Column(db.String(120), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	users = db.relationship('User', backref='user_type', lazy=True)

	def __repr__(self):
		return f"User Type ('{self.user_type}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

class User(db.Model, UserMixin):

	__tablename__ = "users"
	id = db.Column(db.BigInteger, primary_key=True)
	username = db.Column(db.String(120), unique=True, nullable=False)
	email = db.Column(db.String(120))
	image_file = db.Column(db.String(120), nullable=False, default="users/default.jpg")
	password = db.Column(db.String(120), nullable=False)
	first_name = db.Column(db.String(120), nullable=False)
	last_name = db.Column(db.String(120), nullable=False)
	phone = db.Column(db.String(120))
	bank_account = db.Column(db.String(120))
	virtual_account_number_0 = db.Column(db.String(120))
	virtual_account_number_1 = db.Column(db.String(120))
	virtual_account_number_2 = db.Column(db.String(120))
	account_note = db.Column(db.String(120))
	active = db.Column(db.Boolean, nullable=False, default=True)
	verified_email = db.Column(db.Boolean, nullable=False, default=False)
	verified_phone = db.Column(db.Boolean, nullable=False, default=False)
	verified_bank_account = db.Column(db.Boolean, nullable=False, default=False)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	last_login = db.Column(db.DateTime)
	last_ip = db.Column(db.String(120))
	org_id = db.Column(db.Integer, db.ForeignKey("user_org.id"), nullable=False)
	cohort_id = db.Column(db.Integer, db.ForeignKey("user_cohort.id"), nullable=False)
	user_type_id = db.Column(db.Integer, db.ForeignKey("user_type.id"), nullable=False)
	services = db.relationship('Service', backref='pic', lazy=True)
	bills = db.relationship('Bill', foreign_keys="Bill.user_id", backref='customer', lazy=True)
	bills_admin = db.relationship('Bill', foreign_keys="Bill.admin_id", backref='admin_bill', lazy=True)
	payments = db.relationship('Payment', foreign_keys="Payment.user_id", backref='payor', lazy=True)
	payments_admin = db.relationship('Payment', foreign_keys="Payment.admin_id", backref='admin_payment', lazy=True)
	withdrawals_admin = db.relationship('Withdrawal', backref='admin_withdrawal', lazy=True)

	def __repr__(self):
		return f"User ('{self.username}', '{self.email}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

	@property
	def full_name(self):
		return f"{self.first_name} {self.last_name}"

	def get_reset_token(self, expires_sec=1800):
		serializer = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		token = serializer.dumps({'user_id' : self.id}).decode('utf-8')
		return token

	@staticmethod
	def verify_reset_token(token):
		serial = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = serial.loads(token)['user_id']
		except :
			return None
		return User.query.get(user_id)
	