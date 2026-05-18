from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    FORNECEDORES_API_BASE_URL: str
    RECEITA_API_BASE_URL: str

    PROTHEUS_API_BASE_URL: str
    PROTHEUS_C_AUTH: str
    PROTHEUS_AUTHORIZATION_TOKEN: str

    ENV: str = "dev"

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_IS_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    RABBIT_HOST: str
    RABBIT_PORT: int
    RABBIT_VIRTUAL_HOST: str
    RABBIT_USER: str
    RABBIT_PASSWORD: str
    RABBIT_QUEUE_NAME: str
    RABBIT_CONNECTION_NAME: str


settings = Settings()
