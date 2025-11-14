#!/usr/bin/env python3
"""
API endpoint para exclusão de critérios
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.prompt import GeneralCriteria

app = Flask(__name__)
# Habilitar CORS para todas as origens
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/delete-criterion/<criterion_id>', methods=['POST'])
def delete_criterion_api(criterion_id):
    """API endpoint para deletar um critério"""
    try:
        # Extrair o ID numérico
        actual_id = int(criterion_id.replace("criteria_", ""))
    except ValueError:
        return jsonify({"error": "Invalid criteria ID format"}), 400

    db = SessionLocal()
    try:
        # Encontrar o critério
        criterion = db.query(GeneralCriteria).filter(
            GeneralCriteria.id == actual_id
        ).first()

        if not criterion:
            return jsonify({"error": f"Criterion not found with ID {actual_id}"}), 404

        # Deletar o critério
        db.delete(criterion)
        db.commit()

        return jsonify({
            "message": "Criterion deleted successfully",
            "deleted_id": actual_id
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='localhost', port=8001, debug=True)