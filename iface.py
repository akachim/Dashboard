import os
from flask import Flask, render_template, redirect, flash, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.datastructures import FileStorage
from wtforms import SubmitField, SelectField
from flask_modals import Modal
from flask_modals import render_template_modal
from werkzeug.utils import secure_filename

#-----Data analysis modules
import joblib
import pandas as pd
import numpy as np
from wtforms.validators import DataRequired


#---------configurations--------------

app = Flask(__name__)
app.config["SECRET_KEY"]="oh well i hope it works this time"
#app.config["MAX_CONTENT_LENGTH"]=1024*1024

#-------------initializations-----------------------
bootstrap=Bootstrap(app)
modal=Modal(app)

#--------------forms---------------------------
class FileForm(FlaskForm):
    data=FileField(validators=[
		FileRequired(),
		FileAllowed(['csv', 'xls','xlsx'],'File must be a csv or excel')
		])
    model=SelectField(label="Choose Model",
                        choices=[
                            ('bnb','Bernoulli Classifier'),
                            ('clf','Support Vector Classifier'),
                            ('dtc', 'Decision Tree'),
                            ('lgr', 'Logistic Regression'),
                            ('knn', 'K Nearest Neighbour'),
                            ('lr','Linear Regression')
                            ], 
                            validators=[DataRequired()])
    submit=SubmitField("Submit")


@app.route('/', methods=['GET','POST'])
def index():
    
    form=FileForm()
    models=['bnb','clf','dtc','knn','lgr','lr']
    if request.method=="POST":
        
        if form.validate_on_submit():
            mod=form.model.data
            if mod=='bnb':
                mod="Bernoulli Classifier"
                model=joblib.load('model_BNB.pkl')

            elif mod=='clf':
                mod='Support Vector Classifier'
                model=joblib.load('model_clf.pkl')

            elif mod=='dtc':
                mod='Decision Tree'
                model=joblib.load('model_DTC.pkl')

            elif mod=='knn':
                mod='K Nearest Neighbour'
                model=joblib.load('model_knn.pkl')

            elif mod=='lgr':
                mod='Logistic Regression'
                model=joblib.load('model_LGR.pkl')

            elif mod=='lr':
                mod='Linear Regression'
                model=joblib.load('model_LR2.pkl')

            else:
                flash('Model does not exist', 'error')
                return redirect(url_for('index'))
                        
            f = request.files['data']

            filename = secure_filename(f.filename)
                    
            file_ext=os.path.splitext(filename)[1] #getting the file extension
            if file_ext in ['xlx','xlsx', 'xls']:
                    df = pd.read_excel(filename)
            else:
                
                df = pd.read_csv(filename)

            test_data=df
            y_predicted=model.predict(test_data) #assesing the first value of returned vals in DataTransform function

            y_pred=np.array(y_predicted)
            prediction = pd.DataFrame(y_pred, columns=["Prediction"])

            global new_dataframe
            new_dataframe = pd.concat([prediction, test_data], axis=1)
            table=new_dataframe.head(10)
            html = table.to_html(classes='mystyle')
            # write html to file
            text_file = open("templates/table.html", "w",  encoding="utf8")
            text_file.write(html)
            text_file.close()

            
            flash("You selected the {} model".format(mod), 'info')
            
            return render_template_modal('result_table.html',form=form, modal=None)
    
    return render_template_modal('index.html',form=form, modal='modal-form')



@app.route('/predict', methods=["GET", "POST"])
def predict():
    try:
        table=new_dataframe.head(20)
        html = table.to_html(classes='mystyle')
        # write html to file
        text_file = open("templates/table.html", "w")
        text_file.write(html)
        text_file.close()
    except:
        flash("You have to make a Prediction First",'danger')
        return redirect(url_for('index'))
    
    return render_template('result_table.html')

@app.route('/download', methods=["GET","POST"])
def download():
    try:
        new_dataframe.to_csv("Results.csv")
        flash("File saved successfully", 'info')
        return redirect(url_for('index'))

    except:
        flash("File could not be saved or you have not made a prediction yet, try Again", 'warning')
    return redirect(url_for('index'))
