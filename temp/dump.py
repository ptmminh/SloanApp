#dump page for discarding outdated code

#opt1 = labs[0], opt2 = labs[1], opt3 = labs[2],\
		#opt4 = labs[3], opt5 = labs[4], opt6 = labs[5], opt7 = labs[6], opt8 = labs[7], opt9 = labs[8],\
		#opt10 = labs[9], opt11 = labs[10], opt12 = labs[11], opt13 = labs[12]

#for accessing checked options
#https://coderwall.com/p/pkthoa/read-checkbox-in-flask --> this seems helpful

py function callback:

'''def callback(source = bar_source, s2 = table_source, p = p):
	br_data = source.get('data')
	tbl_data = s2.get('data')
	f = cb_obj.get('value') #selected id
	#print(f)
	#for x in db.job.find({"_id": ObjectId(f)}):
		#doc = x
	br_data['SampleSize'] = tbl_data['Sample'][tbl_data['_id'].index(f)]#[int(doc[lab]) for lab in col_lab]
	#print(bar_data)
	#bar_data['SampleSize'] = [int(doc[lab]) for lab in col_lab]
	#p.title = doc['Question Text - First Wave Available']
	p.trigger('change')
	source.trigger('change')'''