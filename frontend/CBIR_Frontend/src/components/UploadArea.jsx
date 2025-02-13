// UploadArea.jsx (CORRECTED)
import React, { useState, useRef } from 'react';
import { toast } from 'react-toastify'; // Import only 'toast'
// import 'react-toastify/dist/ReactToastify.css'; // NO - CSS imported in App.jsx

const UploadArea = () => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files);
    }
  };

  const handleUpload = async (files) => {
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files[]', file));

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      });
      if (response.ok) {
        toast.success('Files uploaded successfully!');
      } else {
        toast.error('Failed to upload files.');
      }
    } catch (error) {
      toast.error('Error uploading files.');
    }
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div
      className={`upload-area ${isDragging ? 'dragging' : ''}`}
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input type="file" ref={fileInputRef} style={{ display: 'none' }} multiple onChange={(e) => handleUpload(e.target.files)} />
      <p>Drag and drop images here or click to upload</p>
      {/* <ToastContainer />  REMOVE THIS */}
    </div>
  );
};

export default UploadArea;