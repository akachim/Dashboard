from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

#---------configurations--------------

app = Flask(__name__)
app.config["SECRET_KEY"]="oh well i hope it works this time"
BOOTSTRAP_SERVE_LOCAL=True
#-------------initializations-----------------------
bootstrap=Bootstrap(app)

#--------------forms---------------------------
class FileForm(FlaskForm):
	data=FileField("uplaod csv", validators=[DataRequired()])
	submit=SubmitField("upload")


#---------views/routes---------------------

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')


@app.route('/load', methods=['GET','POST'])
def load():
	form=FileForm()
	return render_template('load.html', form=form)
