import { useEffect, useState, useRef } from "react";

const WS_URL = "http://10.100.102.6:3333";

export function useWebSocket() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      console.log("✅ WebSocket connected!");
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        console.log("📩 Received data:", parsedData);
        setData(parsedData);
      } catch (error) {
        console.error("❌ Error parsing WebSocket message:", error);
      }
    };

    ws.current.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
    };

    ws.current.onclose = () => {
      console.log("⚠️ WebSocket disconnected.");
      setIsConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  return { data, isConnected };
}
