// =====================================================
// ARQUIVO DE TESTE COM VIOLAÇÕES INTENCIONAIS
// Este código contém erros específicos para testar a análise
// =====================================================

import { DatabaseService } from 'typeorm';
import { EmailService } from './email-service';

// ===========================================
// VIOLAÇÃO DE CAMADAS - LÓGICA DE NEGÓCIO EM CONTROLLER
// ===========================================

interface UserController {
    createUser: (userData: any) => Promise<any>;
    updateUser: (id: number, userData: any) => Promise<any>;
    deleteUser: (id: number) => Promise<any>;
    calculateUserBonus: (userId: number) => Promise<number>;
    generateUserReport: (userId: number) => Promise<string>;
    processPayment: (userId: number, amount: number) => Promise<boolean>;
}

class BadUserController implements UserController {
    private db: DatabaseService;

    constructor(db: DatabaseService) {
        this.db = db;
    }

    // VIOLAÇÃO: Controller contendo lógica de negócio complexa
    async createUser(userData: any) {
        // VIOLAÇÃO DE CAMADAS: Regra de negócio de validação de CPF no controller
        const cpfRegex = /^\d{3}\.\d{3}\.\d{3}\-\d{2}$/;
        if (!cpfRegex.test(userData.cpf)) {
            throw new Error('CPF inválido');
        }

        // VIOLAÇÃO DE CAMADAS: Cálculo de desconto no controller
        let discount = 0;
        if (userData.age > 60) {
            discount = userData.total * 0.1;
        } else if (userData.age > 30) {
            discount = userData.total * 0.05;
        }

        const user = {
            ...userData,
            discount,
            finalTotal: userData.total - discount,
            status: 'active',
            createdAt: new Date()
        };

        return await this.db.save('users', user);
    }

    // VIOLAÇÃO DE CAMADAS: Lógica de negócio financeira no controller
    async calculateUserBonus(userId: number): Promise<number> {
        const user = await this.db.findById('users', userId);

        // Lógica complexa de cálculo de bônus que deveria estar em um serviço
        let bonus = 0;
        const monthsActive = this.calculateMonthsActive(user.createdAt);

        if (monthsActive > 12) {
            bonus = user.salary * 0.15;
        } else if (monthsActive > 6) {
            bonus = user.salary * 0.10;
        } else if (monthsActive > 3) {
            bonus = user.salary * 0.05;
        }

        // Regra de negócio: bônus adicional por performance
        const performance = await this.db.query(
            'SELECT AVG(score) as avg_score FROM user_performance WHERE user_id = ?',
            [userId]
        );

        if (performance.avg_score > 8) {
            bonus *= 1.2; // 20% extra
        }

        return bonus;
    }

    // VIOLAÇÃO DE CAMADAS: Geração de relatório complexo no controller
    async generateUserReport(userId: number): Promise<string> {
        const user = await this.db.findById('users', userId);
        const purchases = await this.db.find('purchases', { userId });
        const payments = await this.db.find('payments', { userId });

        // Lógica de negócio complexa de análise de dados
        let report = `Relatório do Usuário: ${user.name}\n`;
        report += `----------------------------------------\n`;

        const totalSpent = purchases.reduce((sum, p) => sum + p.amount, 0);
        const avgPurchase = totalSpent / purchases.length;

        report += `Total gasto: R$ ${totalSpent.toFixed(2)}\n`;
        report += `Média por compra: R$ ${avgPurchase.toFixed(2)}\n`;

        // Classificação baseada em gasto
        if (totalSpent > 10000) {
            report += 'Classificação: Cliente Premium\n';
        } else if (totalSpent > 5000) {
            report += 'Classificação: Cliente VIP\n';
        } else {
            report += 'Classificação: Cliente Regular\n';
        }

        return report;
    }

    // VIOLAÇÃO DE CAMADAS: Processamento de pagamento no controller
    async processPayment(userId: number, amount: number): Promise<boolean> {
        const user = await this.db.findById('users', userId);

        // Lógica de negócio de validação e processamento
        if (user.balance < amount) {
            throw new Error('Saldo insuficiente');
        }

        // Taxas baseadas em regras de negócio
        let fee = 0;
        if (amount > 1000) {
            fee = amount * 0.02; // 2%
        } else if (amount > 500) {
            fee = amount * 0.01; // 1%
        }

        // Processamento complexo que deveria estar em um serviço
        const transaction = {
            userId,
            amount,
            fee,
            total: amount + fee,
            status: 'processing',
            timestamp: new Date()
        };

        await this.db.save('transactions', transaction);

        // Atualização de saldo
        user.balance -= (amount + fee);
        await this.db.save('users', user);

        // Envio de notificação
        this.sendNotification(user.email, 'Pagamento processado', `Pagamento de R$${amount} processado com sucesso.`);

        return true;
    }

    private calculateMonthsActive(createdAt: Date): number {
        const now = new Date();
        return (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24 * 30);
    }

    private sendNotification(email: string, subject: string, message: string) {
        // VIOLAÇÃO: Lógica de notificação no controller
        console.log(`Email enviado para ${email}: ${subject} - ${message}`);
    }
}

// ===========================================
// VIOLAÇÃO SRP - CLASSE COM MÚLTIPLAS RESPONSABILIDADES
// ===========================================

class UserService {
    private db: DatabaseService;
    private emailService: EmailService;

    constructor(db: DatabaseService, emailService: EmailService) {
        this.db = db;
        this.emailService = emailService;
    }

    // VIOLAÇÃO SRP: Gerenciamento de usuários
    async createUser(userData: any): Promise<any> {
        const user = { ...userData, createdAt: new Date() };
        return await this.db.save('users', user);
    }

    // VIOLAÇÃO SRP: Validação de dados (deveria ser separada)
    validateUser(userData: any): boolean {
        if (!userData.name || userData.name.length < 3) {
            return false;
        }
        if (!userData.email || !userData.email.includes('@')) {
            return false;
        }
        return true;
    }

    // VIOLAÇÃO SRP: Formatação de dados (deveria ser separada)
    formatUserData(userData: any): any {
        return {
            ...userData,
            name: userData.name.trim(),
            email: userData.email.toLowerCase(),
            phone: this.formatPhone(userData.phone)
        };
    }

    // VIOLAÇÃO SRP: Envio de emails (deveria estar em um serviço separado)
    async sendWelcomeEmail(user: any): Promise<void> {
        const subject = 'Bem-vindo ao nosso sistema!';
        const body = `Olá ${user.name}, seja bem-vindo!`;
        await this.emailService.send(user.email, subject, body);
    }

    // VIOLAÇÃO SRP: Geração de relatórios
    async generateUserReport(userId: number): Promise<string> {
        const user = await this.db.findById('users', userId);
        return `Relatório do usuário: ${user.name}`;
    }

    // VIOLAÇÃO SRP: Cálculos complexos
    calculateUserMetrics(user: any): any {
        const metrics = {
            completeness: this.calculateProfileCompleteness(user),
            engagement: this.calculateEngagementScore(user),
            health: this.calculateAccountHealth(user)
        };
        return metrics;
    }

    // VIOLAÇÃO SRP: Autenticação
    authenticateUser(email: string, password: string): Promise<any> {
        return this.db.findOne('users', { email, password });
    }

    // VIOLAÇÃO SRP: Autorização
    checkPermissions(userId: number, resource: string): Promise<boolean> {
        return this.db.findOne('permissions', { userId, resource });
    }

    private formatPhone(phone: string): string {
        return phone.replace(/\D/g, '');
    }

    private calculateProfileCompleteness(user: any): number {
        // Lógica complexa de cálculo
        let score = 0;
        if (user.name) score += 25;
        if (user.email) score += 25;
        if (user.phone) score += 25;
        if (user.address) score += 25;
        return score;
    }

    private calculateEngagementScore(user: any): number {
        // Lógica complexa de cálculo
        return Math.random() * 100;
    }

    private calculateAccountHealth(user: any): number {
        // Lógica complexa de cálculo
        return Math.random() * 100;
    }
}

// ===========================================
// VIOLAÇÃO DI - INSTANCIAÇÃO MANUAL DE DEPENDÊNCIAS
// ===========================================

class BadOrderService {
    // VIOLAÇÃO DI: Instanciação direta de dependências
    private db = new DatabaseService();
    private emailService = new EmailService();
    private userService = new UserService(this.db, this.emailService);
    private paymentService = new PaymentService();
    private notificationService = new NotificationService();

    async processOrder(orderData: any): Promise<any> {
        // VIOLAÇÃO DI: Criação manual de múltiplas dependências
        const validator = new OrderValidator();
        const calculator = new PriceCalculator();
        const processor = new OrderProcessor();
        const logger = new OrderLogger();

        try {
            validator.validate(orderData);
            const price = calculator.calculate(orderData);
            const result = processor.process(orderData, price);
            logger.logSuccess(result);

            return result;
        } catch (error) {
            logger.logError(error);
            throw error;
        }
    }
}

// Classes de serviço com dependências manualmente criadas
class PaymentService {
    private db = new DatabaseService();
    private emailService = new EmailService();

    async processPayment(data: any): Promise<boolean> {
        // Processamento complexo sem injeção de dependência
        return true;
    }
}

class NotificationService {
    private emailService = new EmailService();
    private smsService = new SMSService();

    async sendNotification(message: string): Promise<void> {
        // Notificação sem injeção de dependência
    }
}

class SMSService {
    // Serviço de SMS hardcoded
}

class OrderValidator {
    // Validação hardcoded sem dependências injetadas
    validate(order: any): void {
        if (!order.items || order.items.length === 0) {
            throw new Error('Order must have items');
        }
    }
}

class PriceCalculator {
    // Cálculo hardcoded sem dependências injetadas
    calculate(order: any): number {
        return order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    }
}

class OrderProcessor {
    private db = new DatabaseService();

    process(order: any, price: number): any {
        return { orderId: Date.now(), status: 'processed', total: price };
    }
}

class OrderLogger {
    private db = new DatabaseService();

    logSuccess(result: any): void {
        console.log('Order processed successfully:', result);
    }

    logError(error: any): void {
        console.error('Order processing failed:', error);
    }
}

export { BadUserController, UserService, BadOrderService };