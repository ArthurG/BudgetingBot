import datetime
import uuid
import csv
import json
import gspread
import pytz

from oauth2client.service_account import ServiceAccountCredentials


with open ('config.txt') as json_file:
	data = json.load(json_file)
	sheetName = data['sheetName'] # -> share this spreadsheet with our api client mail
	filename = data['filename']
	delimiter = data['delimiter']
timezone = pytz.timezone('America/Atikokan')
	
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open(sheetName).sheet1  # processing the first workbook

class Expense(object):
	
	isLastSaved = False
	lastExpense = None
	
	def __init__(self, category, amount,billable):
		self.id = str(uuid.uuid4())
		self.category = category
		self.amount = amount
		self.billable = billable
		
		date = datetime.datetime.now(tz = timezone)
		self.time = date.strftime('%Y-%m-%d_%H:%M:%S')
		
		
def log(content):  # modified print() function that adds the hour to the print. More convenient for logging purposes.
    print(str(datetime.datetime.utcnow())[11:19] + " : " + content)

def saveToCsv():
	with open(filename, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter=delimiter)
		writer.writerows(sheet.get_all_values())
	log(f"Saved the spreadsheet to {filename}.")

def addExpense(expense):
	"adds an expense object in the sheet."
	lastRow = len(sheet.get_all_values())
	sliceStr = "A"+str(lastRow+1)+":E"+str(lastRow+1)
	
	sheet.update(sliceStr, [[expense.id, expense.category, expense.amount,expense.time,expense.billable]])
	log("Saved Expense to the spreadhseet.")
	saveToCsv()

def delExpense(id):
	"deletes an activity based on a given id."
	try:
		cell = sheet.find(id)
		sheet.delete_rows(cell.row)
		log(f"successfully deleted the row of id {id}")
		saveToCsv()
	except gspread.exceptions.CellNotFound:
		log("Could not delete : the given Id does not exists in the sheet.")

