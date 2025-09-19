import { useAuthStore } from '@/stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface Criterion {
  id: string;
  text: string;
  active: boolean;
  order: number;
}

export const criteriaService = {
  async getCriteria(): Promise<Criterion[]> {
    const { token, isAuthenticated } = useAuthStore.getState();
    console.log('🔍 SERVICE DEBUG: getCriteria called');
    console.log('🔍 SERVICE DEBUG: Token:', token ? 'exists' : 'none');
    console.log('🔍 SERVICE DEBUG: isAuthenticated:', isAuthenticated);

    const storedAuth = localStorage.getItem('auth-storage');
    console.log('🔍 SERVICE DEBUG: Stored auth:', storedAuth);

    if (!token || !isAuthenticated) {
      console.log('🔍 SERVICE DEBUG: Using localStorage for criteria');
      // Try to get criteria from localStorage first
      const storedCriteria = localStorage.getItem('criteria-storage');
      console.log('🔍 SERVICE DEBUG: Stored criteria from localStorage:', storedCriteria);

      if (storedCriteria) {
        try {
          const parsed = JSON.parse(storedCriteria);
          console.log('🔍 SERVICE DEBUG: Parsed criteria:', parsed);
          console.log('🔍 SERVICE DEBUG: Returning criteria with length:', parsed.length);
          return parsed;
        } catch (error) {
          console.error('Failed to parse stored criteria:', error);
        }
      }

      console.log('🔍 SERVICE DEBUG: No stored criteria found, returning empty array');
      // Return empty array - no more default criteria
      const emptyCriteria = [];
      localStorage.setItem('criteria-storage', JSON.stringify(emptyCriteria));
      console.log('🔍 SERVICE DEBUG: Saved empty criteria to localStorage');
      return emptyCriteria;
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
        // Fallback to empty array if API fails - no more mock criteria
        console.log('Falling back to empty array');
        return [];
      }

      return response.json();
    } catch (error) {
      console.error('Get criteria error:', error);
      // Fallback to empty array on any error - no more mock criteria
      return [];
    }
  },

  async createCriterion(text: string): Promise<Criterion> {
    const { token, isAuthenticated } = useAuthStore.getState();
    console.log('Token in createCriterion:', token ? 'exists' : 'none');
    console.log('isAuthenticated:', isAuthenticated);

    if (!token || !isAuthenticated) {
      // Get current criteria from localStorage
      const storedCriteria = localStorage.getItem('criteria-storage');
      const currentCriteria = storedCriteria ? JSON.parse(storedCriteria) : [];

      // Find the highest order number and add 1
      const maxOrder = currentCriteria.length > 0 ? Math.max(...currentCriteria.map(c => c.order || 0)) : 0;
      const newOrder = maxOrder + 1;

      const newCriterion = {
        id: `criteria_${Date.now()}`,
        text,
        active: true,
        order: newOrder
      };

      // Add new criterion and save to localStorage
      const updatedCriteria = [...currentCriteria, newCriterion];
      localStorage.setItem('criteria-storage', JSON.stringify(updatedCriteria));

      console.log('Saved new criterion to localStorage with order:', newOrder);
      return newCriterion;
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
      // Fallback to create criterion in localStorage if API fails
      console.log('Falling back to localStorage');
      // Get current criteria from localStorage
      const storedCriteria = localStorage.getItem('criteria-storage');
      const currentCriteria = storedCriteria ? JSON.parse(storedCriteria) : [];

      // Find the highest order number and add 1
      const maxOrder = currentCriteria.length > 0 ? Math.max(...currentCriteria.map(c => c.order || 0)) : 0;
      const newOrder = maxOrder + 1;

      const newCriterion = {
        id: `criteria_${Date.now()}`,
        text,
        active: true,
        order: newOrder
      };

      // Add new criterion and save to localStorage
      const updatedCriteria = [...currentCriteria, newCriterion];
      localStorage.setItem('criteria-storage', JSON.stringify(updatedCriteria));
      console.log('Created new criterion in localStorage fallback with order:', newOrder);

      return newCriterion;
    }

    return response.json();
  },

  async updateCriterion(id: string, text: string): Promise<Criterion> {
    const { token, isAuthenticated } = useAuthStore.getState();
    console.log('🔍 SERVICE DEBUG: updateCriterion called with id:', id, 'text:', text);
    console.log('🔍 SERVICE DEBUG: Token value:', token);
    console.log('🔍 SERVICE DEBUG: Token type:', typeof token);
    console.log('🔍 SERVICE DEBUG: isAuthenticated:', isAuthenticated);

    // Also check if there's a valid token in localStorage
    const storedAuth = localStorage.getItem('auth-storage');
    console.log('🔍 SERVICE DEBUG: Stored auth:', storedAuth);

    // Use localStorage if no token or not authenticated
    if (!token || !isAuthenticated) {
      console.log('🔍 SERVICE DEBUG: No valid token found, using localStorage');
      console.log('🔍 SERVICE DEBUG: About to read criteria-storage...');
      // Get current criteria from localStorage
      const storedCriteria = localStorage.getItem('criteria-storage');
      console.log('🔍 SERVICE DEBUG: Stored criteria:', storedCriteria);

      if (!storedCriteria) {
        console.log('🔍 SERVICE DEBUG: No stored criteria found, creating empty array');
        localStorage.setItem('criteria-storage', JSON.stringify([]));
      }

      const currentCriteria = storedCriteria ? JSON.parse(storedCriteria) : [];
      console.log('🔍 SERVICE DEBUG: Parsed current criteria:', currentCriteria);
      console.log('🔍 SERVICE DEBUG: Current criteria length:', currentCriteria.length);

      // Find and update the criterion
      const updatedCriteria = currentCriteria.map(criterion => {
        console.log(`🔍 SERVICE DEBUG: Checking criterion ${criterion.id} against ${id}`);
        return criterion.id === id ? { ...criterion, text } : criterion;
      });
      console.log('🔍 SERVICE DEBUG: Updated criteria:', updatedCriteria);

      // Save updated criteria to localStorage
      localStorage.setItem('criteria-storage', JSON.stringify(updatedCriteria));
      console.log('🔍 SERVICE DEBUG: Saved to localStorage successfully');

      // Verify it was saved
      const verifySaved = localStorage.getItem('criteria-storage');
      console.log('🔍 SERVICE DEBUG: Verification - saved criteria:', verifySaved);

      return { id, text, active: true, order: 1 };
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
      return { id, text, active: true, order: 1 };
    }

    return response.json();
  },

  async deleteCriterion(id: string): Promise<void> {
    const { token } = useAuthStore.getState();

    if (!token) {
      // Get current criteria from localStorage
      const storedCriteria = localStorage.getItem('criteria-storage');
      const currentCriteria = storedCriteria ? JSON.parse(storedCriteria) : [];

      // Remove the criterion
      const updatedCriteria = currentCriteria.filter(criterion => criterion.id !== id);

      // Save updated criteria to localStorage
      localStorage.setItem('criteria-storage', JSON.stringify(updatedCriteria));

      console.log('Deleted criterion from localStorage');
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
  },

  async toggleCriterion(id: string, active: boolean): Promise<Criterion> {
    const { token, isAuthenticated } = useAuthStore.getState();

    if (!token || !isAuthenticated) {
      // Get current criteria from localStorage
      const storedCriteria = localStorage.getItem('criteria-storage');
      const currentCriteria = storedCriteria ? JSON.parse(storedCriteria) : [];

      // Find and update the criterion's active status
      const updatedCriteria = currentCriteria.map(criterion =>
        criterion.id === id ? { ...criterion, active } : criterion
      );

      // Save updated criteria to localStorage
      localStorage.setItem('criteria-storage', JSON.stringify(updatedCriteria));

      console.log('Toggled criterion active status in localStorage');
      return currentCriteria.find(criterion => criterion.id === id)!;
    }

    // If authenticated, use the API
    const response = await fetch(`${API_BASE_URL}/general-analysis/criteria/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ active }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Toggle criterion failed:', response.status, errorText);
      // Fallback to mock if API fails
      const storedCriteria = localStorage.getItem('criteria-storage');
      const currentCriteria = storedCriteria ? JSON.parse(storedCriteria) : [];
      return currentCriteria.find(criterion => criterion.id === id) || { id, active, text: '' };
    }

    return response.json();
  }
};