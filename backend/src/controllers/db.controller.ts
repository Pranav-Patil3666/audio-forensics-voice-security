import { Request, Response } from "express";
import { sql } from "../config/db.js";

export const dbCheck = async (req: Request, res: Response) => {
  try {
    const result = await sql`SELECT NOW()`;

    res.status(200).json({
      success: true,
      message: "Database connected successfully",
      time: result[0]
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Database error",
      error
    });
  }
};