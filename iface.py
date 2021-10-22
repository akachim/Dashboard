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
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import numpy as np


#---------configurations--------------

app = Flask(__name__)
app.config["SECRET_KEY"]="oh well i hope it works this time"
#app.config["MAX_CONTENT_LENGTH"]=1024*1024

#app.config["UPLOAD_EXTENSIONS"]=['.csv', '.xlx', '.xls']

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
    A function that performs data tranformation before apllying to model
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
    
    y = data["class"]
    
    vals=[processed_df, y]
    
    return vals
#---------views/routes---------------------

@app.route('/', methods=['GET','POST'])
def index():
    form = FileForm()
    if request.method=="POST":
        if form.validate_on_submit():
            f = request.files['data']
            filename = secure_filename(f.filename)
            
            file_ext=os.path.splitext(filename)[1] #getting the file extension
            if file_ext in ['xlx','xlsx', 'xls']:
                df = pd.read_excel(filename)
            else:
                df = pd.read_csv(filename)
            
            test_data= DataTransform(df)[0]
            
            model=joblib.load("model_LR.pkl")
            
            y_predicted=model.predict(test_data)
            
            print(y_predicted)
            
            #A loop that determines the class 1:normal, 0:anormaly
            net_class=[]
            for i in y_predicted:
                if i ==0:
                    net_class_cat= "anormaly"
                elif i ==1:
                    net_class_cat="normal"
                    
                net_class.append(net_class_cat)
                
            net_class=pd.DataFrame(net_class, columns=["network class"])   
            #print(net_class.head())
                    
                    
            y_act= np.array(DataTransform(df)[1])
            y_act=pd.DataFrame(y_act, columns=["actual values"])    
            pred = pd.DataFrame(y_predicted, columns=["Predicted class"])
            
            new_output = pd.concat([y_act, pred, net_class], axis=1)
            
            #print(new_output.head())
            
            #result=new_output.to_html()
            
            #text_file = open("templates/table.html", "w")
            #text_file.write(result)
            #text_file.close()
            
            fig = px.bar(new_output, x='Predicted class', y='actual values', color="network class", title="Predicted class")
            
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            return render_template('result.html', form=form, graphJSON=graphJSON, modal=None)
            #return render_template('table.html', form=form, modal=None)
    return render_template_modal('index.html', form=form, modal='modal-form')



@app.errorhandler(413)
def too_large(e):
	return 'File too large', 413