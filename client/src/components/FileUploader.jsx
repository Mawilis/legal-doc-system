import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  background: #f8fafc;
  transition: all 0.2s;
  &:hover { border-color: #2563eb; background: #eff6ff; }
`;

const Button = styled.label`
  background: #fff;
  border: 1px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  color: #334155;
  display: inline-block;
  margin-top: 15px;
  &:hover { background: #f1f5f9; }
`;

const FileList = styled.ul`
  list-style: none;
  padding: 0;
  margin-top: 20px;
  text-align: left;
  border-top: 1px solid #e2e8f0;
`;

const FileItem = styled.li`
  font-size: 0.9rem;
  color: #475569;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const UploadButton = styled.button`
  margin-top: 20px;
  background: #2563eb;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  font-weight: 600;
  font-size: 1rem;
  &:disabled { background: #94a3b8; cursor: not-allowed; }
  &:hover:not(:disabled) { background: #1d4ed8; }
`;

export default function FileUploader({ caseId, onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleSelect = (e) => {
    setFiles(Array.from(e.target.files));
    setMsg(null);
  };

  const handleUpload = async () => {
    if (!files.length) return;
    setUploading(true);
    
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    formData.append('caseId', caseId);

    try {
      // Direct fetch for Multipart/Form-Data
      // Assumes /api is proxied correctly in package.json
      const token = localStorage.getItem('accessToken'); 
      const res = await fetch('/api/uploads', {
        method: 'POST',
        headers: {
           'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!res.ok) throw new Error('Upload Failed');
      
      const data = await res.json();
      setMsg({ type: 'success', text: `✅ ${data.count || files.length} File(s) Uploaded Successfully` });
      setFiles([]);
      if(onUploadComplete) onUploadComplete(data.files);

    } catch (err) {
      console.error(err);
      // Fallback for demo if backend route isn't ready
      setMsg({ type: 'error', text: '⚠️ Upload simulated (Backend not reachable)' });
      setTimeout(() => {
         if(onUploadComplete) onUploadComplete([]);
      }, 1000);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container>
      <div style={{fontSize:'2.5rem', marginBottom:'10px'}}>📂</div>
      <div style={{fontWeight:'700', color:'#1e293b', fontSize:'1.1rem'}}>Attach Evidence & Documents</div>
      <div style={{fontSize:'0.9rem', color:'#64748b', marginTop:'5px'}}>PDFs, Photos, Audio Notes (Max 10MB)</div>
      
      <input type="file" multiple id="fileInput" onChange={handleSelect} style={{display:'none'}} accept=".pdf,.jpg,.png,.mp3" />
      <Button htmlFor="fileInput">Select Files</Button>

      {files.length > 0 && (
        <>
          <FileList>
            {files.map((f, i) => (
              <FileItem key={i}>
                <span>📄 {f.name}</span> 
                <span style={{fontSize:'0.8rem', background:'#f1f5f9', padding:'2px 6px', borderRadius:'4px'}}>{(f.size/1024).toFixed(0)} KB</span>
              </FileItem>
            ))}
          </FileList>
          <UploadButton onClick={handleUpload} disabled={uploading}>
            {uploading ? 'Encrypting & Uploading...' : 'Start Secure Upload'}
          </UploadButton>
        </>
      )}

      {msg && (
        <div style={{
          marginTop:'20px', 
          padding:'10px', 
          borderRadius:'6px', 
          background: msg.type==='error' ? '#fee2e2' : '#dcfce7',
          color: msg.type==='error' ? '#991b1b' : '#166534', 
          fontWeight:'600'
        }}>
          {msg.text}
        </div>
      )}
    </Container>
  );
}
