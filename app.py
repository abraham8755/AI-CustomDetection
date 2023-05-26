from flask import Flask, render_template, request
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
        file.save(file_path)
        message = 'Resim yüklendi.'
        run_python_code(file_path)  # Python kodunu çalıştır
        result = read_result_file()  # Sonuç dosyasını oku
    else:
        message = 'Resim yüklenemedi.'
        result = None

    return render_template('index.html', message=message, result=result)

def run_python_code(file_path):
    # Çalıştırmak istediğiniz Python kodunun dosya adını ve parametrelerini belirtin
    python_script = '100epochs.py'
    script_args = [file_path]

    # Komutu oluşturun
    command = ['python', python_script] + script_args

    # Komutu çalıştırın
    subprocess.run(command)

def read_result_file():
    result_file = 'eslesen_veriler.txt'
    result = None

    try:
        with open(result_file, 'r', encoding='UTF-8') as file:
            result = file.read()
    except FileNotFoundError:
        pass

    return result

if __name__ == '__main__':
    app.run(debug=True)