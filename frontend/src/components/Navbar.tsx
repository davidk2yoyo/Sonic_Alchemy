import React from 'react';
import { useNavigate } from 'react-router-dom';

interface NavbarProps {
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  
  return (
    <nav className="navbar">
      <h1>🎵 VoiceCanvas</h1>
      <div className="nav-links">
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/dashboard'); }}>
          Dashboard
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/canvas'); }}>
          Canvas
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/voice'); }}>
          Voice
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/lyrics'); }}>
          Lyrics
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); navigate('/projects'); }}>
          Projects
        </a>
        <button onClick={onLogout}>Logout</button>
      </div>
    </nav>
  );
};
