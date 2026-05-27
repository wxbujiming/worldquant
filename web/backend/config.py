from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    wqb_email: str = ""
    wqb_password: str = ""

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
