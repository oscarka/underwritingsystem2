import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
    base: '/admin/',
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        port: 3004,
        strictPort: true,
        cors: true,
        hmr: {
            protocol: 'ws',
            host: 'localhost',
            port: 3004,
            clientPort: 3004
        },
        watch: {
            usePolling: true
        },
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
                secure: false
            }
        }
    },
    build: {
        sourcemap: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    'vue-vendor': ['vue', 'vue-router']
                }
            }
        }
    },
    css: {
        devSourcemap: true
    },
    esbuild: {
        jsxFactory: 'h',
        jsxFragment: 'Fragment'
    }
}) 