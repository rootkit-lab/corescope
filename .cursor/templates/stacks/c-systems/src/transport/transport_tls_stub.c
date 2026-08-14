#include "project/transport.h"

#include <stdlib.h>
#include <string.h>

struct ProjectTransport {
    int dummy; // stub: sem conexão real
};

ProjectTransport* project_transport_connect(const char* server_url, int timeout_ms) {
    (void)server_url;
    (void)timeout_ms;
    // Stub: TLS desabilitado em build. Retorna NULL para indicar que não conectou.
    return NULL;
}

int project_transport_send(ProjectTransport* t, const char* msg, size_t len) {
    (void)t;
    (void)msg;
    (void)len;
    return -1;
}

int project_transport_receive(ProjectTransport* t, char* out, size_t len) {
    (void)t;
    (void)out;
    (void)len;
    return -1;
}

void project_transport_free(ProjectTransport* t) {
    free(t);
}
