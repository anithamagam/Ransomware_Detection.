import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from './theme'; // 👈 Import your theme
import CssBaseline from '@mui/material/CssBaseline'; // 👈 Add this

const rootElement = document.getElementById('root');
if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      {/* 👇 Wrap your App */}
      <ThemeProvider theme={theme}>
        <CssBaseline /> {/* This resets CSS and applies background color */}
        <App />
      </ThemeProvider>
    </React.StrictMode>
  );
} else {
  console.error("Root element with id 'root' not found.");
}
