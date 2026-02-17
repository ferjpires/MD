# exercicio3_paginacao.py
import sys
import os
import json
import random
import time

import pandas as pd
from bs4 import BeautifulSoup

from utils import ensure_dados_dir, requisicao_segura, extrair_livros

OUT_DIR = ensure_dados_dir()
OUT_FILE = f"{OUT_DIR}/exercicio3_output.txt"

url_base = "http://books.toscrape.com/catalogue/page-{}.html"

todos_livros = []
pagina = 1

with open(OUT_FILE, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f

    print("#######################################################################")
    print("# Exercício 3 - Paginação / Crawling (BooksToScrape)")
    print("#######################################################################\n")

    while True:
        url = url_base.format(pagina)
        print(f"\n==================== Página {pagina} ====================")
        print("URL:", url)

        resp = requisicao_segura(url, timeout=15, tentativas=3)
        if resp is None:
            print("Sem resposta (404/fim ou erro definitivo). Terminar.")
            break

        soup = BeautifulSoup(resp.text, "lxml")
        livros = extrair_livros(soup)

        if not livros:
            print("Nenhum livro encontrado. Terminar.")
            break

        print(f"Livros extraídos nesta página: {len(livros)}")

        for i, l in enumerate(livros, start=1):
            print(f"\nLivro {i}:")
            print("  Título:", l["titulo"])
            print("  Preço:", l["preco"])
            print("  Disponível:", l["disponibilidade"])
            print("  Rating:", l["rating"])
            print("  URL (relativa):", l["url_relativa"])

        todos_livros.extend(livros)
        pagina += 1

        delay = random.uniform(1, 3)
        print(f"\nDelay ético: {delay:.2f}s")
        time.sleep(delay)

    print("\n#######################################################################")
    print("# Resumo final")
    print("#######################################################################\n")
    print("Total de livros extraídos:", len(todos_livros))

    df = pd.DataFrame(todos_livros)

    csv_path = os.path.join(OUT_DIR, "books.csv")
    json_path = os.path.join(OUT_DIR, "books.json")

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print("CSV gravado em:", csv_path)
    print("JSON gravado em:", json_path)

    if len(df) > 0:
        mais_caro = df.loc[df["preco"].idxmax()]
        print("\nLivro mais caro:")
        print(json.dumps(mais_caro.to_dict(), ensure_ascii=False, indent=2))

        disponiveis = int(df["disponibilidade"].sum())
        print("\nQuantos disponíveis:", disponiveis)

        dist = df["rating"].value_counts().sort_index()
        print("\nDistribuição ratings:")
        for rating, count in dist.items():
            print(f"  {rating}: {count}")

    sys.stdout = original_stdout

print(f"[OK] Output gravado em: {OUT_FILE}")
print(f"[OK] CSV/JSON em: {OUT_DIR}/")
