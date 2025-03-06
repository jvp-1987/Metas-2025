# Backend en Python (Flask) para IAAPS 2025
from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Endpoint para subir archivos
@app.route('/api/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Formato de archivo no soportado, debe ser .xlsx'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # Procesar archivo y calcular indicadores
        data = pd.read_excel(file_path)
        indicadores = calcular_indicadores(data)
        return jsonify(indicadores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Función para calcular indicadores detallados

def calcular_indicadores(df):
    resultados = []
    for index, row in df.iterrows():
        try:
            meta = row['Meta']
            objetivo = row['Objetivo'] if row['Objetivo'] != 0 else 1  # Evitar división por cero
            cumplimiento = (row['Actual'] / objetivo) * 100
            estado = "Cumplido" if cumplimiento >= 100 else ("En Riesgo" if cumplimiento >= 75 else "No Cumplido")
            resultados.append({
                'meta': meta,
                'cumplimiento': round(cumplimiento, 2),
                'estado': estado
            })
        except KeyError:
            return {'error': 'Columnas faltantes en el archivo'}, 400
        except Exception as e:
            return {'error': str(e)}, 500
    return resultados

if __name__ == "__main__":
    app.run(debug=True)
