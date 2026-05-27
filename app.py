from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
app = Flask(__name__)
app.secret_key = "codemaster"

# CONEXIÓN MYSQL

conexion = mysql.connector.connect(

    host=os.getenv("DB_HOST", "localhost"),

    port=int(os.getenv("DB_PORT", 3306)),

    user=os.getenv("DB_USER", "root"),

    password=os.getenv("DB_PASSWORD", ""),

    database=os.getenv("DB_NAME", "codemaster"),

    autocommit=True

)

cursor = conexion.cursor(buffered=True)

# INICIO
@app.route('/')
def inicio():
    return render_template('index.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        correo = request.form['correo']
        password = request.form['password']

        sql = """
        SELECT *
        FROM usuarios
        WHERE correo=%s AND password=%s
        """

        valores = (correo, password)

        cursor.execute(sql, valores)

        usuario = cursor.fetchone()

        if usuario:

            session['usuario_id'] = usuario[0]
            session['usuario_nombre'] = usuario[1]

            return redirect('/dashboard')

        else:
            return "Correo o contraseña incorrectos"

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():

    usuario_id = session['usuario_id']

    sql = """
    SELECT puntos
    FROM usuarios
    WHERE id = %s
    """

    cursor.execute(sql, (usuario_id,))

    resultado = cursor.fetchone()

    if resultado:
        puntos = resultado[0]
    else:
        puntos = 0

    return render_template(
        'dashboard.html',
        puntos=puntos,
        nombre=session['usuario_nombre']
    )

# RANKING
@app.route('/ranking')
def ranking():

    sql = """
    SELECT nombre, puntos
    FROM usuarios
    ORDER BY puntos DESC
    """

    cursor.execute(sql)

    usuarios = cursor.fetchall()

    return render_template(
        'ranking.html',
        usuarios=usuarios
    )

# NIVELES
@app.route('/niveles')
def niveles():

    usuario_id = session['usuario_id']

    sql = """
    SELECT puntos,
           nivel1_completado,
           nivel2_completado
    FROM usuarios
    WHERE id = %s
    """

    cursor.execute(sql, (usuario_id,))

    resultado = cursor.fetchone()

    if resultado:
        puntos = resultado[0]
        nivel1 = resultado[1]
        nivel2 = resultado[2]
    else:
        puntos = 0
        nivel1 = False
        nivel2 = False

    return render_template(
        'niveles.html',
        puntos=puntos,
        nivel1=nivel1,
        nivel2=nivel2
    )

# PREGUNTA 1
@app.route('/pregunta1')
def pregunta1():

    usuario_id = session['usuario_id']

    sql = """
    SELECT nivel1_completado
    FROM usuarios
    WHERE id = %s
    """

    cursor.execute(sql, (usuario_id,))

    resultado = cursor.fetchone()

    # SI YA TERMINÓ NIVEL 1
    if resultado and resultado[0] == 1:
        return redirect('/nivel2')

    return render_template('pregunta1.html')

# RESPUESTA CORRECTA 1
@app.route('/correcto')
def correcto():

    return render_template('correcto.html')

# RESPUESTA INCORRECTA

# PREGUNTA 2
@app.route('/pregunta2')
def pregunta2():

    return render_template('pregunta2.html')

# RESPUESTA CORRECTA 2
@app.route('/correcto2')
def correcto2():

    return render_template('correcto2.html')

# PREGUNTA 3
@app.route('/pregunta3')
def pregunta3():

    return render_template('pregunta3.html')
# INCORRECTO 1
@app.route('/incorrecto1')
def incorrecto1():

    return render_template(
        'incorrecto.html',
        volver='/pregunta1'
    )

# INCORRECTO 2
@app.route('/incorrecto2')
def incorrecto2():

    return render_template(
        'incorrecto.html',
        volver='/pregunta2'
    )

# INCORRECTO 3
@app.route('/incorrecto3')
def incorrecto3():

    return render_template(
        'incorrecto.html',
        volver='/pregunta3'
    )
# FINAL NIVEL 1
@app.route('/final')
def final():

    usuario_id = session['usuario_id']

    sql = """
    SELECT nivel1_completado
    FROM usuarios
    WHERE id = %s
    """

    cursor.execute(sql, (usuario_id,))

    resultado = cursor.fetchone()

    # SOLO DA XP UNA VEZ
    if resultado and resultado[0] == 0:

        sql_update = """
        UPDATE usuarios
        SET puntos = puntos + 30,
            nivel1_completado = TRUE
        WHERE id = %s
        """

        cursor.execute(sql_update, (usuario_id,))

        conexion.commit()

    return redirect('/nivel2')

# NIVEL 2
@app.route('/nivel2')
def nivel2():

    return render_template('nivel2.html')
@app.route('/pregunta4')
def pregunta4():

    return render_template('pregunta4.html')

@app.route('/correcto4')
def correcto4():

    usuario_id = session['usuario_id']

    sql = """
    UPDATE usuarios
    SET puntos = puntos + 20
    WHERE id = %s
    """

    cursor.execute(sql, (usuario_id,))

    conexion.commit()

    return render_template('correcto4.html')

@app.route('/incorrecto4')
def incorrecto4():

    return render_template(
        'incorrecto.html',
        volver='/pregunta4'
    )

# REGISTRO
@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

        # VERIFICAR CORREO
        sql_verificar = """
        SELECT *
        FROM usuarios
        WHERE correo = %s
        """

        cursor.execute(sql_verificar, (correo,))

        usuario_existente = cursor.fetchone()

        if usuario_existente:
            return "Este correo ya está registrado"

        # INSERTAR USUARIO
        sql = """
        INSERT INTO usuarios(nombre, correo, password)
        VALUES(%s,%s,%s)
        """

        valores = (nombre, correo, password)

        cursor.execute(sql, valores)

        conexion.commit()

        return redirect('/login')

    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)