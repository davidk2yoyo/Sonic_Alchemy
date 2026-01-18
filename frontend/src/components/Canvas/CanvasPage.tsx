import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

interface CanvasResult {
  id: number;
  image_url: string;
  emotion_analysis: any;
  status: string;
  created_at: string;
}

export const CanvasPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [canvas, setCanvas] = useState<CanvasResult | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select an image file');
      return;
    }

    console.log('📤 Starting upload...', { fileName: file.name, fileSize: file.size, fileType: file.type });
    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('📤 Sending request to /canvas/upload...');
      // Don't set Content-Type header, let browser set it with boundary
      const response = await api.post('/canvas/upload', formData);

      console.log('✅ Upload successful:', response.data);
      setCanvas(response.data);
      setSuccess('Image uploaded successfully!');
    } catch (err: any) {
      console.error('❌ Upload error:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      
      if (err.response) {
        setError(err.response.data?.detail || `Failed to upload image: ${err.response.status} ${err.response.statusText}`);
      } else if (err.request) {
        setError('No response from server. Check if backend is running at http://localhost:8000');
      } else {
        setError(`Failed to upload image: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!canvas) {
      setError('Please upload an image first');
      return;
    }

    setAnalyzing(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/canvas/analyze', null, {
        params: { canvas_id: canvas.id }
      });
      setCanvas(response.data);
      setSuccess('Image analyzed successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze image');
    } finally {
      setAnalyzing(false);
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
          <h2>🎨 Emotion Canvas</h2>
          <p style={{ color: '#666', marginBottom: '2rem' }}>
            Upload an image and let AI analyze the emotions to generate music
          </p>

          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          <div className="form-group">
            <label>Select Image (JPG, PNG, WEBP)</label>
            <div className="file-upload">
              <label className="file-upload-label">
                <span className="file-upload-icon">📁</span>
                <span>{file ? file.name : 'Choose file or drag here'}</span>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileChange}
                />
              </label>
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload Image'}
          </button>

          {canvas && (
            <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8f9ff', borderRadius: '12px' }}>
              <h3>Uploaded Image</h3>
              <img
                src={canvas.image_url}
                alt="Canvas"
                style={{ maxWidth: '100%', borderRadius: '8px', marginTop: '1rem' }}
              />
              <p style={{ marginTop: '1rem' }}>
                <strong>Status:</strong>{' '}
                <span className={`status-badge status-${canvas.status}`}>
                  {canvas.status}
                </span>
              </p>

              <button
                className="btn btn-success"
                onClick={handleAnalyze}
                disabled={analyzing || canvas.status === 'analyzed'}
                style={{ marginTop: '1rem' }}
              >
                {analyzing ? 'Analyzing...' : 'Analyze Emotions'}
              </button>

              {canvas.emotion_analysis && Object.keys(canvas.emotion_analysis).length > 0 && (
                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'white', borderRadius: '8px' }}>
                  <h4>Emotion Analysis Results:</h4>
                  <pre style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>
                    {JSON.stringify(canvas.emotion_analysis, null, 2)}
                  </pre>
                </div>
              )}
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
