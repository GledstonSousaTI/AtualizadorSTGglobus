-- Migration: tabela stg_funcionarios (schema public)
-- Origem: VW_FUNCIONARIOS + FLP_FUNCIONARIOS_IMAGENS (Oracle Globus)
-- Filtro: CODIGOEMPRESA=1, CODIGOFL=1 (todos os status)
-- Fotos: Supabase Storage, bucket "funcionarios", path "fotos/{codintfunc}.jpg"
-- Prefixo STG_ = dados espelho do Globus (não editar manualmente)

CREATE TABLE IF NOT EXISTS public.stg_funcionarios (
    codintfunc   TEXT PRIMARY KEY,
    codfunc      TEXT,
    nome         TEXT,
    funcao       TEXT,
    setor        TEXT,
    dt_admissao  DATE,
    jornada_h    NUMERIC(6, 4),
    sal_base     NUMERIC(12, 2),
    foto_url     TEXT,
    situacao     TEXT,
    ativo        BOOLEAN DEFAULT TRUE,
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stg_funcionarios_codfunc  ON public.stg_funcionarios (codfunc);
CREATE INDEX IF NOT EXISTS idx_stg_funcionarios_nome     ON public.stg_funcionarios (nome);
CREATE INDEX IF NOT EXISTS idx_stg_funcionarios_ativo    ON public.stg_funcionarios (ativo);
CREATE INDEX IF NOT EXISTS idx_stg_funcionarios_situacao ON public.stg_funcionarios (situacao);

-- Storage: criar bucket no Supabase Dashboard
-- Bucket name: funcionarios
-- Acesso público: SIM
-- Pasta: fotos/
