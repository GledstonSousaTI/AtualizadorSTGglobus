import oracledb
from app.config import config_manager

# oracledb thin mode — sem Oracle Client instalado
oracledb.init_oracle_client = lambda **_: None  # garante thin mode mesmo se chamado


def _get_conn():
    cfg = config_manager.get_oracle()
    dsn = oracledb.makedsn(cfg["host"], cfg["port"], service_name=cfg["service"])
    return oracledb.connect(user=cfg["user"], password=cfg["password"], dsn=dsn)


def testar_conexao() -> tuple[bool, str]:
    try:
        with _get_conn() as conn:
            conn.ping()
        return True, "Conexão Oracle OK"
    except Exception as e:
        return False, str(e)


def listar_tabelas_disponiveis() -> list[str]:
    """Retorna tabelas e views acessíveis pelo usuário Oracle."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT object_name FROM user_objects "
                "WHERE object_type IN ('TABLE','VIEW') ORDER BY object_name"
            )
            return [row[0] for row in cur.fetchall()]


def listar_colunas(nome_oracle: str) -> list[dict]:
    """Retorna colunas e tipos de uma tabela/view Oracle."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name, data_type, nullable "
                "FROM user_tab_columns WHERE table_name = :t ORDER BY column_id",
                {"t": nome_oracle.upper()},
            )
            return [
                {"nome": r[0], "tipo": r[1], "nullable": r[2] == "Y"}
                for r in cur.fetchall()
            ]


def buscar_funcionarios() -> list[dict]:
    """
    Retorna todos os funcionários (empresa=1, filial=1) com JOIN de imagens.
    Campo IMAGEM é retornado como bytes ou None.
    """
    sql = """
        SELECT
            f.CODINTFUNC,
            f.CODFUNC,
            f.NOMEFUNC,
            f.DESCFUNCAO,
            f.DESCSETOR,
            f.DTADMFUNC,
            f.JORNADAFUNC,
            f.SALBASE,
            f.SITUACAOFUNC,
            i.IMAGEM
        FROM VW_FUNCIONARIOS f
        LEFT JOIN FLP_FUNCIONARIOS_IMAGENS i ON i.CODINTFUNC = f.CODINTFUNC
        WHERE f.CODIGOEMPRESA = 1
          AND f.CODIGOFL = 1
        ORDER BY f.NOMEFUNC
    """
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d[0].lower() for d in cur.description]
            rows = []
            for row in cur:
                rec = {}
                for i, col in enumerate(cols):
                    val = row[i]
                    # LONG RAW → lê o LOB como bytes
                    if hasattr(val, "read"):
                        val = val.read()
                    rec[col] = val
                rows.append(rec)
            return rows


def buscar_tabela_generica(nome_oracle: str, filtros: dict | None = None) -> list[dict]:
    """
    Leitura genérica de qualquer tabela/view Oracle.
    filtros: dict coluna→valor adicionado ao WHERE.
    """
    where = ""
    params = {}
    if filtros:
        clausulas = []
        for col, val in filtros.items():
            clausulas.append(f"{col} = :{col}")
            params[col] = val
        where = "WHERE " + " AND ".join(clausulas)

    sql = f"SELECT * FROM {nome_oracle} {where}"
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0].lower() for d in cur.description]
            rows = []
            for row in cur:
                rec = {}
                for i, col in enumerate(cols):
                    val = row[i]
                    if hasattr(val, "read"):
                        val = val.read()
                    rec[col] = val
                rows.append(rec)
            return rows
