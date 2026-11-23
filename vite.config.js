import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  publicDir: 'assets',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'esbuild',
    cssMinify: true,
    rollupOptions: {
      input: {
        main: 'index.html',
        avanyamehra: 'avanyamehra.html',
        mairamehra: 'mairamehra.html',
        iamgagankumar: 'iamgagankumar.html',
        resrise: 'resrise.html',
        gagankumarrocks: 'gagankumarrocks.html',
      },
    },
  },
  server: {
    port: 3000,
    open: true,
  },
});