import { useState, useEffect } from 'react';
import { Search, BookOpen, Clock, Database, ExternalLink, AlertCircle, Loader2, Globe } from 'lucide-react';
import { search, getStats, checkHealth } from './api';
import type { SearchResult, IndexStats } from './types';

// Nombres de idiomas para mostrar
const LANGUAGE_NAMES: Record<string, string> = {
  es: 'Castellano',
  ca: 'Catalán',
  pt: 'Portugués',
};

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [selectedLang, setSelectedLang] = useState<string>('es');
  const [availableLanguages, setAvailableLanguages] = useState<string[]>([]);

  // Verificar estado del backend al cargar
  useEffect(() => {
    const checkBackend = async () => {
      const online = await checkHealth();
      setBackendOnline(online);
      if (online) {
        try {
          const indexStats = await getStats();
          setStats(indexStats);
          if (indexStats.available_languages && indexStats.available_languages.length > 0) {
            setAvailableLanguages(indexStats.available_languages);
            // Seleccionar el primer idioma disponible si el actual no esta
            if (!indexStats.available_languages.includes(selectedLang)) {
              setSelectedLang(indexStats.available_languages[0]);
            }
          }
        } catch (e) {
          console.error('Error obteniendo estadísticas:', e);
        }
      }
    };
    checkBackend();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await search(query.trim(), selectedLang);
      setResults(response.results);
      setSearchTime(response.processing_time_ms);
      setTotalResults(response.total_results);
      // Actualizar stats despues de la busqueda (el indice ya esta cargado)
      const updatedStats = await getStats();
      setStats(updatedStats);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error desconocido');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <BookOpen className="w-10 h-10 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">WikiSearch</h1>
              <p className="text-sm text-gray-500">Buscador de Wikipedia multilingüe</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Estado del backend */}
        {backendOnline === false && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <div>
              <p className="font-medium text-red-800">Backend no disponible</p>
              <p className="text-sm text-red-600">
                Ejecuta <code className="bg-red-100 px-1 rounded">uvicorn main:app --reload</code> en el directorio backend/
              </p>
            </div>
          </div>
        )}

        {/* Estadísticas del índice */}
        {stats && (
          <div className="mb-6 grid grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <Database className="w-4 h-4" />
                Documentos
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {stats.total_documents.toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <BookOpen className="w-4 h-4" />
                Vocabulario
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {stats.vocabulary_size.toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <Clock className="w-4 h-4" />
                Estado
              </div>
              <p className="text-2xl font-bold text-green-600">
                {stats.index_loaded ? 'Activo' : 'Sin índice'}
              </p>
            </div>
          </div>
        )}

        {/* Selector de idioma */}
        {availableLanguages.length > 0 && (
          <div className="mb-4 flex items-center gap-3">
            <Globe className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-500">Buscar en:</span>
            <div className="flex gap-2">
              {availableLanguages.map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLang(lang)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedLang === lang
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {LANGUAGE_NAMES[lang] || lang.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Barra de busqueda */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Buscar en Wikipedia ${LANGUAGE_NAMES[selectedLang] || ''}...`}
              className="w-full px-5 py-4 pr-14 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
              disabled={!backendOnline}
            />
            <button
              type="submit"
              disabled={loading || !backendOnline}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </button>
          </div>
        </form>

        {/* Información de resultados */}
        {searchTime !== null && (
          <div className="mb-4 text-sm text-gray-500">
            {totalResults.toLocaleString()} resultados encontrados en {searchTime.toFixed(2)} ms
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Resultados */}
        <div className="space-y-4">
          {results.map((result, index) => (
            <article
              key={result.doc_id}
              className="bg-white p-5 rounded-lg shadow-sm border hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-400">#{index + 1}</span>
                    <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                      Score: {result.score.toFixed(4)}
                    </span>
                  </div>
                  <h2 className="text-xl font-semibold text-blue-700 hover:underline mb-2">
                    <a href={result.url} target="_blank" rel="noopener noreferrer">
                      {result.title}
                    </a>
                  </h2>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {result.snippet}...
                  </p>
                </div>
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Abrir en Wikipedia"
                >
                  <ExternalLink className="w-5 h-5" />
                </a>
              </div>
            </article>
          ))}
        </div>

        {/* Sin resultados */}
        {results.length === 0 && searchTime !== null && !loading && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No se encontraron resultados para "{query}"</p>
          </div>
        )}

        {/* Estado inicial */}
        {results.length === 0 && searchTime === null && backendOnline && (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-200 mx-auto mb-4" />
            <p className="text-gray-400">Escribe una consulta para buscar en Wikipedia</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white mt-12">
        <div className="max-w-5xl mx-auto px-4 py-6 text-center text-sm text-gray-500">
          <p>Sistema de Recuperación de Información - Práctica 4</p>
          <p className="mt-1">Jesús J. Cantero · Ceuta · 2024/25</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
