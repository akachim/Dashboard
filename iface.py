from flask import Flask, render_template, redirect, flash, session, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm, form
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_modals import Modal
from flask_modals import render_template_modal
import csv
import pandas as pd
import json
import plotly
import plotly.express as px

#---------configurations--------------

app = Flask(__name__)
app.config["SECRET_KEY"]="oh well i hope it works this time"

#-------------initializations-----------------------
bootstrap=Bootstrap(app)
modal=Modal(app)

BOOTSTRAP_SERVE_LOCAL=True
#--------------forms---------------------------
class FileForm(FlaskForm):
	data=FileField("uplaod csv", validators=[DataRequired()])
	submit=SubmitField("Submit")


#---------views/routes---------------------

@app.route('/', methods=['GET','POST'])
def index():
	form = FileForm()
	if form.validate_on_submit():
		flash('You have logged in successfully!', 'success')
		redirect(url_for('predict'))
	return render_template_modal('index.html', form=form, modal='modal-form')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
	if request.method == 'POST':
		# Create variable for uploaded file
		f = request.files['fileupload']
		#store the file contents as a string
		fstring = f.read()
		#create list of dictionaries keyed by header row
		csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
	df = pd.DataFrame({
		"Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
		"Amount": [4, 1, 2, 2, 4, 5],
		"City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]})
	fig = px.bar(df, x="Fruit", y="Amount", color="City",    barmode="group")
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	
	return render_template("results.html", graphJSON=graphJSON)