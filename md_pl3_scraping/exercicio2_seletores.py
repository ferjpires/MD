# exercicio2_seletores.py
import sys
import requests
from bs4 import BeautifulSoup

from utils import ensure_dados_dir

OUT_DIR = ensure_dados_dir()
OUT_FILE = f"{OUT_DIR}/exercicio2_output.txt"

url = "http://quotes.toscrape.com"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "lxml")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f

    print("#######################################################################")
    print("# Exercício 2 - Seletores (BeautifulSoup)")
    print("#######################################################################\n")

    #######################################################################
    # Questão 2.1 - find() e find_all()
    #######################################################################
    print("2.1 - Extração com find() e find_all()\n")

    print("Todas as citações:\n")
    for quote in soup.find_all("div", class_="quote"):
        quote_text = quote.find("span", class_="text")
        if quote_text:
            print(quote_text.get_text())

    print("\n\nTodos os autores:\n")
    for author in soup.find_all("small", class_="author"):
        print(author.get_text())

    print("\n\nTodas as tags:\n")
    for tag in soup.find_all("a", class_="tag"):
        print(tag.get_text())

    print("\n\nO primeiro autor da página:")
    first_author = soup.find("small", class_="author")
    print(first_author.get_text() if first_author else None)

    print("\n\nA primeira citação:")
    first_quote = soup.find("div", class_="quote")
    first_quote_text = first_quote.find("span", class_="text") if first_quote else None
    print(first_quote_text.get_text() if first_quote_text else None)

    print("\n\nO link 'Next' (se existir):")
    next_li = soup.find("li", class_="next")
    next_a = next_li.find("a") if next_li else None
    print(next_a.get("href") if next_a else None)

    #######################################################################
    # Questão 2.2 - select() e select_one()
    #######################################################################
    print("\n\n\n2.2 - Extração com select() e select_one()\n")

    print("Todas as tags:\n")
    for tag in soup.select("a.tag"):
        print(tag.get_text())

    print("\n\nTodas as citações:\n")
    for quote_text in soup.select("div.quote span.text"):
        print(quote_text.get_text())

    print("\n\nTodos os autores:\n")
    for author in soup.select("small.author"):
        print(author.get_text())

    print("\n\nO primeiro autor da página:")
    first_author_css = soup.select_one("small.author")
    print(first_author_css.get_text() if first_author_css else None)

    print("\n\nA primeira citação:")
    first_quote_css = soup.select_one("div.quote span.text")
    print(first_quote_css.get_text() if first_quote_css else None)

    print("\n\nO link 'Next' (se existir):")
    next_a_css = soup.select_one("li.next > a")
    print(next_a_css.get("href") if next_a_css else None)

    print("\n\nTodas as tags dentro de cada citação (texto das tags):")
    for i, quote in enumerate(soup.select("div.quote"), start=1):
        tags = [t.get_text(strip=True) for t in quote.select(".tags a.tag")]
        print(f"Citação #{i} -> {tags}")

    print("\n\nO autor da primeira citação (hierarquia CSS):")
    first_quote_author = soup.select_one("div.quote small.author")
    print(first_quote_author.get_text() if first_quote_author else None)

    #######################################################################
    # Questão 2.3 - Atributos
    #######################################################################
    print("\n\n\n2.3 - Extração de atributos\n")

    for i, quote in enumerate(soup.select("div.quote"), start=1):
        texto = quote.select_one("span.text").get_text(strip=True)
        autor = quote.select_one("small.author").get_text(strip=True)

        # Mais robusto: link que começa por /author/
        about_link = quote.select_one('a[href^="/author/"]')
        about_href = about_link.get("href") if about_link else None

        tags = quote.select(".tags a.tag")
        num_tags = len(tags)

        classes = quote.get("class", [])

        print(f"\n--- Citação #{i} ---")
        print("Texto:", texto)
        print("Autor:", autor)
        print("About href:", about_href)
        print("Nº tags:", num_tags)
        print("Classes do div.quote:", classes)

    sys.stdout = original_stdout

print(f"[OK] Output gravado em: {OUT_FILE}")
