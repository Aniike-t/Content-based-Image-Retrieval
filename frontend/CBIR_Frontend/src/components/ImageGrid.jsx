 // --- START OF FILE ImageGrid.jsx ---
 import React, { useState, useEffect } from 'react';
 import { FaThumbsUp, FaThumbsDown } from 'react-icons/fa';
 import axios from 'axios';
 import { toast } from 'react-toastify'; // Import only toast
 // import 'react-toastify/dist/ReactToastify.css'; // NO CSS import here, in App.jsx

 const ImageGrid = ({ images, query, filenames }) => {
 const [sentences, setSentences] = useState({});

 // Initialize sentences for each image when filenames change
 useEffect(() => {
     const initialSentences = {};
     filenames.forEach(filename => {
     initialSentences[filename] = ''; // Initialize with empty string
     });
     setSentences(initialSentences);
 }, [filenames]);  // This effect runs when filenames change

 const handleFeedback = async (filename, feedback) => {
     try {
     const response = await axios.post('http://localhost:5000/feedback', {
         filename: filename,
         feedback: feedback,
         query: query,
     });
     console.log(response.data.message);
     toast.success(response.data.message);
     } catch (error) {
     console.error('Error sending feedback:', error);
     toast.error('Error sending feedback');
     }
 };

 const handleSentenceSubmit = async (filename) => {
     const sentence = sentences[filename]; // Get the sentence for *this* image

     if (!sentence || !sentence.trim()) {
     toast.error("Please enter a sentence for this image.");
     return;
     }

     try {
      const response = await axios.post('http://localhost:5000/user_sentence', {
          filename: filename,
          sentence: sentence,
      });
      console.log(response.data.message);
      toast.success(response.data.message); // This should show if successful
  
      setSentences(prevSentences => ({
          ...prevSentences,
          [filename]: '',
      }));
  
  } catch (error) {
      console.error('Error sending sentence:', error); // Log the full error
      if (error.response) {
         // The request was made and the server responded with a status code
         // that falls out of the range of 2xx
         console.error("Data:", error.response.data);
         console.error("Status:", error.response.status);
         console.error("Headers:", error.response.headers);
         toast.error(`Server Error (${error.response.status}): ${error.response.data.error || 'Unknown error'}`); // Display server error
       } else if (error.request) {
         // The request was made but no response was received
         console.error("No response received:", error.request);
         toast.error("No response from server. Please check your network connection.");
       } else {
         // Something happened in setting up the request that triggered an Error
         console.error('Error setting up request:', error.message);
          toast.error('Error sending sentence:'+ error.message); // More descriptive
       }
  }
 };

 return (
     <>
     <div className="image-grid" style={{ display: 'grid', width: '75%', gap: '16px' }}>
         {images.map((image, index) => {
         const filename = filenames[index]; // Get the filename for the current image
        return (
          <div key={index} className="image-item">
            <img src={`data:image/jpeg;base64,${image}`} alt={`Result ${index}`} />
            <div className="feedback-buttons">
              <button
                className="feedback-button positive"
                onClick={(e) => { e.stopPropagation(); handleFeedback(filename, 'positive'); }}
                title="Useful"
              >
                <FaThumbsUp />
              </button>
              <button
                className="feedback-button negative"
                onClick={(e) => { e.stopPropagation(); handleFeedback(filename, 'negative'); }}
                title="Not Useful"
              >
                <FaThumbsDown />
              </button>
            </div>
            {/* Sentence Input and Submit Button - Per Image */}
            <div className="sentence-input-area" style={{ display: 'flex', alignItems: 'flex-start' }}>
              <input
                type="text"
                placeholder="Add a sentence about this image..."
                value={sentences[filename] || ''} // Get sentence for *this* image
                onChange={(e) =>
                  setSentences(prevSentences => ({
                    ...prevSentences,  // Copy previous sentences
                    [filename]: e.target.value, // Update sentence for *this* image
                  }))
                }
                className="sentence-input"
                style={{ flex: 1, marginRight: '8px' }}
              />
              <button
                className="sentence-submit-button"
                onClick={() => handleSentenceSubmit(filename)} // Pass filename
                style={{ flexShrink: 0 }}
              >
                Submit
              </button>
            </div>
          </div>
        );
         })}
     </div>
     {/* <ToastContainer /> REMOVE THIS */}
     </>
     );
 };

 export default ImageGrid;