import { useState } from "react";

function UploadPanel({ onUpload, isUploading }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!selectedFile || isUploading) {
      return;
    }
    onUpload(selectedFile);
  };

  return (
    <section className="card upload-card">
      <h2>1. Upload Research Paper (PDF)</h2>
      <p>
        The backend extracts text and figures, runs multimodal models, and produces explainable outputs.
      </p>
      <form className="upload-form" onSubmit={handleSubmit}>
        <label className="file-input-wrap">
          <span>Select PDF</span>
          <input
            type="file"
            accept="application/pdf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />
        </label>
        <button type="submit" disabled={!selectedFile || isUploading}>
          {isUploading ? "Processing..." : "Upload and Analyze"}
        </button>
      </form>
      {selectedFile && (
        <p className="file-meta">
          Selected: {selectedFile.name} ({Math.round(selectedFile.size / 1024)} KB)
        </p>
      )}
    </section>
  );
}

export default UploadPanel;
