from flask import Flask, request, render_template, redirect, url_for, session
import requests
import logging

app = Flask(__name__)
app.secret_key = 'my_secret_key'
@app.route('/')
def Mostrarlogin():
    # Obtener el mensaje de error o éxito si existe
    error_message = request.args.get('error')
    success_message = session.pop('message', None)  # Obtener mensaje de éxito de la sesión, si existe
    return render_template('login.html', error_message=error_message, success_message=success_message)

@app.route('/login', methods=['POST'])
def login():
    Login = request.form.get('Login')
    Contrasenia = request.form.get('Contrasenia')

    external_api_url = 'https://altis-ws.grupoagencia.com:444/JAgencia/JAgencia.asmx/wsLogin'
    payload = {
        'Login': Login,
        'Contrasenia': Contrasenia
    }

    try:
        response = requests.post(external_api_url, data=payload)
        response_json = response.json()

        if response.status_code == 200 and response_json.get('result') == 0:
            session['ID_Session'] = response_json.get('ID_Session')
            return redirect(url_for('index'))  # Redirige a la ruta 'index'
        else:
            return redirect(url_for('Mostrarlogin') + '?error=Contraseña incorrecta')
    except requests.RequestException as e:
        logging.error(f'Error al enviar solicitud: {e}')
        return redirect(url_for('Mostrarlogin') + '?error=Error de conexión')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/api1.html')
def api1():
    url = 'https://jsonplaceholder.typicode.com/todos/1'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        data = {'error': 'No se pudieron obtener los datos'}

    return render_template('api1.html', data=data)

@app.route('/api2.html')
def api2():
    url = 'https://jsonplaceholder.typicode.com/todos'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        data = {'error': 'No se pudieron obtener los datos'}

    return render_template('api2.html', data=data)



@app.route('/logout', methods=['POST'])
def logout():
    ID_Session = session.get('ID_Session')

    if not ID_Session:
        session['message'] = 'No hay sesión activa para cerrar'
        return redirect(url_for('Mostrarlogin'))

    external_api_url = 'https://altis-ws.grupoagencia.com:444/JAgencia/JAgencia.asmx/wsLogOut'
    payload = {
        'ID_Session': ID_Session
    }

    try:
        response = requests.post(external_api_url, data=payload)

        if response.status_code == 200:
            response_json = response.json()
            logging.info(f'{response_json}')
            if response_json.get('result') == 0:
                session.pop('ID_Session', None)
                session['message'] = 'Sesión cerrada con éxito'
                return redirect(url_for('Mostrarlogin'))
            else:
                session['message'] = 'Error al cerrar sesión'
                return redirect(url_for('Mostrarlogin'))
        else:
            session['message'] = 'Error al cerrar sesión'
            return redirect(url_for('Mostrarlogin'))
    except requests.RequestException as e:
        logging.error(f'Error al enviar solicitud de logout: {e}')
        session['message'] = 'Error de conexión'
        return redirect(url_for('Mostrarlogin'))

if __name__ == '__main__':
    app.run(debug=True)
