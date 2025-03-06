import json
import random
import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import time
import sqlite3
from contextlib import closing
import sys
import io
from pwn import log

# Configurar salida estándar en UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URL base del sitio a scrapear
BASE_URL = "https://quotes.toscrape.com"


OUTPUT_FILE = "datos.json"


def setup_database():
    """Crea las tablas en la base de datos SQLite."""
    with closing(sqlite3.connect("/app/data/quotes.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_text TEXT NOT NULL,
                author TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quote_tags (
                quote_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY(quote_id) REFERENCES quotes(id),
                FOREIGN KEY(tag_id) REFERENCES tags(id)
            )
        """)
        conn.commit()

def save_to_database(quotes):
    """Almacena las citas en la base de datos SQLite."""
    with closing(sqlite3.connect("/app/data/quotes.db")) as conn:
        cursor = conn.cursor()
        for quote in quotes:
            # Insertar quote y autor
            cursor.execute(
                "INSERT INTO quotes (quote_text, author) VALUES (?, ?)",
                (quote['quote_text'], quote['author'])
            )
            quote_id = cursor.lastrowid
            
            # Insertar etiquetas
            for tag_name in quote['tags']:
                cursor.execute(
                    "INSERT OR IGNORE INTO tags (tag_name) VALUES (?)",
                    (tag_name,)
                )
                cursor.execute(
                    "SELECT id FROM tags WHERE tag_name = ?", (tag_name,)
                )
                tag_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO quote_tags (quote_id, tag_id) VALUES (?, ?)",
                    (quote_id, tag_id)
                )
        conn.commit()
    log.success("Datos guardados en la base de datos")


def get_random_user_agent():
    """Genera un User-Agent aleatorio para cada solicitud."""
    user_agent_rotator = UserAgent(
        software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value],
        operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    )
    return user_agent_rotator.get_random_user_agent()

def fetch_page(url):
    """Petición para la pagina"""
    for attempt in range(3):  # 3 reintentos máximo
        try:
            log.info(f"Intentando conexión proxy: {url}")
            proxies = [
                {
                    "socks4": "socks4://202.146.228.254:8088"
                },
                {
                    "socks5": "socks5://192.241.177.96:10599"
                }
]

            # Seleccionar proxy aleatorio
            proxy = random.choice(proxies)
            headers = {
                'User-Agent': get_random_user_agent(),
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/'
            }

            response = requests.get(
                url,
                headers=headers,
                proxies=proxy,
                timeout=10   # Timeout incremental
            )

            log.info(f"Solicitando {url} - Status: {response.status_code}")
            response.raise_for_status()
            
            return response.content

        except requests.exceptions.RequestException as error:
            log.warning(f"Intento {attempt + 1}/3 fallido: {str(error)}")
            time.sleep(1 + attempt)  # Espera progresiva
            continue
    
    # Último intento sin proxy
    try:
        log.info("Intentando conexión directa")
        return requests.get(url, headers=headers, timeout=15).content
    except Exception as e:
        log.error(f"Fallo definitivo: {str(e)}")
        return None

def extract_quotes_from_page(html_content):
    """Extrae las citas de una página HTML dada y devuelve una lista de diccionarios."""
    soup = BeautifulSoup(html_content, 'html.parser')
    quotes_elements = soup.find_all('div', class_='quote')

    if not quotes_elements:
        return None

    quotes_data = []
    for quote in quotes_elements:
        quote_text = quote.find('span', class_='text').get_text(strip=True)
        author = quote.find('small', class_='author').get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in quote.find('div', class_='tags').find_all('a', class_='tag')]

        quotes_data.append({
            'quote_text': quote_text,
            'author': author,
            'tags': tags
        })
    
    return quotes_data

def save_quotes_to_json(quotes, file_path):
    """Guarda las citas extraídas en un archivo JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(quotes, json_file, indent=2, ensure_ascii=False)
        log.success(f"Datos guardados en {file_path}")
    except IOError as error:
        log.failure(f"Error al escribir el archivo JSON: {error}")


def scrape_quotes():
    """Función principal para extraer todas las citas del sitio."""
    setup_database()
    all_quotes = []
    page_number = 1
    progress = log.progress("Scraping de citas")

    while True:
        page_url = f"{BASE_URL}/page/{page_number}"
        html_content = fetch_page(page_url)

        if not html_content:
            log.warning(f"No se pudo obtener contenido de {page_url}. Terminando scraping.")
            break

        quotes = extract_quotes_from_page(html_content)

        if not quotes:
            log.success(f"Scraping finalizado. Última página procesada: {page_number - 1}")
            break

        all_quotes.extend(quotes)
        progress.status(f"Procesando página {page_number}")
        page_number += 1

    save_quotes_to_json(all_quotes, OUTPUT_FILE)
    save_to_database(all_quotes)

if __name__ == "__main__":
    scrape_quotes()
