import React, { useState } from 'react'; 
import axios from 'axios';
import './ImageSearch.css';
import { FaSearch } from 'react-icons/fa'; // Ensure this path is correct

const ImageSearch = () => {
    const [query, setQuery] = useState('');
    const [images, setImages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Handler for search form submission
    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) {
            setError('Please enter a query to get related images..');
            return;
        }

        setLoading(true);
        setError(null);
        setImages([]);

        try {
            const uuid = localStorage.getItem('uuid'); // Get UUID from local storage

            // Replace 'http://localhost:5000/search' with your actual backend endpoint
            const response = await axios.post('http://localhost:5000/search', { query, uuid }); // Send UUID with the query

            // Assuming your backend returns an array of base64 image strings in response.data.images
            setImages(response.data.images);
        } catch (err) {
            console.error('Error fetching images:', err);
            setError('Failed to fetch images. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="cbir-container">
            <h1 className="cbir-title">Content-Based Image Retrieval System</h1>
            <form className="cbir-form" onSubmit={handleSearch}>
                <input
                    className="cbir-input"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search images..."
                />
                <button className="cbir-button" type="submit"><FaSearch /></button>
            </form>

            {loading && <div className="cbir-spinner"></div>}

            {error && <div className="cbir-error-message">{error}</div>}
            
            {images.length > 0 && (
                <hr className="cbir-divider" />
            )}

            {!images.length && !loading && !error && (
                <div className="cbir-placeholder">
                    <p>No Content to show</p>
                </div>
            )}

            <div className="cbir-image-grid">
                {images.map((image, index) => (
                    <div key={index} className="cbir-image-item">
                        <img src={`data:image/jpeg;base64,${image}`} alt={`img-${index}`} />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ImageSearch;
