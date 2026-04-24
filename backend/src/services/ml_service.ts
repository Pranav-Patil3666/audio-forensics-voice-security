import axios from "axios";
import fs from "fs";
import FormData from "form-data";

export const sendToML = async (filePath: string) => {
  try {
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    const response = await axios.post(
      "http://127.0.0.1:8000/predict",
      form,
      {
        headers: form.getHeaders(),
      }
    );

    const data = response.data;
    console.log("ML RAW RESPONSE:", data);

    // 🔥 STEP 1: HANDLE VAD SKIP
    if (data.skip) {
      console.log("⛔ Skipped by VAD");
      return null;
    }

    // 🔥 STEP 2: NORMALIZE OUTPUT
    const real = data.real_prob ?? 0;
    const fake = data.fake_prob ?? 0;

    const label = fake > real ? "FAKE" : "REAL";
    const confidence = Math.max(real, fake);

    
    return {
      label,
      confidence,
      fake_prob: fake, // 🔥 IMPORTANT: used in risk engine
    };

  } catch (error: any) {
    console.error("❌ ML service error:", error.message);
    return null; // 🔥 fail-safe (don’t crash stream)
  }
};