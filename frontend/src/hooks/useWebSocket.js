import { useEffect, useState } from "react";

const WS_BASE = process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws";

export default function useWebSocket(analysisId) {
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!analysisId) return;
    const ws = new WebSocket(`${WS_BASE}/${analysisId}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessage(data.message || "");
      } catch {
        setMessage("");
      }
    };
    return () => ws.close();
  }, [analysisId]);

  return message;
}
