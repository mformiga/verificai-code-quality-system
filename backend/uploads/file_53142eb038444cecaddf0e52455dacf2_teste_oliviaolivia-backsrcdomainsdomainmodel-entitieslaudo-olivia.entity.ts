import {
  Entity,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  PrimaryGeneratedColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Usuario } from './usuario.entity';

@Entity({ name: 's_laudo_olivia', schema: process.env.POSTGRES_SCHEMA })
export class LaudoOlivia {
  @PrimaryGeneratedColumn({ name: 'id_laudo_olivia' })
  id!: number;

  @Column({ name: 'nr_lpco', type: 'varchar', length: 255 })
  nrLpco!: string;

  @Column({ name: 'js_dado_bruto', type: 'json', nullable: true })
  jsDadoBruto?: any | null;

  @Column({ name: 'js_dado_usuario', type: 'json', nullable: true })
  jsDadoUsuario?: any | null;

  @Column({ name: 'ob_laudo_usuario', type: 'varchar', length: 255, nullable: true })
  obLaudoUsuario?: string | null;

  @Column({ name: 'ob_laudo_ia', type: 'varchar', length: 255, nullable: true })
  obLaudoIa?: string | null;

  @CreateDateColumn({ name: 'dh_criacao_registro', type: 'timestamp', default: () => 'NOW()' })
  dhCriacaoRegistro!: Date;

  @UpdateDateColumn({ name: 'dh_atualizacao_registro', type: 'timestamp', default: () => 'NOW()' })
  dhAtualizacaoRegistro!: Date;

  @ManyToOne(() => Usuario, (usuario: Usuario) => usuario.laudos, {
    nullable: false,
    onDelete: 'RESTRICT',
  })
  @JoinColumn([{ name: 'id_usuario', referencedColumnName: 'id' }])
  usuario!: Usuario;
}
