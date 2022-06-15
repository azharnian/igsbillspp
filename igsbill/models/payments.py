from datetime import datetime

from igsbill import db

class Payment_Type(db.Model):

	__tablename__ = "payment_type"
	id = db.Column(db.Integer, primary_key=True)
	transaction_type = db.Column(db.String(32), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	payments = db.relationship('Payment', backref='payment_type', lazy=True)

	def __repr__(self):
		return f"Transaction Type ('{self.transaction_type}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

class Payment_Method(db.Model):

	__tablename__ = "payment_method"
	id = db.Column(db.Integer, primary_key=True)
	method = db.Column(db.String(32), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	payments = db.relationship('Payment', backref='payment_method', lazy=True)

	def __repr__(self):
		return f"Payment Type ('{self.method}', '{self.active}', '{self.added_on}', '{self.last_updated}')"


class Payment(db.Model):

	__tablename__=  "payments"
	id = db.Column(db.BigInteger, primary_key=True)
	code = db.Column(db.String(120), nullable=False)
	amount = db.Column(db.Float, nullable=False, default=0)
	note = db.Column(db.String(120))
	reference = db.Column(db.String(120))
	image_file = db.Column(db.String(120), nullable=False, default="payments/default.jpg")
	confirmation = db.Column(db.Boolean, nullable=False, default=False)
	on_process = db.Column(db.Boolean, nullable=False, default=False)
	success = db.Column(db.Boolean, nullable=False, default=False)
	payment_type_id = db.Column(db.Integer, db.ForeignKey("payment_type.id"), nullable=False)
	payment_method_id = db.Column(db.Integer, db.ForeignKey("payment_method.id"), nullable=False)
	bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	
	def __repr__(self):
		return f"Payment ('{self.code}', '{self.amount}', '{self.active}', '{self.user_id}', '{self.admin_id}', '{self.bill_id}','{self.added_on}', '{self.last_updated}')"

	@property
	def kwitansi_number(self):
		return f"{self.id:08d}"
	
