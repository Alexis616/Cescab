""" import mysql.connector """
from datetime import timedelta
import mysql.connector
from flask import Flask
from flask_jwt_extended import JWTManager
import os

programa = Flask(__name__)
programa.config['SECRET_KEY'] = os.urandom(24)
programa.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
jwt = JWTManager(programa)

""" def get_db_connection():
    mydb = mysql.connector.connect(
        host='85.31.231.136', #85.31.231.136
        port='4030',
        user='bcab',    #bcab
        password='Bc4b', #Bc4b
        database='bcab'
    )
    return mydb
 """

def get_db_connection():
    mydb = mysql.connector.connect(
        host='localhost', #85.31.231.136
        user='root',    #bcab
        password='', #Bc4b
        database='bcabv2'
    )
    return mydb

#Westa es de pruebas 

def get_db_connection2():
    mydb = mysql.connector.connect(
        host='localhost', #85.31.231.136
        user='root',    #bcab
        password='', #Bc4b
        database='pruebas'
    )
    return mydb