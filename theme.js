import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2563eb', contrastText: '#ffffff' },
    secondary: { main: '#6b7280', contrastText: '#ffffff' },
    error: { main: '#dc2626', light: '#fee2e2', dark: '#7f1d1d' },
    warning: { main: '#d97706', light: '#fef3c7', dark: '#92400e' },
    success: { main: '#16a34a', light: '#dcfce7', dark: '#14532d' },
    info: { main: '#2563eb', light: '#dbeafe', dark: '#1e3a8a' },
    background: { default: '#f5f7fa', paper: '#ffffff' },
    text: {
      primary: '#1e293b', // Dark gray for primary text
      secondary: '#4b5563', // Medium gray for secondary text
    },
    gradient: {
      primary: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)',
      navbar: 'linear-gradient(90deg, #dbeafe 0%, #93c5fd 100%)', // Lighter gradient for light mode
    },
  },
  typography: {
    h4: { fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.5px' },
    h5: { fontSize: '1.5rem', fontWeight: 600 },
    body1: { fontSize: '1.1rem', lineHeight: 1.6 },
    caption: { fontSize: '0.9rem', fontWeight: 500 },
    button: { fontSize: '1rem', fontWeight: 600, textTransform: 'none' },
    fontFamily: ['"Inter", "Roboto", "Helvetica", "Arial", sans-serif'].join(','),
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: ({ palette }) => palette.gradient.navbar,
          boxShadow: '0 4px 16px rgba(147, 197, 253, 0.2)', // Adjusted shadow to match lighter gradient
          borderRadius: 12,
          transition: 'all 0.3s ease',
          '& .MuiToolbar-root': { justifyContent: 'space-between', padding: '0 16px' },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '6px 12px',
          transition: 'all 0.3s ease',
          '&:disabled': { backgroundColor: 'rgba(0, 0, 0, 0.12)', color: 'rgba(0, 0, 0, 0.38)' },
        },
        contained: { 
          background: ({ palette }) => palette.gradient.primary,
          '&:hover': { 
            transform: 'translateY(-2px)', 
            boxShadow: '0 8px 16px rgba(37, 99, 235, 0.3)',
          },
        },
        outlined: {
          '&:hover': { 
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            borderColor: ({ palette }) => palette.primary.main,
          },
        },
        text: {
          '&:hover': { 
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
          },
        },
      },
    },   
  },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#60a5fa', contrastText: '#ffffff' },
    secondary: { main: '#9ca3af', contrastText: '#ffffff' },
    error: { main: '#dc2626', light: '#7f1d1d', dark: '#fee2e2' },
    warning: { main: '#d97706', light: '#92400e', dark: '#fef3c7' },
    success: { main: '#16a34a', light: '#14532d', dark: '#dcfce7' },
    info: { main: '#60a5fa', light: '#1e3a8a', dark: '#dbeafe' },
    background: { default: '#1a202c', paper: '#2d3748' },
    text: {
      primary: '#d1d5db', // Light gray for primary text
      secondary: '#9ca3af', // Slightly darker for secondary text
    },
    gradient: {
      primary: 'linear-gradient(135deg, #60a5fa 0%, #818cf8 100%)',
      navbar: 'linear-gradient(90deg, #1a202c 0%, #4b5563 100%)', // Dark gradient for dark mode
    },
  },
  typography: theme.typography,
  components: theme.components,
});

export default null;
