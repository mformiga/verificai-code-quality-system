import { MigrationInterface, QueryRunner } from 'typeorm';

export class Migrations1757515541761 implements MigrationInterface {
  name = 'Migrations1757515541761';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(
      `CREATE TABLE "olivia_mapa"."s_sessao" ("id_sessao" character varying(64) NOT NULL, "dh_criacao_registro" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), "dh_expiracao_sessao" TIMESTAMP WITH TIME ZONE, "id_usuario" integer NOT NULL, CONSTRAINT "PK_4842a973d8b254f89a075d60c3a" PRIMARY KEY ("id_sessao"))`
    );
    await queryRunner.query(
      `CREATE TABLE "olivia_mapa"."s_usuario" ("id_usuario" SERIAL NOT NULL, "nr_cpf" character varying(11) NOT NULL, "nm_usuario" character varying(255) NOT NULL, "dh_criacao_registro" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), "dh_atualizacao_registro" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), CONSTRAINT "UQ_0b9a97349b1b06be3e44922b67a" UNIQUE ("nr_cpf"), CONSTRAINT "PK_4ac900da05e737c4810055d0dc8" PRIMARY KEY ("id_usuario"))`
    );
    await queryRunner.query(
      `CREATE TABLE "olivia_mapa"."s_laudo_olivia" ("id_laudo_olivia" SERIAL NOT NULL, "nr_lpco" character varying(255) NOT NULL, "js_dado_bruto" json, "js_dado_usuario" json, "ob_laudo_usuario" character varying(255), "ob_laudo_ia" character varying(255), "dh_criacao_registro" TIMESTAMP NOT NULL DEFAULT NOW(), "dh_atualizacao_registro" TIMESTAMP NOT NULL DEFAULT NOW(), "id_usuario" integer NOT NULL, CONSTRAINT "PK_b162fbc209bf4950874131af66a" PRIMARY KEY ("id_laudo_olivia"))`
    );
    await queryRunner.query(
      `ALTER TABLE "olivia_mapa"."s_sessao" ADD CONSTRAINT "FK_465dda9a2afa421bd3f92da5b5d" FOREIGN KEY ("id_usuario") REFERENCES "olivia_mapa"."s_usuario"("id_usuario") ON DELETE CASCADE ON UPDATE NO ACTION`
    );
    await queryRunner.query(
      `ALTER TABLE "olivia_mapa"."s_laudo_olivia" ADD CONSTRAINT "FK_3cce3fbff91dc0d2ad8db058dab" FOREIGN KEY ("id_usuario") REFERENCES "olivia_mapa"."s_usuario"("id_usuario") ON DELETE RESTRICT ON UPDATE NO ACTION`
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(
      `ALTER TABLE "olivia_mapa"."s_laudo_olivia" DROP CONSTRAINT "FK_3cce3fbff91dc0d2ad8db058dab"`
    );
    await queryRunner.query(
      `ALTER TABLE "olivia_mapa"."s_sessao" DROP CONSTRAINT "FK_465dda9a2afa421bd3f92da5b5d"`
    );
    await queryRunner.query(`DROP TABLE "olivia_mapa"."s_laudo_olivia"`);
    await queryRunner.query(`DROP TABLE "olivia_mapa"."s_usuario"`);
    await queryRunner.query(`DROP TABLE "olivia_mapa"."s_sessao"`);
  }
}
