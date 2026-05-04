import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_oracle() -> dict:
    return load().get("oracle", {})


def get_supabase() -> dict:
    return load().get("supabase", {})


def get_tabelas() -> list:
    return load().get("tabelas", [])


def get_storage() -> dict:
    return load().get("storage", {"bucket_fotos": "funcionarios", "pasta_fotos": "fotos"})


def get_tabela(tabela_id: str) -> dict | None:
    return next((t for t in get_tabelas() if t["id"] == tabela_id), None)


def update_oracle(dados: dict) -> None:
    cfg = load()
    cfg["oracle"] = dados
    save(cfg)


def update_supabase(dados: dict) -> None:
    cfg = load()
    cfg["supabase"] = dados
    save(cfg)


def upsert_tabela(tabela: dict) -> None:
    cfg = load()
    tabelas = cfg.get("tabelas", [])
    idx = next((i for i, t in enumerate(tabelas) if t["id"] == tabela["id"]), None)
    if idx is not None:
        tabelas[idx] = tabela
    else:
        tabelas.append(tabela)
    cfg["tabelas"] = tabelas
    save(cfg)


def remover_tabela(tabela_id: str) -> None:
    cfg = load()
    cfg["tabelas"] = [t for t in cfg.get("tabelas", []) if t["id"] != tabela_id]
    save(cfg)
