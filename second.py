##########################
# Name : Minh Pham
# Email: minh.pham@columbia.edu
# Module contains bokeh visualization 
# and interactions to support 2nd page 
# of the main Sloan app framework 
##########################

from bokeh.models import ColumnDataSource, CustomJS, Select, HoverTool
from bokeh.models.widgets import DataTable, TableColumn, Panel, Tabs
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.io import vform, hplot 
from bokeh.plotting import Figure

def build_app(list_cursor):
	'''function to build 2nd page Bokeh app with interactions'''

	#create a list of years for sample size years
	years = [str(i) for i in range(1992,2015,2)]
	years.insert(1,str(1993)); years.insert(3,str(1995)) #the odd ducks
	col_lab_sam = ['Sample Size - ' + i for i in years] #sample column labels
	col_lab_var = ['Variable Name - ' + i for i in years] #variable column labels
	col_lab_qtxt = ['Question Text - ' + i for i in years] #question text column labels
	col_lab_res = ['Response Options - ' + i for i in years] #response options column labels

	#to handle CAMS waves
	years_c = [str(i) for i in range(2001,2014,2)]
	col_lab_sam_c = ['Sample Size- ' + i + ' CAMS' for i in years_c]
	col_lab_var_c = ['Variable Name- ' + i + ' CAMS' for i in years_c]
	col_lab_qtxt_c = ['Question Text - ' + i + ' CAMS' for i in years_c]
	col_lab_res_c = ['Response Options - ' + i + ' CAMS' for i in years_c]

	#create results data table

	l_id = []; l_q = []; l_g = []; l_n = []; l_sample = []
	l_var = [];	l_qtext = []; l_res = []; l_cac = []; l_years = []
	i = 1
	
	for table_cursor in list_cursor:
		for doc in table_cursor:
			l_id.append(str(i))
			i += 1
			l_q.append(doc['Question Text - First Wave Available'])
			l_g.append(doc['Database Section'])
			l_n.append(doc['General Notes'])
			l_cac.append(doc['CAC Label'])			
			if doc['Database Section'] != 'CAMS':
				l_sample.append([int(doc[lab]) if doc[lab] is not '' else 0 for lab in col_lab_sam])
				l_var.append([doc[lab] for lab in col_lab_var])
				l_qtext.append([doc[lab] for lab in col_lab_qtxt])
				l_res.append([doc[lab] for lab in col_lab_res])
				l_years.append(years)
			else:
				l_sample.append([int(doc[lab]) if doc[lab] is not '' else 0 for lab in col_lab_sam_c])
				l_var.append([doc[lab] for lab in col_lab_var_c])
				l_qtext.append([doc[lab] for lab in col_lab_qtxt_c])
				l_res.append([doc[lab] for lab in col_lab_res_c])
				l_years.append(years_c)

	table_source = ColumnDataSource(data=dict(_id = l_id, question = l_q, gray = l_g, notes = l_n, \
		Sample = l_sample, var = l_var, qtext = l_qtext, res = l_res, \
		cac = l_cac, years = l_years))

	columns = [TableColumn(field = '_id', title = "ID", width=5),\
	TableColumn(field = 'cac', title = 'CAC Label',width=70),\
	TableColumn(field = 'gray', title = 'Sections',width=80),\
	TableColumn(field = 'question', title = "Question Text",width =150),\
	TableColumn(field = 'notes', title = "Notes",width = 50)]

	data_table = DataTable(source=table_source, columns=columns, selectable = True, fit_columns = True)

	
	#create selected item table data (only display after callback)
	table_source_2 = ColumnDataSource(data=dict(years = years, var = ['na']*len(years),\
		qtext = ['na']*len(years), res = ['na']*len(years)))
	
	columns_2 = [TableColumn(field = 'years', title = 'Wave',width=3),\
	TableColumn(field = 'var', title = 'Variable',width=3),\
	TableColumn(field = 'qtext', title = 'Question Text',width=100),\
	TableColumn(field = 'res', title = 'Response Options',width=100)]

	data_table_2 = DataTable(source=table_source_2, columns=columns_2, selectable = True, fit_columns = True)

	
	#create data for circle/line graphs	(only display after callback)
	bar_data = dict(Years= years, SampleSize = [0]*len(years)) #place-holding zeros  
	bar_source = ColumnDataSource(data = bar_data)
	
	#draw line and circle graphs in two tabs
	hover = HoverTool(tooltips=[("wave","@Years"),\
		("Sample Size", "@SampleSize")])
	p1 = gen_fig('circle', bar_source, tool=hover)	
	tab1 = Panel(child=p1, title="circle")
	p2 = gen_fig('line', bar_source)
	tab2 = Panel(child=p2, title="line")
	tabs = Tabs(tabs=[ tab1, tab2 ])

	#requires (bar_source, table_source, table_source_2)
	callback = """
	var br_data = source.get('data');
	var tbl_data = s2.get('data');
	var tbl2_data = s3.get('data');
	var f = cb_obj.get('value');
	var i = tbl_data['_id'].indexOf(f);
	br_data['SampleSize'] = tbl_data['Sample'][i];
	br_data['Years'] = tbl_data['years'][i];
	tbl2_data['years'] = tbl_data['years'][i];;
	tbl2_data['var'] = tbl_data['var'][i];
	tbl2_data['qtext'] = tbl_data['qtext'][i];
	tbl2_data['res'] = tbl_data['res'][i];
	source.trigger('change');
	s3.trigger('change');
	dt2.trigger('change');"""

	#Select ID
	id_select = Select(title='Select an ID from the table above',\
		value ='select',options=['None']+l_id,\
		callback = CustomJS(\
			args = dict(source=bar_source, s2=table_source, dt2 = data_table_2, s3 = table_source_2),\
			code = callback))

	html = file_html(vform(data_table,id_select,hplot(tabs,data_table_2)), CDN, "data_table")

	return html

def gen_fig(shape, source, tool=''):
	'''function to generate either a circle or line graph'''
	p = Figure(plot_width=500, plot_height=500,\
		title='Selected - Sample by Wave', tools = [tool])
	p.title_text_color = "CadetBlue"
	p.title_text_font = "helvetica"
	p.xaxis.axis_label = "Wave"
	p.xaxis.axis_label_text_font_size = '9pt'
	p.yaxis.axis_label = "Sample Size"
	p.yaxis.axis_label_text_font_size = '9pt'
	if shape == 'circle':
		p.circle('Years', 'SampleSize', source=source,\
			size=10, color="CadetBlue", alpha=0.5)
	elif shape == 'line':
		p.line('Years', 'SampleSize', source=source,\
			line_width=3, color='CadetBlue',line_alpha=0.7)
	return p
