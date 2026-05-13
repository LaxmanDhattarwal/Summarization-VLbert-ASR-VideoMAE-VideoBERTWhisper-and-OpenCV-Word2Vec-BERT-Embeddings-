import { toAssetUrl } from "../api";

function FiguresPanel({ figures = [] }) {
  if (!figures.length) {
    return (
      <section className="card">
        <h2>3. Figure Understanding (ViT)</h2>
        <p>No embedded figures were detected in this PDF.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>3. Figure Understanding (ViT)</h2>
      <p>
        Captions are generated using a ViT-based image captioning model, then linked with the paper context.
      </p>
      <div className="figure-grid">
        {figures.map((figure) => (
          <article className="figure-card" key={figure.figureId}>
            <img src={toAssetUrl(figure.url)} alt={`Figure ${figure.figureId}`} loading="lazy" />
            <div>
              <h3>Figure {figure.figureId}</h3>
              <p className="muted">Page {figure.page}</p>
              <p>{figure.caption}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default FiguresPanel;
