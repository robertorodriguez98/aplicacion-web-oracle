import os
import sys
import cx_Oracle
from flask import Flask, render_template, request,abort

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template("inicio.html")

@app.route('/consulta',methods=["POST"])
def iniciosesion():
    usuario=request.form['usuario']
    contra=request.form['contra']
    while True:
        try:
            connection = cx_Oracle.connect(
            user=usuario,
            password=contra,
            dsn="192.168.122.204:1521/ORCLCDB")
            cursor = connection.cursor()
            cursor.execute("select * from emp")
            res = cursor.fetchall()        
            return render_template("consulta.html", res=res)
        except cx_Oracle.DatabaseError:
            return render_template("error.html")
    

    #return(res)



if __name__ == '__main__':

    # Start a pool of connections
    #pool = start_pool()


    # Start a webserver
    app.run(port=int(os.environ.get('PORT', '8080')))