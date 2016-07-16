##########################
# Name : Minh Pham
# Email: minh.pham@columbia.edu
# File contains main flask framework for Sloan web app
##########################

from flask import Flask, render_template, request, redirect
import db
import second


app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def index():
	'''function to display the index page with checkboxes'''
	if request.method == 'GET':	
		labs = db.get_labels()
		return render_template('checkbox_page.html',\
			labs_jobs = labs['job'],\
			labs_vol = labs['vol'], \
			labs_lei = labs['lei'],\
			labs_demo = labs['demo'],\
			labs_hlth = labs['hlth'],\
			labs_psysoc = labs['psysoc'],\
			labs_cogn = labs['cogn'])
		
	else:
		global x
		x = store_input()
		return redirect('/table_results')


@app.route('/table_results', methods = ['GET', 'POST'])
def table_results():
	'''function to return results bokeh web app'''
	try: 
		page = second.build_app(db.obtain_results(x))
		return render_template('app.html', snippet=page)
	except:
		return "Sorry, somehow you have managed to break my script.\
		 If you have selected Interview Information for Leisure and Volunteering, \
		they cannot be displayed. Try something else!"


def store_input():
	'''storing user input on index page
	function returns nothing'''
	selected = []
	labs = ['job_gray','lei_gray','vol_gray','demo_gray',\
	'hlth_gray','psysoc_gray','cogn_gray','search_lulu']
	for lab in labs:
		if lab != 'search_lulu':
			selected.append(request.form.getlist(lab))
		else:
			selected.append(request.form[lab])
	return selected


if __name__ == "__main__":
	app.run(debug=True) 