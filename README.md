# Sistema de Scraping y API para Quotes

Este proyecto automatiza la extracción de citas, autores y etiquetas de [Quotes to Scrape](https://quotes.toscrape.com/), almacena los datos en una base de datos y los expone mediante una API REST. Todo el sistema se ejecuta en contenedores Docker para garantizar portabilidad.

---

## 🚀 Instalación y Ejecución

### Requisitos
- Docker y Docker Compose instalados.

### Pasos:

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/kira2222/Scraper.git && cd proyecto

2. **Ingresar a la carpeta config**

3. **Construir y levantar los contenedores**:
   ```bash
   docker-compose up 

4. **Acceder a la API**:
- Abre http://localhost:5000/quotes en tu navegador.


# 📂Estructura del Proyecto
![Logo](https://i.ibb.co/MvLgpmW/imagen-2025-03-05-191718363.png)


# 🔧Componentes Técnicos
1. **Scraping (QuoteScraper.py)**
- Tecnologías: Python, Beautiful Soup, Requests.

Funcionalidades:

- Extrae citas, autores y etiquetas.

- Guarda los datos en datos.json y una base de datos SQLite.

- Mecanismos anti-bloqueo:

- Uso de User-Agent personalizado.

- Delays entre solicitudes.

- Uso de proxys. 

2. **API (app.py)**

Endpoints:

- GET /quotes: Devuelve todas las citas.

- GET /quotes/author/{nombre}: Devuelve las citas de un autor
específico.

- Base de datos: SQLite (almacenada en data/quotes.db).

3. **Dockerización**

Contenedores:

- scraper: Ejecuta el script de scraping.

- api: Inicia el servidor Flask en el puerto 5000.

- Volúmenes: La carpeta data/ persiste los datos entre ejecuciones.



# Imagenes creadas de docker.
https://hub.docker.com/repository/docker/word2000/config_scraper/
https://hub.docker.com/repository/docker/word2000/config_api/
