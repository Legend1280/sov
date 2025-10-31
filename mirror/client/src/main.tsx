import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { initializePulseWebSocket } from "./core/pulse/pulseWebSocket";

// Initialize Pulse WebSocket connection to Core
initializePulseWebSocket();

createRoot(document.getElementById("root")!).render(<App />);
