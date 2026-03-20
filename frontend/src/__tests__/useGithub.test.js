import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useGithub } from '../composables/useGithub';
import axios from 'axios';

vi.mock('axios');

describe('useGithub', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('by mal inicializovať token z localStorage', () => {
    localStorage.setItem('ghp_token', 'test_token');
    const { token } = useGithub();
    expect(token.value).toBe('test_token');
  });

  it('setToken by mal uložiť token do localStorage', () => {
    const { setToken, token } = useGithub();
    setToken('new_token');
    expect(token.value).toBe('new_token');
    expect(localStorage.getItem('ghp_token')).toBe('new_token');
  });

  it('fetchProfile by mal načítať dáta profilu', async () => {
    const mockProfile = { login: 'testuser', name: 'Test User' };
    axios.get.mockResolvedValueOnce({ data: mockProfile });

    const { fetchProfile, profile, token } = useGithub();
    token.value = 'valid_token';
    
    await fetchProfile();

    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/user'), expect.any(Object));
    expect(profile.value).toEqual(mockProfile);
  });

  it('logout by mal vymazať token a dáta', () => {
    localStorage.setItem('ghp_token', 'test_token');
    const { logout, token } = useGithub();
    logout();
    expect(token.value).toBe('');
    expect(localStorage.getItem('ghp_token')).toBe(null);
  });
});
