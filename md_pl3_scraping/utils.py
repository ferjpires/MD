# utils.py
from __future__ import annotations

import os
import time
from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}

RATING_MAP: Dict[str, int] = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def ensure_dados_dir() -> str:
    """Garante que a pasta 'dados/' existe e devolve o caminho."""
    out_dir = "dados"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


# ---------------------------------------------------------------------------
# Ex. 1.3 - Requisição segura
# ---------------------------------------------------------------------------

def requisicao_segura(
    url: str,
    *,
    timeout: int = 10,
    tentativas: int = 3,
    session: Optional[requests.Session] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Optional[requests.Response]:
    """GET com re-tentativas e backoff.

    Re-tenta em:
      - erros de rede (Timeout/ConnectionError)
      - HTTP 5xx
      - HTTP 429

    Não re-tenta em 4xx (exceto 429) porque normalmente é erro definitivo.

    Retorna Response em sucesso, ou None em falha/erro definitivo.
    """
    sess = session or requests.Session()
    hdrs = dict(DEFAULT_HEADERS)
    if headers:
        hdrs.update(headers)

    resp: Optional[requests.Response] = None

    for i in range(1, tentativas + 1):
        try:
            resp = sess.get(url, headers=hdrs, timeout=timeout)
            resp.encoding = "utf-8"

            # 4xx definitivo (exceto 429)
            if 400 <= resp.status_code < 500 and resp.status_code != 429:
                return None

            # 429 e 5xx vão levantar e cair no except para repetir
            resp.raise_for_status()
            return resp

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            # erro de rede -> repetir
            pass
        except requests.exceptions.HTTPError:
            # aqui tipicamente 429 ou 5xx -> repetir
            pass

        time.sleep(1.5 * i)

    return None


# ---------------------------------------------------------------------------
# Ex. 3 - parsing Books
# ---------------------------------------------------------------------------

def extrair_livros(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extrai lista de livros de uma página do books.toscrape.com"""
    livros: List[Dict[str, Any]] = []

    for art in soup.select("article.product_pod"):
        a = art.select_one("h3 > a")
        titulo = (a.get("title") or a.get_text(strip=True)) if a else ""
        url_relativa = a.get("href") if a else ""

        preco_el = art.select_one("p.price_color")
        preco_txt = preco_el.get_text(strip=True) if preco_el else "£0.00"
        preco_limpo = (
            preco_txt
            .replace("Â", "")
            .replace("£", "")
            .strip()
        )
        preco = float(preco_limpo)

        instock_el = art.select_one("p.instock")
        instock_txt = instock_el.get_text(" ", strip=True).lower() if instock_el else ""
        disponibilidade = "in stock" in instock_txt

        rating_p = art.select_one("p.star-rating")
        rating = None
        if rating_p:
            for c in rating_p.get("class", []):
                if c in RATING_MAP:
                    rating = RATING_MAP[c]
                    break

        livros.append(
            {
                "titulo": titulo,
                "preco": preco,
                "disponibilidade": disponibilidade,
                "rating": rating,
                "url_relativa": url_relativa,
            }
        )

    return livros
