import gc
import time
from flask import Flask, render_template, request
import requests

from getProducts import get_file_content, increase_prices

app = Flask(__name__)

def send_data_to_api(api_key, data):
    post_url = 'https://app.stelorder.com/app/products'

    for item in data:
        print(f"Procesando item: {item}")

        post_data = {
            'name': item['name'],
            'description': item['description'],
            'sales-price': item['sales-price']
        }

        post_headers = {
            'Content-Type': 'application/json',
            'APIKEY': api_key
        }

        response = requests.post(post_url, json=post_data, headers=post_headers)

        if response.status_code == 200:
            print(f"Producto {item['name']} enviado correctamente.")
        else:
            print(f"Error al enviar el producto {item['name']}. Código de estado: {response.status_code}")

def process_file_in_batches(api_key, items_list, batch_size=20, timeout_between_batches=30):
    for i in range(0, len(items_list), batch_size):
        batch = items_list[i:i+batch_size]
        send_data_to_api(api_key, batch)

        # Liberar memoria después de procesar cada lote
        del batch
        gc.collect()

        time.sleep(timeout_between_batches)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-file', methods=['POST'])
def get_file():
    token = request.form.get('token_get')
    file_path = get_file_content(token)
    
    if file_path:
        return f"Archivo descargado correctamente en la carpeta 'tarifas'."
    else:
        return "Error al descargar el archivo. Verifica el token proporcionado o inténtalo de nuevo más tarde.", 400

@app.route('/process-file', methods=['POST'])
def process_file():
    print("Iniciando procesamiento del archivo.")
    token = request.form['api_key']
    get_file_content(token)
    items_list = increase_prices()

    api_key = request.form.get('api_key')
    if not api_key:
        return "API key no proporcionada en el formulario.", 400

    print(f"API key: {api_key}")

    # Procesar por bloques de 100
    process_file_in_batches(api_key, items_list, batch_size=50)

    print("Finalizando procesamiento del archivo.")
    return "Datos procesados y enviados a la URL de productos."

if __name__ == '__main__':
    app.run(debug=True)  # Ajusta el valor de timeout según tus necesidades
