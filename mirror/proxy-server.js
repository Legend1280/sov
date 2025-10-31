/**
 * Simple proxy server to bypass Vite's host checking
 * Forwards all requests to localhost:5173 with the correct host header
 */

import http from 'http';
import httpProxy from 'http-proxy';

const proxy = httpProxy.createProxyServer({
  target: 'http://localhost:5173',
  changeOrigin: true,
  ws: true,
});

const server = http.createServer((req, res) => {
  // Override the host header to localhost
  req.headers.host = 'localhost:5173';
  
  // Add CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  proxy.web(req, res);
});

// Proxy WebSocket connections for HMR
server.on('upgrade', (req, socket, head) => {
  req.headers.host = 'localhost:5173';
  proxy.ws(req, socket, head);
});

proxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err);
  if (res && res.writeHead) {
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Proxy error: ' + err.message);
  }
});

const PORT = 5174;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Proxy server running on port ${PORT}`);
  console.log(`Forwarding to Vite on port 5173`);
});
