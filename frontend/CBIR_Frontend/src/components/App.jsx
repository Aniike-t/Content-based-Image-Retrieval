// --- START OF FILE App.jsx ---
import React, { useState, useEffect } from 'react';
import SearchBar from './SearchBar';
import ImageGrid from './ImageGrid';
import UploadArea from './UploadArea';
import Footer from './Footer';
import axios from 'axios';
import '../styles/App.css';
import { useTheme } from '../context/ThemeContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FaHome } from 'react-icons/fa';

const App = () => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [imageFilenames, setImageFilenames] = useState([]);

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setError('Please enter a search query.');
      setImages([]);
      setSearchPerformed(true);
      return;
    }

    setLoading(true);
    setError(null);
    setSearchPerformed(true);
    setImages([]);
    setImageFilenames([]);

    try {
      const response = await axios.post('http://localhost:5000/search', { query });
      setImages(response.data.images);
      setImageFilenames(response.data.filenames);
    } catch (err) {
      console.error('Error fetching images:', err);
      setError('Failed to fetch images. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const { isDarkMode, toggleTheme } = useTheme();

  const handleGetAllImages = async () => {
    setLoading(true);
    setError(null);
    setSearchPerformed(false);
    setSearchQuery('');
    setImages([]);
    setImageFilenames([]);

    try {
      const response = await axios.get('http://localhost:5000/all_images');
      setImages(response.data.images);
      setImageFilenames(response.data.filenames);
    } catch (err) {
      console.error('Error fetching all images:', err);
      setError('Failed to fetch all images. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGetAllImages();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Content-Based Image Retrieval</h1>
          <div className="header-buttons"> {/* Container for buttons */}
            <button className="home-button" onClick={handleGetAllImages} title="Home">
              <FaHome />
            </button>
            <button className="theme-toggle-button" onClick={toggleTheme}>
              {isDarkMode ? 'Light Mode' : 'Dark Mode'}
            </button>
          </div>
        </div>
      </header>
      <main className="app-main" >
        <SearchBar onSearch={handleSearch} />

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <UploadArea />
        </div>
        
        {loading && <div className="spinner"></div>}
        {error && <div className="error-message">{error}</div>}
        {searchPerformed && images.length === 0 && !loading && (
          <div className="no-results">No images found.</div>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <ImageGrid images={images} query={searchQuery} filenames={imageFilenames} />
        </div>
      </main>
      <Footer />
      <ToastContainer />
    </div>
  );
};

export default App;