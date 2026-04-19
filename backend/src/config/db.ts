import { neon } from "@neondatabase/serverless";
import dotenv from "dotenv";

dotenv.config();

const DATABASE_URL = process.env.DB_URL;

if (!DATABASE_URL) {
  throw new Error("❌ DB_URL is not defined in .env");
}

export const sql = neon(DATABASE_URL);

// Optional test function
export const connectDB = async () => {
  try {
    await sql`SELECT 1`;
    console.log("✅ Database connected");
  } catch (error) {
    console.error("❌ Database connection failed", error);
    process.exit(1);
  }
};