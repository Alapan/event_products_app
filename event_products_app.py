import MySQLdb
import re
from re import sub
from decimal import Decimal


def connection():
	'''returns a cursor object which can access the database'''
	try:
		# open database connection. The parameters have to be set according to the MySQL installation being used
		db = MySQLdb.connect(host="127.0.0.1", port=3306, user="root", passwd="root")
		cursor = db.cursor()
		return cursor

	except MySQLdb.Error as e:
		print(e)

def validate_event_name(event_name):
	'''run query against entered event name to check if it exists or not. If a null object is returned, an error return code is set and the function returns.'''
	try:
	
		cursor = connection()
		# As the event name is unique in the database, only one valid event object for an entered name may be returned.
		# avoid directly appending user input to query to avoid injection problems
		SQL_verify_event = "SELECT * FROM test.events WHERE name = (%s);"
		cursor.execute(SQL_verify_event, event_name)
		event = cursor.fetchone()
		if event is None:
			return -1
		else:
			return 
		
	except MySQLdb.Error as e:
		print(e)
	# close database connection object
	finally:
		cursor.close()

def validate_product_name(product_name):
	'''run query against entered product name to check if it exists or not. If a null object is returned, an error return code is set and the function returns.'''
	try:
		cursor = connection()
		#As the product name is unique in the database as well, only one valid product object for an entered name may be returned.
		SQL_verify_product = "SELECT * FROM test.products WHERE name = (%s);"
		cursor.execute(SQL_verify_product, product_name)
		product = cursor.fetchone()
		if product is None:
			return -1
		else:
			return
		
	except MySQLdb.Error as e:
		print(e)

	finally:
		cursor.close()

def validate_quantity_amount(product_name, input_quantity):	
	'''check the entered quantity against the amount available as recorded in the database'''
	try:
		cursor = connection()
		SQL_quantity = "SELECT * FROM test.products WHERE name = (%s);"
		cursor.execute(SQL_quantity, product_name)
		product_row = cursor.fetchone()
		quantity = product_row[2]

		# if the entered amount required is more than that present in the database, inform the 	user of the amount of stock available, and accordingly ask user to enter a lesser or equal value
		if input_quantity > quantity:
			return quantity;
			
		else:
			return 

	except MySQLdb.Error as e:
		print(e)

	finally:
		cursor.close()


def validate_quantity_symbol(input_quantity):
	'''Validate sign on input quantity'''
	if input_quantity < 0:
		return -1
	else:
		return

def readInput():
	'''This function reads the entered input and calls other methods for input data validation and processing'''

	# an input dictionary to hold product name(key)-quantity(value) pairs. If the same product name is entered twice, only the first is considered.
	input_dict = {}
	# a list which will hold the prices of the products according to their quantities
	price_list = []

	event_name = raw_input("Event name: ")
	# call validate_event_name method to check if entered event name exists in database. If not, an error string is printed, and continues until a valid name is entered.
	retval_event = validate_event_name(event_name)

	# keep prompting user to enter valid event name until the user does so
	while retval_event == -1:
		print "Please enter a valid event!"
		event_name = raw_input("Event name: ")
		retval_event = validate_event_name(event_name)

	# run an infinite loop which runs as long the user enters valid combinations of products and their quantities
	while(True):
			
		product_name = raw_input("Product name: ")
		# call validate_product_name method to check if entered product name exists in database. If not, an error string is printed, and continues until a valid name is entered.
		retval_product = validate_product_name(product_name)
		while retval_product == -1:
			print "Please enter a valid product!"
			product_name = raw_input("Product name: ")
			retval_product = validate_product_name(product_name)

			
		try:
			# the integer form of the input quantity is taken, so if the user enters 2.6, the input quantity will be 2
			input_quantity = int(input("Quantity (number): "))

			# Verify that the quantity is not negative. If so, ask the user to enter a positive value.
			retval_quantity_sign = validate_quantity_symbol(input_quantity)
			while retval_quantity_sign == -1:
				print "Quantity cannot be negative!"
				input_quantity = int(input("Quantity (number): "))
				retval_quantity_sign = validate_quantity_symbol(input_quantity)
				
			retval_quantity = validate_quantity_amount(product_name, input_quantity)
			while retval_quantity is not None:
				print "Quantity is too large! The total number of this product available currently is %s. Please enter a smaller amount." % retval_quantity
				input_quantity = int(input("Quantity (number): "))
				retval_quantity = validate_quantity_amount(product_name, input_quantity)
				
				
		# number conversion error (e.g. alphabets entered)
		except NameError as e:
			print "Please enter a number for quantity!"	
			raise e

		# the inputs being valid, add them to the dictionary
		input_dict[product_name] = input_quantity
		prompt = raw_input("Do you want to continue? y/N: ")
		if prompt == 'N':
			break

	# price_list will have the prices for each set of products ordered after the loop completes
	for product_name in input_dict:
		price_list.append(runquery(product_name, input_dict[product_name]))

	calculate_total_service_fee(price_list)



		

def calculate_total_service_fee(price_list):
	'''this function will calculate the total price of all ordered items'''
	price = 0
	# the list items are in string format, so they have to converted to number and the currency symbol removed to perform the addition
	for i in price_list:
		price += Decimal(sub(r'[^\d.]', '', i))

	''' at this point, price holds the numerical total cost, but not the currency. Assuming the prices have the same currency (this may not be always right, but for simplicity's sake), the currency symbol of the last item is 		extracted by regex '''
	pattern =  r'(\D*)\d*\.?\d*(\D*)'
	g = re.match(pattern,i).groups()

	# a price may be $200 or 200USD. extract whichever one is present		
	currency = g[0] if g[0] != '' else g[1]
	
	# finally convert price to string and concatenate with the extracted currency symbol to display to user
	total_price_with_currency = currency + str(price)
	print "Your total price is " + total_price_with_currency
	return total_price_with_currency

	


def runquery(product_name, input_quantity):
	'''run all queries from this function'''
	try:

		cursor = connection()

		# Query the database for a product with the entered product name
		SQL_product = "SELECT * FROM test.products WHERE name = (%s);"
		cursor.execute(SQL_product, product_name)	
		product_row = cursor.fetchone()
		event_id = product_row[3]
		product_service_fee_amount = product_row[4]
		product_service_fee_currency = product_row[5]

	
		# if the product service fee is 0, apply the event service fee to the product cost		
		if product_service_fee_amount == 0:
			SQL_event = "SELECT * FROM test.events WHERE event_id = (%s);"
			cursor.execute(SQL_event, event_id)
			event_row = cursor.fetchone()
			event_service_fee_amount = event_row[2]
			event_service_fee_currency = event_row[3]
			# call method to calculate service fee
			price_one_product = calculate_service_fee_one_product(input_quantity,event_service_fee_amount,event_service_fee_currency)
		
		else:	
			# call method to calculate service fee
			price_one_product = calculate_service_fee_one_product(input_quantity,product_service_fee_amount,product_service_fee_currency)

		
		return price_one_product

	except MySQLdb.Error as e:
		print(e)

	finally:
		cursor.close()


def calculate_service_fee_one_product(input_quantity, service_fee_amount, currency):
	'''for each set of products, this function is called to calculate fee'''
	# at this stage price is an integer
	price = input_quantity * service_fee_amount
	# the price will be displayed to the user as a currency value, so the currency value from the database will be appended to the string version of the price
	price_with_currency = currency + str(price)
	return price_with_currency

if __name__ == '__main__':		
	readInput()
