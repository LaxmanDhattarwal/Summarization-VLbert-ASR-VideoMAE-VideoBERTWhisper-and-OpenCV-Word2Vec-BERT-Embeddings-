function SummaryPanel({ data }) {
  if (!data) {
    return null;
  }

  const { summary, metadata } = data;

  return (
    <section className="card">
      <h2>2. Paper Summary</h2>
      <div className="stats-grid">
        <article>
          <h3>Chunks Indexed</h3>
          <p>{metadata?.totalChunks ?? 0}</p>
        </article>
        <article>
          <h3>Figures Found</h3>
          <p>{metadata?.totalFigures ?? 0}</p>
        </article>
        <article>
          <h3>Characters Parsed</h3>
          <p>{metadata?.textCharacters ?? 0}</p>
        </article>
      </div>
      <p className="summary-text">{summary}</p>
    </section>
  );
}

export default SummaryPanel;
