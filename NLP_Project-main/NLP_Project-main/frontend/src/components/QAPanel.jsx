import { useState } from "react";

function QAPanel({ documentId, onAsk, response, isLoading }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!question.trim() || !documentId || isLoading) {
      return;
    }
    onAsk(question.trim());
  };

  return (
    <section className="card">
      <h2>4. Ask Questions with Explainability</h2>
      <form className="qa-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask: What is the main methodology of this paper?"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={!documentId || isLoading}
        />
        <button type="submit" disabled={!documentId || isLoading || !question.trim()}>
          {isLoading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {response && (
        <div className="qa-result">
          <h3>Answer</h3>
          <p>{response.answer}</p>
          <p className="muted">Confidence: {response.confidence}</p>

          <h3>Reasoning Trace (Evidence)</h3>
          <ul className="trace-list">
            {response.reasoningTrace?.map((item) => (
              <li key={`${item.rank}-${item.page}`}>
                <strong>Rank {item.rank} | Page {item.page} | Score {item.retrievalScore}</strong>
                <p>{item.evidence}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default QAPanel;
