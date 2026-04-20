import http from "http";
import app from "./app.js";
import { connectDB } from "./config/db.js";
import { initWebSocket } from "./ws/stream.handler.js";

const PORT = process.env.PORT || 5000;

const startServer = async () => {
  await connectDB();

  const server = http.createServer(app);

  initWebSocket(server);   //ws attached

  server.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
  });
};

startServer();