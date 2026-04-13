from __future__ import annotations

import argparse
import csv
import unicodedata
from datetime import datetime
from pathlib import Path

BASE_CSV = Path(r"C:\Users\antoniogc\Downloads\votacao_secao_2024_CE")


def normalizar(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return " ".join(sem_acento.lower().strip().split())


def resolver_csv() -> Path:
    for nome in [
        "votacao_secao_2024_CE.csv",
        "votacao_secao_2024_CE - Copia.csv",
    ]:
        p = BASE_CSV / nome
        if p.exists():
            return p

    candidatos = sorted(BASE_CSV.glob("*.csv")) if BASE_CSV.exists() else []
    if candidatos:
        return candidatos[0]

    raise FileNotFoundError(f"Nenhum CSV encontrado em: {BASE_CSV}")


def detectar_formato(caminho: Path) -> tuple[str, str]:
    for enc in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
        try:
            with caminho.open("r", encoding=enc, newline="") as f:
                amostra = f.read(4096)
            if not amostra.strip():
                raise ValueError("Arquivo vazio.")
            try:
                delimitador = csv.Sniffer().sniff(amostra, delimiters=";,\t").delimiter
            except csv.Error:
                delimitador = ";"
            return enc, delimitador
        except UnicodeDecodeError:
            continue
    raise ValueError("Nao foi possivel detectar a codificacao do arquivo.")


def coluna_municipio(campos: list[str]) -> str:
    prioridade = ["NM_MUNICIPIO", "MUNICIPIO", "NOME_MUNICIPIO"]
    for col in prioridade:
        if col in campos:
            return col
    for col in campos:
        if "municipio" in normalizar(col):
            return col
    raise ValueError(f"Coluna de municipio nao encontrada. Colunas disponiveis: {campos}")


def exportar(municipio: str) -> Path:
    caminho = resolver_csv()
    enc, delim = detectar_formato(caminho)
    alvo = normalizar(municipio)
    sufixo = alvo.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = BASE_CSV / f"votacao_secao_2024_CE_{sufixo}_{timestamp}.csv"

    with caminho.open("r", encoding=enc, newline="") as origem:
        leitor = csv.DictReader(origem, delimiter=delim)
        col_mun = coluna_municipio(leitor.fieldnames or [])

        with saida.open("w", encoding="utf-8", newline="") as destino:
            escritor = csv.DictWriter(destino, fieldnames=leitor.fieldnames, delimiter=delim)
            escritor.writeheader()
            total = sum(
                1 for linha in leitor
                if normalizar(linha.get(col_mun, "")) == alvo
                and not escritor.writerow(linha)
            )

    print(f"Exportado: {saida}")
    print(f"Total de registros: {total}")
    return saida


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Exporta registros de votacao filtrados por municipio."
    )
    parser.add_argument(
        "municipio",
        nargs="?",
        default="Itapipoca",
        help="Nome do municipio (padrao: Itapipoca)",
    )
    args = parser.parse_args()
    exportar(args.municipio)
