from __future__ import annotations

import csv
from pathlib import Path


def resolver_caminho_csv() -> Path:
    """Resolve o caminho do CSV de votacao no diretorio Downloads."""
    base = Path(r"C:\Users\antoniogc\Downloads\votacao_secao_2024_CE")
    candidatos = [
        base / "votacao_secao_2024_CE.csv",
        base / "votacao_secao_2024_CE - Copia.csv",
    ]

    for candidato in candidatos:
        if candidato.exists():
            return candidato

    encontrados = sorted(base.glob("*.csv")) if base.exists() else []
    if encontrados:
        return encontrados[0]

    raise FileNotFoundError(
        "Nao encontrei o CSV em C:\\Users\\antoniogc\\Downloads\\votacao_secao_2024_CE"
    )


def detectar_formato(caminho: Path) -> tuple[str, str]:
    """Tenta detectar codificacao e delimitador de um CSV."""
    codificacoes = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]

    for cod in codificacoes:
        try:
            with caminho.open("r", encoding=cod, newline="") as f:
                amostra = f.read(4096)
                if not amostra.strip():
                    raise ValueError("Arquivo CSV vazio.")

                try:
                    dialeto = csv.Sniffer().sniff(amostra, delimiters=";,\t,")
                    delimitador = dialeto.delimiter
                except csv.Error:
                    # TSE costuma usar ';'
                    delimitador = ";"

                return cod, delimitador
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("codec", b"", 0, 1, "Nao foi possivel identificar a codificacao do arquivo.")


def ler_csv(caminho_csv: Path, max_linhas: int = 5) -> None:
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_csv}")

    codificacao, delimitador = detectar_formato(caminho_csv)

    print(f"Arquivo: {caminho_csv}")
    print(f"Codificacao detectada: {codificacao}")
    print(f"Delimitador detectado: '{delimitador}'")

    with caminho_csv.open("r", encoding=codificacao, newline="") as f:
        leitor = csv.DictReader(f, delimiter=delimitador)

        if not leitor.fieldnames:
            print("O arquivo nao possui cabecalho reconhecido.")
            return

        print(f"Total de colunas: {len(leitor.fieldnames)}")
        print("Colunas:")
        for col in leitor.fieldnames:
            print(f"- {col}")

        print(f"\nPrimeiras {max_linhas} linhas:")
        for i, linha in enumerate(leitor, start=1):
            print(f"Linha {i}: {linha}")
            if i >= max_linhas:
                break


if __name__ == "__main__":
    caminho = resolver_caminho_csv()
    ler_csv(caminho_csv=caminho, max_linhas=5)
