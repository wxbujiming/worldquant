from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    wqb_email: str = ""
    wqb_password: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
