from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_type: str = "sqlite"
    db_url: str = "sqlite+aiosqlite:////app/data/arex_platform.db"
    secret_key: str = "changeme"
    ssh_keys_dir: str = "/app/ssh_keys"
    cors_origins: list[str] = ["*"]
    debug: bool = False
    # AREX-specific settings
    arex_storage_url: str = "http://arex-storage:8080"          # backend → arex-storage (Docker内部)
    arex_agent_storage_url: str = ""                             # agent → arex-storage (目标JVM能访问的地址，留空则回退到 arex_storage_url)
    arex_agent_jar_path: str = "/opt/arex-agent/arex-agent.jar"

    model_config = SettingsConfigDict(env_prefix="AP_")

settings = Settings()
