# Importacion de modulos requeridos
from distutils.log import error
from operator import methodcaller
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
import loaf
import re

# Se crea objeto de Flask
app = Flask(__name__)
CORS(app)

app.secret_key="CONSUltores"

# Datos de la BD
loaf.bake(
    host='127.0.0.1',
    port=3306,
    user='root',
    pasw='',
    db='cerella'
)

@app.route("/")
def index():
    try:
        if not (session["usuario"] and session["password"]):
            session["usuario"]=""
            session["password"]=""
    except KeyError:
        session["usuario"]=""
        session["password"]=""
    return render_template("index.html")

# Funcion de registro
@app.route('/registro', methods=["POST","GET"])
def registro():

    error=""
    specialChars = '\\\'./<>!@#$%^&*()-=+~`'
    if request.method == "POST": 
        # Recibe datos de la pagina
        correo = request.form.get('correo')
        password = request.form.get('passw')
        confirmarPassword = request.form.get('passw3')
        userName = request.form.get('userName')

        # Checa que se reciban todos los datos
        if not (correo and password and userName):
            print(correo, password, userName)
            error="Faltan campos"
            return render_template("Registro.html",error=error)
        
        # Checa si el correo ya esta registrado
        checkExistenciaCorreo = loaf.query(f''' SELECT usuarioID FROM usuario WHERE correo = '{correo}' ''')

        # Checa si el nombre de usuario ya esta registrado
        checkExistenciaUser = loaf.query(f''' SELECT usuarioID FROM usuario WHERE username = '{userName}' ''')
        
        if checkExistenciaCorreo or checkExistenciaUser:
            error="Esta cuenta ya existe"
            return render_template("Registro.html",error=error)
        
        for c in specialChars:
            if c in userName:
                error = 'Nombre de usuario invalido'
                return render_template("Registro.html",error=error)
        
        if password != confirmarPassword:
            error = 'Las contrasenas no coinciden'
            return render_template("Registro.html",error=error)

        # Inserta datos de usuario
        loaf.query(f''' INSERT INTO usuario (correo, password, username)
                        VALUES ('{correo}', '{password}', '{userName}')''')

        return redirect(url_for("login"))

    else:
        return render_template("Registro.html")

# Funcion de Login
@app.route('/login', methods=["POST","GET"])
def login():
    error=""
    if request.method == "POST":
        # Recibe datos de la pagina
        usuario = request.form.get('usuario')
        password = request.form.get('passw')

        session["usuario"]=usuario
        session["password"]=password

        # Checa que se reciban todos los campos
        if not (password and usuario):
            error="faltan campos"
            return render_template("Login.html",error=error)
        else:
            # Checa si se hace login con correo
            login = loaf.query(f''' SELECT usuarioID FROM usuario
                                            WHERE (correo = '{usuario}' AND password = '{password}') OR (username = '{usuario}' AND password = '{password}') '''.replace('\n',' '))
                        
            # Retorna userID si login fue exitoso, o indica si los datos no coinciden
            if login:
                session['userID']=login[0][0]
                return redirect(url_for("catalogo"))
            else:
                error="Usuario o constraseña equivocados"
                return render_template("Login.html",error=error)
    else:
        return render_template("Login.html",error=error)

@app.route('/perfil', methods=["POST","GET"])
def perfil():
    error=""
    errorCambio=""
    usuario = ''
    uid = request.args.get('userid')

    specialChars = '\\\'./<>!@#$%^&*()-=+~`'
    
    if request.method == "POST":
        print('Updating profile')
        newUsuario = request.form.get('username')
        newPassword = request.form.get('passw')
        confirmarPassword = request.form.get('passw2')
        valid = True

        print(newUsuario)
        print(newPassword)

        for c in specialChars:
            if c in newUsuario:
                error = 'Nombre de usuario invalido'
                valid = False
                # return render_template("Perfil.html",error=error)
        if newPassword != confirmarPassword:
            error = 'Las contrasenas no coinciden'
            valid = False
            
        if valid:
            userID = session['userID']

            userNameExists = loaf.query(f''' SELECT usuarioID FROM usuario WHERE username = '{newUsuario}' ''')

            if newPassword == '':
                newPassword=session["password"]

            if userNameExists and (newUsuario != session["usuario"]):
                errorCambio = 'El nombre de usuario ya esta registrado'
            else:
                loaf.query(f''' UPDATE usuario SET username='{newUsuario}', password='{newPassword}' WHERE usuarioID = '{userID}' ''')
                session['usuario']=newUsuario
    
    username = session["usuario"]
    # print('UserName', username)
    
    userInfo = loaf.query(f''' SELECT username, correo, password FROM usuario
                                WHERE username = '{username}' OR correo = '{username}' ''')[0]
    
    if not userInfo:
        error="El usuario no existe"

    # print('Eli', userInfo)
    usuario = [userInfo[0], userInfo[1], userInfo[2]]

    return render_template('Perfil.html', error=error, usuario=usuario, errorCambio=errorCambio)

@app.route("/catalogo")
def catalogo():
    usuario=session["usuario"]
    password=session["password"]
    if usuario and password:
        return render_template("Catalogo.html")
    else:
        return redirect(url_for("login"))

# Ejecuta el API
if __name__ == "__main__":
    app.run(debug=True)