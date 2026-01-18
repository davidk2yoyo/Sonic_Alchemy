import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import './Dashboard.css';

interface Project {
  id: number;
  title: string;
  description: string;
  created_at: string;
}

export const Dashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
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
        <div className="dashboard-header">
          <h1>Welcome to VoiceCanvas</h1>
          <p>Create amazing music with AI-powered tools</p>
        </div>

        <div className="feature-cards">
          <div className="feature-card" onClick={() => navigate('/canvas')}>
            <div className="feature-icon">🎨</div>
            <h3>Emotion Canvas</h3>
            <p>Upload an image and generate music based on emotions</p>
            <button className="btn btn-primary">Try Canvas</button>
          </div>

          <div className="feature-card" onClick={() => navigate('/voice')}>
            <div className="feature-icon">🎤</div>
            <h3>Voice Alchemy</h3>
            <p>Transform your voice with AI-powered processing</p>
            <button className="btn btn-primary">Try Voice</button>
          </div>

          <div className="feature-card" onClick={() => navigate('/lyrics')}>
            <div className="feature-icon">📝</div>
            <h3>Lyric Composer</h3>
            <p>Generate beautiful lyrics with AI</p>
            <button className="btn btn-primary">Try Lyrics</button>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2>My Projects</h2>
            <button className="btn btn-primary" onClick={() => navigate('/projects')}>
              Create New Project
            </button>
          </div>
          {projects.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
              <p>No projects yet. Create your first project!</p>
            </div>
          ) : (
            <div className="grid">
              {projects.map((project) => (
                <div key={project.id} className="project-card" onClick={() => navigate(`/projects/${project.id}`)}>
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
