DROP SCHEMA IF EXISTS OLIVIA CASCADE;
BEGIN;

-- =========================================================
-- SCHEMA
-- =========================================================
CREATE SCHEMA IF NOT EXISTS OLIVIA;

-- =========================================================
-- TABELA: S_USUARIO
-- Finalidade: cadastro mínimo para identificação local (Gov.br)
-- =========================================================
CREATE TABLE IF NOT EXISTS OLIVIA.S_USUARIO (
  ID_USUARIO              SERIAL PRIMARY KEY,
  NR_CPF                  VARCHAR(11) NOT NULL,
  NM_USUARIO              VARCHAR(255) NOT NULL,
  DH_CRIACAO_REGISTRO     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  DH_ATUALIZACAO_REGISTRO TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT UK_USUARIO_NR_CPF UNIQUE (NR_CPF)
);

-- =========================================================
-- TABELA: S_LAUDO_OLIVIA
-- Finalidade: armazenar laudos processados pela aplicação OLIVIA
-- =========================================================
CREATE TABLE IF NOT EXISTS OLIVIA.S_LAUDO_OLIVIA
(
    ID_LAUDO_OLIVIA         SERIAL PRIMARY KEY,
    NR_LPCO                 VARCHAR(255) NOT NULL,
    JS_DADO_BRUTO           JSON,
    JS_DADO_USUARIO         JSON,
    OB_LAUDO_USUARIO        VARCHAR(255),
    OB_LAUDO_IA             VARCHAR(255),
    DH_CRIACAO_REGISTRO     TIMESTAMPTZ DEFAULT NOW(),
    DH_ATUALIZACAO_REGISTRO TIMESTAMPTZ DEFAULT NOW(),
    ID_USUARIO              INTEGER NOT NULL
);

-- =========================================================
-- TABELA: S_SESSAO
-- Finalidade: controle de sessão da aplicação (sem persistir tokens OIDC)
-- =========================================================
CREATE TABLE IF NOT EXISTS OLIVIA.S_SESSAO (
  ID_SESSAO               VARCHAR(64) PRIMARY KEY,
  ID_USUARIO              INTEGER NOT NULL,
  DH_CRIACAO_REGISTRO     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  DH_EXPIRACAO_SESSAO     TIMESTAMPTZ
);

-- =========================================================
-- CONSTRAINTS (FK)
-- =========================================================
ALTER TABLE OLIVIA.S_LAUDO_OLIVIA
  ADD CONSTRAINT FK_LAUDO_USUARIO
    FOREIGN KEY (ID_USUARIO) REFERENCES OLIVIA.S_USUARIO (ID_USUARIO)
    ON DELETE RESTRICT;

ALTER TABLE OLIVIA.S_SESSAO
  ADD CONSTRAINT FK_SESSAO_USUARIO
    FOREIGN KEY (ID_USUARIO) REFERENCES OLIVIA.S_USUARIO (ID_USUARIO)
    ON DELETE CASCADE;

-- =========================================================
-- ÍNDICES
-- =========================================================
CREATE INDEX IF NOT EXISTS I_USUARIO_NM_USUARIO   ON OLIVIA.S_USUARIO (NM_USUARIO);
CREATE INDEX IF NOT EXISTS I_FK_SESSAO_USUARIO    ON OLIVIA.S_SESSAO (ID_USUARIO);
CREATE INDEX IF NOT EXISTS I_SESSAO_DH_EXPIRACAO  ON OLIVIA.S_SESSAO (DH_EXPIRACAO_SESSAO);

-- =========================================================
-- COMENTÁRIOS
-- =========================================================
-- S_USUARIO
COMMENT ON TABLE  OLIVIA.S_USUARIO                          IS 'Cadastro mínimo do usuário autenticado via Gov.br';
COMMENT ON COLUMN OLIVIA.S_USUARIO.ID_USUARIO               IS 'Identificador interno do usuário (PK)';
COMMENT ON COLUMN OLIVIA.S_USUARIO.NR_CPF                   IS 'CPF do usuário (equivale ao sub do provedor); apenas números';
COMMENT ON COLUMN OLIVIA.S_USUARIO.NM_USUARIO               IS 'Nome do usuário para exibição na interface';
COMMENT ON COLUMN OLIVIA.S_USUARIO.DH_CRIACAO_REGISTRO      IS 'Data/hora de criação do registro';
COMMENT ON COLUMN OLIVIA.S_USUARIO.DH_ATUALIZACAO_REGISTRO  IS 'Data/hora da última atualização do registro';

-- S_LAUDO_OLIVIA
COMMENT ON TABLE  OLIVIA.S_LAUDO_OLIVIA                       IS 'Tabela de laudos processados e vinculados a usuários autenticados';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.ID_LAUDO_OLIVIA       IS 'Identificador único do laudo (PK)';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.NR_LPCO               IS 'Número do LPCO vinculado ao laudo';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.JS_DADO_BRUTO         IS 'Dados originais do laudo em formato JSON';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.JS_DADO_USUARIO       IS 'Dados complementares informados pelo usuário em JSON';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.OB_LAUDO_USUARIO      IS 'Observação registrada pelo usuário';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.OB_LAUDO_IA           IS 'Observação registrada pela inteligência artificial';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.DH_CRIACAO_REGISTRO   IS 'Data/hora de criação do registro';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.DH_ATUALIZACAO_REGISTRO IS 'Data/hora da última atualização do registro';
COMMENT ON COLUMN OLIVIA.S_LAUDO_OLIVIA.ID_USUARIO            IS 'Usuário responsável pelo laudo (FK para S_USUARIO)';

-- S_SESSAO
COMMENT ON TABLE  OLIVIA.S_SESSAO                         IS 'Sessões da aplicação para usuários autenticados';
COMMENT ON COLUMN OLIVIA.S_SESSAO.ID_SESSAO               IS 'Identificador da sessão (string/hex gerado pelo backend)';
COMMENT ON COLUMN OLIVIA.S_SESSAO.ID_USUARIO              IS 'FK para OLIVIA.S_USUARIO';
COMMENT ON COLUMN OLIVIA.S_SESSAO.DH_CRIACAO_REGISTRO     IS 'Data/hora de criação da sessão';
COMMENT ON COLUMN OLIVIA.S_SESSAO.DH_EXPIRACAO_SESSAO     IS 'Data/hora de expiração da sessão';

COMMIT;
