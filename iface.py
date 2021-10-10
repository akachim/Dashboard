from flask import Flask, render_template, redirect, flash, session, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm, form
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_modals import Modal
from flask_modals import render_template_modal
#import csv
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
	data=FileField(validators=[DataRequired()])
	submit=SubmitField("Submit")


#---------views/routes---------------------

@app.route('/', methods=['GET','POST'])
def index():
	form = FileForm()
	if request.method=="POST":
		if form.validate_on_submit():
			f = request.files['data']
			#store the file contents as a string
			#fstring = f.read()
			#create list of dictionaries keyed by header row
			#csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
			df = pd.read_csv(f)
			fig = px.line(df, x="fruits", y="amount", title="Fruits vs amount")
			graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			
			return render_template('index.html', form=form, graphJSON=graphJSON, modal=None)

	return render_template_modal('index.html', form=form, modal='modal-form')