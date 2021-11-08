import os
from flask import Flask, render_template, redirect, flash, session, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from pandas.core.frame import DataFrame
from werkzeug.datastructures import FileStorage
from wtforms import SubmitField
from flask_modals import Modal
from flask_modals import render_template_modal
from werkzeug.utils import secure_filename

#-----Data analysis modules
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
import numpy as np
from wtforms.fields.core import SelectField
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
                            ('esm', 'Essembly Learning'),
                            ('lr', 'Logistic regression')
                            ], 
                            validators=[DataRequired()])
    dataset=SelectField(label="Select data set type", 
                        choices=[
                            ("tr", "Training data"),
                            ("ts","Test data")
                        ],validators=[DataRequired()])

    submit=SubmitField("Submit")



def DataTransform(file):
    """
    A function that performs data tranformation before apllying to prediction model
    it takes test data frame as the only argument
    
    """
    non_numeric = file[["protocol_type","service","flag"]]
    
    label_encoder = LabelEncoder()
    
    non_numeric['protocol_type'] = label_encoder.fit_transform(non_numeric['protocol_type'])
    non_numeric['service'] = label_encoder.fit_transform(non_numeric['service'])
    non_numeric['flag'] = label_encoder.fit_transform(non_numeric['flag'])

    num = file.drop(["protocol_type","service","flag", 'class'], axis=1)
    file['class'] = LabelEncoder().fit_transform(file['class'])
    y_actual = file["class"]
    num[num.columns]= StandardScaler().fit_transform(num[num.columns])

    processed_df = pd.concat([non_numeric, num], axis=1)

    vals=[processed_df, y_actual]

    
    return vals


def NetworkClass(y_predicted):
    """
    A function that takes the predicted value and returns the predicted categorical value
    1: normal, 0: anormaly, storing it as dataframe column.
    """
    network_class=[]
    
    for i in y_predicted:
        if i==0:
            network_class_cat= "anormaly"
        elif i==1:
            network_class_cat="normal"
            
        network_class.append(network_class_cat)
        
    network_class=pd.DataFrame(network_class, columns=["network class"])
    
    return network_class

                    
def ToDataFrame(y_actual, y_predicted):
    """
    A function that takes the actual values and predicted values
    converts them to dataframe and concats them with the predicted network class 
    to return a new dataframe containing the actual, predicted values and the Predicted network class 
    """
    network_class= NetworkClass(y_predicted)
    
    y_act= np.array(y_actual)
    
    y_predicted=np.array(y_predicted)
    
    y_act=pd.DataFrame(y_act, columns=["actual values"])
    
    pred = pd.DataFrame(y_predicted, columns=["Predicted class"])
    
    new_dataframe = pd.concat([y_act, pred, network_class], axis=1)
    
    return new_dataframe

def to_lm(cm):
    lm= cm.tolist()

    return lm
#---------views/routes---------------------



@app.route('/', methods=['GET','POST'])
def index():
    
    form=FileForm()
    
    if request.method=="POST":
        
        if form.validate_on_submit():
            mod=form.model.data
            if mod=='lr':
                model=joblib.load("model_LR.pkl")
                mod='Logistic regression'
            else:
                mod=='esm'
                model=joblib.load('model_z.pkl')
                mod='Esembling Learning'
                        
            f = request.files['data']

            filename = secure_filename(f.filename)
                    
            file_ext=os.path.splitext(filename)[1] #getting the file extension
            if file_ext in ['xlx','xlsx', 'xls']:
                    df = pd.read_excel(filename)
            else:
                
                df = pd.read_csv(filename)
            
            dat=form.dataset.data

            test_data= DataTransform(df)[0] #assesing the first value of returned vals in DataTransform function

            global y_actual
            y_actual = DataTransform(df)[1] #assesing the second value of the returned valas in DataTransform
            
            global y_predicted      
            y_predicted=model.predict(test_data)
            
            global cm
            cm=confusion_matrix(y_actual, y_predicted)
            lm=to_lm(cm) #converts the confusion matrix to list
        
            #fig = go.Figure(data=go.Heatmap(z=[y_predicted, y_actual]))
            
            #graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            flash("You selected the {} model".format(mod), 'info')
            
            return render_template_modal('result_js.html',lm=lm,form=form, modal=None)
    
    return render_template_modal('index.html',form=form, modal='modal-form')



@app.route('/predict', methods=["GET", "POST"])
def predict():
    lm=to_lm(cm)
    return render_template('result_js.html',lm=lm)

@app.route('/download', methods=["GET","POST"])
def download():
    try:
        prediction=ToDataFrame(y_actual, y_predicted)
        prediction.to_csv("predicted_values.csv")
        flash("File saved successfully", 'info')
        return redirect(url_for('index'))

    except:
        flash("File could not be saved, try Again", 'warning')
    return redirect(url_for('index'))
