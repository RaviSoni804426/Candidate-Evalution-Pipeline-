const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = 'Request failed';
    try {
      const data = await response.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function getDashboard() {
  return request('/dashboard');
}

export async function getLatestJob() {
  return request('/job-descriptions/latest');
}

export async function createJobDescription(payload) {
  return request('/job-descriptions', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function evaluateCandidate(formData) {
  return request('/evaluate-candidate', {
    method: 'POST',
    body: formData,
  });
}

export async function bulkEvaluateCandidates(formData) {
  return request('/bulk-evaluate-candidates', {
    method: 'POST',
    body: formData,
  });
}

export async function shortlistCandidate(payload) {
  return request('/shortlist-candidate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export { API_BASE_URL };
