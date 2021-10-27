import os
from flask import Flask, render_template, redirect, flash, session, request
from flask.helpers import url_for
from flask_bootstrap import Bootstrap 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from pandas.core.frame import DataFrame
from wtforms import SubmitField
from flask_modals import Modal
from flask_modals import render_template_modal
from werkzeug.utils import secure_filename

#-----Data analysis modules
#import csv
import joblib
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np


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
	submit=SubmitField("Submit")



def DataTransform(data):
    """
    A function that performs data tranformation before apllying to prediction model
    it takes test data frame as the only argument
    
    """
    non_num = data[["protocol_type","service","flag"]]
    non_num.head()
    label_encoder = LabelEncoder()
    non_num['protocol_type'] = label_encoder.fit_transform(non_num['protocol_type'])
    non_num['service'] = label_encoder.fit_transform(non_num['service'])
    non_num['flag'] = label_encoder.fit_transform(non_num['flag'])
    
    num = data.drop(["protocol_type","service","flag", 'class'], axis=1)
    
    num[num.columns]= StandardScaler().fit_transform(num[num.columns])
    
    processed_df = pd.concat([non_num, num], axis=1)
    
    data['class'] = LabelEncoder().fit_transform(data['class'])
    
    y_actual = data["class"]
    
    vals=[processed_df, y_actual]
    
    return vals


def NetworkClass(y_predicted):
    """
    A function that takes the predicted value and returns the predicted categorical value
    1: normal, 0: anormaly, storing it as dataframe column.
    """
    network_class=[]
    
    for i in y_predicted:
        if i ==0:
            nework_class_cat= "anormaly"
        elif i ==1:
            network_class_cat="normal"
            
        network_class.append(network_class_cat)
        
    network_class=pd.DataFrame(network_class, columns=["network class"])
    
    return network_class

#---------views/routes---------------------

@app.route('/', methods=['GET','POST'])
def index():
    form = FileForm()
    if request.method=="POST":
        if form.validate_on_submit():
            #Making sure the user selects a model
            
            z=request.form.get("models")
            
            if z=='lr':
                model=joblib.load("model_LR.pkl")
                
            else:
                z=='esm'
                model=joblib.load("model_z.pkl")
                flash("You selected the Esembling Learning")
                
            f = request.files['data']
            
            filename = secure_filename(f.filename)
            
            file_ext=os.path.splitext(filename)[1] #getting the file extension
            if file_ext in ['xlx','xlsx', 'xls']:
                df = pd.read_excel(filename)
            else:
                df = pd.read_csv(filename)
            
            test_data= DataTransform(df)[0] #assesing the first value of returned vals in DataTransform function
            y_actual = DataTransform(df)[1] #assesing the second value of the returned valas in DataTransform
               
            y_predicted=model.predict(test_data)
            
            #cf_matrix = confusion_matrix(y_actual, y_predicted) #Confusion matrix
            #ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True, 
            #fmt='.2%', cmap='Blues')

            #ax.set_title('Confusion Matrix for Predicted and Actual class\n\n');
            #ax.set_xlabel('\nPredicted Values')
            #ax.set_ylabel('Actual Values ');

            ## Ticket labels - List must be in alphabetical order
            #ax.xaxis.set_ticklabels(['False','True'])
            #ax.yaxis.set_ticklabels(['False','True'])

            ## Display the visualization of the Confusion Matrix.
            #plt.show()
                    
            network_class= NetworkClass(y_predicted)
            
            y_act= np.array(y_actual)
            y_predicted=np.array(y_predicted)
            y_act=pd.DataFrame(y_act, columns=["actual values"])    
            pred = pd.DataFrame(y_predicted, columns=["Predicted class"])
            
            new_output = pd.concat([y_act, pred, network_class], axis=1)
            
            #result=new_output.to_html()
            
            #text_file = open("templates/table.html", "w")
            #text_file.write(result)
            #text_file.close()
            
            #fig = go.Figure(data=go.Heatmap(
                    #z=[y_predicted, y_act]))
            
            #fig = px.imshow(new_output)
            
            #graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            #return render_template('result.html', form=form, graphJSON=graphJSON, modal=None)
    return render_template_modal('index.html', form=form, modal='modal-form')



@app.errorhandler(413)
def too_large(e):
	return 'File too large', 413