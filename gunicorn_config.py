bind = '0.0.0.0:5000'  # Flask uygulamanızın çalışacağı IP adresi ve port numarası
workers = 4  # Aynı anda çalışacak işçi süreç sayısı

from waitress import serve

serve(app, host='0.0.0.0', port=8000)
