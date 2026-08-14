#ifndef PROJECT_CONFIG_H
#define PROJECT_CONFIG_H

#include <stddef.h>

typedef struct {
    const char* server_url;
    const char* token;
    const char* log_level;
} ProjectConfig;

// Carrega config de env vars (APP_SERVER_URL, APP_TOKEN, APP_LOG_LEVEL).
// Retorna 0 em sucesso, -1 em erro (errno definido).
int project_config_load_from_env(ProjectConfig* out);

#endif
