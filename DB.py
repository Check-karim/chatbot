import mysql.connector
from mysql.connector import Error

def con():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot"
        )
        if con.is_connected():
            print("You're connected to database ")
            return con
    except Error as e:
        print("Error while connecting to MySQL", e)

