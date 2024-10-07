import React from 'react';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileUpload from './fileupload';
import ImageSearch from './ImageSearch';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<ImageSearch />} />
        <Route path="/upload" element={<FileUpload />} />
      </Routes>
    </Router>
  </StrictMode>
);
