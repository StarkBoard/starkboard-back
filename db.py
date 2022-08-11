import os
import pymysql
from dotenv import load_dotenv
load_dotenv()

RDS_HOST = os.environ.get('RDS_HOST')
RDS_PORT = int(os.environ.get('RDS_PORT'))
RDS_USER = os.environ.get('RDS_USER')
RDS_PWD = os.environ.get('RDS_PWD')
AWS_REGION = os.environ.get('AWS_REGION')

def get_connection():
    connection = pymysql.connect(host=RDS_HOST, user=RDS_USER, port=RDS_PORT, password=RDS_PWD, database='starkboard', 
        cursorclass=pymysql.cursors.DictCursor)
    return connection
