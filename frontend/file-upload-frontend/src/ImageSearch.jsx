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
            // Replace 'http://localhost:5000/search' with your actual backend endpoint
            const response = await axios.post('http://localhost:5000/search', { query });

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
        <div className="container">
            <h1>Content-Based Image Retrieval System</h1>
            <form onSubmit={handleSearch}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search images..."
                />
                <button type="submit"><FaSearch/></button>
            </form>

            {loading && <div className="spinner"></div>}

            {error && <div className="error-message">{error}</div>}
            
            {/* Conditionally render the hr tag only if images are present */}
            {images.length > 0 && (
                <hr style={{ marginTop: '5%', opacity: '50%', border: '1.7px solid', width: '100%', borderRadius: '20px' }} />
            )}

            {!images.length && !loading && !error && (
                <div className="placeholder">
                    <p>No Content to show</p>
                </div>
            )}

            <div className="image-grid">
                {images.map((image, index) => (
                    <div key={index} className="image-item">
                        {/* Set the src to the base64 image string */}
                        <img src={`data:image/jpeg;base64,${image}`} alt={`img-${index}`} />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ImageSearch;
