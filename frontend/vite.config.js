import { defineConfig } from 'vite'

export default defineConfig({
  root: 'src',
  build: {
    outDir: '../dist',
    emptyOutDir: true
  },
  server: {
    port: 5173,
    host: true
  },
  preview: {
    port: 4173
  },
  test: {
    environment: 'jsdom',
    globals: true,
    root: '.',
    include: ['tests/**/*.test.js', 'src/**/*.test.js']
  }
})
