import { useEffect, useRef, useState } from "react";

export default function ArchitectureDiagram({ diagram, title }) {
  const ref = useRef(null);
  const viewportRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef({ startX: 0, startY: 0, left: 0, top: 0 });

  const clampZoom = (value) => Math.max(0.3, Math.min(4, value));
  const zoomIn = () => setZoom((z) => clampZoom(z + 0.15));
  const zoomOut = () => setZoom((z) => clampZoom(z - 0.15));
  const resetZoom = () => setZoom(1);

  useEffect(() => {
    setZoom(1);
    let mounted = true;
    async function render() {
      if (!diagram || !ref.current) return;
      const mermaid = (await import("mermaid")).default;
      mermaid.initialize({
        startOnLoad: false,
        theme: "base",
        flowchart: { curve: "linear" },
        themeVariables: {
          primaryColor: "#101214",
          primaryBorderColor: "#5f6368",
          primaryTextColor: "#e8eaed",
          lineColor: "#8ab4f8",
          secondaryColor: "#101214",
          tertiaryColor: "#101214",
          background: "#000000",
          fontSize: "13px",
        },
      });
      const { svg } = await mermaid.render(`diag_${Date.now()}`, diagram);
      if (mounted) ref.current.innerHTML = svg;
    }
    render();
    return () => {
      mounted = false;
    };
  }, [diagram]);

  useEffect(() => {
    const element = viewportRef.current;
    if (!element) return undefined;
    const wheelHandler = (event) => {
      event.preventDefault();
      event.stopPropagation();
      const delta = event.deltaY > 0 ? -0.12 : 0.12;
      setZoom((z) => clampZoom(z + delta));
    };
    element.addEventListener("wheel", wheelHandler, { passive: false });
    return () => element.removeEventListener("wheel", wheelHandler);
  }, []);

  const onMouseDown = (event) => {
    const element = viewportRef.current;
    if (!element) return;
    setIsDragging(true);
    dragRef.current = {
      startX: event.clientX,
      startY: event.clientY,
      left: element.scrollLeft,
      top: element.scrollTop,
    };
  };

  const onMouseMove = (event) => {
    if (!isDragging) return;
    const element = viewportRef.current;
    if (!element) return;
    const dx = event.clientX - dragRef.current.startX;
    const dy = event.clientY - dragRef.current.startY;
    element.scrollLeft = dragRef.current.left - dx;
    element.scrollTop = dragRef.current.top - dy;
  };

  const onMouseUp = () => setIsDragging(false);

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: ".5rem", gap: ".6rem" }}>
        <div className="panel-title" style={{ marginBottom: 0 }}>
          {title}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: ".35rem" }}>
          <button className="btn" onClick={zoomOut} type="button">
            -
          </button>
          <span className="muted" style={{ minWidth: 54, textAlign: "center", fontSize: ".8rem" }}>
            {Math.round(zoom * 100)}%
          </span>
          <button className="btn" onClick={zoomIn} type="button">
            +
          </button>
          <button className="btn" onClick={resetZoom} type="button">
            Reset
          </button>
        </div>
      </div>
      <div
        ref={viewportRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        style={{
          overflow: "auto",
          minHeight: 320,
          maxHeight: 520,
          border: "1px solid var(--border)",
          borderRadius: 10,
          padding: ".75rem",
          overscrollBehavior: "contain",
          cursor: isDragging ? "grabbing" : "grab",
          userSelect: "none",
        }}
      >
        <div
          ref={ref}
          style={{
            transform: `scale(${zoom})`,
            transformOrigin: "top left",
            width: "max-content",
          }}
        />
      </div>
    </div>
  );
}
