import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Database, 
  Download, 
  Upload, 
  CheckCircle, 
  XCircle, 
  Loader2, 
  Activity,
  Settings,
  BarChart3,
  RefreshCw,
  AlertCircle,
  FileCheck
} from 'lucide-react';
import { mcpAPI } from '@/lib/api/endpoints';

interface ConnectionConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
}

interface TaskStatus {
  status: 'idle' | 'running' | 'completed' | 'error' | 'starting';
  progress: number;
  message: string;
  total?: number;
  current?: number;
  stats?: any;
}

interface DatabaseStats {
  authors: number;
  publications: number;
  collaborations: number;
  venues: number;
  faculty: number;
  recent_by_year: Array<{ year: number; count: number }>;
}

interface QualityCheckItem {
  faculty_name: string;
  db_name: string;
  dblp_pid: string;
  expected: number;
  actual: number;
  difference: number;
  pct_difference: number;
}

interface QualityCheckResult {
  status: string;
  timestamp: string;
  summary: {
    total_faculty: number;
    perfect_matches: number;
    close_matches: number;
    mismatches: number;
    accuracy_rate: number;
    perfect_match_rate: number;
  };
  overall_stats: {
    total_expected_publications: number;
    total_actual_publications: number;
    overall_difference: number;
    overall_accuracy: number;
  };
  perfect_matches: QualityCheckItem[];
  close_matches: QualityCheckItem[];
  mismatches: QualityCheckItem[];
}

// Ollama Configuration Component
function OllamaConfigSection() {
  const [settings, setSettings] = useState({
    mode: 'cloud',
    cloud_host: 'https://ollama.com',
    cloud_model: 'qwen3-coder-next',
    cloud_api_key: '',
    local_host: 'http://localhost:11434',
    local_model: 'llama3.2'
  });
  const [originalMaskedKey, setOriginalMaskedKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [saveMessage, setSaveMessage] = useState('');

  // Load current settings
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/v1/admin/settings/ollama');
      const data = await response.json();
      setSettings(data);
      // Store the masked key to detect if user actually changed it
      setOriginalMaskedKey(data.cloud_api_key);
    } catch (error) {
      console.error('Failed to load Ollama settings:', error);
    }
  };

  const testConnection = async () => {
    setLoading(true);
    setTestResult(null);
    
    // Check if we're trying to test with a masked key
    if (settings.mode === 'cloud' && settings.cloud_api_key === originalMaskedKey && originalMaskedKey.includes('...')) {
      setTestResult({ 
        success: false, 
        message: 'Cannot test with masked API key. Please enter your full API key to test the connection.' 
      });
      setLoading(false);
      return;
    }
    
    try {
      const testConfig = {
        mode: settings.mode,
        host: settings.mode === 'cloud' ? settings.cloud_host : settings.local_host,
        model: settings.mode === 'cloud' ? settings.cloud_model : settings.local_model,
        api_key: settings.mode === 'cloud' ? settings.cloud_api_key : null
      };

      const response = await fetch('/api/v1/admin/settings/ollama/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testConfig)
      });

      const result = await response.json();
      setTestResult(result);
    } catch (error) {
      setTestResult({ success: false, message: `Error: ${error}` });
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setLoading(true);
    setSaveMessage('');
    try {
      // If the API key hasn't been changed (still masked), don't send it
      const settingsToSave = { ...settings };
      if (settingsToSave.cloud_api_key === originalMaskedKey && originalMaskedKey.includes('...')) {
        // Don't include the masked key - backend will keep the existing one
        settingsToSave.cloud_api_key = '';
      }
      
      const response = await fetch('/api/v1/admin/settings/ollama', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settingsToSave)
      });

      const result = await response.json();
      if (result.success) {
        setSaveMessage('Settings saved successfully!');
        setTimeout(() => setSaveMessage(''), 3000);
        // Reload settings to get the updated masked key
        await loadSettings();
      } else {
        setSaveMessage('Failed to save settings: ' + result.message);
      }
    } catch (error) {
      setSaveMessage(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <div className="space-y-2">
        <Label>Ollama Mode</Label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="cloud"
              checked={settings.mode === 'cloud'}
              onChange={(e) => setSettings({ ...settings, mode: e.target.value })}
              className="w-4 h-4"
            />
            <span>Cloud (https://ollama.com)</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="local"
              checked={settings.mode === 'local'}
              onChange={(e) => setSettings({ ...settings, mode: e.target.value })}
              className="w-4 h-4"
            />
            <span>Local (localhost)</span>
          </label>
        </div>
      </div>

      {/* Cloud Configuration */}
      {settings.mode === 'cloud' && (
        <div className="space-y-4 p-4 bg-teal-50 dark:bg-teal-950 rounded-lg">
          <h4 className="font-semibold text-teal-700 dark:text-teal-400">Cloud Ollama Settings</h4>
          
          <div className="space-y-2">
            <Label htmlFor="cloud_host">Host URL</Label>
            <Input
              id="cloud_host"
              value={settings.cloud_host}
              onChange={(e) => setSettings({ ...settings, cloud_host: e.target.value })}
              placeholder="https://ollama.com"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cloud_model">Model</Label>
            <Input
              id="cloud_model"
              value={settings.cloud_model}
              onChange={(e) => setSettings({ ...settings, cloud_model: e.target.value })}
              placeholder="qwen3-coder-next"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cloud_api_key">API Key</Label>
            <Input
              id="cloud_api_key"
              type="password"
              value={settings.cloud_api_key}
              onChange={(e) => setSettings({ ...settings, cloud_api_key: e.target.value })}
              placeholder={originalMaskedKey.includes('...') ? "Leave unchanged or enter new key" : "Enter your Ollama API key"}
              className={originalMaskedKey.includes('...') ? 'border-green-300 dark:border-green-700' : ''}
            />
            {originalMaskedKey.includes('...') ? (
              <p className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
                <CheckCircle className="h-3 w-3" />
                API key already configured (masked for security). Enter a new key to update.
              </p>
            ) : (
              <p className="text-xs text-slate-500">Required for cloud Ollama access</p>
            )}
          </div>
        </div>
      )}

      {/* Local Configuration */}
      {settings.mode === 'local' && (
        <div className="space-y-4 p-4 bg-slate-50 dark:bg-slate-950 rounded-lg">
          <h4 className="font-semibold text-slate-700 dark:text-slate-400">Local Ollama Settings</h4>
          
          <div className="space-y-2">
            <Label htmlFor="local_host">Host URL</Label>
            <Input
              id="local_host"
              value={settings.local_host}
              onChange={(e) => setSettings({ ...settings, local_host: e.target.value })}
              placeholder="http://localhost:11434"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="local_model">Model</Label>
            <Input
              id="local_model"
              value={settings.local_model}
              onChange={(e) => setSettings({ ...settings, local_model: e.target.value })}
              placeholder="llama3.2"
            />
          </div>
        </div>
      )}

      {/* Test Connection Button */}
      <div className="flex gap-2">
        <Button 
          onClick={testConnection}
          disabled={loading}
          variant="outline"
          className="flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Testing...
            </>
          ) : (
            <>
              <Activity className="h-4 w-4" />
              Test Connection
            </>
          )}
        </Button>

        <Button 
          onClick={saveSettings}
          disabled={loading}
          className="flex items-center gap-2 bg-teal-600 hover:bg-teal-700"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <CheckCircle className="h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </div>

      {/* Test Result */}
      {testResult && (
        <div className={`p-4 rounded-lg ${testResult.success ? 'bg-green-50 dark:bg-green-950' : 'bg-red-50 dark:bg-red-950'}`}>
          <div className="flex items-start gap-2">
            {testResult.success ? (
              <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
            ) : (
              <XCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5" />
            )}
            <div className="flex-1">
              <p className={`font-semibold ${testResult.success ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}`}>
                {testResult.message}
              </p>
              {testResult.model_count && (
                <p className="text-sm mt-1 text-slate-600 dark:text-slate-400">
                  Found {testResult.model_count} available models
                </p>
              )}
              {testResult.available_models && testResult.available_models.length > 0 && (
                <details className="mt-2">
                  <summary className="text-sm cursor-pointer text-slate-600 dark:text-slate-400">
                    View available models
                  </summary>
                  <ul className="mt-2 text-sm space-y-1 text-slate-600 dark:text-slate-400">
                    {testResult.available_models.map((model: string) => (
                      <li key={model} className="ml-4">• {model}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Save Message */}
      {saveMessage && (
        <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-400">
          {saveMessage}
        </div>
      )}
    </div>
  );
}

export function AdminPage() {
  // Connection testing
  const [connectionConfig, setConnectionConfig] = useState<ConnectionConfig>({
    host: 'localhost',
    port: 5432,
    database: 'scislisa-service',
    user: 'postgres',
    password: 'postgres'
  });
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [connectionMessage, setConnectionMessage] = useState('');

  // DBLP API Test
  const [dblpApiStatus, setDblpApiStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [dblpApiMessage, setDblpApiMessage] = useState('');

  // DBLP Fetch
  const [fetchStatus, setFetchStatus] = useState<TaskStatus>({ status: 'idle', progress: 0, message: '' });
  const [fetchPath, setFetchPath] = useState('dataset/dblp');

  // Data Ingestion
  const [ingestStatus, setIngestStatus] = useState<TaskStatus>({ status: 'idle', progress: 0, message: '' });
  const [ingestPath, setIngestPath] = useState('dataset/dblp');

  // Database Stats
  const [dbStats, setDbStats] = useState<DatabaseStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // Data Quality Check
  const [qualityCheckResult, setQualityCheckResult] = useState<QualityCheckResult | null>(null);
  const [qualityCheckLoading, setQualityCheckLoading] = useState(false);

  // Poll for task status
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (fetchStatus.status === 'running' || fetchStatus.status === 'starting') {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`/api/v1/admin/fetch-status`);
          const data = await response.json();
          setFetchStatus(data);
        } catch (error) {
          console.error('Failed to get fetch status:', error);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [fetchStatus.status]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (ingestStatus.status === 'running' || ingestStatus.status === 'starting') {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`/api/v1/admin/ingest-status`);
          const data = await response.json();
          setIngestStatus(data);
          
          // Refresh stats immediately when ingestion completes
          if (data.status === 'completed') {
            setTimeout(() => loadDatabaseStats(), 500);
          }
        } catch (error) {
          console.error('Failed to get ingest status:', error);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [ingestStatus.status]);

  // Load database stats on mount
  useEffect(() => {
    loadDatabaseStats();
  }, []);

  const testCurrentConnection = async () => {
    setConnectionStatus('testing');
    setConnectionMessage('Testing current database connection...');

    try {
      const response = await fetch(`/api/v1/admin/test-current-db`);
      const data = await response.json();
      if (response.ok) {
        setConnectionStatus('success');
        setConnectionMessage(`Connected successfully! Database version: ${data.database_version?.split(' ')[1] || 'Unknown'}`);
      } else {
        setConnectionStatus('error');
        setConnectionMessage(data.detail || 'Connection failed');
      }
    } catch (error: any) {
      setConnectionStatus('error');
      setConnectionMessage(error.message || 'Connection failed');
    }
  };

  const testCustomConnection = async () => {
    setConnectionStatus('testing');
    setConnectionMessage('Testing custom database connection...');

    try {
      const response = await fetch(`/api/v1/admin/test-db-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(connectionConfig)
      });
      const data = await response.json();
      if (response.ok) {
        setConnectionStatus('success');
        setConnectionMessage('Custom connection successful!');
      } else {
        setConnectionStatus('error');
        setConnectionMessage(data.detail || 'Connection failed');
      }
    } catch (error: any) {
      setConnectionStatus('error');
      setConnectionMessage(error.message || 'Connection failed');
    }
  };

  const testDblpApi = async () => {
    setDblpApiStatus('testing');
    setDblpApiMessage('Testing DBLP API connectivity...');

    try {
      const response = await fetch(`/api/v1/admin/test-dblp-api`);
      const data = await response.json();
      if (response.ok) {
        setDblpApiStatus('success');
        setDblpApiMessage(data.message);
      } else {
        setDblpApiStatus('error');
        setDblpApiMessage(data.detail || 'DBLP API test failed');
      }
    } catch (error: any) {
      setDblpApiStatus('error');
      setDblpApiMessage(error.message || 'DBLP API test failed');
    }
  };

  const startFetchDblp = async () => {
    try {
      const response = await fetch(`/api/v1/admin/fetch-dblp-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          output_directory: fetchPath,
          faculty_json_path: 'src/backend/references/dblp/faculty_dblp_matched.json'
        })
      });
      const data = await response.json();
      if (response.ok) {
        setFetchStatus({ status: 'starting', progress: 0, message: 'Starting fetch...' });
      } else {
        alert(`Failed to start fetch: ${data.detail || 'Unknown error'}`);
      }
    } catch (error: any) {
      alert(`Failed to start fetch: ${error.message || 'Unknown error'}`);
    }
  };

  const startIngestion = async () => {
    try {
      const response = await fetch(`/api/v1/admin/ingest-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_path: ingestPath,
          source_name: 'DBLP'
        })
      });
      const data = await response.json();
      if (response.ok) {
        setIngestStatus({ status: 'starting', progress: 0, message: 'Starting ingestion...' });
      } else {
        alert(`Failed to start ingestion: ${data.detail || 'Unknown error'}`);
      }
    } catch (error: any) {
      alert(`Failed to start ingestion: ${error.message || 'Unknown error'}`);
    }
  };

  const loadDatabaseStats = async () => {
    setStatsLoading(true);
    try {
      const response = await mcpAPI.analytics.stats();
      console.log('API Response:', response);
      // API client already returns response.data, so response is the actual data object
      // API returns { totals: { faculty, publications, authors, ... } }
      const stats = response.totals || response || {};
      console.log('Extracted stats:', stats);
      setDbStats(stats);
    } catch (error: any) {
      console.error('Failed to load database stats:', error);
      const errorMsg = error?.message || 'Cannot connect to backend. Make sure the backend is running at http://localhost:8000';
      alert(errorMsg);
    } finally {
      setStatsLoading(false);
    }
  };

  const runDataQualityCheck = async () => {
    setQualityCheckLoading(true);
    try {
      const response = await fetch(`/api/v1/admin/data-quality-check`);
      const data = await response.json();
      if (response.ok) {
        setQualityCheckResult(data);
      } else {
        alert(`Data quality check failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (error: any) {
      console.error('Failed to run data quality check:', error);
      alert(`Failed to run data quality check: ${error.message || 'Unknown error'}`);
    } finally {
      setQualityCheckLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
          System Administration
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2 font-medium">
          Configure system settings, test connections, and manage data ingestion
        </p>
      </div>

      {/* Configuration & Testing */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
            <Settings className="h-5 w-5" />
            Configuration & Testing
          </CardTitle>
          <CardDescription>Test database and API connections before starting operations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Current Connection Test */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Current Database Connection</Label>
            <div className="flex flex-wrap items-center gap-3">
              <Button onClick={testCurrentConnection} disabled={connectionStatus === 'testing'}>
                {connectionStatus === 'testing' ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Testing...</>
                ) : (
                  <><Database className="h-4 w-4 mr-2" /> Test Connection</>
                )}
              </Button>
              <Button variant="outline" onClick={testDblpApi} disabled={dblpApiStatus === 'testing'}>
                {dblpApiStatus === 'testing' ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Testing...</>
                ) : (
                  <><Activity className="h-4 w-4 mr-2" /> Test DBLP API</>
                )}
              </Button>
            </div>
            
            {connectionMessage && (
              <div className={`flex items-center gap-2 p-3 rounded-lg ${
                connectionStatus === 'success' 
                  ? 'bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-400'
                  : connectionStatus === 'error'
                  ? 'bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400'
                  : 'bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400'
              }`}>
                {connectionStatus === 'success' && <CheckCircle className="h-5 w-5" />}
                {connectionStatus === 'error' && <XCircle className="h-5 w-5" />}
                {connectionStatus === 'testing' && <Loader2 className="h-5 w-5 animate-spin" />}
                <span className="text-sm">{connectionMessage}</span>
              </div>
            )}

            {dblpApiMessage && (
              <div className={`flex items-center gap-2 p-3 rounded-lg ${
                dblpApiStatus === 'success' 
                  ? 'bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-400'
                  : dblpApiStatus === 'error'
                  ? 'bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400'
                  : 'bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400'
              }`}>
                {dblpApiStatus === 'success' && <CheckCircle className="h-5 w-5" />}
                {dblpApiStatus === 'error' && <XCircle className="h-5 w-5" />}
                {dblpApiStatus === 'testing' && <Loader2 className="h-5 w-5 animate-spin" />}
                <span className="text-sm">{dblpApiMessage}</span>
              </div>
            )}
          </div>

          {/* Custom Connection Test */}
          <div className="space-y-3 pt-4 border-t">
            <Label className="text-base font-semibold">Test Custom Connection (Optional)</Label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="host">Host</Label>
                <Input
                  id="host"
                  value={connectionConfig.host}
                  onChange={(e) => setConnectionConfig({ ...connectionConfig, host: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="port">Port</Label>
                <Input
                  id="port"
                  type="number"
                  value={connectionConfig.port}
                  onChange={(e) => setConnectionConfig({ ...connectionConfig, port: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <Label htmlFor="database">Database</Label>
                <Input
                  id="database"
                  value={connectionConfig.database}
                  onChange={(e) => setConnectionConfig({ ...connectionConfig, database: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="user">User</Label>
                <Input
                  id="user"
                  value={connectionConfig.user}
                  onChange={(e) => setConnectionConfig({ ...connectionConfig, user: e.target.value })}
                />
              </div>
              <div className="col-span-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={connectionConfig.password}
                  onChange={(e) => setConnectionConfig({ ...connectionConfig, password: e.target.value })}
                />
              </div>
            </div>
            <Button onClick={testCustomConnection} variant="outline">
              <Database className="h-4 w-4 mr-2" /> Test Custom Connection
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Database Statistics */}
      <Card className="border-l-4 border-l-purple-500">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-400">
                <BarChart3 className="h-5 w-5" />
                Database Statistics
              </CardTitle>
              <CardDescription>Current database record counts</CardDescription>
            </div>
            <Button size="sm" variant="outline" onClick={loadDatabaseStats} disabled={statsLoading} className="w-full sm:w-auto">
              <RefreshCw className={`h-4 w-4 mr-2 ${statsLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {dbStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-950/30 rounded-lg">
                <div className="text-2xl font-bold text-blue-700 dark:text-blue-400">{dbStats.faculty}</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Faculty Members</div>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-950/30 rounded-lg">
                <div className="text-2xl font-bold text-green-700 dark:text-green-400">{dbStats.publications}</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Publications</div>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-950/30 rounded-lg">
                <div className="text-2xl font-bold text-purple-700 dark:text-purple-400">{dbStats.authors}</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Total Authors</div>
              </div>
              <div className="p-4 bg-orange-50 dark:bg-orange-950/30 rounded-lg">
                <div className="text-2xl font-bold text-orange-700 dark:text-orange-400">{dbStats.collaborations}</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Collaborations</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* DBLP Data Fetch */}
      <Card className="border-l-4 border-l-green-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
            <Download className="h-5 w-5" />
            Fetch DBLP Data
          </CardTitle>
          <CardDescription>Download BibTeX files from DBLP for all faculty members</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="fetchPath">Output Directory</Label>
            <Input
              id="fetchPath"
              value={fetchPath}
              onChange={(e) => setFetchPath(e.target.value)}
              placeholder="dataset/dblp"
            />
          </div>

          <Button 
            onClick={startFetchDblp}
            disabled={fetchStatus.status === 'running' || fetchStatus.status === 'starting'}
            className="bg-gradient-to-r from-green-500 to-emerald-600"
          >
            {(fetchStatus.status === 'running' || fetchStatus.status === 'starting') ? (
              <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Fetching...</>
            ) : (
              <><Download className="h-4 w-4 mr-2" /> Start Fetch</>
            )}
          </Button>

          {fetchStatus.status !== 'idle' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-400">{fetchStatus.message}</span>
                <span className="font-medium">{fetchStatus.progress}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${fetchStatus.progress}%` }}
                />
              </div>
              {fetchStatus.current && fetchStatus.total && (
                <p className="text-xs text-slate-500">
                  Processing: {fetchStatus.current} of {fetchStatus.total} faculty members
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Data Ingestion */}
      <Card className="border-l-4 border-l-orange-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-700 dark:text-orange-400">
            <Upload className="h-5 w-5" />
            Ingest Data into Database
          </CardTitle>
          <CardDescription>Parse BibTeX files and import into PostgreSQL database</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="ingestPath">Dataset Directory</Label>
            <Input
              id="ingestPath"
              value={ingestPath}
              onChange={(e) => setIngestPath(e.target.value)}
              placeholder="dataset/dblp"
            />
          </div>

          <Button 
            onClick={startIngestion}
            disabled={ingestStatus.status === 'running' || ingestStatus.status === 'starting'}
            className="bg-gradient-to-r from-orange-500 to-red-600"
          >
            {(ingestStatus.status === 'running' || ingestStatus.status === 'starting') ? (
              <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Ingesting...</>
            ) : (
              <><Upload className="h-4 w-4 mr-2" /> Start Ingestion</>
            )}
          </Button>

          {ingestStatus.status !== 'idle' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-400">{ingestStatus.message}</span>
                <span className="font-medium">{ingestStatus.progress}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-orange-500 to-red-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${ingestStatus.progress}%` }}
                />
              </div>
              {ingestStatus.current && ingestStatus.total && (
                <p className="text-xs text-slate-500">
                  Processing: {ingestStatus.current} of {ingestStatus.total} files
                </p>
              )}
              
              {ingestStatus.stats && Object.keys(ingestStatus.stats).length > 0 && (
                <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-1">
                  <p className="text-sm font-semibold mb-2">Ingestion Statistics:</p>
                  <p className="text-xs">Publications Added: {ingestStatus.stats.publications_added}</p>
                  <p className="text-xs">Publications Skipped: {ingestStatus.stats.publications_skipped}</p>
                  <p className="text-xs">Authors Added: {ingestStatus.stats.authors_added}</p>
                  <p className="text-xs">Collaborations Added: {ingestStatus.stats.collaborations_added}</p>
                  <p className="text-xs">Venues Added: {ingestStatus.stats.venues_added}</p>
                  {ingestStatus.stats.errors > 0 && (
                    <p className="text-xs text-red-600">Errors: {ingestStatus.stats.errors}</p>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Data Quality Check */}
      <Card className="border-l-4 border-l-indigo-500">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="flex items-center gap-2 text-indigo-700 dark:text-indigo-400">
                <FileCheck className="h-5 w-5" />
                Data Quality Validation
              </CardTitle>
              <CardDescription>
                Verify publication counts match DBLP expectations after ingestion
              </CardDescription>
            </div>
            <Button 
              size="sm" 
              onClick={runDataQualityCheck} 
              disabled={qualityCheckLoading}
              className="bg-gradient-to-r from-indigo-500 to-purple-600 w-full sm:w-auto"
            >
              {qualityCheckLoading ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Checking...</>
              ) : (
                <><FileCheck className="h-4 w-4 mr-2" /> Run Check</>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {qualityCheckResult ? (
            <div className="space-y-6">
              {/* Summary Statistics */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 dark:bg-green-950/30 rounded-lg">
                  <div className="text-2xl font-bold text-green-700 dark:text-green-400">
                    {qualityCheckResult.summary.perfect_matches}
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Perfect Matches</div>
                  <div className="text-xs text-slate-500 mt-1">
                    {qualityCheckResult.summary.perfect_match_rate}%
                  </div>
                </div>
                <div className="p-4 bg-yellow-50 dark:bg-yellow-950/30 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">
                    {qualityCheckResult.summary.close_matches}
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Close Matches</div>
                  <div className="text-xs text-slate-500 mt-1">
                    Within 5% tolerance
                  </div>
                </div>
                <div className="p-4 bg-red-50 dark:bg-red-950/30 rounded-lg">
                  <div className="text-2xl font-bold text-red-700 dark:text-red-400">
                    {qualityCheckResult.summary.mismatches}
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Mismatches</div>
                  <div className="text-xs text-slate-500 mt-1">
                    &gt;5% difference
                  </div>
                </div>
              </div>

              {/* Overall Accuracy */}
              <div className="p-4 bg-indigo-50 dark:bg-indigo-950/30 rounded-lg">
                <div className="text-sm font-semibold text-indigo-700 dark:text-indigo-400 mb-2">
                  Overall Accuracy: {qualityCheckResult.summary.accuracy_rate}%
                </div>
                <div className="text-xs space-y-1 text-slate-600 dark:text-slate-400">
                  <p>Total Expected Publications: {qualityCheckResult.overall_stats.total_expected_publications}</p>
                  <p>Total Actual Publications: {qualityCheckResult.overall_stats.total_actual_publications}</p>
                  <p>
                    Overall Difference: 
                    <span className={qualityCheckResult.overall_stats.overall_difference >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {' '}{qualityCheckResult.overall_stats.overall_difference >= 0 ? '+' : ''}{qualityCheckResult.overall_stats.overall_difference}
                    </span>
                  </p>
                </div>
              </div>

              {/* Mismatches Table (only show if there are any) */}
              {qualityCheckResult.mismatches.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-3 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5" />
                    Mismatches (Requires Attention)
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-red-50 dark:bg-red-950/30">
                        <tr>
                          <th className="text-left p-2">Faculty Name</th>
                          <th className="text-left p-2">DBLP PID</th>
                          <th className="text-right p-2">Expected</th>
                          <th className="text-right p-2">Actual</th>
                          <th className="text-right p-2">Diff</th>
                          <th className="text-right p-2">% Diff</th>
                        </tr>
                      </thead>
                      <tbody>
                        {qualityCheckResult.mismatches.map((item, idx) => (
                          <tr key={idx} className="border-t border-slate-200 dark:border-slate-700">
                            <td className="p-2">{item.faculty_name}</td>
                            <td className="p-2 font-mono text-xs">{item.dblp_pid}</td>
                            <td className="p-2 text-right">{item.expected}</td>
                            <td className="p-2 text-right">{item.actual}</td>
                            <td className={`p-2 text-right font-semibold ${item.difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.difference >= 0 ? '+' : ''}{item.difference}
                            </td>
                            <td className="p-2 text-right text-red-600 dark:text-red-400 font-semibold">
                              {item.pct_difference}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Close Matches Table (only show if there are any) */}
              {qualityCheckResult.close_matches.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-yellow-700 dark:text-yellow-400 mb-3 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5" />
                    Close Matches (Within Tolerance)
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-yellow-50 dark:bg-yellow-950/30">
                        <tr>
                          <th className="text-left p-2">Faculty Name</th>
                          <th className="text-left p-2">DBLP PID</th>
                          <th className="text-right p-2">Expected</th>
                          <th className="text-right p-2">Actual</th>
                          <th className="text-right p-2">Diff</th>
                          <th className="text-right p-2">% Diff</th>
                        </tr>
                      </thead>
                      <tbody>
                        {qualityCheckResult.close_matches.map((item, idx) => (
                          <tr key={idx} className="border-t border-slate-200 dark:border-slate-700">
                            <td className="p-2">{item.faculty_name}</td>
                            <td className="p-2 font-mono text-xs">{item.dblp_pid}</td>
                            <td className="p-2 text-right">{item.expected}</td>
                            <td className="p-2 text-right">{item.actual}</td>
                            <td className={`p-2 text-right font-semibold ${item.difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.difference >= 0 ? '+' : ''}{item.difference}
                            </td>
                            <td className="p-2 text-right text-yellow-600 dark:text-yellow-400">
                              {item.pct_difference}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Perfect Matches Summary (collapsed by default) */}
              {qualityCheckResult.perfect_matches.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-green-700 dark:text-green-400 mb-2 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5" />
                    Perfect Matches ({qualityCheckResult.perfect_matches.length})
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    All counts exactly match DBLP expectations. Excellent! ✓
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <FileCheck className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>Click "Run Check" to validate publication counts</p>
              <p className="text-sm mt-2">
                This will compare database counts with DBLP expectations
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Ollama Configuration */}
      <Card className="border-l-4 border-l-teal-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-teal-700 dark:text-teal-400">
            <Settings className="h-5 w-5" />
            Ollama Configuration
          </CardTitle>
          <CardDescription>Configure Ollama mode and connection settings for natural language queries</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <OllamaConfigSection />
        </CardContent>
      </Card>
    </div>
  );
}

