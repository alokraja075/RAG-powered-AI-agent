import { useEffect, useMemo, useState } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [chat, setChat] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  useEffect(() => {
    if (!token) {
      setDocuments([]);
      setChat([]);
      return;
    }
    fetchDocuments();
    fetchHistory();
  }, [token]);

  async function api(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Request failed');
    return res;
  }

  async function authenticate(e) {
    e.preventDefault();
    setError('');
    try {
      if (!isLogin) {
        await api('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
      }
      const res = await api('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  async function fetchDocuments() {
    try {
      const res = await api('/api/documents/', { headers: authHeaders });
      setDocuments(await res.json());
    } catch (err) {
      setError(err.message);
    }
  }

  async function fetchHistory() {
    try {
      const res = await api('/api/chat/history', { headers: authHeaders });
      setChat(await res.json());
    } catch (err) {
      setError(err.message);
    }
  }

  async function uploadDocument(e) {
    e.preventDefault();
    if (!file) return;
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        headers: authHeaders,
        body: formData,
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed');
      setFile(null);
      await fetchDocuments();
    } catch (err) {
      setError(err.message);
    }
  }

  async function deleteDocument(id) {
    try {
      await api(`/api/documents/${id}`, { method: 'DELETE', headers: authHeaders });
      await fetchDocuments();
    } catch (err) {
      setError(err.message);
    }
  }

  async function sendMessage(e) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setError('');
    setLoading(true);

    const prompt = chatInput.trim();
    setChatInput('');
    setChat((prev) => [...prev, { role: 'user', content: prompt, created_at: new Date().toISOString() }]);
    const assistantIndex = Date.now();
    setChat((prev) => [...prev, { id: assistantIndex, role: 'assistant', content: '', created_at: new Date().toISOString(), sources: [] }]);

    try {
      const res = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { ...authHeaders, 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: prompt, top_k: 4 }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Chat failed');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';

        for (const event of events) {
          if (!event.startsWith('data: ')) continue;
          const payload = JSON.parse(event.replace('data: ', ''));
          if (payload.type === 'chunk') {
            setChat((prev) => prev.map((m) => (m.id === assistantIndex ? { ...m, content: m.content + payload.content } : m)));
          }
          if (payload.type === 'sources') {
            setChat((prev) => prev.map((m) => (m.id === assistantIndex ? { ...m, sources: payload.sources } : m)));
          }
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem('token');
    setToken('');
  }

  if (!token) {
    return (
      <main className="auth-layout">
        <form className="card auth-card" onSubmit={authenticate}>
          <h1>RAG AI Agent</h1>
          <p>{isLogin ? 'Sign in to chat with your knowledge base' : 'Create account to start'}</p>
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          <button type="submit">{isLogin ? 'Login' : 'Register & Login'}</button>
          <button className="ghost" type="button" onClick={() => setIsLogin((v) => !v)}>
            {isLogin ? 'Need an account?' : 'Already have an account?'}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <h1>RAG AI Agent</h1>
        <button className="ghost" onClick={logout}>Logout</button>
      </header>
      <section className="grid">
        <aside className="card">
          <h2>Knowledge Base</h2>
          <form onSubmit={uploadDocument} className="stack">
            <input type="file" accept=".pdf,.txt,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
            <button type="submit">Upload & Index</button>
          </form>
          <ul className="docs">
            {documents.map((d) => (
              <li key={d.id}>
                <div>
                  <strong>{d.filename}</strong>
                  <small>{d.indexed ? 'Indexed' : 'Pending'}</small>
                </div>
                <button className="danger" onClick={() => deleteDocument(d.id)}>Delete</button>
              </li>
            ))}
          </ul>
        </aside>

        <section className="card chat-card">
          <h2>Chat</h2>
          <div className="chat-box">
            {chat.map((m, idx) => (
              <div key={m.id || idx} className={`message ${m.role}`}>
                <p>{m.content}</p>
                {m.sources?.length > 0 && <small>Sources: {m.sources.join(', ')}</small>}
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="chat-form">
            <input value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Ask about your uploaded files..." required />
            <button type="submit" disabled={loading}>{loading ? 'Thinking...' : 'Send'}</button>
          </form>
          {error && <p className="error">{error}</p>}
        </section>
      </section>
    </main>
  );
}

export default App;
