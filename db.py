##########################
# Name : Minh Pham
# Email: minh.pham@columbia.edu
# Module contains database connection 
# and querying user input 
# the main Sloan app framework 
##########################

from itertools import chain
from pymongo import MongoClient, TEXT


#create a db connection
client = MongoClient()

#initialize a database
db = client['sloandb']

#all collections
collections = [db.job, db.leisure, db.volunteering, db.demographics,\
db.health, db.psychosocial, db.cognitive]

def get_labels():
	'''getting labels for index page'''

	#getting checkbox selection
	cursors = []
	for col in collections:
		cursors.append(col.aggregate([{"$group":\
			{"_id": "$Database Section", "count": {"$sum": 1}}}]))

	##iterate to create labels
	labs = {}
	cursor_str = ['job','lei','vol','demo','hlth','psysoc','cogn']
	for i,j in zip(cursors, cursor_str):
		x = []
		for doc in i:
			x.append(doc['_id'])
		labs[j] = x

	return labs



def search(term):
	'''function to receive text search input and retuns 
	a results iterable (not quite a MongoDB cursor) but 
	should be fit for purpose'''

	#create text indices
	#search fields: CAC Label + Initial question text
	for col in collections:
		col.create_index([('CAC Label', TEXT),\
			('Question Text - First Wave Available', TEXT)],\
			name= 'text_search')

	#search for input
	results = []
	for col in collections:
		r = col.find({"$text": {"$search": term}})
		if r.count() > 0:
			results.append(r)
	data = [x for x in chain(*results)]

	#drop text indices
	for col in collections:
		col.drop_index('text_search')

	return data


def obtain_results(selected):
	'''function to gather selected checkboxes or text input'''
	
	output = []
	
	term = selected.pop()
	for col,i in zip(collections, selected):
		output.append(col.find({"Database Section" : { "$in": i}}))

	if len(term) > 0:
		output.append(search(term))

	return output
