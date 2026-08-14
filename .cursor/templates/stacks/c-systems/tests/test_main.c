#include "unity.h"

#include "project/config.h"

#include <stdlib.h>

// Unity exige setUp/tearDown mesmo que vazios — chamados antes/depois de cada teste.
void setUp(void) {}
void tearDown(void) {}

static void test_config_load_from_env_returns_neg_on_null(void) {
    TEST_ASSERT_EQUAL_INT(-1, project_config_load_from_env(NULL));
}

static void test_config_load_from_env_uses_defaults_when_url_missing(void) {
    unsetenv("APP_SERVER_URL");
    unsetenv("APP_LOG_LEVEL");
    setenv("APP_TOKEN", "test-token", 1);

    ProjectConfig cfg;
    TEST_ASSERT_EQUAL_INT(0, project_config_load_from_env(&cfg));
    TEST_ASSERT_EQUAL_STRING("127.0.0.1:8443", cfg.server_url);
    TEST_ASSERT_EQUAL_STRING("info", cfg.log_level);
    TEST_ASSERT_EQUAL_STRING("test-token", cfg.token);
}

static void test_config_load_from_env_returns_neg_when_token_missing(void) {
    unsetenv("APP_TOKEN");
    ProjectConfig cfg;
    TEST_ASSERT_EQUAL_INT(-1, project_config_load_from_env(&cfg));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_config_load_from_env_returns_neg_on_null);
    RUN_TEST(test_config_load_from_env_uses_defaults_when_url_missing);
    RUN_TEST(test_config_load_from_env_returns_neg_when_token_missing);
    return UNITY_END();
}
