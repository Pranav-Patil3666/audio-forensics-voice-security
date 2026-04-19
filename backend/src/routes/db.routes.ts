import { Router } from "express";
import { dbCheck } from "../controllers/db.controller.js";

const router = Router();

router.get("/", dbCheck);

export default router;