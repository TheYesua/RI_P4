// Cliente API para comunicación con el backend FastAPI

import type { SearchResponse, IndexStats, PipelineAnalysis } from './types';

const API_BASE = 'http://localhost:8000';

export async function search(query: string, lang: string = 'es', topK: number = 20): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    lang: lang,
    top_k: topK.toString(),
  });
  
  const response = await fetch(`${API_BASE}/search?${params}`);
  
  if (!response.ok) {
    throw new Error(`Error en búsqueda: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getStats(): Promise<IndexStats> {
  const response = await fetch(`${API_BASE}/stats`);
  
  if (!response.ok) {
    throw new Error(`Error obteniendo estadísticas: ${response.statusText}`);
  }
  
  return response.json();
}

export async function analyzeQuery(query: string): Promise<PipelineAnalysis> {
  const params = new URLSearchParams({
    query: query,
    language: 'spanish',
  });
  
  const response = await fetch(`${API_BASE}/analyze_query?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Error analizando consulta: ${response.statusText}`);
  }
  
  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/`);
    return response.ok;
  } catch {
    return false;
  }
}
