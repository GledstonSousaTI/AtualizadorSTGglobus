"""
Orquestrador de sincronização Oracle -> Supabase.

Uso via CLI:
    python -m app.core.sync_engine                  # sincroniza todas as tabelas ativas
    python -m app.core.sync_engine --table funcionarios  # sincroniza tabela específica
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from app.config import config_manager
from app.core import globus_reader, supabase_writer

LOG_PATH = Path(__file__).parent.parent.parent / "logs" / "sync.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)),
    ],
)
logger = logging.getLogger("sync_engine")


def _log(msg: str, callback=None):
    logger.info(msg)
    if callback:
        callback(msg)


def sincronizar_funcionarios(log_fn=None) -> dict:
    _log("Iniciando sync: funcionarios (Oracle -> Supabase)", log_fn)
    try:
        registros = globus_reader.buscar_funcionarios()
        _log(f"  {len(registros)} funcionários ativos lidos do Oracle", log_fn)
    except Exception as e:
        _log(f"[ERRO] Leitura Oracle: {e}", log_fn)
        return {"tabela": "funcionarios", "status": "erro", "detalhe": str(e)}

    try:
        resultado = supabase_writer.upsert_funcionarios(registros, log_fn=log_fn)
        _log(
            f"  Resultado: {resultado['enviados']}/{resultado['total']} enviados | "
            f"{resultado['erros']} erros | {resultado['sem_foto']} sem foto",
            log_fn,
        )
        return {"tabela": "funcionarios", "status": "ok", **resultado}
    except Exception as e:
        _log(f"[ERRO] Escrita Supabase: {e}", log_fn)
        return {"tabela": "funcionarios", "status": "erro", "detalhe": str(e)}


def sincronizar_tabela_generica(tabela_cfg: dict, log_fn=None) -> dict:
    nome_oracle = tabela_cfg["nome_oracle"]
    nome_supabase = tabela_cfg["nome_supabase"]
    pk = tabela_cfg["pk"]
    filtros = tabela_cfg.get("filtros")

    _log(f"Iniciando sync: {nome_oracle} -> {nome_supabase}", log_fn)
    try:
        registros = globus_reader.buscar_tabela_generica(nome_oracle, filtros)
        _log(f"  {len(registros)} registros lidos do Oracle", log_fn)
    except Exception as e:
        _log(f"[ERRO] Leitura Oracle ({nome_oracle}): {e}", log_fn)
        return {"tabela": nome_supabase, "status": "erro", "detalhe": str(e)}

    try:
        resultado = supabase_writer.upsert_generico(
            nome_supabase, pk, registros, log_fn=log_fn
        )
        _log(
            f"  Resultado: {resultado['enviados']}/{resultado['total']} enviados | "
            f"{resultado['erros']} erros",
            log_fn,
        )
        return {"tabela": nome_supabase, "status": "ok", **resultado}
    except Exception as e:
        _log(f"[ERRO] Escrita Supabase ({nome_supabase}): {e}", log_fn)
        return {"tabela": nome_supabase, "status": "erro", "detalhe": str(e)}


def run(tabela_id: str | None = None, log_fn=None) -> list[dict]:
    """
    Executa a sincronização.
    tabela_id=None -> todas as tabelas ativas.
    tabela_id='funcionarios' -> só aquela.
    """
    inicio = datetime.now()
    _log(f"=== SYNC INICIADO {inicio.strftime('%Y-%m-%d %H:%M:%S')} ===", log_fn)

    tabelas = config_manager.get_tabelas()
    if tabela_id:
        tabelas = [t for t in tabelas if t["id"] == tabela_id]

    tabelas_ativas = [t for t in tabelas if t.get("ativo", True)]
    if not tabelas_ativas:
        _log("Nenhuma tabela ativa encontrada.", log_fn)
        return []

    resultados = []
    for tab in tabelas_ativas:
        if tab["id"] == "funcionarios":
            res = sincronizar_funcionarios(log_fn)
        else:
            res = sincronizar_tabela_generica(tab, log_fn)
        resultados.append(res)

    fim = datetime.now()
    duracao = (fim - inicio).seconds
    _log(f"=== SYNC CONCLUÍDO em {duracao}s ===", log_fn)
    return resultados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincronizador Globus -> Supabase")
    parser.add_argument("--table", help="ID da tabela a sincronizar (omitir = todas)")
    args = parser.parse_args()
    run(tabela_id=args.table)
