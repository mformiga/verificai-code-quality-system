// Arquivo de teste para análise de código
class BadUserController {
    private users: any[] = [];

    constructor() {
        this.users = [];
    }

    // Violação: Lógica de negócio no controller
    validateUser(user: any): boolean {
        // Validação complexa de negócio no controller
        const cpf = user.cpf;
        if (!this.validateCPF(cpf)) {
            return false;
        }

        // Lógica de negócio complexa
        if (user.age < 18) {
            return false;
        }

        return true;
    }

    // Violação: múltiplas responsabilidades
    calculateBonus(user: any): number {
        let bonus = 0;

        // Lógica de negócio complexa no controller
        if (user.salary > 5000) {
            bonus = user.salary * 0.1;
        } else if (user.salary > 3000) {
            bonus = user.salary * 0.05;
        }

        // Regras de negócio adicionais
        if (user.yearsOfService > 5) {
            bonus += 1000;
        }

        return bonus;
    }

    private validateCPF(cpf: string): boolean {
        // Validação de CPF - deveria estar em um serviço separado
        return cpf.length === 11 && !isNaN(Number(cpf));
    }

    // Violação: gerando relatório no controller
    generateUserReport(users: any[]): string {
        let report = "Relatório de Usuários\n\n";

        for (const user of users) {
            report += `Nome: ${user.name}\n`;
            report += `Salário: ${user.salary}\n`;

            // Classificação complexa de negócio
            let classification = "Regular";
            if (user.salary > 10000) {
                classification = "Premium";
            } else if (user.salary > 5000) {
                classification = "VIP";
            }

            report += `Classificação: ${classification}\n\n`;
        }

        return report;
    }

    // Violação: processamento de pagamento no controller
    processPayment(userId: string, amount: number): boolean {
        const user = this.users.find(u => u.id === userId);
        if (!user) {
            return false;
        }

        // Lógica de pagamento complexa
        const fee = amount * 0.02;
        const total = amount + fee;

        if (user.balance >= total) {
            user.balance -= total;
            // Deveria estar em um serviço de pagamento
            console.log(`Pagamento processado: ${total}`);
            return true;
        }

        return false;
    }
}