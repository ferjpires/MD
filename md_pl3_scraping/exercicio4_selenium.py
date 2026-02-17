# exercicio4_selenium.py
import sys
import os
import json
import time
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from utils import ensure_dados_dir

OUT_DIR = ensure_dados_dir()
OUT_FILE = f"{OUT_DIR}/exercicio4_output.txt"
OUT_JSON = f"{OUT_DIR}/quotes_js.json"

URL = "http://quotes.toscrape.com/js/"


def criar_driver_headless() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def extrair_quotes_selenium(driver: webdriver.Chrome) -> List[Dict[str, Any]]:
    quotes = driver.find_elements(By.CLASS_NAME, "quote")
    dados = []
    for q in quotes:
        texto = q.find_element(By.CLASS_NAME, "text").text
        autor = q.find_element(By.CLASS_NAME, "author").text
        tags = [t.text for t in q.find_elements(By.CSS_SELECTOR, ".tags a.tag")]
        dados.append({"texto": texto, "autor": autor, "tags": tags})
    return dados


with open(OUT_FILE, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f

    print("#######################################################################")
    print("# Exercício 4 - Selenium (site com JS)")
    print("#######################################################################\n")

    #######################################################################
    # 4.2 Selenium puro
    #######################################################################
    print("4.2 - Extração com Selenium (puro)\n")
    driver = criar_driver_headless()
    try:
        driver.get(URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))

        dados_42 = extrair_quotes_selenium(driver)
        print("Total quotes extraídas:", len(dados_42))
        for i, q in enumerate(dados_42, start=1):
            print(f"\n--- Quote #{i} ---")
            print("Texto:", q["texto"])
            print("Autor:", q["autor"])
            print("Tags:", q["tags"])

    finally:
        driver.quit()

    #######################################################################
    # 4.3 Híbrido (Selenium + BeautifulSoup)
    #######################################################################
    print("\n\n4.3 - Extração híbrida (page_source -> BeautifulSoup)\n")
    driver = criar_driver_headless()
    try:
        driver.get(URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))

        soup = BeautifulSoup(driver.page_source, "lxml")
        dados_43 = []
        for q in soup.select("div.quote"):
            texto = q.select_one("span.text").get_text(strip=True)
            autor = q.select_one("small.author").get_text(strip=True)
            tags = [t.get_text(strip=True) for t in q.select(".tags a.tag")]
            dados_43.append({"texto": texto, "autor": autor, "tags": tags})

        print("Total quotes extraídas:", len(dados_43))
        for i, q in enumerate(dados_43, start=1):
            print(f"\n--- Quote #{i} ---")
            print("Texto:", q["texto"])
            print("Autor:", q["autor"])
            print("Tags:", q["tags"])

    finally:
        driver.quit()

    #######################################################################
    # 4.4 Paginação
    #######################################################################
    print("\n\n4.4 - Paginação (Next)\n")
    driver = criar_driver_headless()
    todas: List[Dict[str, Any]] = []

    try:
        driver.get(URL)

        page = 1
        while True:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))
            page_quotes = extrair_quotes_selenium(driver)

            print(f"\n==================== Página JS {page} ====================")
            print("Quotes nesta página:", len(page_quotes))

            for i, q in enumerate(page_quotes, start=1):
                print(f"\n--- Quote #{i} (página {page}) ---")
                print("Texto:", q["texto"])
                print("Autor:", q["autor"])
                print("Tags:", q["tags"])

            todas.extend(page_quotes)

            next_links = driver.find_elements(By.CSS_SELECTOR, "li.next > a")
            if not next_links:
                print("\nNão existe botão Next. Terminar paginação.")
                break

            next_links[0].click()
            time.sleep(1.2)
            page += 1

    finally:
        driver.quit()

    print("\n#######################################################################")
    print("# Resumo final")
    print("#######################################################################\n")
    print("Total de citações apanhadas na paginação:", len(todas))

    # Guardar JSON com tudo
    with open(OUT_JSON, "w", encoding="utf-8") as jf:
        json.dump(todas, jf, ensure_ascii=False, indent=2)

    print("JSON gravado em:", OUT_JSON)

    sys.stdout = original_stdout

print(f"[OK] Output gravado em: {OUT_FILE}")
print(f"[OK] JSON gravado em: {OUT_JSON}")
