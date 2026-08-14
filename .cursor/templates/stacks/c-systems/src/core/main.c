#include "project/config.h"
#include "project/transport.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    ProjectConfig cfg;
    if (project_config_load_from_env(&cfg) != 0) {
        fprintf(stderr, "erro: APP_TOKEN nao definido\n");
        return 1;
    }

    printf("hello from c-systems preset (log_level=%s)\n", cfg.log_level);

    ProjectTransport* t = project_transport_connect(cfg.server_url, 5000);
    if (!t) {
        fprintf(stderr, "aviso: nao conectou a %s (esperado se TLS stub)\n", cfg.server_url);
        return 0;
    }

    const char* msg = "ping";
    if (project_transport_send(t, msg, strlen(msg)) == 0) {
        char buf[256];
        project_transport_receive(t, buf, sizeof(buf));
    }

    project_transport_free(t);
    return 0;
}
