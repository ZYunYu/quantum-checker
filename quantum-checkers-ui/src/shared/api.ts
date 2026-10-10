const API_BASE = (process.env.REACT_APP_API_BASE_URL || '').replace(/\/$/, '');

export interface SessionInfo {
  isauthenticated: boolean;
  userId: number | null;
  isStaff: boolean;
  csrfToken: string;
  studentId?: string | null;
  classroom?: {id: number; name: string} | null;
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const method = (options.method || 'GET').toUpperCase();
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const session = await apiRequest<SessionInfo>('/api/session/');
    headers.set('X-CSRFToken', session.csrfToken);
    headers.set('Content-Type', 'application/json');
  }
  const response = await fetch(API_BASE + path, {...options, headers, credentials: 'include'});
  const data = await response.json().catch(() => ({error: 'The server could not complete this request. Please try again.'}));
  if (!response.ok) {
    throw new Error(data.error || data.detail || Object.values(data).flat().join(' ') || 'Request failed.');
  }
  return data as T;
}
