# main.py# import the necessary packages
from flask import Flask, flash, render_template, Response, request, redirect, url_for, session, make_response
from camera import VideoCamera
from flask_mysqldb import MySQL
from train_model import entrenar_sistema
from extract_embeddings import extraer
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import os
import pathlib
import sys
import pyexcel as pe
import io

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '123456789'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'sergio'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'sistema'

# Intialize MySQL
mysql = MySQL(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOADED_FILES'] = 'dataset'

data = []

camara_nombre = "Camara"

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and "camara" in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        camara = request.form["camara"]

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        usuario = cursor.fetchone()

        # If account exists in accounts table in out database
        if usuario:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = usuario['id']
            session['username'] = usuario['username']
            session['camara'] = camara

            global camara_nombre
            camara_nombre = camara
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Username/password incorrecto!'

    return render_template('index.html', msg=msg)

# http://127.0.0.1:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('camara', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://127.0.0.1:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://127.0.0.1:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
        usuario = cursor.fetchone()
        return render_template('profile.html', usuario=usuario)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/reconocimiento', methods=['GET', 'POST'])
def reconocimiento():
    # rendering webpage
    if 'loggedin' in session:
        if request.method == 'POST':
            return render_template('reconocimiento.html', camara = session['camara'])
    return redirect(url_for('login'))

@app.route('/pythonlogin/agregar', methods=['GET', 'POST'])
def agregar():
    # rendering webpage
    msg = ""
    if 'loggedin' in session:
        if request.method == 'POST' and 'nombre' in request.form and 'carpeta' in request.form and 'agregar' in request.form:
            try:
                uploaded_files = request.files.getlist('fotos[]')
                task_name = request.form.get('carpeta')
                nombre_completo = request.form.get('nombre')
                
                task_name = task_name.replace(" ", "_")

                cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor2.execute('SELECT url FROM imagenes WHERE url = %s', (task_name,))
                # Fetch one record and return result
                url = cursor2.fetchone()
                if not(str(url) == 'None') and str(url['url']) == task_name:
                    msg = "Error, nombre de la carpeta repetido."    
                else:
                    filename = []
                    pathlib.Path(app.config['UPLOADED_FILES'], task_name).mkdir(exist_ok=True)
                    contador = 0
                    for file in uploaded_files:
                        extension = file.filename.split('.')
                        filename = str(contador).zfill(5)
                        filename = filename + '.' + extension[1]
                        file.save(os.path.join(app.config['UPLOADED_FILES'], task_name, filename))
                        contador = contador + 1

                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('Insert into imagenes (nombre,url) values (%s,%s)', (nombre_completo, task_name,))
                    mysql.connection.commit()
                    msg = "Fotos agregadas correctamente."
            except:
                msg = "Error de subida.",sys.exc_info()[0]
        elif request.method == 'POST' and 'aprender' in request.form:
            msg = extraer()
            msg = msg + entrenar_sistema()
        return render_template('agregar.html', msg=msg)
    return redirect(url_for('login'))

@app.route('/pythonlogin/accesos', methods=['GET', 'POST'])
def accesos():
    # rendering webpage
    if 'loggedin' in session:
        global data
        tabla = """<tr>
            <th>Nombre</th>
            <th>Fecha</th>
            <th>Camara</th> 
            </tr>"""
        if request.method == 'POST' and 'inicial' in request.form and 'final' in request.form and 'rango' in request.form:
            inicial = request.form.get('inicial')
            final = request.form.get('final')
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('select imagenes.nombre, entradas.fecha, entradas.camara from imagenes, entradas where imagenes.url = entradas.nombre and entradas.fecha between %s and %s;', (inicial,final))
            datos = cursor.fetchall()

            data = [["Nombre","Fecha","Camara"]]

            for dato in datos:
                nombre = dato['nombre']
                fecha = dato['fecha']
                camara = dato['camara']
                data.append([str(nombre),str(fecha),str(camara)])
                tabla = tabla + "<tr> <td>" + str(nombre) + "</td> <td>" + str(fecha) + "</td> <td>" + str(camara) + "</td> </tr>"
        elif request.method == 'POST' and 'todos' in request.form:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('select imagenes.nombre, entradas.fecha, entradas.camara from imagenes, entradas where imagenes.url = entradas.nombre;')
            datos = cursor.fetchall()

            data = [["Nombre","Fecha","Camara"]]

            for dato in datos:
                nombre = dato['nombre']
                fecha = dato['fecha']
                camara = dato['camara']
                data.append([str(nombre),str(fecha)])
                tabla = tabla + "<tr> <td>" + str(nombre) + "</td> <td>" + str(fecha) + "</td> <td>" + str(camara) + "</td> </tr>"
        return render_template('accesos.html', tabla=tabla)
    return redirect(url_for('login'))

@app.route('/pythonlogin/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        sheet = pe.Sheet(data)
        iovariable = io.StringIO()
        sheet.save_to_memory("csv", iovariable)
        output = make_response(iovariable.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=accesos.csv"
        output.headers["Content-type"] = "text/csv"
        return output

def gen(camera,nombre):
    camera.read_data()
    camera.set_nombre(nombre)
    while True:
        #get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera(),session['camara']),mimetype='multipart/x-mixed-replace; boundary=frame')
    
if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0',port='5000', debug=True)
