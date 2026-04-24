import { WebSocketServer, WebSocket } from "ws";
import { sendToML } from "../services/ml_service.js";
import { RiskEngine } from "../services/risk_service.js";
import fs from "fs";

export const initWebSocket = (server: any) => {
  const wss = new WebSocketServer({ server });

  wss.setMaxListeners(20);

  wss.on("connection", (ws: WebSocket) => {
    console.log("🔌 Client connected");

    const riskEngine = new RiskEngine(); // 🔥 per connection

    ws.on("message", async (message: any) => {
      try {
        const data = JSON.parse(message.toString());

        if (data.type === "chunk") {
          const filePath = data.filePath;

          const result = await sendToML(filePath);

          // 🔥 SKIP NON-SPEECH CHUNKS
          if (!result) {
            fs.unlinkSync(filePath);
            return;
          }

          const fakeProb = result.fake_prob || 0;

          // 🔥 compute rolling risk
          const risk = riskEngine.addPrediction(fakeProb);

          ws.send(
            JSON.stringify({
              type: "prediction",
              label: result.label,
              confidence: result.confidence,
              risk,
              stats: riskEngine.getStats(),
            })
          );

          // cleanup
          fs.unlinkSync(filePath);
        }
      } catch (err) {
        console.error("❌ WS error:", err);
      }
    });

    ws.on("close", () => {
      console.log("❌ Client disconnected");
    });
  });

  console.log("🔥 WebSocket server ready");
};