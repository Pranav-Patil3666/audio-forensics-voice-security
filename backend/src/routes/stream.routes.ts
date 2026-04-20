import { Router } from "express";
import { simulateStream } from "../controllers/stream.controller.js";
import { upload } from "../middleware/upload.js";

const router = Router();

// 🔥 FIXED
router.post("/simulate", upload.single("file"), simulateStream);

export default router;