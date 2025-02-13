import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './components/App';
import './styles/index.css';
import { ThemeProvider } from './context/ThemeContext'; // Import ThemeProvider

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);