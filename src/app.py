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
    """Endpoint para obtener todas las citas con sus autores y etiquetas."""
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            
            # Consulta para obtener citas con sus etiquetas
            cursor.execute("""
                SELECT q.quote_text, q.author, GROUP_CONCAT(t.tag_name) as tags
                FROM quotes q
                LEFT JOIN quote_tags qt ON q.id = qt.quote_id
                LEFT JOIN tags t ON qt.tag_id = t.id
                GROUP BY q.id
            """)
            
            # Procesar resultados y construir respuesta
            quotes = [
                {
                    "quote": row["quote_text"],
                    "author": row["author"],
                    "tags": row["tags"].split(',') if row["tags"] else []
                } 
                for row in cursor.fetchall()
            ]
            
            return jsonify(quotes)
            
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@app.route('/tags', methods=['GET'])
def get_tags_count():
    """Endpoint para contar cuántas citas hay asociadas a cada etiqueta."""
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            
            # Consulta para contar citas por etiqueta
            cursor.execute("""
                SELECT 
                    t.tag_name AS etiqueta,
                    COUNT(q.id) AS total_citas
                FROM tags t
                LEFT JOIN quote_tags qt ON t.id = qt.tag_id
                LEFT JOIN quotes q ON qt.quote_id = q.id
                GROUP BY t.tag_name
            """)
            
            # Procesar resultados
            stats = [
                {"etiqueta": row["etiqueta"], "total_citas": row["total_citas"]} 
                for row in cursor.fetchall()
            ]
            
            return jsonify({"estadisticas_etiquetas": stats})
            
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)