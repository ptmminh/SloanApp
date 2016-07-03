from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bokeh.charts import Bar
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.io import vform 

sloan_app = Flask(__name__)

sloan_app.selected = {}

#create a db connection
client = MongoClient()

#initialize a database
db = client['sloandb']

@sloan_app.route('/sloan_app',methods=['GET','POST'])
def index():
	'''function to display the index page with checkboxes'''
	if request.method == 'GET':
		cursor = db.job.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])
		##iterate to create labels
		labs = []
		for doc in cursor:
			labs.append(doc['_id'])

		return render_template('checkbox_page.html', labs = labs)
		
	else:
		sloan_app.selected['Job'] = request.form.getlist('gray')
		return redirect('/table_results')

@sloan_app.route('/table_results', methods = ['GET', 'POST'])
def table_results():
	'''function to return tables'''
	
	#create bokeh data table
	table_cursor= db.job.find({"Database Section" : { "$in": sloan_app.selected['Job']}})
	l_q = []
	l_g = []
	l_n = []
	for doc in table_cursor:
		l_q.append(doc['Question Text - First Wave Available'])
		l_g.append(doc['Database Section'])
		l_n.append(doc['General Notes'])
	table_data = dict(question = l_q, gray = l_g, notes = l_n)
	table_source = ColumnDataSource(table_data)

	columns = [TableColumn(field = 'question', title = "Question Text"), \
	TableColumn(field = 'gray', title = 'Gray Section'),\
	TableColumn(field = 'notes', title = 'General Notes')]


	data_table = DataTable(source=table_source, columns=columns, selectable = True)
	#width=1500, height = Auto
	#selectable can also be set to 'checkbox' for multiple selection


	html = file_html(vform(data_table, CDN, "data_table")

	return html




if __name__ == "__main__":
	sloan_app.run(debug=True) 