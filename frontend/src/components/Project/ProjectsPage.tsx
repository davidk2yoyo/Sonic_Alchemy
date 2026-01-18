import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

interface Project {
  id: number;
  title: string;
  description: string;
  created_at: string;
}

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) {
      setError('Title is required');
      return;
    }

    setCreating(true);
    setError('');

    try {
      const response = await api.post('/projects', {
        title: newTitle,
        description: newDescription,
      });
      setProjects([...projects, response.data]);
      setNewTitle('');
      setNewDescription('');
      setShowCreateForm(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (loading) {
    return (
      <div>
        <Navbar onLogout={handleLogout} />
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar onLogout={handleLogout} />
      <div className="container">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2>My Projects</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowCreateForm(!showCreateForm)}
            >
              {showCreateForm ? 'Cancel' : '+ New Project'}
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          {showCreateForm && (
            <form onSubmit={handleCreate} style={{ marginBottom: '2rem', padding: '1.5rem', background: '#f8f9ff', borderRadius: '12px' }}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="Project title"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Project description"
                  rows={3}
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={creating}
              >
                {creating ? 'Creating...' : 'Create Project'}
              </button>
            </form>
          )}

          {projects.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
              <p>No projects yet. Create your first project!</p>
            </div>
          ) : (
            <div className="grid">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="project-card"
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <h3>{project.title}</h3>
                  <p>{project.description || 'No description'}</p>
                  <small style={{ color: '#999' }}>
                    Created: {new Date(project.created_at).toLocaleDateString()}
                  </small>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const Navbar: React.FC<{ onLogout: () => void }> = ({ onLogout }) => {
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <h1>🎵 VoiceCanvas</h1>
      <div className="nav-links">
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/dashboard'); }}>Dashboard</a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/canvas'); }}>Canvas</a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/voice'); }}>Voice</a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/lyrics'); }}>Lyrics</a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/projects'); }}>Projects</a>
        <button onClick={onLogout}>Logout</button>
      </div>
    </nav>
  );
};
