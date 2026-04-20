import { Request, Response } from "express";
import { sendToML } from "../services/ml_service.js";
import fs from "fs";

export const detectAudio = async (req: Request, res: Response) => {
  try {
    const file = req.file;

    if (!file) {
      return res.status(400).json({ error: "No file uploaded" });
    }

    const result = await sendToML(file.path);

    // optional cleanup
    fs.unlinkSync(file.path);

    return res.json({
      success: true,
      result,
    });
  } catch (error: any) {
    return res.status(500).json({
      error: error.message,
    });
  }
};