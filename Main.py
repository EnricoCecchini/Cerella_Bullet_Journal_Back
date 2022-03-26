# Importacion de modulos requeridos
from crypt import methods
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
    # try:
    #     if not (session["usuario"] and session["password"]):
    #         session["usuario"]=""
    #         session["password"]=""
    # except KeyError:
    #     session["usuario"]=""
    #     session["password"]=""
    try:
        if (session["usuario"] and session["password"]):
            return render_template("index_session.html")
    except KeyError:
        session["usuario"] = ""
        session["password"] = ""
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
        
        specialPassw = False
        passwMayus = False

        for c in specialChars:
            if c in password:
                specialPassw = True
                break
        
        for c in password:
            if c.isupper():
                passwMayus = True
                break
        
        if not (specialPassw and passwMayus):
            error=f"La contrasena debe contener minimo 1 caracter especial y 1 letra mayuscula {password, specialPassw, passwMayus}"
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
            error = f'Las contrasenas no coinciden {password, confirmarPassword}'
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
    check=""
    errorCambio=""
    usuario = ''
    uid = request.args.get('userid')

    specialChars = '\\\'./<>!@#$%^&*()-=+~`'
    
    if request.method == "POST":
        
        print("Hola 1")
        if 'logout' in request.form:
            session["usuario"]=""
            session["password"]=""
            print("Hola 2")
            return redirect(url_for("index"))
        
        print('Updating profile')
        newUsuario = request.form.get('username')
        newPassword = request.form.get('passw')
        confirmarPassword = request.form.get('passw2')
        valid = True

        print(newUsuario)
        print(newPassword)

        passwMayus = False
        specialPassw = False

        for c in specialChars:
            if c in newUsuario:
                error = 'Nombre de usuario invalido'
                valid = False

        for c in newPassword:
            if c.isupper():
                passwMayus = True
                break
        
        for c in specialChars:
            if c in newPassword:
                specialPassw = True
                break
        
        if not (passwMayus and specialPassw):
            error = 'La contrasena debe contener minimo 1 caracter especial y 1 letra mayuscula'
            valid = False

        if newPassword != confirmarPassword:
            error = 'Las contraseñas no coinciden'
            valid = False
            
        if valid:
            check = "Información actualizada!"
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

    return render_template('Perfil.html', error=error, check=check, usuario=usuario, errorCambio=errorCambio)

@app.route("/catalogo")
def catalogo():
    usuario=session["usuario"]
    password=session["password"]
    if usuario and password:
        return render_template("Catalogo.html")
    else:
        return redirect(url_for("login"))

@app.route("/nuevoJournal", methods=["POST","GET"])
def nuevoJournal():

    plantilla1 = ["nombre"]
    plantilla2 = ["nombre2"]
    plantilla3 = ["nombre3"]
    plantillas = [plantilla1, plantilla2, plantilla3]

    if request.method == "POST":
        categoria = request.form.get('categoria')
        print(categoria)
    
    return render_template("NuevoJournal.html", plantillas=plantillas)

# Ejecuta el API
if __name__ == "__main__":
    app.run(debug=True)