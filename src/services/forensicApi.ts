import { DebateApiResponse, InvestigationRecord } from '../types';

/**
 * Backend URL configuration:
 * Uses VITE_BACKEND_URL or VITE_API_URL from environment variables if defined (defaulting to http://localhost:3000).
 * If accessed remotely in a hosted container preview while VITE_BACKEND_URL points to localhost,
 * dynamically falls back to the current window origin so that browser requests route safely through Express.
 */
const RAW_BACKEND_URL = (
  import.meta.env.VITE_BACKEND_URL ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:3000'
).trim();

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined' && window.location) {
    const isLocalhost =
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname === '0.0.0.0';
    if (
      !isLocalhost ||
      (window.location.protocol === 'https:' && RAW_BACKEND_URL.startsWith('http:'))
    ) {
      return '';
    }
  }
  return RAW_BACKEND_URL.replace(/\/+$/, '');
}

export const BACKEND_URL = RAW_BACKEND_URL.replace(/\/+$/, '');

const STORAGE_KEY = 'forenxai_investigations';
const DEFAULT_TIMEOUT_MS = 120000; // 2 minutes for deep forensic analysis

export class ForensicApiError extends Error {
  statusCode?: number;
  details?: any;

  constructor(message: string, statusCode?: number, details?: any) {
    super(message);
    this.name = 'ForensicApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * Uploads an image file and executes the 4-agent LangGraph forensic debate.
 * Endpoint: POST /debate
 */
export async function uploadImageAndDebate(
  file: File,
  signal?: AbortSignal
): Promise<DebateApiResponse> {
  if (!file) {
    throw new ForensicApiError('No image file selected for forensic investigation.');
  }

  if (file.size === 0) {
    throw new ForensicApiError('The selected image file is empty (0 bytes). Please select a valid image.');
  }

  const formData = new FormData();
  formData.append('image', file);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, DEFAULT_TIMEOUT_MS);

  if (signal) {
    signal.addEventListener('abort', () => controller.abort());
  }

  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/debate`;

  try {
    const response = await fetch(targetUrl, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const rawText = await response.text();
    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.toLowerCase().includes('application/json');
    const isHtml = rawText.trim().startsWith('<') || rawText.includes('<!doctype') || rawText.includes('<html');

    let data: any = null;
    if (isJson && !isHtml && rawText.trim().length > 0) {
      try {
        data = JSON.parse(rawText);
      } catch (parseErr) {
        console.warn('[ForenXAI API] JSON parse warning:', parseErr);
        data = null;
      }
    }

    if (!response.ok || isHtml) {
      if (response.status === 502 || response.status === 503 || response.status === 504 || isHtml) {
        throw new ForensicApiError(
          'The forensic engine is currently starting up or busy. Please wait a few seconds and try again.',
          response.status || 503,
          data
        );
      }

      let errorMsg = `Forensic investigation failed with HTTP ${response.status}: ${response.statusText}`;
      if (typeof data?.detail === 'string') {
        errorMsg = data.detail;
      } else if (Array.isArray(data?.detail)) {
        errorMsg = data.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
      } else if (typeof data?.error === 'string') {
        errorMsg = data.error;
      } else if (rawText && rawText.length < 300 && !rawText.includes('<html') && !rawText.includes('<!doctype')) {
        errorMsg = rawText;
      }

      throw new ForensicApiError(errorMsg, response.status, data);
    }

    if (!data || typeof data !== 'object') {
      const hint = isHtml ? ' The server returned an HTML error page instead of JSON.' : '';
      throw new ForensicApiError(
        `Invalid response format received from forensic debate engine.${hint}`
      );
    }

    if (data.error && !data.debate && !data.evidence) {
      throw new ForensicApiError(data.error, response.status, data);
    }

    return data as DebateApiResponse;
  } catch (error: any) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new ForensicApiError(
        'Investigation timed out. The forensic analysis and multi-agent debate took too long to complete. Please try again.'
      );
    }

    if (error instanceof ForensicApiError) {
      throw error;
    }

    throw new ForensicApiError(
      'Unable to connect to ForenXAI forensic service. Please verify the backend is running.'
    );
  }
}

/**
 * Executes the 4-agent LangGraph forensic debate on previously extracted evidence.
 * Endpoint: POST /debate-evidence
 */
export async function runDebateOnEvidence(
  payload: { analysis_result?: any; evidence?: any[]; image_id?: string },
  signal?: AbortSignal
): Promise<{ debate: any }> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, DEFAULT_TIMEOUT_MS);

  if (signal) {
    signal.addEventListener('abort', () => controller.abort());
  }

  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/debate-evidence`;

  try {
    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const rawText = await response.text();
    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.toLowerCase().includes('application/json');
    const isHtml = rawText.trim().startsWith('<') || rawText.includes('<!doctype') || rawText.includes('<html');

    let data: any = null;
    if (isJson && !isHtml && rawText.trim().length > 0) {
      try {
        data = JSON.parse(rawText);
      } catch (parseErr) {
        console.warn('[ForenXAI API] JSON parse warning in debate-evidence:', parseErr);
        data = null;
      }
    }

    if (!response.ok || isHtml) {
      if (response.status === 502 || response.status === 503 || response.status === 504 || isHtml) {
        throw new ForensicApiError(
          'The forensic debate engine is currently initializing. Please try again shortly.',
          response.status || 503,
          data
        );
      }

      let errorMsg = `Evidence debate failed with status ${response.status}`;
      if (typeof data?.detail === 'string') {
        errorMsg = data.detail;
      } else if (Array.isArray(data?.detail)) {
        errorMsg = data.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
      } else if (typeof data?.error === 'string') {
        errorMsg = data.error;
      } else if (rawText && rawText.length < 300 && !rawText.includes('<html') && !rawText.includes('<!doctype')) {
        errorMsg = rawText;
      }
      throw new ForensicApiError(errorMsg, response.status, data);
    }

    if (!data || typeof data !== 'object') {
      const hint = isHtml ? ' The server returned an HTML error page instead of JSON.' : '';
      throw new ForensicApiError(`Invalid response format received from debate-evidence.${hint}`);
    }

    return data;
  } catch (error: any) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new ForensicApiError('Debate on evidence timed out.');
    }

    if (error instanceof ForensicApiError) {
      throw error;
    }

    throw new ForensicApiError('Failed to execute debate on extracted evidence.');
  }
}

/**
 * Verifies backend and forensic engine service health.
 * Endpoint: GET /api/health
 */
export async function checkApiHealth(
  signal?: AbortSignal
): Promise<{ status: string; service?: string; pythonEngine?: string }> {
  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/health`;

  try {
    const response = await fetch(targetUrl, {
      method: 'GET',
      signal,
    });

    if (!response.ok) {
      throw new ForensicApiError(`Health check failed with status ${response.status}`, response.status);
    }

    return await response.json();
  } catch (error: any) {
    if (error instanceof ForensicApiError) {
      throw error;
    }
    throw new ForensicApiError('Backend health service unreachable.');
  }
}

/**
 * Local Storage Persistence Layer
 * Operates purely client-side without external database.
 */
export function getStoredInvestigations(): InvestigationRecord[] {
  try {
    const serialized = localStorage.getItem(STORAGE_KEY);
    if (!serialized) return [];
    const parsed = JSON.parse(serialized);
    if (Array.isArray(parsed)) {
      return parsed;
    }
    return [];
  } catch (err) {
    console.warn('Failed to parse investigations from localStorage:', err);
    return [];
  }
}

export function saveInvestigation(record: InvestigationRecord): void {
  try {
    const existing = getStoredInvestigations();
    // Filter out duplicate ID if already exists
    const filtered = existing.filter((item) => item.id !== record.id);
    // Keep newest at the top, max 20 records to preserve storage quota
    const updated = [record, ...filtered].slice(0, 20);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.warn('Failed to save investigation to localStorage:', err);
  }
}

export function getInvestigationById(id: string): InvestigationRecord | null {
  const list = getStoredInvestigations();
  return list.find((item) => item.id === id) || null;
}

export function deleteInvestigation(id: string): void {
  try {
    const existing = getStoredInvestigations();
    const updated = existing.filter((item) => item.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.warn('Failed to delete investigation from localStorage:', err);
  }
}

export function clearAllInvestigations(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (err) {
    console.warn('Failed to clear investigations from localStorage:', err);
  }
}
