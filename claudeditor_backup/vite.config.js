import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: '.',
  publicDir: 'public',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'monaco-editor': ['monaco-editor'],
          'react-vendor': ['react', 'react-dom'],
        },
      },
    },
  },
  server: {
    port: 5175,
    host: '0.0.0.0',
    strictPort: true,
    allowedHosts: [
      '5175-i2q85i2gb7dchq7unsorp-0fdb191e.manusvm.computer',
      '5175-iombq8cye6vkzxjj2gt7n-030bfc10.manusvm.computer',
      'localhost',
      '127.0.0.1',
      '0.0.0.0'
    ],
  },
  optimizeDeps: {
    include: ['monaco-editor', '@tauri-apps/api'],
  },
  define: {
    global: 'globalThis',
  },
  clearScreen: false,
  envPrefix: ['VITE_', 'TAURI_'],
})