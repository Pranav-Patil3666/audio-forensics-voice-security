import { Router } from "express";
import { detectAudio } from "../controllers/ml.controller.js";
import { upload } from "../middleware/upload.js";

const router = Router();

router.post("/detect", upload.single("audio"), detectAudio);

export default router;