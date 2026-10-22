// Where the backend WebSocket lives.
// Running locally (localhost or opening the file directly) → the local uvicorn server.
// Phase 5 replaces the second URL with the real Render address.
const LOCAL_HOSTS = ["localhost", "127.0.0.1", ""];

window.BACKEND_URL = LOCAL_HOSTS.includes(location.hostname)
  ? "ws://localhost:8000/ws"
  : "wss://REPLACE-WITH-RENDER-URL.onrender.com/ws";
