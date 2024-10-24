import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './FileUpload.module.css'; // Import the CSS module
import { useNavigate } from 'react-router-dom';

const FileUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [fileNames, setFileNames] = useState([]);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [faceBlurEnabled, setFaceBlurEnabled] = useState(false); // State for face blur
  const [textBlurEnabled, setTextBlurEnabled] = useState(false); // State for text blur
  const navigate = useNavigate(); // Initialize useNavigate

  const handleFileChange = (e) => {
    const files = e.target.files;
    setSelectedFiles(files);
    setFileNames(Array.from(files).map(file => file.name));
  };

  useEffect(() => {
    const uuid = localStorage.getItem('uuid');
    if (!uuid || uuid === 'undefined' || uuid === null || uuid === 'null' || uuid === '' || uuid === undefined) {
      navigate('/login');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFiles) {
      setMessage('Please select files.');
      setIsSuccess(false);
      toast.error('Please select files.');
      navigate('/login');
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < selectedFiles.length; i++) {
      formData.append('files[]', selectedFiles[i]);
    }

    const userUUID = localStorage.getItem('uuid');
    if (!userUUID) {
      setMessage('UUID not found in localStorage.');
      setIsSuccess(false);
      toast.error('UUID not found.');
      return;
    }

    formData.append('uuid', userUUID);
    formData.append('faceBlur', faceBlurEnabled); // Add face blur option
    formData.append('textBlur', textBlurEnabled); // Add text blur option

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

  const showToastNotification = (message) => {
    toast.error(message);
  };

  useEffect(() => {
    const interval = setInterval(checkProcessingErrors, 5000);
    return () => clearInterval(interval);
  }, []);

  const displayFiles = fileNames.slice(0, 5);
  const additionalFilesCount = fileNames.length - displayFiles.length;

  return (
    <div className={styles.fileUploadContainer}>
      <title>CBIR system</title>
      <div>
        <h2 style={{ color: 'white' }}>Upload Images</h2>
        <form className={styles.fileUploadForm} onSubmit={handleSubmit}>
          <label className={styles.customFileInput}>
            Choose Files
            <input
              type="file"
              multiple
              onChange={handleFileChange}
              className={styles.fileInput}
            />
          </label>

          <button type="submit" className={styles.uploadButton}>Upload</button>

          <br />
          {/* Bootstrap Toggle Switch for Face Blur */}
          <div className="form-check form-switch">
            <input
              className="form-check-input"
              type="checkbox"
              role="switch"
              id="flexSwitchCheckFaceBlur"
              checked={faceBlurEnabled}
              onChange={() => setFaceBlurEnabled(!faceBlurEnabled)}
            />
            <label className="form-check-label" htmlFor="flexSwitchCheckFaceBlur">
              Face Blur
            </label>
          </div>
          
          {/* Bootstrap Toggle Switch for Text Blur */}
          <div className="form-check form-switch">
            <input
              className="form-check-input"
              type="checkbox"
              role="switch"
              id="flexSwitchCheckTextBlur"
              checked={textBlurEnabled}
              onChange={() => setTextBlurEnabled(!textBlurEnabled)}
            />
            <label className="form-check-label" htmlFor="flexSwitchCheckTextBlur">
              Text Blur
            </label>
          </div>
        </form>
        <br />
        {fileNames.length > 0 && (
          <div>
            <h3 className={styles.selectedFilesHeader}>
              Selected Files ({fileNames.length}):
            </h3>
            <ul className={styles.fileList}>
              {displayFiles.map((fileName, index) => (
                <li key={index} className={styles.fileItem}>{fileName}</li>
              ))}
              {additionalFilesCount > 0 && (
                <li className={styles.fileItem}>
                  ...and {additionalFilesCount} more file{additionalFilesCount > 1 ? 's' : ''}
                </li>
              )}
            </ul>
          </div>
        )}
        {message && <p className={`${styles.message} ${isSuccess ? styles.success : styles.error}`}>{message}</p>}
        <ToastContainer />
      </div>
    </div>
  );
};


export default FileUpload;
