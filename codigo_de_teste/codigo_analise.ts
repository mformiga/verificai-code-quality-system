import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Exemplo de código com violações de arquitetura para análise

interface UserData {
  id: number;
  name: string;
  email: string;
  cpf: string;
  salary: number;
}

class BadUserController {
  private databaseService: any;
  private emailService: any;

  constructor() {
    // VIOLAÇÃO: Instanciação manual de dependências
    this.databaseService = new DatabaseService();
    this.emailService = new EmailService();
  }

  async createUser(userData: any): Promise<UserData> {
    // VIOLAÇÃO: Lógica de negócio em controller
    const cpfRegex = /^\d{3}\.\d{3}\.\d{3}\-\d{2}$/;
    if (!cpfRegex.test(userData.cpf)) {
      throw new Error('CPF inválido');
    }

    // VIOLAÇÃO: Validação de negócio complexa em camada errada
    if (userData.salary < 1320) {
      userData.salary = 1320; // Salário mínimo
    }

    // VIOLAÇÃO: Acesso direto a banco de dados do controller
    const savedUser = await this.databaseService.save('users', userData);

    // VIOLAÇÃO: Efeito colateral (logging) no controller
    console.log('User created:', savedUser);

    // VIOLAÇÃO: Envio de email direto do controller
    await this.emailService.sendWelcomeEmail(savedUser.email);

    return savedUser;
  }

  // VIOLAÇÃO: Múltiplas responsabilidades em uma única classe
  async calculateBonus(user: UserData): Promise<number> {
    let bonus = 0;

    // Lógica de negócio complexa
    if (user.salary > 5000) {
      bonus = user.salary * 0.1;
    } else if (user.salary > 3000) {
      bonus = user.salary * 0.05;
    }

    // Regra de negócio adicional
    const yearsOfService = this.calculateYearsOfService(user.id);
    if (yearsOfService > 5) {
      bonus += 1000;
    }

    return bonus;
  }

  // VIOLAÇÃO: Mais uma responsabilidade unrelated
  private calculateYearsOfService(userId: number): number {
    // Consulta direta ao banco
    const user = this.databaseService.findById('users', userId);
    const createdAt = new Date(user.createdAt);
    const now = new Date();
    return now.getFullYear() - createdAt.getFullYear();
  }

  // VIOLAÇÃO: Geração de relatórios no controller
  async generateUserReport(userId: number): Promise<string> {
    const user = await this.databaseService.findById('users', userId);
    const bonus = await this.calculateBonus(user);

    // Lógica de formatação e relatório misturada
    return `
      Relatório do Usuário: ${user.name}
      Salário: R$ ${user.salary.toFixed(2)}
      Bônus Calculado: R$ ${bonus.toFixed(2)}
      Status: ${user.salary > 3000 ? 'Senior' : 'Junior'}
    `;
  }
}

// VIOLAÇÃO: Classes fortemente acopladas
class DatabaseService {
  private connection: any;

  constructor() {
    this.connection = this.createConnection();
  }

  private createConnection(): any {
    // Configuração de banco de dados hard-coded
    return {
      host: 'localhost',
      database: 'myapp',
      user: 'admin',
      password: 'secret123'
    };
  }

  async save(table: string, data: any): Promise<any> {
    // Lógica de persistência misturada com validação
    if (!data.id) {
      data.id = Math.floor(Math.random() * 1000000);
    }
    data.createdAt = new Date().toISOString();

    // Simulação de save
    console.log(`Saving to ${table}:`, data);
    return data;
  }

  async findById(table: string, id: number): Promise<any> {
    // Simulação de busca
    return {
      id: id,
      name: 'John Doe',
      email: 'john@example.com',
      cpf: '123.456.789-00',
      salary: 4000,
      createdAt: '2020-01-01T00:00:00.000Z'
    };
  }
}

class EmailService {
  async sendWelcomeEmail(email: string): Promise<void> {
    // VIOLAÇÃO: Implementação específica de SMTP acoplada
    const transporter = nodemailer.createTransporter({
      host: 'smtp.gmail.com',
      port: 587,
      secure: false,
      auth: {
        user: 'myapp@gmail.com',
        pass: 'password123'
      }
    });

    const mailOptions = {
      from: 'myapp@gmail.com',
      to: email,
      subject: 'Bem-vindo ao sistema!',
      text: 'Seu cadastro foi realizado com sucesso.'
    };

    await transporter.sendMail(mailOptions);
  }
}

// VIOLAÇÃO: Componente React com lógica de negócio
const UserProfileComponent: React.FC = () => {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // VIOLAÇÃO: Lógica de negócio e chamada de API no componente
    const fetchUserData = async () => {
      try {
        const response = await axios.get('/api/user/123');
        const userData = response.data;

        // VIOLAÇÃO: Validação de negócio no componente
        if (userData.salary < 1320) {
          userData.salary = 1320;
        }

        setUser(userData);
      } catch (error) {
        // VIOLAÇÃO: Tratamento de erro de negócio no componente
        console.error('Failed to fetch user:', error);
        alert('Erro ao carregar dados do usuário');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  // VIOLAÇÃO: Lógica de formatação e cálculo no componente
  const calculateBonus = (salary: number): number => {
    if (salary > 5000) return salary * 0.1;
    if (salary > 3000) return salary * 0.05;
    return 0;
  };

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <h2>User Profile</h2>
      <p>Name: {user.name}</p>
      <p>Email: {user.email}</p>
      <p>Salary: ${user.salary.toFixed(2)}</p>
      <p>Bonus: ${calculateBonus(user.salary).toFixed(2)}</p>
    </div>
  );
};

export default BadUserController;
export { UserProfileComponent };