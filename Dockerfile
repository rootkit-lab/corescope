# syntax=docker/dockerfile:1
#
# Sandbox isolado para analise dinamica de binarios/amostras nao confiaveis.
# Isto NAO e uma imagem de "producao" — corescope nao roda como servico.
#
# Uso recomendado (sem rede, amostra somente leitura):
#   docker build -t corescope-sandbox .
#   docker run --rm -it --network=none -v "$(pwd)/cases:/cases:ro" corescope-sandbox

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils \
        file \
        less \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir -e ".[memory,re]"

RUN useradd -m analyst
USER analyst
WORKDIR /cases

CMD ["corescope", "--help"]
