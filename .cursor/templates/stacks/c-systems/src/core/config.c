#include "project/config.h"

#include <stdlib.h>
#include <string.h>

int project_config_load_from_env(ProjectConfig* out) {
    if (!out) {
        return -1;
    }

    out->server_url = getenv("APP_SERVER_URL");
    out->token = getenv("APP_TOKEN");
    out->log_level = getenv("APP_LOG_LEVEL");

    if (!out->server_url) {
        out->server_url = "127.0.0.1:8443";
    }
    if (!out->token) {
        return -1;
    }
    if (!out->log_level) {
        out->log_level = "info";
    }
    return 0;
}
