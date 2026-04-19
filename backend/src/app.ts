import express from "express";
import cors from "cors";

import healthRoutes from "./routes/health.routes.js";

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/api/health", healthRoutes);

export default app;