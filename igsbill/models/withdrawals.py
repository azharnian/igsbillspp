from datetime import datetime

from igsbill import db

class Withdrawal_Type(db.Model):

	__tablename__ = "withdrawal_type"
	id = db.Column(db.Integer, primary_key=True)
	withdrawal_type = db.Column(db.String(32), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	withdrawals = db.relationship('Withdrawal', backref='withdrawal_type', lazy=True)

	def __repr__(self):
		return f"Withdrawal Type ('{self.withdrawal_type}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

class Withdrawal_Method(db.Model):

	__tablename__ = "withdrawal_method"
	id = db.Column(db.Integer, primary_key=True)
	method = db.Column(db.String(32), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	withdrawals = db.relationship('Withdrawal', backref='withdrawal_method', lazy=True)

	def __repr__(self):
		return f"Withdrawal Type ('{self.method}', '{self.active}', '{self.added_on}', '{self.last_updated}')"


class Withdrawal(db.Model):

	__tablename__=  "withdrawals"
	id = db.Column(db.BigInteger, primary_key=True)
	code = db.Column(db.String(16), nullable=False)
	amount = db.Column(db.Float, nullable=False, default=0)
	note = db.Column(db.String(120))
	reference = db.Column(db.String(120))
	image_file = db.Column(db.String(120), nullable=False, default="withdrawals/default.jpg")
	confirmation = db.Column(db.Boolean, nullable=False, default=False)
	on_process = db.Column(db.Boolean, nullable=False, default=False)
	success = db.Column(db.Boolean, nullable=False, default=False)
	withdrawal_type_id = db.Column(db.Integer, db.ForeignKey("withdrawal_type.id"), nullable=False)
	withdrawal_method_id = db.Column(db.Integer, db.ForeignKey("withdrawal_method.id"), nullable=False)
	service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
	admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	
	def __repr__(self):
		return f"Payment ('{self.code}', '{self.amount}', '{self.active}', '{self.user_id}', '{self.admin_id}', '{self.bill_id}','{self.added_on}', '{self.last_updated}')"

	@property
	def kwitansi_number(self):
		return f"{self.id:08d}"