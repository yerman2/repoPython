# getProducts.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import pandas as pd
import requests
import json

app = Flask(__name__)

def get_file_content(token):
    url = f'https://apiv2.infortisa.com/api/Tarifa/GetFile?user={token}'
    response = requests.get(url)

    if response.status_code == 200:
        file_path = os.path.join('tarifas', 'TARIFAS.CSV')
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # Verificar si el archivo existe después de la descarga
        if os.path.exists(file_path):
            print("Archivo descargado correctamente en la carpeta 'tarifas'.")
            return file_path
        else:
            print("Error: El archivo no se encuentra después de la descarga.")
            return None
    else:
        print(f"Error al descargar el archivo. Código de estado: {response.status_code}")
        print("Error: El archivo no se descargó correctamente.")
        return None

def increase_prices():
    file_path = os.path.join('tarifas', 'TARIFAS.CSV')
    datos = pd.read_csv(file_path, sep=';', encoding='latin-1')

    # Increase the prices by 25%
    datos['PRECIO'] = pd.to_numeric(datos['PRECIO'].str.replace(',', '.'), errors='coerce')
    datos['PRECIO_AUMENTADO'] = datos['PRECIO'] * 1.25
    datos['PRECIO_AUMENTADO'] = pd.to_numeric(datos['PRECIO_AUMENTADO'], errors='coerce').round(2)

    items_list = []
    for index, row in datos.iterrows():
        item = {
            'name': row['TITULO'],
            'description': row['TITULO'],
            'sales-price': row['PRECIO_AUMENTADO']
        }
        items_list.append(item)

    return items_list

def save_to_json(items_list):
    with open('result.json', 'w') as json_file:
        json.dump(items_list, json_file)

if __name__ == "__main__":
    app.run(debug=True)
