import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/

// NOTE: The babel-plugin-react-compiler is experimental and may not be stable for production use.
// To disable it, set the environment variable USE_REACT_COMPILER=false.
// See: https://github.com/babel/babel-plugin-react-compiler

const useReactCompiler = process.env.USE_REACT_COMPILER !== 'false';

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: useReactCompiler ? [['babel-plugin-react-compiler']] : [],
      },
    }),
  ],
})
