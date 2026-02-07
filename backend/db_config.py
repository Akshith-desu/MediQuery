import mysql.connector

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=" ",#enter the password
        database="mediquery"
    )
 