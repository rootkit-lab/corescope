// Wrapper TLS minimalista em torno de OpenSSL.
// Compilado quando WINDOWS_TLS=1 (ver Makefile). Fornece a mesma API de transport_tls_stub.c
// para que o resto do código não precise saber qual variante está linkada.
//
// NÃO é um cliente TLS completo — é o esqueleto. Produções reais devem:
//   - adicionar verificação de certificado (CA bundle) e/ou pinning
//   - tratar SNI explicitamente (já feito via SSL_set_tlsext_host_name)
//   - lidar com renegotiação, timeouts de handshake, fallback de cipher suite
//   - integrar com o event loop do app (non-blocking BIO)

#include "project/transport.h"

#include <openssl/bio.h>
#include <openssl/err.h>
#include <openssl/ssl.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct ProjectTransport {
    SSL_CTX* ctx;
    SSL* ssl;
    BIO* bio;
};

static int parse_host_port(const char* url, char* host, size_t host_len, int* port) {
    // Aceita "host:port". Não aceita URL completa — simplificação intencional.
    const char* colon = strrchr(url, ':');
    if (!colon) {
        return -1;
    }
    size_t hlen = (size_t)(colon - url);
    if (hlen >= host_len) {
        return -1;
    }
    memcpy(host, url, hlen);
    host[hlen] = '\0';
    *port = atoi(colon + 1);
    if (*port <= 0 || *port > 65535) {
        return -1;
    }
    return 0;
}

ProjectTransport* project_transport_connect(const char* server_url, int timeout_ms) {
    (void)timeout_ms; // simplificação: blocking connect; produção deve usar BIO_s_connect com timeout

    char host[256];
    int port;
    if (parse_host_port(server_url, host, sizeof(host), &port) != 0) {
        return NULL;
    }

    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();

    SSL_CTX* ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        return NULL;
    }
    SSL_CTX_set_default_verify_paths(ctx);
    SSL_CTX_set_options(ctx, SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1);

    BIO* bio = BIO_new_ssl_connect(ctx);
    if (!bio) {
        SSL_CTX_free(ctx);
        return NULL;
    }

    char conn_str[280];
    snprintf(conn_str, sizeof(conn_str), "%s:%d", host, port);
    BIO_set_conn_hostname(bio, conn_str);

    SSL* ssl = NULL;
    BIO_get_ssl(bio, &ssl);
    if (!ssl) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return NULL;
    }
    SSL_set_tlsext_host_name(ssl, host);

    if (BIO_do_connect(bio) <= 0 || BIO_do_handshake(bio) <= 0) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return NULL;
    }

    ProjectTransport* t = malloc(sizeof(*t));
    if (!t) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return NULL;
    }
    t->ctx = ctx;
    t->ssl = ssl;
    t->bio = bio;
    return t;
}

int project_transport_send(ProjectTransport* t, const char* msg, size_t len) {
    if (!t || !msg) {
        return -1;
    }
    int written = SSL_write(t->ssl, msg, (int)len);
    if (written <= 0) {
        return -1;
    }
    return 0;
}

int project_transport_receive(ProjectTransport* t, char* out, size_t len) {
    if (!t || !out || len == 0) {
        return -1;
    }
    int n = SSL_read(t->ssl, out, (int)(len - 1));
    if (n <= 0) {
        return -1;
    }
    out[n] = '\0';
    return n;
}

void project_transport_free(ProjectTransport* t) {
    if (!t) {
        return;
    }
    if (t->bio) {
        BIO_free_all(t->bio);
    }
    if (t->ctx) {
        SSL_CTX_free(t->ctx);
    }
    free(t);
}
