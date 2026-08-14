#ifndef PROJECT_TRANSPORT_H
#define PROJECT_TRANSPORT_H

#include <stddef.h>

typedef struct ProjectTransport ProjectTransport;

// Conecta em server_url (formato "host:port"). Retorna NULL em erro.
ProjectTransport* project_transport_connect(const char* server_url, int timeout_ms);

// Envia mensagem. Retorna 0 em sucesso, -1 em erro.
int project_transport_send(ProjectTransport* t, const char* msg, size_t len);

// Recebe até len-1 bytes + null terminator. Retorna bytes lidos, -1 em erro, 0 em EOF.
int project_transport_receive(ProjectTransport* t, char* out, size_t len);

// Libera o transporte. Recebe o ponteiro por ownership (deleta ao final).
void project_transport_free(ProjectTransport* t);

#endif
