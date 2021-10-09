from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
bootstrap=Bootstrap(app)

class FileForm(FlaskForm):
	data=FileField("uplaod csv", validators=[DataRequired()])
	submit=SubmitField("upload")

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')


@app.route('/import', methods=['GET','POST'])
def load():
	form=FileForm()
	return render_template('import.html', form=form)
