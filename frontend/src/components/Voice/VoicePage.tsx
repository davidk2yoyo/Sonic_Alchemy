import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Navbar } from '../Navbar';

interface VoiceResult {
  id: number;
  raw_audio_url: string;
  processed_audio_url: string | null;
  status: string;
  duration_seconds: number | null;
  created_at: string;
}

export const VoicePage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [voice, setVoice] = useState<VoiceResult | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [pitchCorrection, setPitchCorrection] = useState(true);
  const [timingQuantization, setTimingQuantization] = useState(true);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select an audio file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/voice/upload', formData);

      setVoice(response.data);
      setSuccess('Audio uploaded successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload audio');
    } finally {
      setUploading(false);
    }
  };

  const handleProcess = async () => {
    if (!voice) {
      setError('Please upload an audio file first');
      return;
    }

    setProcessing(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post(`/voice/process?voice_id=${voice.id}`, {
        corrections: {
          pitch_correction: pitchCorrection,
          timing_quantization: timingQuantization,
          breath_control: false,
        },
      });
      setVoice(response.data);
      setSuccess('Audio processing started!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process audio');
    } finally {
      setProcessing(false);
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
          <h2>🎤 Voice Alchemy</h2>
          <p style={{ color: '#666', marginBottom: '2rem' }}>
            Upload your voice and transform it with AI-powered processing
          </p>

          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          <div className="form-group">
            <label>Select Audio File (WAV, MP3, M4A, OGG)</label>
            <div className="file-upload">
              <label className="file-upload-label">
                <span className="file-upload-icon">🎵</span>
                <span>{file ? file.name : 'Choose audio file or drag here'}</span>
                <input
                  type="file"
                  accept="audio/wav,audio/mp3,audio/m4a,audio/ogg"
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
            {uploading ? 'Uploading...' : 'Upload Audio'}
          </button>

          {voice && (
            <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8f9ff', borderRadius: '12px' }}>
              <h3>Uploaded Audio</h3>
              <p style={{ marginTop: '0.5rem' }}>
                <strong>Status:</strong>{' '}
                <span className={`status-badge status-${voice.status}`}>
                  {voice.status}
                </span>
              </p>
              {voice.duration_seconds && (
                <p style={{ marginTop: '0.5rem' }}>
                  <strong>Duration:</strong> {voice.duration_seconds.toFixed(2)} seconds
                </p>
              )}

              {voice.raw_audio_url && (
                <div style={{ marginTop: '1rem' }}>
                  <audio controls style={{ width: '100%' }}>
                    <source src={voice.raw_audio_url} />
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}

              <div style={{ marginTop: '1.5rem' }}>
                <h4>Processing Options:</h4>
                <div style={{ marginTop: '1rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <input
                      type="checkbox"
                      checked={pitchCorrection}
                      onChange={(e) => setPitchCorrection(e.target.checked)}
                    />
                    Pitch Correction
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input
                      type="checkbox"
                      checked={timingQuantization}
                      onChange={(e) => setTimingQuantization(e.target.checked)}
                    />
                    Timing Quantization
                  </label>
                </div>
              </div>

              <button
                className="btn btn-success"
                onClick={handleProcess}
                disabled={processing || voice.status === 'processing' || voice.status === 'completed'}
                style={{ marginTop: '1rem' }}
              >
                {processing ? 'Processing...' : 'Process Audio'}
              </button>

              {voice.processed_audio_url && (
                <div style={{ marginTop: '1.5rem' }}>
                  <h4>Processed Audio:</h4>
                  <audio controls style={{ width: '100%', marginTop: '0.5rem' }}>
                    <source src={voice.processed_audio_url} />
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
