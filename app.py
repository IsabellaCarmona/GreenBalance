from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        contraseña TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consumo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        mes TEXT NOT NULL,
        consumo FLOAT NOT NULL
    )
    ''')
    # Inserta el usuario solo si no existe
    cursor.execute('''
    INSERT OR IGNORE INTO usuarios (id, nombre, contraseña)
    VALUES (1, "admin", "1234")
    ''')
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            data = request.json
            if not data:
                return jsonify({"message": "No se enviaron datos"}), 400

            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"message": "Faltan campos obligatorios"}), 400

            conn = sqlite3.connect('database.sqlite')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND contraseña = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                return jsonify({"message": "Ok"}), 200      
            else:
                return jsonify({"message": "Credenciales inválidas"}), 401

        except Exception as e:
            return jsonify({"message": f"Error interno del servidor: {str(e)}"}), 500

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/dataConsumeRegister', methods=['GET','POST'])
def consume_register():
    if request.method == 'GET':
        return render_template('dataConsume.html')
    else:
        try:
            data = request.json
            type = data.get('type')
            month = data.get('month')
            consume = data.get('consume')

            if not type or not month or consume is None:
                return jsonify({"error": "Datos incompletos"}), 400

            # Guardar el consumo en la base de datos
            conn = sqlite3.connect('database.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO consumo (tipo, contraseña) VALUES ( ? , ? , ? )",(type,month,consume))

            conn.commit()
            conn.close()

            return jsonify({"message": "Consumo registrado exitosamente"}), 200
        except Exception as e:
            return jsonify({"message": f"Error interno del servidor: {str(e)}"}), 500

@app.route('/dataConsumeGraphics', methods=['GET','POST'])
def calcular_consumo():
    if request.method == 'GET':
        return render_template('dataConsumeGraphics.html')
    else:
        try:
            tipos = ['agua', 'energia', 'gas']
            resultados = {}

            # Calcular el consumo total por tipo
            conn = sqlite3.connect('database.sqlite')
            cursor = conn.cursor()
            for tipo in tipos:
                cursor.execute("SELECT SUM(consumo) FROM consumo WHERE tipo = ?", (tipo,))
                total = cursor.fetchone()[0]
                resultados[tipo] = total if total else 0
            conn.close()

            return jsonify(resultados), 200
        except Exception as e:
            return jsonify({"message": f"Error interno del servidor: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=8080)
