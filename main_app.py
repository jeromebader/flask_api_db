
# Import of required files
from crypt import methods
from flask import Flask, render_template, request, session,redirect
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from flask import Flask, jsonify, request, render_template, session
import numpy as np
import pandas as pd
import pickle 
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from datetime import datetime
from flask import Flask, request, jsonify
import sqlite3,csv


def dbconn ():
    connection = sqlite3.connect('advertising_sales.db')
    cursor = connection.cursor()
    return connection, cursor


os.chdir(os.path.dirname(__file__))

#*** Flask configuration
 
# Define folder to save uploaded files to process further
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploads/')
 
# Define allowed files for uploading (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv'}
 
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
# Define secret key to enable session
#app.secret_key = 'This is your secret key to utilize session in Flask'
 
 
@app.route('/')
def index():
    """
    Function for rendering the main page
    """
    return render_template('show_upload.html')


@app.route('/',  methods=("POST", "GET"))
def uploadFile():
    """ Function for upload a CSV to flask server"""

    if request.method == 'POST':
        # upload file flask
        uploaded_df = request.files['uploaded-file']
 
        # Extracting uploaded data file name
        data_filename = secure_filename(uploaded_df.filename)
 
        # flask upload file to database (defined uploaded folder in static path)
        uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
 
        # Storing uploaded file path in flask session
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
      
 
        #return render_template('show_upload')
        source=session['uploaded_data_file_path']
        return redirect(f'/readcsv' )


@app.route("/readcsv", methods=['GET'])
def readcsv():
    """ Function for dump uploaded CSV to DB"""

    con, cursor = dbconn ()
    source = session['uploaded_data_file_path'] 
    with open(source,'r') as fin: 
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [( float(i['TV']),float(i['radio']),float(i['newspaper']),float(i['sales'])) for i in dr]

    if cursor.executemany("INSERT INTO estimators ( TV, radio, newspaper,sales) VALUES ( ?,?,?,?);", to_db):
        con.commit()
        con.close()
        saved = '<p style="color:green;">file uploaded and data saved in DB</p>'
    else:
        saved = '<p style="color:red;">file not uploaded and data not saved in DB</p>'

    return render_template('show_upload.html',saved=saved)


@app.route('/show_data')
def showData():
    """ Function for fetching all data from DB and sending to render"""

    con, cursor = dbconn ()
    select_values = "SELECT * FROM estimators"
    records = cursor.execute(select_values)
    df = pd.DataFrame(records.fetchall(), columns = ['id','TV', 'radio','newspaper','sales','version']).set_index("id")
    # pandas dataframe to html table flask
    uploaded_df_html = df.to_html(col_space='120px',justify='left')
    return render_template('show_csv_data.html', data_var = uploaded_df_html)


@app.route("/predict", methods=['GET','POST'])
def model():
    """Endpoint for executing the prediction for sales predictions based on advertising costs. Returns JSON if request is made by POST,
    if it's made by GET it gives back html.
    """

    con, cursor = dbconn ()
    select_values = "SELECT id, TV, radio, newspaper, sales FROM estimators"
    records = cursor.execute(select_values)
    df = pd.DataFrame(records.fetchall(), columns = ['id','TV', 'radio','newspaper', 'sales']).set_index("id")
    df = df[df["sales"].isna()]
    X = df.drop(columns=['sales'])
    filename_model = './data/advertising_model.pkl'
    pickled_model = pickle.load(open(filename_model, 'rb'))
    results = pickled_model.predict(X)
    df_new = df
    df_new["Estimation"] = np.round(results,2)
    if request.method == "POST":
        html_df = df_new.to_json()
        return   html_df
    else:
        html_df = df_new.to_html(col_space='120px',justify='left')
        return render_template('show_predictions.html', data_var = html_df)


### Arguments per line
@app.route("/ingest_data", methods=['POST'])
def ingest():
    """ Function for receiving new DATA by POST of arguments or JSON to the database"""
    message = ''
    data= {}
    if not request.is_json: 
        # Data by Argument received
        
        if 'tv' in request.args:
                data['tv'] = float(request.args['tv'])
        else:
                data['tv']= 0.0

        if 'radio' in request.args:
                data['radio']= float(request.args['radio'])
        else:
                data['radio']= 0.0

        if 'newspaper' in request.args:
                data['newspaper'] = float(request.args['newspaper'])
        else:
                data['newspaper'] = 0.0

    else:  # JSON data received
        request_data = request.get_json()
        if request_data:
            if 'tv' in request_data:
                data['tv'] = float(request_data['tv'])
            else:
                data['tv']= 0.0

            if 'radio' in request_data:
                data['radio'] = float(request_data['radio'])
            else:
                data['radio']= 0.0

            if 'python' in request_data:
                data['newspaper'] = float(request_data['newspaper'])
            else:
                data['newspaper'] = 0.0

     

    # Data is not blank?!
    if data['tv'] >= 0 or data['radio'] >= 0.0 or data['newspaper'] >= 0:
         con, cursor = dbconn ()
         to_db = (data['tv'],data['radio'],data['newspaper'])
         if cursor.execute("INSERT INTO estimators ( TV, radio, newspaper) VALUES ( ?,?,?);", (data['tv'],data['radio'],data['newspaper'],)):
            con.commit()
            con.close()
            message += 'Data added'
         else:
            message += 'error in adding the data to DB'
           

    else:
        message += 'data arguments not complete'


    return message  ### Message for data upload by API

    

@app.route('/retrain', methods=['PUT'])
def retrain():
    """
    Retrains the model with advertising costs that have also sales \n
    """
    con, cursor = dbconn ()
    select_values = "SELECT id, TV, radio, newspaper, sales FROM estimators"
    records = cursor.execute(select_values)
    df = pd.DataFrame(records.fetchall(), columns = ['id','TV', 'radio','newspaper','sales']).set_index("id")
    df = df[~df['sales'].isna()]
    X = df.drop(columns=['sales'])
    y = df['sales']
    # Load and train the model
    model = pickle.load(open('data/advertising_model.pkl','rb'))
    model.fit(X,y)

    tiempo = datetime.today().strftime('%Y%m%d%H%M%S')
    filename = f'./data/advertising_model_v{tiempo}.pkl'

    # Save the new model
    pickle.dump(model, open(filename,'wb'))
    scores = cross_val_score(model, X, y, cv=10, scoring='neg_mean_absolute_error')

    return f"New model retrained and saved as {filename} . The results of MAE with cross validation of 10 folds is: " + str(abs(round(scores.mean(),2)))


# RUN MAIN
app.run(debug = True)