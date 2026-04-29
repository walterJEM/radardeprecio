import yaml
from pathlib import Path

def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_active_urls() -> list:
    config = load_config()
    return [
        site for site in config["sites"]
        if site.get("active", True)
    ]

def get_scraper_settings() -> dict:
    return load_config()["scraper"]