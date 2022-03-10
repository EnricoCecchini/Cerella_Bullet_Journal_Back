from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from itsdangerous import json
import loaf

app = Flask(__name__)
CORS(app)

loaf.bake(
    host='127.0.0.1',
    port=3306,
    user='root',
    pasw='',
    db='cerella'
)

@app.route('/registro')
def registro():
    correo = request.args.get('correo')
    password = request.args.get('passw')
    userName = request.args.get('userName')

    if not (correo and password and userName):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    checkExistenciaCorreo = loaf.query(f''' SELECT FROM usuario
                                    WHERE correo = '{correo}' ''')

    checkExistenciaUser = loaf.query(f''' SELECT FROM usuario
                                    WHERE nombreUsuario = '{userName}' ''')
    
    if checkExistenciaCorreo or checkExistenciaUser:
        return jsonify({
            'success': 'False',
            'message': 'Esata cuenta ya existe'
        })
    
    loaf.query(f''' INSERT INTO usuario (correo, contrasena, nombreUsuario)
                    VALUES ('{correo}', '{password}', '{userName}')''')
    
    return jsonify({
        'success': 'True',
        'message': 'Usuario registrado exitosamente'
    })

@app.route('/login')
def login():
    usuario = request.args.get('usuario')
    password = request.args.get('passw')

    if not password and usuario:
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    loginCorreo = loaf.query(f''' SELECT IDUsuario FROM usuario
                                    WHERE correo = '{usuario}' AND contrasena = '{password}' ''')

    loginUserName = loaf.query(f''' SELECT IDUsuario FROM usuario
                                    WHERE nombreUsuario = '{usuario}' AND contrasena = '{password}' ''')
    
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

if __name__ == "__main__":
    app.run(debug=True)