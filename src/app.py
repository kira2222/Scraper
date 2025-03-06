from flask import Flask, jsonify
import sqlite3
from contextlib import closing

app = Flask(__name__)

def get_db_connection():
    """Crea y retorna una conexión a la base de datos SQLite."""
    try:
        conn = sqlite3.connect("/app/data/quotes.db")
        conn.row_factory = sqlite3.Row  # Para acceder a los datos por nombre de columna
        return conn
    except sqlite3.Error as e:
        # Registra el error en logs en un escenario real
        raise RuntimeError(f"Error al conectar a la base de datos: {str(e)}")

@app.route('/quotes', methods=['GET'])
def get_all_quotes():
    """Endpoint para obtener todas las citas"""
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            
            # Consulta para obtener citas 
            cursor.execute("SELECT quote_text FROM quotes")
            
            # Procesar resultados y construir respuesta
            quotes = [
                {"quote": row["quote_text"]}
                for row in cursor.fetchall()
            ]
            
            return jsonify(quotes)
            
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@app.route('/quotes/author/<string:author>', methods=['GET'])
def get_quotes_by_author(author):
    """Endpoint para obtener citas de un autor específico."""
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quote_text FROM quotes WHERE author = ?", (author,))
            quotes = [
                {"quote": row["quote_text"]} 
                for row in cursor.fetchall()
            ]
            
            if not quotes:
                return jsonify({"error": "No quotes found for this author"}), 404
            
            return jsonify(quotes)
            
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
