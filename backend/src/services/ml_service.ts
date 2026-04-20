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

    return response.data;
  } catch (error: any) {
    throw new Error("ML service error: " + error.message);
  }
};