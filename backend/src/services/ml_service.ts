import axios from "axios";
import fs from "fs";
import FormData from "form-data";
import path from "path";

export const sendToML = async (
  filePath: string
): Promise<{
  label?: string;
  confidence?: number;
  fake_prob?: number;
  real_prob?: number;
  risk?: string;
  threshold?: number;
  skip?: boolean;
  error?: string;
} | null> => {

  try {

    const form = new FormData();

    form.append(
      "file",
      fs.createReadStream(filePath),
      path.basename(filePath)
    );

    const response = await axios.post(
      "http://127.0.0.1:8000/predict",
      form,
      {
        headers: form.getHeaders(),
        timeout: 120000,
      }
    );

    const data = response.data;

    console.log("ML RAW RESPONSE:", data);

    
    // VAD SKIP
    
    if (data.skip) {

      console.log("⛔ Skipped by VAD");

      return {
        skip: true,
      };
    }

    
    // NORMALIZED RESPONSE
    
    return {

      label:
        data.label ??
        (data.fake_prob > data.real_prob
          ? "FAKE"
          : "REAL"),

      confidence:
        data.confidence ??
        Math.max(
          data.real_prob ?? 0,
          data.fake_prob ?? 0
        ),

      fake_prob:
        data.fake_prob ?? 0,

      real_prob:
        data.real_prob ?? 0,

      risk:
        data.risk ?? "LOW",

      threshold:
        data.threshold ?? 0.5,
    };

  } catch (error: any) {

    console.error(
      "❌ ML service error:",
      error.message
    );

    return {
      error: error.message,
    };
  }
};