import express from "express";
import cors from "cors";

import healthRoutes from "./routes/health.routes.js";
import dbRoutes from "./routes/db.routes.js";
import mlRoutes from "./routes/ml.routes.js";

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/api/health", healthRoutes);
app.use("/api/db", dbRoutes);
app.use("/api/ml", mlRoutes);

export default app;