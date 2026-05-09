import { exec } from "child_process";
import fs from "fs";
import path from "path";

export const splitAudio = (
  inputPath: string,
  outputDir: string
): Promise<string[]> => {

  return new Promise((resolve, reject) => {

    try {

      
      // VALIDATION
      
      if (!fs.existsSync(inputPath)) {
        return reject(
          new Error("Input audio file not found")
        );
      }

      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      
      // CLEAN OLD FILES
      
      const existingFiles =
        fs.readdirSync(outputDir);

      for (const file of existingFiles) {

        fs.unlinkSync(
          path.join(outputDir, file)
        );
      }

      const input = path.resolve(inputPath);

      console.log("🎧 Getting audio duration...");

      
      // GET DURATION
      
      const probeCmd =
        `ffprobe -i "${input}" ` +
        `-show_entries format=duration ` +
        `-v quiet -of csv="p=0"`;

      exec(probeCmd, (err, stdout) => {

        if (err) {
          return reject(err);
        }

        const totalDuration =
          parseFloat(stdout.trim());

        if (
          !totalDuration ||
          isNaN(totalDuration)
        ) {

          return reject(
            new Error(
              "Could not determine audio duration"
            )
          );
        }

        console.log(
          `⏱ Audio Duration: ${totalDuration}s`
        );

        
        // CHUNK CONFIG
        
        const chunkDuration = 2;
        const step = 1;

        let start = 0;
        let index = 0;

        const chunkPaths: string[] = [];

        
        // GENERATE CHUNKS
        
        const generateChunk = () => {

          // avoid useless tail chunks
          if (
            start + 0.5 >= totalDuration
          ) {

            console.log(
              `✅ Generated ${chunkPaths.length} chunks`
            );

            return resolve(chunkPaths);
          }

          const outputPath = path.join(
            outputDir,
            `chunk_${String(index).padStart(3, "0")}.wav`
          );

          
          // FORCE PIPELINE FORMAT
          
          const cmd =
            `ffmpeg -loglevel error -y ` +
            `-i "${input}" ` +
            `-ss ${start} ` +
            `-t ${chunkDuration} ` +
            `-ar 16000 ` +
            `-ac 1 ` +
            `-acodec pcm_s16le ` +
            `"${outputPath}"`;

          exec(cmd, (error) => {

            if (error) {

              console.error(
                "FFmpeg error:",
                error
              );

              return reject(error);
            }

            chunkPaths.push(outputPath);

            start += step;
            index++;

            generateChunk();
          });
        };

        console.log(
          "🎧 Splitting audio into overlapping chunks..."
        );

        generateChunk();
      });

    } catch (err) {

      reject(err);
    }
  });
};