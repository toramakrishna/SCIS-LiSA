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
  RefreshCw
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

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

  // Poll for task status
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (fetchStatus.status === 'running' || fetchStatus.status === 'starting') {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/admin/fetch-status`);
          setFetchStatus(response.data);
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
          const response = await axios.get(`${API_BASE_URL}/admin/ingest-status`);
          setIngestStatus(response.data);
          
          // Refresh stats when ingestion completes
          if (response.data.status === 'completed') {
            loadDatabaseStats();
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
      const response = await axios.get(`${API_BASE_URL}/admin/test-current-db`);
      setConnectionStatus('success');
      setConnectionMessage(`Connected successfully! Database version: ${response.data.database_version.split(' ')[1]}`);
    } catch (error: any) {
      setConnectionStatus('error');
      setConnectionMessage(error.response?.data?.detail || 'Connection failed');
    }
  };

  const testCustomConnection = async () => {
    setConnectionStatus('testing');
    setConnectionMessage('Testing custom database connection...');

    try {
      const response = await axios.post(`${API_BASE_URL}/admin/test-db-connection`, connectionConfig);
      setConnectionStatus('success');
      setConnectionMessage('Custom connection successful!');
    } catch (error: any) {
      setConnectionStatus('error');
      setConnectionMessage(error.response?.data?.detail || 'Connection failed');
    }
  };

  const testDblpApi = async () => {
    setDblpApiStatus('testing');
    setDblpApiMessage('Testing DBLP API connectivity...');

    try {
      const response = await axios.get(`${API_BASE_URL}/admin/test-dblp-api`);
      setDblpApiStatus('success');
      setDblpApiMessage(response.data.message);
    } catch (error: any) {
      setDblpApiStatus('error');
      setDblpApiMessage(error.response?.data?.detail || 'DBLP API test failed');
    }
  };

  const startFetchDblp = async () => {
    try {
      await axios.post(`${API_BASE_URL}/admin/fetch-dblp-data`, {
        output_directory: fetchPath,
        faculty_json_path: 'src/backend/references/dblp/faculty_dblp_matched.json'
      });
      setFetchStatus({ status: 'starting', progress: 0, message: 'Starting fetch...' });
    } catch (error: any) {
      alert(`Failed to start fetch: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const startIngestion = async () => {
    try {
      await axios.post(`${API_BASE_URL}/admin/ingest-data`, {
        dataset_path: ingestPath,
        source_name: 'DBLP'
      });
      setIngestStatus({ status: 'starting', progress: 0, message: 'Starting ingestion...' });
    } catch (error: any) {
      alert(`Failed to start ingestion: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const loadDatabaseStats = async () => {
    setStatsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/database-stats`);
      setDbStats(response.data.stats);
    } catch (error) {
      console.error('Failed to load database stats:', error);
    } finally {
      setStatsLoading(false);
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
            <div className="flex items-center gap-3">
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
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-400">
                <BarChart3 className="h-5 w-5" />
                Database Statistics
              </CardTitle>
              <CardDescription>Current database record counts</CardDescription>
            </div>
            <Button size="sm" variant="outline" onClick={loadDatabaseStats} disabled={statsLoading}>
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
    </div>
  );
}
