-- Migration: ficha médica, exames e afastamentos
-- Prefixo STG_ = dados espelho do Globus (não editar manualmente)

-- ============================================================
-- stg_fichamedica
-- Origem: SRH_FICHAMEDICA + SRH_CRM + FRQ_CID
-- PK composta: (codintfunc, datafichamed, codocorr)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.stg_fichamedica (
    codintfunc          TEXT        NOT NULL,
    datafichamed        TIMESTAMP   NOT NULL,
    codocorr            INTEGER     NOT NULL,
    codcid              TEXT,
    desccid             TEXT,
    nrdiasatestmed      NUMERIC,
    nrhorasatestmed     NUMERIC,
    atest_horaini       TIMESTAMP,
    atest_horafin       TIMESTAMP,
    historicofichamed   TEXT,
    tipoatestfichamed   TEXT,
    tipoconsulta        TEXT,
    crmmedicoexterno    TEXT,
    nomemedico          TEXT,
    aso_tpexame         INTEGER,
    aso_apto            INTEGER,
    aso_riscos          TEXT,
    aso_risco_sem       TEXT,
    aso_risco_qui       TEXT,
    aso_risco_fis       TEXT,
    aso_risco_bio       TEXT,
    aso_risco_erg       TEXT,
    aso_risco_aci       TEXT,
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (codintfunc, datafichamed, codocorr)
);

CREATE INDEX IF NOT EXISTS idx_stg_fichamedica_func    ON public.stg_fichamedica (codintfunc);
CREATE INDEX IF NOT EXISTS idx_stg_fichamedica_data    ON public.stg_fichamedica (datafichamed);
CREATE INDEX IF NOT EXISTS idx_stg_fichamedica_codocorr ON public.stg_fichamedica (codocorr);
CREATE INDEX IF NOT EXISTS idx_stg_fichamedica_cid     ON public.stg_fichamedica (codcid);

-- ============================================================
-- stg_fichamedica_exames
-- Origem: SRH_FICHAMEDICA_EXAMES + SRH_TIPOEXAME
-- PK composta: (codintfunc, datafichamed, codtipoexa)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.stg_fichamedica_exames (
    codintfunc          TEXT        NOT NULL,
    datafichamed        DATE        NOT NULL,
    codtipoexa          INTEGER     NOT NULL,
    desctipoexa         TEXT,
    resultadoexame      TEXT,
    dtrealizouexame     DATE,
    dtproxexamedigit    DATE,
    historicoexa        TEXT,
    observacaoexa       TEXT,
    indresult           TEXT,
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (codintfunc, datafichamed, codtipoexa)
);

CREATE INDEX IF NOT EXISTS idx_stg_fmexames_func  ON public.stg_fichamedica_exames (codintfunc);
CREATE INDEX IF NOT EXISTS idx_stg_fmexames_tipo  ON public.stg_fichamedica_exames (codtipoexa);

-- ============================================================
-- stg_afastamentos
-- Origem: FLP_AFASTADOS + FRQ_CID
-- PK composta: (codintfunc, dtafast)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.stg_afastamentos (
    codintfunc      TEXT    NOT NULL,
    dtafast         DATE    NOT NULL,
    dtretafast      DATE,
    codcid          TEXT,
    desccid         TEXT,
    nrbeneficio     TEXT,
    especie         TEXT,
    dtpericia       DATE,
    dtprevretorno   DATE,
    nomemedico      TEXT,
    codcrm          TEXT,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (codintfunc, dtafast)
);

CREATE INDEX IF NOT EXISTS idx_stg_afastamentos_func ON public.stg_afastamentos (codintfunc);
CREATE INDEX IF NOT EXISTS idx_stg_afastamentos_data ON public.stg_afastamentos (dtafast);
CREATE INDEX IF NOT EXISTS idx_stg_afastamentos_cid  ON public.stg_afastamentos (codcid);
