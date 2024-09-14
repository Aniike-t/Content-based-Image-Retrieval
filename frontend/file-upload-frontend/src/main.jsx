import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import FileUpload from './fileupload'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <FileUpload />
  </StrictMode>,
)
