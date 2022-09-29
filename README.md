# Flask + ML + SQL + API

Simple demo Application for API, SQL used with Machine Learning Scikit-Learn Library, and FLASK + HTML/Bootstrap deployed in PythonAnywhere with Git Pipeline. 

[see the App deployed on PythonAnywhere by clicking on the link](https://jeroba.pythonanywhere.com/)

## API Endpoints
```API

/ingest_data   [POST]

Receives values in $ for the estimators:
tv (float), mandatory
radio(float, mandatory
newspaper (float) , mandatory
sales (float), optional

Example:
https://jeroba.pythonanywhere.com/ingest_data?tv=100&radio=200&newspaper=400

or send 
JSON
Example:
{
"tv": 400,
"radio" : 300,
"newspaper" : 600
}

/predict  [GET,POST]

Predicts sales based on $ amounts spent on tv,radio,newspaper.
A pre-trained pickle file is used.
Output [POST : JSON
Output [GET] : HTML 


/retrain  [PUT]
Retrains the Machine Learning model based on a Pickle file 
with the new sales data.
Output:  Message

```

## Installation

### Folders

    .
    ├── src 
        ── creat_db.py              # Reads CSV to SQL
        ── sample_uploadfile.csv    # Sample Upload CSV
    ├── data                        # Contains the model and base CSV
    ├── static                      # Contains assets / CSS Bootstrap
    ├── templates                   # Contains HTML 
    ├── uploads                     # Contains folder for saving the uploads
    └── README.md                   # README
    └── advertising_sales.db        # DB Sqlite
    └── main_app.py                 # Main App
    
```
On localhost please uncomment #app.run(debug = True).
Install the libraries:
numpy 
pandas
pickle 
flask
sqlite
sklearn


```

## Considerations
The CSV File should be in the sample format, 

Please have in mind that the deployed app on PythonAnywhere doesn't permit the upload of large CSV files.

## License
[MIT](https://choosealicense.com/licenses/mit/)