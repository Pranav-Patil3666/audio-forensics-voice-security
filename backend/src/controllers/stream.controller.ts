import { Request, Response } from "express";
import { splitAudio } from "../services/chunk_service.js";
import WebSocket from "ws";
import fs from "fs";

export const simulateStream = async (req: Request, res: Response) => {
  try {
    const file = req.file;

    if (!file) {
      return res.status(400).json({ error: "No file uploaded" });
    }

    const inputPath = file.path;

    const chunks = await splitAudio(inputPath, "chunks");

    console.log("🚀 Starting stream simulation...");

    const ws = new WebSocket("ws://localhost:5000");

    ws.on("open", () => {
      chunks.forEach((chunk: string, index: number) => {
        setTimeout(() => {
          ws.send(
            JSON.stringify({
              type: "chunk",
              filePath: chunk,
            })
          );
        }, index * 2000);
      });
    });

    ws.on("message", (msg: WebSocket.RawData) => {
      console.log("📊 Prediction:", msg.toString());
    });

    ws.on("error", (err: Error) => {
      console.error("WS error:", err);
    });

    // cleanup uploaded file after splitting
    fs.unlinkSync(inputPath);

    res.json({
      success: true,
      message: "Streaming started. Check console for live predictions.",
    });

  } catch (err: any) {
    res.status(500).json({
      error: err.message,
    });
  }
};