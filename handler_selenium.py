import os
import requests
import pandas as pd
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup
from datetime import datetime

driver = webdriver.Chrome(ChromeDriverManager().install())


URL_MERCADO_LIBRE = "https://www.mercadolibre.com.mx"


def get_request_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    req = requests.get(url, headers=headers)
    return {
        "status_code": req.status_code,
        "content": BeautifulSoup(req.content, "html.parser")
        if req.status_code == 200
        else req.content,
    }


request_page = get_request_page(
    f"{URL_MERCADO_LIBRE}/colchon-luuna-memory-foam-individual-hecho-en-mexico/p/MLM15569488"
)
if request_page["status_code"] == 200:
    elements = request_page["content"].find_all(
        "div", {"class": "ui-pdp-variations__picker"}
    )[0]
    count = 0
    for product in elements:
        if count > 0:  # skip first row
            url_product_size = f"{URL_MERCADO_LIBRE}{product.attrs['href']}"
            product_id = url_product_size.split("/")[-1].split("?")[0]
            ecommerce_platform = "Mercado Libre"
            scraper_date = datetime.now()
            print(url_product_size)
            driver.get(url_product_size)

            preloaded_state = driver.execute_script(
                "return JSON.stringify(window.__PRELOADED_STATE__)"
            )
            res = json.loads(preloaded_state)  # convert to json

            # we access to keys and values like json format
            base_initial = res["initialState"]["components"]  # base initial
            stock = base_initial["available_quantity"]["quantity_selector"][
                "available_quantity"
            ]
            availability_text = base_initial["stock_information"]["title"]["text"]
            price = base_initial["price"]["price"]["value"]
            name = res["initialState"]["schema"][0]["name"]

            data = base_initial["highlighted_specs_attrs"]["components"]
            filtered_data = list(
                filter(lambda obj: obj.get("id") == "technical_specifications", data)
            )
            attributes_values = [
                attr
                for obj in filtered_data[0]["specs"]
                for attr in obj.get("attributes", [])
            ]

            df = pd.DataFrame(attributes_values)
            df = df.set_index("id").T.reset_index(drop=True)
            df.insert(0, "product_id", product_id)
            df.insert(1, "product_name", name)
            df.insert(2, "stock", stock)
            df.insert(3, "price", price)
            df.insert(4, "ecommerce_platform", ecommerce_platform)
            df.insert(5, "scraper_date", scraper_date)
            df.insert(6, "availability_text", availability_text)
            df = df.rename(
                columns={
                    "Marca": "brand",
                    "Modelo": "model",
                    "Tamaño del colchón": "size",
                    "Ancho x Largo x Altura": "wxlxh",
                    "Tipo de relleno": "padding_type",
                    "Composición de la tela": "material",
                    "Con memory foam": "with_memory_foam",
                    "Está envasado al vacío": "is_vacuum_packed",
                    "Es infantil": "is_childish",
                    "Es one side": "is_one_side",
                    "Con marco perimetral": "with_perimeter_frame",
                }
            )

            if count == 1:
                if os.stat("selenium_file.csv").st_size > 0:
                    df.to_csv("selenium_file.csv", mode="a", header=False, index=False)
                else:
                    df.to_csv("selenium_file.csv", index=False)
            else:
                df.to_csv("selenium_file.csv", mode="a", header=False, index=False)
        count += 1
else:
    print(request_page)