import os
from flask import Flask, render_template, redirect, flash, session, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from flask_modals import Modal
from flask_modals import render_template_modal
from werkzeug.utils import secure_filename
#import csv
import pandas as pd
import json
import plotly
import plotly.express as px

#---------configurations--------------

app = Flask(__name__)
app.config["SECRET_KEY"]="oh well i hope it works this time"
app.config["MAX_CONTENT_LENGTH"]=1024*1024

#app.config["UPLOAD_EXTENSIONS"]=['.csv', '.xlx', '.xls']

#-------------initializations-----------------------
bootstrap=Bootstrap(app)
modal=Modal(app)

#--------------forms---------------------------
class FileForm(FlaskForm):
	data=FileField(validators=[
		FileRequired(),
		FileAllowed(['csv', 'xls','xlsx'],'File must be a csv or excel')
		])
	submit=SubmitField("Submit")


#---------views/routes---------------------

@app.route('/', methods=['GET','POST'])
def index():
	form = FileForm()
	if request.method=="POST":
		if form.validate_on_submit():
			f = request.files['data']
			filename = secure_filename(f.filename)
			file_ext=os.path.splitext(filename)[1] #getting the file extension
			if file_ext in ['xlx','xlsx', 'xls']:
				df = pd.read_excel(filename)
			else:
				#store the file contents as a string
				#create list of dictionaries keyed by header row
				#csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(filename.splitlines(), skipinitialspace=True)]
				df = pd.read_csv(filename)
			#plotting with plottly
			print(df)
			fig = px.bar(df, x="Days", y="Patients", color="Days", title="DAYS VS NUMBER OF PATIENTS", barmode="relative")
			graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			return render_template('result.html', form=form, graphJSON=graphJSON, modal=None)

	return render_template_modal('index.html', form=form, modal='modal-form')



@app.errorhandler(413)
def too_large(e):
	return 'File too large', 413