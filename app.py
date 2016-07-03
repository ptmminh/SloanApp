from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bokeh.charts import Bar
from bokeh.models import ColumnDataSource, CustomJS, Select
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.io import vform, hplot 
from bokeh.plotting import Figure
from bokeh.models.widgets import Panel, Tabs

app = Flask(__name__)

app.selected = {}

#create a db connection
client = MongoClient()

#initialize a database
db = client['sloandb']

@app.route('/',methods=['GET','POST'])
def index():
	'''function to display the index page with checkboxes'''
	if request.method == 'GET':	
		labs = get_labels()
		#print(labs)
		return render_template('checkbox_page.html', labs_jobs = labs['job'],\
			labs_vol = labs['vol'], \
			labs_lei = labs['lei'],\
			labs_demo = labs['demo'],\
			labs_hlth = labs['hlth'],\
			labs_psysoc = labs['psysoc'])
		
	else:
		app.selected['job'] = request.form.getlist('job_gray')
		app.selected['lei'] = request.form.getlist('lei_gray')
		app.selected['vol'] = request.form.getlist('vol_gray')
		app.selected['demo'] = request.form.getlist('demo_gray')
		app.selected['hlth'] = request.form.getlist('hlth_gray')
		app.selected['psysoc'] = request.form.getlist('psysoc_gray')
		return redirect('/table_results')

def get_labels():
	'''getting labels for index page'''
	#getting checkbox selection
	job_cursor = db.job.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])
	lei_cursor = db.leisure.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])
	vol_cursor = db.volunteering.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])
	demo_cursor = db.demographics.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])
	hlth_cursor = db.health.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])
	psysoc_cursor = db.psychosocial.aggregate([{"$group": {"_id": "$Database Section", "count": {"$sum": 1}}}])

	##iterate to create labels
	labs = {}
	cursors = [job_cursor,lei_cursor,vol_cursor,demo_cursor,hlth_cursor,psysoc_cursor]
	cursor_str = ['job','lei','vol','demo','hlth','psysoc']
	for i,j in zip(cursors, cursor_str):
		x = []
		for doc in i:
			x.append(doc['_id'])
		labs[j] = x

	return labs



@app.route('/table_results', methods = ['GET', 'POST'])
def table_results():
	'''function to return tables'''
	plot_snippet = build_app()
	return render_template('app.html', snippet=plot_snippet)



def build_app():
	'''function to build 2nd page Bokeh app with interactions'''

	#create a list of years for sample size years
	years = [str(i) for i in range(1992,2015,2)]
	years.insert(1,str(1993)) #the odd duck
	years.insert(3,str(1995)) #the odd duck
	col_lab_sam = ['Sample Size - ' + i for i in years] #sample column labels
	col_lab_var = ['Variable Name - ' + i for i in years] #variable column labels
	col_lab_qtxt = ['Question Text - ' + i for i in years] #question text column labels
	col_lab_res = ['Response Options - ' + i for i in years] #response options column labels
	
	#create bokeh data table 1&2
	table_cursor= db.job.find({"Database Section" : { "$in": app.selected['job']}})
	l_id = []
	l_q = []
	l_g = []
	l_n = []
	l_sample = []
	l_var = []
	l_qtext = []
	l_res = []
	l_cac = []
	for doc in table_cursor:
		l_id.append(str(doc['_id']))
		l_q.append(doc['Question Text - First Wave Available'])
		l_g.append(doc['Database Section'])
		l_n.append(doc['General Notes'])
		#print([doc[lab] for lab in col_lab])
		l_sample.append([int(doc[lab]) if doc[lab] is not '' else 0 for lab in col_lab_sam])
		l_var.append([doc[lab] for lab in col_lab_var])
		l_qtext.append([doc[lab] for lab in col_lab_qtxt])
		l_res.append([doc[lab] for lab in col_lab_res])
		l_cac.append(doc['CAC Label'])
	#print(l_sample)
	table_data = dict(_id = l_id, question = l_q, gray = l_g, notes = l_n, \
		Sample = l_sample, var = l_var, qtext = l_qtext, res = l_res, cac = l_cac)
	table_source = ColumnDataSource(table_data)

	columns = [TableColumn(field = '_id', title = "ID"),\
	TableColumn(field = 'cac', title = 'CAC Label'),\
	TableColumn(field = 'gray', title = 'Sections'),\
	TableColumn(field = 'question', title = "Question Text"),\
	TableColumn(field = 'notes', title = "Notes")]


	data_table = DataTable(source=table_source, columns=columns, selectable = True, fit_columns = True)

	#create table data 2 (only display after callback)
	table_data_2 = dict(years = years, var = ['na']*len(years), qtext = ['na']*len(years), res = ['na']*len(years))
	table_source_2 = ColumnDataSource(table_data_2)
	columns_2 = [TableColumn(field = 'years', title = 'Wave'),\
	TableColumn(field = 'var', title = 'Variable Name'),\
	TableColumn(field = 'qtext', title = 'Question Text'),\
	TableColumn(field = 'res', title = 'Response Options')]

	data_table_2 = DataTable(source=table_source_2, columns=columns_2, selectable = True, fit_columns = True)

	#create data for bar graph	
	bar_data = dict(Years= years, SampleSize = [0]*len(years)) #placeholding zeros  
	bar_source = ColumnDataSource(data = bar_data) #for callback later
	
	#draw bar graph
	#p = Bar(bar_source.to_df(), 'Years', values = 'SampleSize', title = 'Whatever here',width = 800)
	#doc['Question Text - First Wave Available'],\
	
	#draw line and circle graph
	p2 = Figure(plot_width=500, plot_height=500,title='Selected - Sample by Wave')
	p2.circle('Years', 'SampleSize', source=bar_source, size=10, color="CadetBlue", alpha=0.5)
	tab2 = Panel(child=p2, title="circle")
	p2.title_text_color = "CadetBlue"
	p2.title_text_font = "helvetica"
	p2.xaxis.axis_label = "Wave"
	p2.xaxis.axis_label_text_font_size = '9pt'
	p2.yaxis.axis_label = "Sample Size"
	p2.yaxis.axis_label_text_font_size = '9pt'

	p1 = Figure(plot_width=500, plot_height=500, title='Selected - Sample by Wave')
	p1.line('Years', 'SampleSize', source=bar_source, line_width=3, color='CadetBlue',line_alpha=0.7)
	tab1 = Panel(child=p1, title="line")
	p1.title_text_color = "CadetBlue"
	p1.title_text_font = "helvetica"
	p1.xaxis.axis_label = "Wave"
	p1.xaxis.axis_label_text_font_size = '9pt'
	p1.yaxis.axis_label = "Sample Size"
	p1.yaxis.axis_label_text_font_size = '9pt'

	tabs = Tabs(tabs=[ tab1, tab2 ])


	#requires (bar_source, table_source, p1, p2, table_source_2)
	callback_code = """
	var br_data = source.get('data');
	var tbl_data = s2.get('data');
	var tbl2_data = s3.get('data');
	var f = cb_obj.get('value');
	var i = tbl_data['_id'].indexOf(f);
	var sam = tbl_data['Sample'][i];
	br_data['SampleSize'] = sam;
	var var_i = tbl_data['var'][i];
	tbl2_data['var'] = var_i;
	var qtext = tbl_data['qtext'][i];
	tbl2_data['qtext'] = qtext;
	var res = tbl_data['res'][i];
	tbl2_data['res'] = res;
	p1.trigger('change');
	p2.trigger('change');
	source.trigger('change');
	dt2.trigger('change');
	s3.trigger('change')"""

	#Select ID
	id_select = Select(title='Select an ID from the table above',value='select',options=['None']+l_id, \
		callback = CustomJS(args=dict(source=bar_source, s2=table_source, p1=p1, p2=p2, s3 = table_source_2, dt2 = data_table_2), code=callback_code))
	#id_select.callback = CustomJS.from_py_func(callback)

	#data_table = DataTable(source=table_source, columns=columns, selectable = True)
	#, callback = CustomJS.from_py_func(callback))

	html = file_html(vform(data_table,id_select,hplot(tabs,data_table_2)), CDN, "data_table")

	return html


if __name__ == "__main__":
	app.run(debug=True) 