import React, { useState, useEffect } from 'react';
import axios from 'axios';


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
    this.databaseService = new DatabaseService();
    this.emailService = new EmailService();
  }

  async createUser(userData: any): Promise<UserData> {
    const cpfRegex = /^\d{3}\.\d{3}\.\d{3}\-\d{2}$/;
    if (!cpfRegex.test(userData.cpf)) {
      throw new Error('CPF inválido');
    }

    if (userData.salary < 1320) {
      userData.salary = 1320; // Salário mínimo
    }

    const savedUser = await this.databaseService.save('users', userData);

    console.log('User created:', savedUser);

    await this.emailService.sendWelcomeEmail(savedUser.email);

    return savedUser;
  }

  async calculateBonus(user: UserData): Promise<number> {
    let bonus = 0;

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

  private calculateYearsOfService(userId: number): number {
    const user = this.databaseService.findById('users', userId);
    const createdAt = new Date(user.createdAt);
    const now = new Date();
    return now.getFullYear() - createdAt.getFullYear();
  }

  async generateUserReport(userId: number): Promise<string> {
    const user = await this.databaseService.findById('users', userId);
    const bonus = await this.calculateBonus(user);

    return `
      Relatório do Usuário: ${user.name}
      Salário: R$ ${user.salary.toFixed(2)}
      Bônus Calculado: R$ ${bonus.toFixed(2)}
      Status: ${user.salary > 3000 ? 'Senior' : 'Junior'}
    `;
  }
}

class DatabaseService {
  private connection: any;

  constructor() {
    this.connection = this.createConnection();
  }

  private createConnection(): any {
    return {
      host: 'localhost',
      database: 'myapp',
      user: 'admin',
      password: 'secret123'
    };
  }

  async save(table: string, data: any): Promise<any> {
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

const UserProfileComponent: React.FC = () => {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get('/api/user/123');
        const userData = response.data;

        if (userData.salary < 1320) {
          userData.salary = 1320;
        }

        setUser(userData);
      } catch (error) {
        console.error('Failed to fetch user:', error);
        alert('Erro ao carregar dados do usuário');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

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