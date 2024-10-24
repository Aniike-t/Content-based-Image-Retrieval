import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  define: { global: 'globalThis' },
  server: {
    host: 'localhost', // or true
    port: 3000, // Set this to your desired port
    hmr: {
      // Options for hot module replacement
      protocol: 'ws', // Use WebSocket for HMR
      host: 'localhost', // Your host
      port: 3000, // The same port as your server
    },
  },
});
