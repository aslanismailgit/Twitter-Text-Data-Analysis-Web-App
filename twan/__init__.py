from flask import Flask
from flask_mail import Mail
# from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == "test":
    app.config.from_object("config.TestingConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

db = SQLAlchemy(app)
print (db)
# mongo = PyMongo(app)

mail = Mail(app)

# comment below in case use of gcp ai platform to get the embeddings
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)

print("Version: ", tf.__version__)
print("GPU is", "available" if tf.config.list_physical_devices('GPU') else "NOT AVAILABLE")

saved_model_link = "./twan/tf_model/"
model_ser_encoder = hub.load(saved_model_link)
print("--------- model imported -------")

# --- 
from twan import routes
from twan.functions import TWAN
