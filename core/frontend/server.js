import viteConfig from './vite.config.js'; // Import your Vite configuration

import express from 'express'
import { createServer } from 'vite'

const DEFAULT_ADDRESS = 'http://blueos.local/';
const SERVER_ADDRESS = process.env.BLUEOS_ADDRESS ?? DEFAULT_ADDRESS;

const parentServer = express()

const vite = await createServer({
  ...viteConfig,
  server: {
    // Enable middleware mode
    middlewareMode: {
      // Provide the parent http server for proxy WebSocket
      server: parentServer,
    },
    proxy: {
      '^/status': {
        target: SERVER_ADDRESS,
      },
      '^/ardupilot-manager': {
        target: SERVER_ADDRESS,
      },
      '^/bag': {
        target: SERVER_ADDRESS,
      },
      '^/beacon': {
        target: SERVER_ADDRESS,
      },
      '^/bridget': {
        target: SERVER_ADDRESS,
      },
      '^/cable-guy': {
        target: SERVER_ADDRESS,
      },
      '^/commander': {
        target: SERVER_ADDRESS,
      },
      '^/docker': {
        target: SERVER_ADDRESS,
      },
      '^/file-browser': {
        target: SERVER_ADDRESS,
      },
      '^/helper': {
        target: SERVER_ADDRESS,
      },
      '^/upload': {
        target: SERVER_ADDRESS,
      },
      '^/kraken': {
        target: SERVER_ADDRESS,
        onProxyRes: (proxyRes, request, response) => {
          proxyRes.on('data', (data) => {
            response.write(data)
          })
          proxyRes.on('end', () => {
            response.end()
          })
        },
      },
      '^/nmea-injector': {
        target: SERVER_ADDRESS,
      },
      '^/logviewer': {
        target: SERVER_ADDRESS,
      },
      '^/mavlink': {
        target: SERVER_ADDRESS,
        changeOrigin: true,
        ws: true,
      },
      '^/mavlink2rest': {
        target: SERVER_ADDRESS,
        changeOrigin: true,
        ws: true,
      },
      '^/mavlink-camera-manager': {
        target: SERVER_ADDRESS,
      },
      '^/network-test': {
        target: SERVER_ADDRESS,
      },
      '^/ping': {
        target: SERVER_ADDRESS,
      },
      '^/system-information': {
        target: SERVER_ADDRESS,
      },
      '^/terminal': {
        target: SERVER_ADDRESS,
      },
      '^/userdata': {
        target: SERVER_ADDRESS,
      },
      '^/vehicles': {
        target: SERVER_ADDRESS,
      },
      '^/version-chooser': {
        target: SERVER_ADDRESS,
        onProxyRes: (proxyRes, request, response) => {
          proxyRes.on('data', (data) => {
            response.write(data)
          })
          proxyRes.on('end', () => {
            response.end()
          })
        },
      },
      '^/wifi-manager': {
        target: SERVER_ADDRESS,
      },
    },
  }
})

parentServer.use(vite.middlewares)
parentServer.listen(8080, () => {
  console.log(`Server running at http://localhost:8080`);
});