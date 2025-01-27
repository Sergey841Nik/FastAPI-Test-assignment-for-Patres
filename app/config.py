from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    # db config
    DB_URL: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def url(self):
        # return "sqlite+aiosqlite:///test_db.db"
        return f"{self.DB_URL}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    echo: bool = True
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

    # auth config
    private_key_path: Path = BASE_DIR / "cert" / "private.pem" 
    public_key_path: Path = BASE_DIR / "cert" / "public.pem"
    algorithms: str = "RS256" #алгоритм шифрования
    access_token_expire_day: int = 30


settings = Settings()
