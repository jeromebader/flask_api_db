import csv, sqlite3, os
directory = os.getcwd()
print(directory)
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
print (dname)

con = sqlite3.connect("./data/advertising_sales.db") # change to 'sqlite:///your_filename.db'
cur = con.cursor()
cur.execute('CREATE TABLE estimators (id INTEGER, TV FLOAT NOT NULL, radio FLOAT NOT NULL, newspaper FLOAT NOT NULL,sales FLOAT NULL, period TEXT NULL,  PRIMARY KEY("id" AUTOINCREMENT));   ') 



# use your column names here

with open('./data/Advertising.csv','r') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i[''], i['TV'],i['radio'],i['newspaper'],i['sales']) for i in dr]

cur.executemany("INSERT INTO estimators (id, TV, radio, newspaper,sales) VALUES (?, ?,?,?,?);", to_db)
con.commit()
con.close()