# syntax=docker/dockerfile:1
# Build reprodutível do projeto C em container — útil para CI sem toolchain local.

FROM debian:bookworm-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    clang-format \
    clang-tidy \
    cppcheck \
    mingw-w64 \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .

RUN make install
RUN make verify

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends libc6 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /src/build/app /app/app
ENTRYPOINT ["/app/app"]
