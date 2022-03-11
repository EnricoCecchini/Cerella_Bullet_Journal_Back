# Importacion de modulos requeridos
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from itsdangerous import json
import loaf

# Se crea objeto de Flask
app = Flask(__name__)
CORS(app)

# Datos de la BD
loaf.bake(
    host='127.0.0.1',
    port=3306,
    user='root',
    pasw='',
    db='cerella'
)

# Funcion de registro
@app.route('/registro')
def registro():
    # Recibe datos de la pagina
    correo = request.args.get('correo')
    password = request.args.get('passw')
    userName = request.args.get('userName')

    # Checa que se reciban todos los datos
    if not (correo and password and userName):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    # Checa si el correo ya esta registrado
    checkExistenciaCorreo = loaf.query(f''' SELECT FROM usuario
                                    WHERE correo = '{correo}' ''')

    # Checa si el nombre de usuario ya esta registrado
    checkExistenciaUser = loaf.query(f''' SELECT FROM usuario
                                    WHERE nombreUsuario = '{userName}' ''')
    
    if checkExistenciaCorreo or checkExistenciaUser:
        return jsonify({
            'success': 'False',
            'message': 'Esta cuenta ya existe'
        })
    
    # Inserta datos de usuario
    loaf.query(f''' INSERT INTO usuario (correo, contrasena, nombreUsuario)
                    VALUES ('{correo}', '{password}', '{userName}')''')

    # Obtiene ID de usuario registrado para ingresar
    userID = loaf.query(f''' SELECT IDUsuario FROM usuario
                                    WHERE correo = '{correo}' AND contrasena = '{password}' ''')
    
    return jsonify({
        'success': 'True',
        'message': 'Usuario registrado exitosamente',
        'userID': userID[0]
    })

# Funcion de Login
@app.route('/login')
def login():
    # Recibe datos de la pagina
    usuario = request.args.get('usuario')
    password = request.args.get('passw')

    # Checa que se reciban todos los campos
    if not password and usuario:
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    # Checa si se hace login con correo
    loginCorreo = loaf.query(f''' SELECT IDUsuario FROM usuario
                                    WHERE correo = '{usuario}' AND contrasena = '{password}' ''')

    # Checa si se hace login con userName
    loginUserName = loaf.query(f''' SELECT IDUsuario FROM usuario
                                    WHERE nombreUsuario = '{usuario}' AND contrasena = '{password}' ''')
    
    # Retorna userID si login fue exitoso, o indica si los datos no coinciden
    if loginCorreo:
        return jsonify({
            'success': 'True',
            'message': 'Login Exitoso',
            'userID': loginCorreo[0]
        })
    elif loginUserName:
        return jsonify({
            'success': 'True',
            'message': 'Login Exitoso',
            'userID': loginUserName[0]
        })
    else:
        return jsonify({
            'success': 'False',
            'message': 'Usuario o contrasena equivocados'
        })

# Ejecuta el API
if __name__ == "__main__":
    app.run(debug=True)