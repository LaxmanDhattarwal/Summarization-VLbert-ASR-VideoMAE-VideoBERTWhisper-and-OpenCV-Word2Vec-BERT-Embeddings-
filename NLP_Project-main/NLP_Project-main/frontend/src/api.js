const API_BASE = (import.meta.env.VITE_API_URL || "http://localhost:5000").replace(/\/$/, "");

async function parseResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    const message = data?.error || "Request failed";
    throw new Error(message);
  }
  return data;
}

export async function uploadPaper(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  return parseResponse(response);
}

export async function askQuestion(documentId, question) {
  const response = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ documentId, question }),
  });

  return parseResponse(response);
}

export function toAssetUrl(path) {
  if (!path) {
    return "";
  }
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE}${path}`;
}
