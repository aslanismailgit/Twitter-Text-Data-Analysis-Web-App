from twan import db
from datetime import datetime

class searchitems(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    search_text = db.Column(db.String(length=300), nullable=False)
    startdate = db.Column(db.Date, nullable=False)
    enddate = db.Column(db.Date, nullable=False)
    searchdate = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    lang = db.Column(db.String(length=30), nullable=False)
    email_address = db.Column(db.String(length=100), nullable=True)
    data_length = db.Column(db.Integer(), nullable=True)


#%% GCP commands to create table
# USE twandb;
# DROP TABLE IF EXISTS searchitems;
# CREATE TABLE searchitems (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
# search_text VARCHAR(100) NOT NULL,
# startdate DATE,
# enddate DATE,
# searchdate INT(6),
# lang VARCHAR(30),
# email_address VARCHAR(100),
# data_length INT(6));
# ALTER TABLE searchitems Modify column searchdate VARCHAR(20);  