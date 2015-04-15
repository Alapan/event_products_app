import unittest
import event_products_app

class TestQueryParams(unittest.TestCase):

	# check for proper handling of invalid event name	
	def test_validate_eventname(self):
		self.assertEqual(event_products_app.validate_event_name('abc'),-1)

	# check for proper handling of invalid product name
	def test_validate_productname(self):
		self.assertEqual(event_products_app.validate_product_name('fsdfs'),-1)

	# check for proper handling of negative quantity
	def test_negative_quantity(self):
		self.assertEqual(event_products_app.validate_quantity_symbol(-1),-1)

	# check for proper handling of quantity larger than actually present
	def test_validate_quantity(self):
		self.assertEqual(event_products_app.validate_quantity_amount('mikes', 40),25)

	# check for service fee value for one product with correct input		
	def test_servicefee(self):
		self.assertEqual(event_products_app.calculate_service_fee_one_product(10,20,'$'),'$200')




if __name__ == '__main__':
	unittest.main()


		

