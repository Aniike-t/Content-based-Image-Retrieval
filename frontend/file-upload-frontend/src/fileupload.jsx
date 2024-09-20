import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

const FileUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [fileNames, setFileNames] = useState([]);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const handleFileChange = (e) => {
    const files = e.target.files;
    setSelectedFiles(files);

    // Convert FileList to Array and map to file names
    setFileNames(Array.from(files).map(file => file.name));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFiles) {
      setMessage('Please select files.');
      setIsSuccess(false);
      toast.error('Please select files.');
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < selectedFiles.length; i++) {
      formData.append('files[]', selectedFiles[i]);
    }

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setMessage('Files uploaded successfully!');
        setIsSuccess(true);
        toast.success('Files uploaded successfully!');
      } else {
        setMessage('Failed to upload files.');
        setIsSuccess(false);
        toast.error('Failed to upload files.');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Error uploading files.');
      setIsSuccess(false);
      toast.error('Error uploading files.');
    }
  };

  // Function to check for processing errors
  const checkProcessingErrors = () => {
    fetch('/processing_errors')
      .then(response => response.json())
      .then(data => {
        if (data.errors) {
          data.errors.forEach(error => {
            showToastNotification(`Error processing ${error.file}: ${error.error}`);
          });
        }
      })
      .catch(err => console.error('Error fetching processing errors:', err));
  };

  // Show toast notification
  const showToastNotification = (message) => {
    toast.error(message);
  };

  // Poll every 5 seconds to check for errors
  useEffect(() => {
    const interval = setInterval(checkProcessingErrors, 5000);
    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  // Limit number of files to display
  const displayFiles = fileNames.slice(0, 5);
  const additionalFilesCount = fileNames.length - displayFiles.length;

  return (
    <>
      <title>CBIR system</title>
      <div>
        <h2>Upload Files</h2>
        <form onSubmit={handleSubmit}>
          <input type="file" multiple onChange={handleFileChange} />
          <button type="submit" color="#000">Upload</button>
        </form>
        {fileNames.length > 0 && (
          <div>
            <h3 style={{ color: '#000' }}>Selected Files ({fileNames.length}):</h3>
            <ul>
              {displayFiles.map((fileName, index) => (
                <li key={index}>{fileName}</li>
              ))}
              {additionalFilesCount > 0 && (
                <li>...and {additionalFilesCount} more file{additionalFilesCount > 1 ? 's' : ''}</li>
              )}
            </ul>
          </div>
        )}
        {message && <p className={isSuccess ? 'success' : 'error'}>{message}</p>}

        {/* Toast Container for Notifications */}
        <ToastContainer />
      </div>
    </>
  );
};

export default FileUpload;
