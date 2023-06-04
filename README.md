# Zebrands scraper

Scraper Mercado Libre para extraer precios, disponibilidad y otros atributos

- Paso 1: Clonar el proyecto
    - ```git clone``` https://github.com/axldanielsantos/zebrands
    - ```cd zebrands```
- Paso 2: Crea y activa el entorno virtual
    - ```virtualenv venv --python=python3.10```
    - ```source ./venv/bin/activate```
- Paso 3: Intalar dependencias
    - ```pip3 install -r requirements.txt```
- Paso 4: Ejecutar el script
    - ```python3 handler_requests.py```
    - ```python3 handler_selenium.py```
- Paso 5: Revisar los .csv ```requests_file.csv``` y ```selenium_file.csv```