import { useState } from "react";
import { askQuestion, uploadPaper } from "./api";
import FiguresPanel from "./components/FiguresPanel";
import QAPanel from "./components/QAPanel";
import SummaryPanel from "./components/SummaryPanel";
import UploadPanel from "./components/UploadPanel";

function App() {
  const [documentData, setDocumentData] = useState(null);
  const [qaResponse, setQaResponse] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (file) => {
    setError("");
    setQaResponse(null);
    setIsUploading(true);

    try {
      const data = await uploadPaper(file);
      setDocumentData(data);
    } catch (uploadError) {
      setError(uploadError.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleAsk = async (question) => {
    if (!documentData?.documentId) {
      return;
    }

    setError("");
    setIsAsking(true);

    try {
      const result = await askQuestion(documentData.documentId, question);
      setQaResponse(result);
    } catch (askError) {
      setError(askError.message || "Question answering failed.");
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">NLP 3rd Year Project</p>
        <h1>Explainable Multimodal Research Paper Assistant</h1>
        <p>
          Upload a research paper PDF, get text and figure understanding, then ask questions with transparent
          evidence traces.
        </p>
      </header>

      <UploadPanel onUpload={handleUpload} isUploading={isUploading} />

      {error && <p className="error-banner">{error}</p>}

      <SummaryPanel data={documentData} />
      <FiguresPanel figures={documentData?.figures || []} />
      <QAPanel
        documentId={documentData?.documentId}
        onAsk={handleAsk}
        response={qaResponse}
        isLoading={isAsking}
      />
    </main>
  );
}

export default App;
