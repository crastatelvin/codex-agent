import { useEffect, useRef } from "react";

const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<>[]{}";

export default function MatrixBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const ctx = canvas.getContext("2d");
    let raf = 0;
    const size = 14;

    const reset = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    reset();
    const cols = Math.floor(canvas.width / size);
    const drops = Array(cols).fill(1);

    const draw = () => {
      ctx.fillStyle = "rgba(0, 0, 0, 0.07)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.font = `${size}px JetBrains Mono`;
      drops.forEach((y, x) => {
        const t = CHARS[Math.floor(Math.random() * CHARS.length)];
        ctx.fillStyle = Math.random() > 0.9 ? "#ffffff" : "#00ff88";
        ctx.fillText(t, x * size, y * size);
        if (y * size > canvas.height && Math.random() > 0.975) drops[x] = 0;
        drops[x] += 1;
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    window.addEventListener("resize", reset);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", reset);
    };
  }, []);

  return <canvas ref={canvasRef} style={{ position: "fixed", inset: 0, zIndex: 0, opacity: 0.08, pointerEvents: "none" }} />;
}
