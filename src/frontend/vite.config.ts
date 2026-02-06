import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Detect if running in GitHub Codespaces
const isCodespaces = process.env.CODESPACE_NAME !== undefined;
const codespaceUrl = isCodespaces 
  ? `https://${process.env.CODESPACE_NAME}-8000.${process.env.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN || 'app.github.dev'}`
  : 'http://localhost:8000';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: codespaceUrl,
        changeOrigin: true,
        secure: false,
        autoRewrite: true,  // Automatically rewrite the Host header on (301/302/307/308) redirects
        protocolRewrite: isCodespaces ? 'https' : 'http',  // Protocol to use for redirects
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request:', req.method, req.url, '-> Target:', proxyReq.path);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response:', proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
})
