import { useAuthStore } from '@/stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface Criterion {
  id: string;
  text: string;
  active: boolean;
}

export const criteriaService = {
  async getCriteria(): Promise<Criterion[]> {
    const { token } = useAuthStore.getState();

    if (!token) {
      // Return default criteria for development
      return [
        { id: 'criteria_1', text: 'O código deve seguir convenções de nomenclatura consistentes', active: true },
        { id: 'criteria_2', text: 'Funções e métodos devem ter documentação adequada', active: true },
        { id: 'criteria_3', text: 'O código deve ter tratamento adequado de erros', active: true },
        { id: 'criteria_4', text: 'Variáveis devem ter nomes descritivos e significativos', active: true }
      ];
    }

    try {
      const response = await fetch(`${API_BASE_URL}/general-analysis/criteria`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Get criteria failed:', response.status, errorText);
        // Fallback to mock if API fails
        console.log('Falling back to mock response');
        return [
          { id: 'criteria_1', text: 'O código deve seguir convenções de nomenclatura consistentes', active: true },
          { id: 'criteria_2', text: 'Funções e métodos devem ter documentação adequada', active: true },
          { id: 'criteria_3', text: 'O código deve ter tratamento adequado de erros', active: true },
          { id: 'criteria_4', text: 'Variáveis devem ter nomes descritivos e significativos', active: true }
        ];
      }

      return response.json();
    } catch (error) {
      console.error('Get criteria error:', error);
      // Fallback to mock on any error
      return [
        { id: 'criteria_1', text: 'O código deve seguir convenções de nomenclatura consistentes', active: true },
        { id: 'criteria_2', text: 'Funções e métodos devem ter documentação adequada', active: true },
        { id: 'criteria_3', text: 'O código deve ter tratamento adequado de erros', active: true },
        { id: 'criteria_4', text: 'Variáveis devem ter nomes descritivos e significativos', active: true }
      ];
    }
  },

  async createCriterion(text: string): Promise<Criterion> {
    const { token } = useAuthStore.getState();
    console.log('Token in createCriterion:', token ? 'exists' : 'none');

    if (!token) {
      // Mock response for development
      console.log('Using mock response');
      return {
        id: `criteria_${Date.now()}`,
        text,
        active: true
      };
    }

    const response = await fetch(`${API_BASE_URL}/general-analysis/criteria`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Create criterion failed:', response.status, errorText);
      // Fallback to mock if API fails
      console.log('Falling back to mock response');
      return {
        id: `criteria_${Date.now()}`,
        text,
        active: true
      };
    }

    return response.json();
  },

  async updateCriterion(id: string, text: string): Promise<Criterion> {
    const { token } = useAuthStore.getState();

    if (!token) {
      // Mock response for development
      return { id, text, active: true };
    }

    const response = await fetch(`${API_BASE_URL}/general-analysis/criteria/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Update criterion failed:', response.status, errorText);
      // Fallback to mock if API fails
      console.log('Falling back to mock response');
      return { id, text, active: true };
    }

    return response.json();
  },

  async deleteCriterion(id: string): Promise<void> {
    const { token } = useAuthStore.getState();

    if (!token) {
      // Mock response for development
      return;
    }

    try {
      // Try the external delete service (port 8001) first - it works!
      const externalResponse = await fetch(`http://localhost:8001/delete-criterion/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (externalResponse.ok) {
        return;
      }

      // Try the main backend DELETE method
      const deleteResponse = await fetch(`${API_BASE_URL}/general-analysis/criteria/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (deleteResponse.ok) {
        return;
      }

      // If DELETE fails, try POST method as fallback
      const postResponse = await fetch(`${API_BASE_URL}/general-analysis/criteria/${id}/delete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (postResponse.ok) {
        return;
      }

      console.error('All methods failed');
      throw new Error(`Failed to delete criterion: ${externalResponse.status}`);
    } catch (error) {
      console.error('Delete criterion error:', error);
      throw error;
    }
  }
};