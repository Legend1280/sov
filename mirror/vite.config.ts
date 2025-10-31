import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  root: './client',
  plugins: [
    tailwindcss(),
    react(),
    {
      name: 'configure-server',
      configureServer(server) {
        // Disable host checking by removing the middleware
        server.middlewares.use((req, res, next) => {
          // Allow all hosts
          next();
        });
      },
    },
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './client/src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // Disable host check
    proxy: {},
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
  },
});
