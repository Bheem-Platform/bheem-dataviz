import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { BarChart3, AlertCircle, CheckCircle } from 'lucide-react';

export function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const { handleOAuthCallback } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    processCallback();
  }, []);

  const processCallback = async () => {
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setError(errorParam);
      setStatus('error');
      setTimeout(() => navigate('/login'), 3000);
      return;
    }

    if (accessToken && refreshToken) {
      try {
        await handleOAuthCallback(accessToken, refreshToken);
        setStatus('success');
        setTimeout(() => navigate('/dashboards'), 1000);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authentication failed');
        setStatus('error');
        setTimeout(() => navigate('/login'), 3000);
      }
    } else {
      setError('Missing authentication tokens');
      setStatus('error');
      setTimeout(() => navigate('/login'), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-indigo-50 flex items-center justify-center px-4">
      {/* Background Elements */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-violet-200/30 rounded-full blur-3xl" />
      </div>

      <div className="text-center">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-indigo-700/90 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <BarChart3 className="w-9 h-9 text-white" />
          </div>
        </div>

        {status === 'processing' && (
          <div className="space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto" />
            <h2 className="text-2xl font-bold text-gray-900">Completing login...</h2>
            <p className="text-gray-600">Please wait while we authenticate you.</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle className="w-9 h-9 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Login successful!</h2>
            <p className="text-gray-600">Redirecting to dashboard...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <AlertCircle className="w-9 h-9 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Authentication Failed</h2>
            <p className="text-red-600">{error}</p>
            <p className="text-gray-500">Redirecting to login...</p>
          </div>
        )}
      </div>
    </div>
  );
}
