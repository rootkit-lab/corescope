# syntax=docker/dockerfile:1

FROM python:3.12-slim AS build
WORKDIR /src
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=build /install /usr/local
COPY . .
RUN useradd -m app
USER app
EXPOSE 8000
CMD ["python", "-m", "src.main"]
