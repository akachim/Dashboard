from flask import Flask, render_template, redirect, flash, session, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm, form
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_modals import Modal
from flask_modals import render_template_modal

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
	modal = 'load-modal'
	if form.validate_on_submit():
		flash('You have logged in successfully!', 'success')
	return render_template_modal('index.html', form=form, modal=modal)