import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    plugins: [vue(), {
      name: 'html-transform',
      transformIndexHtml(html) {
        return html.replace(/%VITE_BAIDU_MAP_AK%/g, env.VITE_BAIDU_MAP_AK)
      }
    }],
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
        '/media': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        }
      }
    }
  }
})
