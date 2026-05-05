from datetime import datetime, timezone

from supabase import create_client, Client, ClientOptions
from app.config import config_manager


def _get_client() -> Client:
    cfg = config_manager.get_supabase()
    return create_client(cfg["url"], cfg["service_key"], options=ClientOptions(schema="public"))


def testar_conexao() -> tuple[bool, str]:
    try:
        client = _get_client()
        client.table("stg_funcionarios").select("codintfunc").limit(1).execute()
        return True, "Conexão Supabase OK"
    except Exception as e:
        return False, str(e)


def _foto_path(codintfunc: str) -> str:
    storage_cfg = config_manager.get_storage()
    return f"{storage_cfg['pasta_fotos']}/{codintfunc}.jpg"


def _foto_url_publica(client: Client, path: str) -> str:
    cfg = config_manager.get_storage()
    return client.storage.from_(cfg["bucket_fotos"]).get_public_url(path)


def _upload_foto(client: Client, codintfunc: str, imagem_bytes: bytes) -> str | None:
    cfg = config_manager.get_storage()
    bucket = cfg["bucket_fotos"]
    path = _foto_path(codintfunc)
    try:
        client.storage.from_(bucket).upload(
            path=path,
            file=imagem_bytes,
            file_options={"content-type": "image/jpeg"},
        )
        return _foto_url_publica(client, path)
    except Exception:
        return None


def _buscar_fotos_existentes(client: Client) -> set[str]:
    """Retorna o set de codintfunc que já têm foto_url salva no Supabase (sem limite de paginação)."""
    try:
        todos = []
        PAGINA = 1000
        offset = 0
        while True:
            res = (
                client.table("stg_funcionarios")
                .select("codintfunc")
                .not_.is_("foto_url", "null")
                .range(offset, offset + PAGINA - 1)
                .execute()
            )
            todos.extend(res.data)
            if len(res.data) < PAGINA:
                break
            offset += PAGINA
        return {r["codintfunc"] for r in todos}
    except Exception:
        return set()


def upsert_funcionarios(registros: list[dict], log_fn=None) -> dict:
    client = _get_client()
    resultado = {"total": len(registros), "enviados": 0, "erros": 0, "sem_foto": 0}

    # busca quais já têm foto salva — não faz upload novamente
    fotos_existentes = _buscar_fotos_existentes(client)
    if log_fn:
        log_fn(f"  {len(fotos_existentes)} funcionários já têm foto no Storage — serão ignorados")

    linhas = []
    for rec in registros:
        imagem_bytes = rec.get("imagem")
        codintfunc = str(rec.get("codintfunc", "")).strip()

        foto_url = None
        if imagem_bytes and isinstance(imagem_bytes, (bytes, bytearray)):
            if codintfunc in fotos_existentes:
                # já tem foto — usa a URL existente sem re-upload
                foto_url = _foto_url_publica(client, _foto_path(codintfunc))
            else:
                foto_url = _upload_foto(client, codintfunc, bytes(imagem_bytes))
                if foto_url is None and log_fn:
                    log_fn(f"[AVISO] Falha no upload da foto: {codintfunc}")
        else:
            resultado["sem_foto"] += 1

        jornada = rec.get("jornadafunc")
        if jornada is not None:
            partes = str(jornada).split(".")
            horas = int(partes[0])
            minutos = int(partes[1]) if len(partes) > 1 else 0
            jornada = round(horas + minutos / 60, 4)

        dt_adm = rec.get("dtadmfunc")
        if hasattr(dt_adm, "strftime"):
            dt_adm = dt_adm.strftime("%Y-%m-%d")

        situacao = (rec.get("situacaofunc") or "").strip()
        linha = {
            "codintfunc": codintfunc,
            "codfunc": str(rec.get("codfunc", "")).strip(),
            "nome": (rec.get("nomefunc") or "").strip(),
            "funcao": (rec.get("descfuncao") or "").strip(),
            "setor": (rec.get("descsetor") or "").strip(),
            "dt_admissao": dt_adm,
            "jornada_h": jornada,
            "sal_base": float(rec["salbase"]) if rec.get("salbase") is not None else None,
            "foto_url": foto_url,
            "situacao": situacao,
            "ativo": situacao == "A",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        linhas.append(linha)

    # deduplicar por codintfunc — mantém o último registro caso haja duplicatas
    vistos = {}
    for linha in linhas:
        vistos[linha["codintfunc"]] = linha
    linhas = list(vistos.values())
    resultado["total"] = len(linhas)

    LOTE = 100
    for i in range(0, len(linhas), LOTE):
        lote = linhas[i : i + LOTE]
        try:
            client.table("stg_funcionarios").upsert(
                lote, on_conflict="codintfunc"
            ).execute()
            resultado["enviados"] += len(lote)
            if log_fn:
                log_fn(f"  Lote {i // LOTE + 1}: {len(lote)} registros enviados")
        except Exception as e:
            resultado["erros"] += len(lote)
            if log_fn:
                log_fn(f"  [ERRO] Lote {i // LOTE + 1}: {e}")

    return resultado


def _upsert_lotes(client, tabela: str, pk: str, linhas: list[dict], log_fn=None) -> dict:
    """Upsert genérico em lotes de 200 com PK simples ou composta."""
    resultado = {"total": len(linhas), "enviados": 0, "erros": 0}
    LOTE = 200
    for i in range(0, len(linhas), LOTE):
        lote = linhas[i : i + LOTE]
        try:
            client.table(tabela).upsert(lote, on_conflict=pk).execute()
            resultado["enviados"] += len(lote)
            if log_fn:
                log_fn(f"  Lote {i // LOTE + 1}: {len(lote)} registros enviados")
        except Exception as e:
            resultado["erros"] += len(lote)
            if log_fn:
                log_fn(f"  [ERRO] Lote {i // LOTE + 1}: {e}")
    return resultado


def _serializar(rec: dict) -> dict:
    """Converte tipos Oracle (Decimal, date) para tipos JSON-serializáveis."""
    linha = {}
    for k, v in rec.items():
        if hasattr(v, "strftime"):
            v = v.isoformat() if hasattr(v, "hour") else str(v)
        elif hasattr(v, "__float__") and not isinstance(v, (int, float, bool)):
            v = float(v)
        linha[k] = v
    return linha


def upsert_fichamedica(registros: list[dict], log_fn=None) -> dict:
    client = _get_client()
    if log_fn:
        log_fn(f"  Preparando {len(registros)} registros de ficha médica...")
    linhas = []
    for r in registros:
        linha = _serializar(r) | {"updated_at": datetime.now(timezone.utc).isoformat()}
        # codocorr faz parte da PK — não pode ser NULL
        if linha.get("codocorr") is None:
            linha["codocorr"] = 0
        # codintfunc como string
        linha["codintfunc"] = str(linha["codintfunc"])
        linhas.append(linha)
    return _upsert_lotes(client, "stg_fichamedica", "codintfunc,datafichamed,codocorr", linhas, log_fn)


def upsert_fichamedica_exames(registros: list[dict], log_fn=None) -> dict:
    client = _get_client()
    if log_fn:
        log_fn(f"  Preparando {len(registros)} registros de exames...")
    vistos = {}
    for r in registros:
        linha = _serializar(r) | {"updated_at": datetime.now(timezone.utc).isoformat()}
        linha["codintfunc"] = str(linha["codintfunc"])
        chave = (linha["codintfunc"], str(linha.get("datafichamed")), str(linha.get("codtipoexa")))
        vistos[chave] = linha
    linhas = list(vistos.values())
    return _upsert_lotes(client, "stg_fichamedica_exames", "codintfunc,datafichamed,codtipoexa", linhas, log_fn)


def upsert_afastamentos(registros: list[dict], log_fn=None) -> dict:
    client = _get_client()
    if log_fn:
        log_fn(f"  Preparando {len(registros)} registros de afastamentos...")
    linhas = []
    for r in registros:
        linha = _serializar(r) | {"updated_at": datetime.now(timezone.utc).isoformat()}
        linha["codintfunc"] = str(linha["codintfunc"])
        linhas.append(linha)
    return _upsert_lotes(client, "stg_afastamentos", "codintfunc,dtafast", linhas, log_fn)


def upsert_generico(
    nome_supabase: str,
    pk: str,
    registros: list[dict],
    log_fn=None,
) -> dict:
    client = _get_client()
    resultado = {"total": len(registros), "enviados": 0, "erros": 0}

    LOTE = 100
    for i in range(0, len(registros), LOTE):
        lote = registros[i : i + LOTE]
        lote_limpo = []
        for rec in lote:
            linha = {}
            for k, v in rec.items():
                if hasattr(v, "strftime"):
                    v = v.isoformat()
                elif hasattr(v, "__float__"):
                    v = float(v)
                linha[k] = v
            lote_limpo.append(linha)
        try:
            client.table(nome_supabase).upsert(
                lote_limpo, on_conflict=pk
            ).execute()
            resultado["enviados"] += len(lote)
            if log_fn:
                log_fn(f"  Lote {i // LOTE + 1}: {len(lote)} registros enviados")
        except Exception as e:
            resultado["erros"] += len(lote)
            if log_fn:
                log_fn(f"  [ERRO] Lote {i // LOTE + 1}: {e}")

    return resultado
