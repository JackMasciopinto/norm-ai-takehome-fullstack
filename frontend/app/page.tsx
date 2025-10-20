'use client';

import { useState } from 'react';
import HeaderNav from '@/components/HeaderNav';

interface Citation {
  source: string;
  text: string;
}

interface ApiResponse {
  query: string;
  response: string;
  citations: Citation[];
}

export default function Page() {
  const [query, setQuery] = useState('');
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setApiResponse(null);
    setError('');
    
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data: ApiResponse = await res.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error querying API');
    }
    setLoading(false);
  }

  return (
    <div>
      <HeaderNav signOut={() => {}} />
      <main style={{ maxWidth: 800, margin: '40px auto', padding: 20 }}>
        <h1 style={{ fontSize: 24, marginBottom: 20, textAlign: 'center' }}>
          Laws Query System
        </h1>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 32 }}>
          <label htmlFor="query" style={{ fontSize: 16, fontWeight: '500' }}>
            Enter your legal query:
          </label>
          <input
            id="query"
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="e.g., What happens if I steal from the Sept?"
            style={{ 
              padding: 12, 
              fontSize: 16, 
              border: '1px solid #ccc', 
              borderRadius: 8,
              outline: 'none'
            }}
            required
          />
          <button 
            type="submit" 
            disabled={loading} 
            style={{ 
              padding: 12, 
              fontSize: 16, 
              backgroundColor: loading ? '#ccc' : '#2800D7',
              color: 'white',
              border: 'none',
              borderRadius: 8,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Querying...' : 'Submit Query'}
          </button>
        </form>

        {error && (
          <div style={{ 
            marginBottom: 32, 
            background: '#fee', 
            padding: 16, 
            borderRadius: 8,
            border: '1px solid #fcc',
            color: '#c00'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {apiResponse && (
          <div style={{ background: '#f9f9f9', padding: 20, borderRadius: 8, border: '1px solid #ddd' }}>
            <h2 style={{ fontSize: 18, marginBottom: 16, color: '#333' }}>Response</h2>
            
            <div style={{ marginBottom: 20 }}>
              <strong style={{ color: '#2800D7' }}>Query:</strong>
              <p style={{ margin: '8px 0', fontStyle: 'italic' }}>{apiResponse.query}</p>
            </div>
            
            <div style={{ marginBottom: 20 }}>
              <strong style={{ color: '#2800D7' }}>Answer:</strong>
              <p style={{ margin: '8px 0', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{apiResponse.response}</p>
            </div>
            
            {apiResponse.citations && apiResponse.citations.length > 0 && (
              <div>
                <strong style={{ color: '#2800D7' }}>Citations:</strong>
                <div style={{ marginTop: 8 }}>
                  {apiResponse.citations.map((citation, index) => (
                    <div 
                      key={index}
                      style={{ 
                        background: 'white',
                        padding: 12,
                        marginBottom: 8,
                        borderRadius: 6,
                        border: '1px solid #e0e0e0'
                      }}
                    >
                      <div style={{ fontSize: 14, fontWeight: '500', marginBottom: 4, color: '#555' }}>
                        Statute: {citation.source}
                      </div>
                      <div style={{ fontSize: 14, lineHeight: 1.4, color: '#666' }}>
                        {citation.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
