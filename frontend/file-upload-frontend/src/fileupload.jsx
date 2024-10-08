import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './FileUpload.module.css'; // Import the CSS module

const FileUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [fileNames, setFileNames] = useState([]);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const handleFileChange = (e) => {
    const files = e.target.files;
    setSelectedFiles(files);
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
        <h2 style={{color:'white'}}>Upload Images</h2>
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