import io
import csv

from igsbill import db

def ImportCSV(csv_file, delimiter):
	stream = io.StringIO(csv_file.read().decode("UTF8"), newline=None)
	return csv.reader(stream, delimiter=delimiter)

def AddToDb(data):
	db.session.add(data)
	try:
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		return (e, 'danger')
	else:
		return ("Telah ditambahkan", 'success')