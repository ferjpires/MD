# exercicio1_http.py
import sys
import json
import requests

from utils import DEFAULT_HEADERS, ensure_dados_dir, requisicao_segura

OUT_DIR = ensure_dados_dir()
OUT_FILE = f"{OUT_DIR}/exercicio1_output.txt"

url = "http://httpbin.org/get"

with open(OUT_FILE, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f

    print("#######################################################################")
    print("# Exercício 1 - HTTP")
    print("#######################################################################\n")

    print("URL:", url)
    print("Headers enviados:", json.dumps(DEFAULT_HEADERS, ensure_ascii=False, indent=2))

    with requests.Session() as sess:
        resp = requisicao_segura(url, timeout=10, tentativas=3, session=sess, headers=DEFAULT_HEADERS)

    if resp is None:
        print("\nFalhou a requisição (erro definitivo ou tentativas esgotadas).")
        sys.stdout = original_stdout
        raise SystemExit(f"Falhou. Vê o ficheiro: {OUT_FILE}")

    print("\nStatus code:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))

    data = resp.json()
    print("\nJSON completo devolvido pelo httpbin:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    origin = data.get("origin", "")
    ip = origin.split(",")[0].strip() if isinstance(origin, str) else origin
    print("\nIP do cliente (origin):", origin)
    print("IP (normalizado):", ip)

    received_headers = data.get("headers", {}) or {}
    print("\nHeaders recebidos pelo servidor (httpbin):")
    print(json.dumps(received_headers, ensure_ascii=False, indent=2))

    print("\nValidação de headers:")
    print("User-Agent recebido igual ao enviado? ->", received_headers.get("User-Agent") == DEFAULT_HEADERS["User-Agent"])
    print(
        "Accept-Language recebido igual ao enviado? ->",
        received_headers.get("Accept-Language") == DEFAULT_HEADERS["Accept-Language"],
    )

    sys.stdout = original_stdout

print(f"[OK] Output gravado em: {OUT_FILE}")
