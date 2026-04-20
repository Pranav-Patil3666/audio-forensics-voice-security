import { exec } from "child_process";
import fs from "fs";
import path from "path";

/**
 * Splits audio into 2-second chunks using FFmpeg
 * @param inputPath - path to input audio file
 * @param outputDir - directory to store chunks
 * @returns array of chunk file paths (sorted)
 */
export const splitAudio = (inputPath: string, outputDir: string): Promise<string[]> => {
  return new Promise((resolve, reject) => {
    try {
      // 🔥 Ensure input exists
      if (!fs.existsSync(inputPath)) {
        return reject(new Error("Input audio file not found"));
      }

      // 🔥 Create output dir if not exists
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      // 🔥 Clean previous chunks (VERY IMPORTANT)
      const existingFiles = fs.readdirSync(outputDir);
      for (const file of existingFiles) {
        fs.unlinkSync(path.join(outputDir, file));
      }

      // 🔥 Normalize paths (important for Windows)
      const input = path.resolve(inputPath);
      const outputPattern = path.join(outputDir, "chunk_%03d.wav");

      // 🔥 FFmpeg command
      const command = `ffmpeg -y -i "${input}" -f segment -segment_time 2 -acodec pcm_s16le "${outputPattern}"`;

      console.log("🎧 Splitting audio into chunks...");

      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error("FFmpeg error:", stderr);
          return reject(error);
        }

        // 🔥 Read generated chunks
        let files = fs.readdirSync(outputDir);

        if (files.length === 0) {
          return reject(new Error("No chunks generated"));
        }

        // 🔥 Sort properly (VERY IMPORTANT)
        files = files.sort();

        const chunkPaths = files.map((file) =>
          path.join(outputDir, file)
        );

        console.log(`✅ Generated ${chunkPaths.length} chunks`);

        resolve(chunkPaths);
      });

    } catch (err) {
      reject(err);
    }
  });
};