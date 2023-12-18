from pydantic_settings import BaseSettings, SettingsConfigDict



class TestSettings(BaseSettings, ):
    foo: str
    bar: str

    model_config = SettingsConfigDict(env_file="frontend/pokus/.env", case_sensitive=True, frozen=True)


if __name__ == "__main__":
    t = TestSettings()
    print(t.case_sensitive)
    t.case_sensitive = False
    print(t)