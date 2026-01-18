import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Navbar } from '../Navbar';

interface LyricsResult {
  id: number;
  theme: string;
  generated_lyrics: string;
  edited_lyrics: string | null;
  structure: any;
  created_at: string;
}

export const LyricsPage: React.FC = () => {
  const [theme, setTheme] = useState('');
  const [emotion, setEmotion] = useState('');
  const [style, setStyle] = useState('');
  const [generating, setGenerating] = useState(false);
  const [lyrics, setLyrics] = useState<LyricsResult | null>(null);
  const [editedLyrics, setEditedLyrics] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (!theme) {
      setError('Please enter a theme');
      return;
    }

    setGenerating(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/lyrics/generate', {
        theme,
        emotion: emotion || undefined,
        style: style || undefined,
      });

      setLyrics(response.data);
      setEditedLyrics(response.data.generated_lyrics);
      setSuccess('Lyrics generated successfully!');
    } catch (err: any) {
      console.error('Lyrics generation error:', err);
      
      // Handle specific error cases
      if (err.response?.status === 429) {
        setError('API quota exceeded. Please check your Gemini API plan and billing. You may need to wait a few minutes or upgrade your plan.');
      } else if (err.response?.status === 503) {
        setError('Service temporarily unavailable. Please try again in a few moments.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (detail.includes('quota') || detail.includes('429')) {
          setError('API quota exceeded. Please check your Gemini API plan and billing.');
        } else {
          setError(`Failed to generate lyrics: ${detail}`);
        }
      } else if (err.request) {
        setError('No response from server. Check if backend is running.');
      } else {
        setError(`Failed to generate lyrics: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!lyrics || !editedLyrics) {
      setError('No lyrics to save');
      return;
    }

    try {
      await api.put(`/lyrics/${lyrics.id}`, {
        edited_lyrics: editedLyrics,
      });
      setSuccess('Lyrics saved successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save lyrics');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div>
      <Navbar onLogout={handleLogout} />
      <div className="container">
        <div className="card">
          <h2>📝 Lyric Composer</h2>
          <p style={{ color: '#666', marginBottom: '2rem' }}>
            Generate beautiful lyrics with AI based on your theme
          </p>

          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          <div className="form-group">
            <label>Theme *</label>
            <input
              type="text"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="e.g., love in the rain, summer vibes, heartbreak"
            />
          </div>

          <div className="form-group">
            <label>Emotion (optional)</label>
            <input
              type="text"
              value={emotion}
              onChange={(e) => setEmotion(e.target.value)}
              placeholder="e.g., happy, sad, energetic, calm"
            />
          </div>

          <div className="form-group">
            <label>Style (optional)</label>
            <select value={style} onChange={(e) => setStyle(e.target.value)}>
              <option value="">Select style</option>
              <option value="pop">Pop</option>
              <option value="rock">Rock</option>
              <option value="ballad">Ballad</option>
              <option value="jazz">Jazz</option>
              <option value="hip-hop">Hip-Hop</option>
              <option value="country">Country</option>
              <option value="electronic">Electronic</option>
            </select>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={!theme || generating}
          >
            {generating ? 'Generating...' : 'Generate Lyrics'}
          </button>

          {lyrics && (
            <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8f9ff', borderRadius: '12px' }}>
              <h3>Generated Lyrics</h3>
              <p style={{ marginTop: '0.5rem', color: '#666' }}>
                <strong>Theme:</strong> {lyrics.theme}
                {lyrics.structure && Object.keys(lyrics.structure).length > 0 && (
                  <span style={{ marginLeft: '1rem' }}>
                    <strong>Structure:</strong> {JSON.stringify(lyrics.structure)}
                  </span>
                )}
              </p>

              <div className="form-group" style={{ marginTop: '1rem' }}>
                <label>Edit Lyrics (if needed)</label>
                <textarea
                  value={editedLyrics}
                  onChange={(e) => setEditedLyrics(e.target.value)}
                  rows={15}
                />
              </div>

              <button
                className="btn btn-success"
                onClick={handleSave}
                style={{ marginTop: '1rem' }}
              >
                Save Lyrics
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
