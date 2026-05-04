"""Entry point CLI — para rodar via Task Scheduler sem abrir a GUI."""
from app.core.sync_engine import run
import sys

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", help="ID da tabela (omitir = todas)")
    args = parser.parse_args()
    run(tabela_id=args.table)
