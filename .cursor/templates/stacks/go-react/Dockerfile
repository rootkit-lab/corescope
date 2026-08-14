# syntax=docker/dockerfile:1

# --- Stage 1: build do frontend ---
FROM node:22-alpine AS web-build
WORKDIR /src/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# --- Stage 2: build do binário Go (com frontend embutido via go:embed) ---
FROM golang:1.23-alpine AS go-build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
COPY --from=web-build /src/web/dist ./web/dist
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/app

# --- Stage 3: imagem final mínima ---
FROM alpine:3.20
RUN adduser -D -H app
USER app
COPY --from=go-build /out/app /app
EXPOSE 8080
ENTRYPOINT ["/app"]
