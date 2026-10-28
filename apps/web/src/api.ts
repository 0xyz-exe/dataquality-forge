const API_BASE = '/api/v1';

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview');
  return res.json();
}

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function createProject(name: string, description?: string) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to create project');
  }
  return res.json();
}

export async function deleteProject(id: string) {
  const res = await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete project');
  return res.json();
}

export async function fetchDatasets(projectId?: string) {
  const url = projectId ? `${API_BASE}/datasets?project_id=${projectId}` : `${API_BASE}/datasets`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch datasets');
  return res.json();
}

export async function fetchDataset(id: string) {
  const res = await fetch(`${API_BASE}/datasets/${id}`);
  if (!res.ok) throw new Error('Failed to fetch dataset');
  return res.json();
}

export async function uploadDataset(file: File, projectId: string, name?: string, description?: string) {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('project_id', projectId);
  if (name) fd.append('name', name);
  if (description) fd.append('description', description);

  const res = await fetch(`${API_BASE}/datasets`, {
    method: 'POST',
    body: fd,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to upload dataset');
  }
  return res.json();
}

export async function deleteDataset(id: string) {
  const res = await fetch(`${API_BASE}/datasets/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete dataset');
  return res.json();
}

export async function fetchDatasetPreview(id: string, limit = 50) {
  const res = await fetch(`${API_BASE}/datasets/${id}/preview?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch preview');
  return res.json();
}

export async function runProfile(id: string, sampleLimit?: number) {
  const url = sampleLimit ? `${API_BASE}/datasets/${id}/profile?sample_limit=${sampleLimit}` : `${API_BASE}/datasets/${id}/profile`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to profile dataset');
  return res.json();
}

export async function fetchLatestProfile(id: string) {
  const res = await fetch(`${API_BASE}/datasets/${id}/profile`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchRules(datasetId: string) {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/rules`);
  if (!res.ok) throw new Error('Failed to fetch rules');
  return res.json();
}

export async function createRule(datasetId: string, ruleData: any) {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ruleData),
  });
  if (!res.ok) throw new Error('Failed to create rule');
  return res.json();
}

export async function deleteRule(id: string) {
  const res = await fetch(`${API_BASE}/rules/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete rule');
  return res.json();
}

export async function runValidation(datasetId: string) {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/validation-runs`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to run validation');
  return res.json();
}

export async function fetchValidationRuns(datasetId?: string) {
  const url = datasetId ? `${API_BASE}/validation-runs?dataset_id=${datasetId}` : `${API_BASE}/validation-runs`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch validation runs');
  return res.json();
}

export async function fetchValidationRun(runId: string) {
  const res = await fetch(`${API_BASE}/validation-runs/${runId}`);
  if (!res.ok) throw new Error('Failed to fetch validation run');
  return res.json();
}

export async function fetchSchemaDiff(datasetId: string) {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/schema-diff`);
  if (!res.ok) throw new Error('Failed to fetch schema diff');
  return res.json();
}

export async function saveExpectedSchema(datasetId: string, columns: any, name = 'Default Expected Schema') {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/expected-schema`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, columns }),
  });
  if (!res.ok) throw new Error('Failed to save expected schema');
  return res.json();
}
