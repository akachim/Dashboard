from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap 

app = Flask(__name__)
bootstrap=Bootstrap(app)


@app.route('/', methods=['GET','POST'])
def index():
	return render_template('base.html')
