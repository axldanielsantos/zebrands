import json
import boto3
import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime


def lambda_handler(event, context):
    # TODO implement

    def get_product_price(soup_page):
        price_element = (
            soup_page.find("div", {"class": "ui-pdp-price__main-container"})
            .find("div", {"class": "ui-pdp-price__second-line"})
            .find("span", {"class": "andes-money-amount__fraction"})
        )
        price = price_element.text.replace(",", "")
        return price

    def get_product_name(soup_page):
        name_element = soup_page.find(
            "div", {"class": "ui-pdp-header__title-container"}
        ).find("h1", {"class": "ui-pdp-title"})
        return name_element.text

    def get_product_availability(soup_page):
        availability = soup_page.find("p", {"class": "ui-pdp-stock-information__title"})
        return availability.text

    def get_product_characteristics(soup_page):
        characteristics_table = soup_page.find("table", {"class": "andes-table"})
        return [
            {tr.find("th").text: tr.find("td").text}
            for tr in characteristics_table.find_all("tr")
        ]

    def get_page_product(url):
        product = get_request_page(url)
        if product["status_code"] == 200:
            soup_page = product["content"]
            product_price = get_product_price(soup_page)
            product_name = get_product_name(soup_page)
            product_availability = get_product_availability(soup_page)
            product_characteristics = get_product_characteristics(soup_page)
            return {
                "product_price": product_price,
                "product_name": product_name,
                "product_availability": product_availability,
                "brand": product_characteristics[0]["Marca"],
                "model": product_characteristics[1]["Modelo"],
                "size": product_characteristics[2]["Tamaño del colchón"],
            }
        else:
            print(request_page)

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

    URL_MERCADO_LIBRE = "https://www.mercadolibre.com.mx"

    request_page = get_request_page(
        f"{URL_MERCADO_LIBRE}/colchon-luuna-memory-foam-individual-hecho-en-mexico/p/MLM15569488"
    )
    if request_page["status_code"] == 200:
        elements = request_page["content"].find_all(
            "div", {"class": "ui-pdp-variations__picker"}
        )[0]
        count = 0
        df_list = []
        for product in elements:
            if count > 0:  # skip first row
                try:
                    url_product_size = f"{URL_MERCADO_LIBRE}{product.attrs['href']}"
                    print(url_product_size)
                    product_id = url_product_size.split("/")[-1].split("?")[0]
                    ecommerce_platform = "Mercado Libre"
                    scraper_date = datetime.now()
                    product = get_page_product(url_product_size)
                    df = pd.DataFrame([product])
                    df.insert(0, "product_id", product_id)
                    df.insert(1, "ecommerce_platform", ecommerce_platform)
                    df.insert(2, "scraper_date", scraper_date)
                    print(df)
                    df_list.append(df)
                except Exception as a:
                    print(a)
            count += 1
        df_concat = pd.concat(df_list)
        bucket_name = "zebrands"
        file_name = "data.csv"

        s3 = boto3.client("s3")

        try:
            response = s3.head_object(Bucket=bucket_name, Key=file_name)
            file_exists = True
        except:
            file_exists = False

        if file_exists:
            # Descargar el archivo CSV existente desde S3
            obj = s3.get_object(Bucket=bucket_name, Key=file_name)
            df_existing = pd.read_csv(obj["Body"])

            # Realizar el append de los nuevos datos al DataFrame existente
            df_appended = pd.concat([df_existing, df_concat], ignore_index=True)
        else:
            df_appended = pd.concat([df_concat], ignore_index=True)

        csv_buffer = StringIO()
        df_appended.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=file_name)

    else:
        print(request_page)

    return {"statusCode": 200, "body": json.dumps("Successfully!")}
lambda_handler(1,2)