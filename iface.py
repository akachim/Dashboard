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
from sklearn import svm
from sklearn.svm import SVC 
from sklearn.naive_bayes import BernoulliNB 
from sklearn import tree
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

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
		FileAllowed(['csv', 'xls','xlsx', 'xlx,'],'File must be a csv or excel')
		])
    model=SelectField(label="Choose Model",
                        choices=[
                            ('bnb','Bernoulli Classifier'),
                            ('clf','Support Vector Classifier'),
                            ('dtc', 'Decision Tree'),
                            ('lgr', 'Logistic Regression'),
                            ('knn', 'K Nearest Neighbour'),
                            ], 
                            validators=[DataRequired()])
    submit=SubmitField("Submit")



def OutcomeClass(y_predicted):
    """
    A function that takes the predicted value and returns the predicted categorical value
    1: YES, 0: NO, storing it as dataframe column.
    """
    out_come=[]
    
    for i in y_predicted:
        if i==0:
            outcome= "NO"
        elif i==1:
            outcome="YES"
            
        out_come.append(outcome)
        
    out_come=pd.DataFrame(out_come, columns=["Outcome"])
    
    return out_come


def LgaDecode(df):
    decode=[]
    vals=df["lgas"]
    dictionary={
        'Omuma': 18, 
        'Eleme': 8, 
        'Asari Toru ': 5, 
        'Ahoada West': 2, 
        'Okrika': 17, 
        'Gokana': 11, 
        'Opobo Nkoro': 19, 
        'Obio  Akpor': 15, 
        'Bonny': 6, 
        'Ogu Bob': 16, 
        'Etche ': 10, 
        'Oyigbo': 20, 
        'Ahoada East': 1, 
        'Akuku Toru': 3, 
        'Tai': 22, 
        'Khana': 13, 
        'ONELGA': 14, 
        'Abua Odual': 0, 
        'Port Harcourt': 21, 
        'Andoni  ': 4, 
        'Degema': 7, 
        'Emohua': 9, 
        'Ikwerre': 12
    }
    for val in vals:
        for key, value in dictionary.items():
            if value==val:
                decode.append(key)
    decode=np.array(decode)
    decode=pd.DataFrame(decode, columns=["LGA"])
    return decode






@app.route('/', methods=['GET','POST'])
def index():
    form=FileForm()
    if request.method=="POST":
        
        if form.validate_on_submit():
            mod=form.model.data
            global model
            if mod=='bnb':
                mod="Bernoulli Classifier"
                model=joblib.load('models/BNB.pkl')

            elif mod=='clf':
                mod='Support Vector Classifier'
                model=joblib.load('models/SVM.pkl')

            elif mod=='dtc':
                mod='Decision Tree'
                model=joblib.load('models/DTC.pkl')

            elif mod=='knn':
                mod='K Nearest Neighbour'
                model=joblib.load('models/KNN.pkl')

            elif mod=='lgr':
                mod='Logistic Regression'
                model=joblib.load('models/LGR.pkl')

            else:
                flash('Model does not exist', 'error')
                return redirect(url_for('index'))
                        
            f = request.files['data']

            filename = secure_filename(f.filename)
                    
            file_ext=os.path.splitext(filename)[1] #getting the file extension
            print(file_ext)
            extension=['.xlx','.xlsx', '.xls']

            global df
            if file_ext == '.xlx' or file_ext=='.xlsx' or file_ext =='.xls':
                df = pd.read_excel(filename)
            elif file_ext=='.csv':
                df = pd.read_csv(filename)
            else:
                flash('Something went wrong, \n Make sure file is saved in one of the following formats(.xlx, .xlsx, .xls or .csv)', 'danger')
                return redirect(url_for('index'))



            y_predicted=model.predict(df)

            #y_predicted=np.array(y_pred)

            prediction = OutcomeClass(y_predicted)

            global new_dataframe
            new_dataframe = pd.concat([prediction, LgaDecode(df)], axis=1)

            #table=new_dataframe.head(10)
            html = new_dataframe.to_html(classes='mystyle')
            # write html to file
            text_file = open("templates/table.html", "w",  encoding="utf8")
            text_file.write(html)
            text_file.close()

            
            flash("You selected the {} model".format(mod), 'info')
            
            return render_template_modal('result_table.html',form=form, modal=None)
    
    return render_template_modal('index.html',form=form, modal='modal-form')



@app.route('/reports', methods=["GET", "POST"])
def reports():
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



@app.route('/detail' ,methods=['GET', 'POST'])
def detail():
    #------------accuracy test and CONFUSION MATRIX PLOT---------
    X_test=df
    y_test=pd.read_csv('outcome_test.csv')
    accuracy = metrics.accuracy_score(y_test, model.predict(X_test))
    accuracy= round(accuracy *100, 2)
    confusion_matrix = metrics.confusion_matrix(y_test, model.predict(X_test))
    lm= confusion_matrix.tolist()

    return render_template("result_js.html", lm=lm, accuracy=accuracy) 