from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import qrcode

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cheie secretă pentru sesiuni

# Setăm calea de încărcare a modelelor 3D și QR codes
UPLOAD_FOLDER = '/home/drumea/Desktop/3dmodel/models'
QR_CODE_FOLDER = '/home/drumea/Desktop/3dmodel/qrcodes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_CODE_FOLDER'] = QR_CODE_FOLDER

# Asigurăm că directoarele există
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_CODE_FOLDER, exist_ok=True)

# Pagina de start (pagina de logare)
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        if session['user_type'] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user'))
    return render_template('login.html')

# Procesul de logare
@app.route('/login', methods=['POST'])
def login():
    user_type = request.form['user_type']
    
    if user_type == 'admin':  # Logare ca admin
        password = request.form['password']
        if password == 'nicu28062003':
            session['logged_in'] = True
            session['user_type'] = 'admin'
            return redirect(url_for('admin'))
        else:
            return 'Parola incorectă!', 403
    elif user_type == 'user':  # Logare ca user simplu
        session['logged_in'] = True
        session['user_type'] = 'user'
        return redirect(url_for('user'))
    
    return 'Tip de utilizator necunoscut!', 400

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_type', None)
    return redirect(url_for('index'))

# Pagina pentru utilizator simplu
@app.route('/user')
def user():
    if 'logged_in' in session and session['user_type'] == 'user':
        return render_template('user.html')  # Aici vei include scanarea QR code-ului
    return redirect(url_for('index'))

# Pagina pentru admin (încărcare STL și generare QR code)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            file = request.files['file']
            if file and file.filename.endswith('.stl'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                # Generare QR Code cu link către modelul STL
                qr = qrcode.make(f"http://localhost:5000/models/{file.filename}")
                qr_code_path = os.path.join(app.config['QR_CODE_FOLDER'], f"{file.filename}.png")
                qr.save(qr_code_path)
                return f'Model {file.filename} încărcat cu succes! Codul QR a fost generat.'
            return 'Fișier invalid!', 400
        return render_template('admin.html')
    return redirect(url_for('index'))

# Servește modelele 3D încărcate
@app.route('/models/<filename>')
def serve_model(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Servește codurile QR generate
@app.route('/qrcodes/<filename>')
def serve_qr_code(filename):
    return send_from_directory(app.config['QR_CODE_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
