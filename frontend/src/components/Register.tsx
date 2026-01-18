import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

export const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await api.post('/auth/register', {
        email,
        username,
        password,
      });
      
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token || '');
        navigate('/dashboard');
      } else {
        setError('Registration successful but no token received');
      }
    } catch (err: any) {
      console.error('Registration error:', err);
      if (err.response) {
        // Server responded with error
        setError(err.response.data?.detail || `Registration failed: ${err.response.status}`);
      } else if (err.request) {
        // Request made but no response
        setError('No response from server. Check if backend is running at http://localhost:8000');
      } else {
        // Something else happened
        setError(`Registration failed: ${err.message || 'Unknown error'}`);
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>🎵 VoiceCanvas</h2>
        <h3 style={{ textAlign: 'center', marginBottom: '2rem', color: '#666', fontWeight: 'normal' }}>
          Create your account
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username"
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a password"
              required
            />
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" className="btn btn-primary">
            Register
          </button>
        </form>
        <div className="auth-link">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </div>
    </div>
  );
};
