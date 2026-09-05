import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import api from './api';

describe('API Service', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should have correct default Content-Type header', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('should add Authorization header if token exists in localStorage', () => {
    localStorage.setItem('token', 'fake-token');
    
    const config = { headers: {} };
    // Get the registered request interceptor
    const interceptorHandler = api.interceptors.request.handlers[0].fulfilled;
    const resultConfig = interceptorHandler(config);
    
    expect(resultConfig.headers.Authorization).toBe('Bearer fake-token');
  });

  it('should not add Authorization header if no token exists in localStorage', () => {
    const config = { headers: {} };
    const interceptorHandler = api.interceptors.request.handlers[0].fulfilled;
    const resultConfig = interceptorHandler(config);
    
    expect(resultConfig.headers.Authorization).toBeUndefined();
  });
});
