"""The intention of this module is to give an easy way to read datasets into DataFrame."""

import pandas as pd
import operator


def get_column(data, column):
	"""
	Get only one column from the DataFrame.
		
	Args:
		- data: Any kind of dictionary/DataFrame.
		- column: A column index.
	Returns:
		A dictionary/DataFrame containing only the index column.
		Or None. 

	Usage:  
		print (get_column(data, 'existent_column').shape) # should return: (n,). 
		print (get_column(data, 'non_existen_column')) # should return: None.
	"""
	try:
		data = data[column]
	except:
		return None 
	return data 

def get_columns(data, columns=None):
	"""
	Get all the wanted columns.

	Args:
		- data: A DataFrame.
		- columns: An array of indexes.
	Returns:
		A DataFrame containing the selected columns.
		Or None.
	
	Usage:
		print (get_columns(data, ['existing_column1', 'existing_column2']).shape) # should return: (n, 2).
		print (get_columns(data, ['non_existing_column1', 'non_existing_column2']) # should return: None.
	"""
	try:
		data = data[columns]
	except:
		return None
	return data
def subsect(data, column, value, relation='=='):
	"""
		Get all the rows where the value of the column is equal to the value.

		Args:
			- data: A DataFrame.
			- column: A index.
			- value: value to compare
			- relation:
				The operator to be used:
					- '>' Greater than value.
					- '<' Value greater than column value.
					- '>=' and '<=' Are for greater or equal than.
					- '==' Equals.
		Returns: 
			A DataFrame containing the rows, where: 'column' [relation] 'value' is true.
			Or None.
		Usage:
			print (subsect_column(data, 'column1', 'column2').shape)
			print (subsect_column(data, 'numeric_column', 'numeric_column', relation='<'))
	"""
	ops = {	'>': operator.gt,
           	'<': operator.lt,
           	'>=': operator.ge,
           	'<=': operator.le,
           	'==': operator.eq}
	try:
		data = data[ops[relation](data[column], value)]
	except:
		return None 
	return data 
