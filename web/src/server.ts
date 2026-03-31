/**
 * TrustWise Web Server — TypeScript / Express
 *
 * Replaces the Flask-based web interface.  Serves the static frontend and
 * provides REST API endpoints that delegate to the Python backend pipeline
 * via a thin JSON-over-subprocess bridge (`api_bridge.py`).
 */

import express, { Request, Response } from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import path from "path";
import { execFile } from "child_process";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PORT = parseInt(process.env.PORT || "5000", 10);
const HOST = process.env.HOST || "127.0.0.1";
const DEBUG = (process.env.FLASK_DEBUG || "false").toLowerCase() === "true";

/** Python executable for `api_bridge.py` (venv or py launcher). Overrides default `python` on PATH. */
const PYTHON_EXE =
  process.env.PYTHON_EXE || process.env.TRUSTWISE_PYTHON || "python";

/** Absolute path to the repository root (one level above `web/`). */
const ROOT_DIR = path.resolve(__dirname, "..", "..");

/** Path to the Python bridge script that wraps the TrustWise pipeline. */
const BRIDGE_SCRIPT = path.join(ROOT_DIR, "api_bridge.py");

/** Directory that contains plans written by the pipeline. */
const PLANS_DIR = path.join(ROOT_DIR, "data", "plans");

/** Directory that contains raw data written by the pipeline. */
const RAW_DATA_DIR = path.join(ROOT_DIR, "data", "raw");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Run the Python bridge with a given action and optional JSON payload.
 * Returns the parsed JSON that the bridge writes to stdout.
 * This keeps the Express layer thin and delegates domain logic to Python.
 */
function callPythonBridge(
  action: string,
  payload: Record<string, unknown> = {}
): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const input = JSON.stringify({ action, ...payload });

    execFile(
      PYTHON_EXE,
      [BRIDGE_SCRIPT],
      { cwd: ROOT_DIR, maxBuffer: 10 * 1024 * 1024, timeout: 300_000 },
      (error, stdout, stderr) => {
        if (error) {
          console.error(`[bridge] stderr: ${stderr}`);
          return reject(new Error(stderr || error.message));
        }
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch {
          reject(new Error(`Invalid JSON from bridge: ${stdout.slice(0, 500)}`));
        }
      }
    ).stdin!.end(input);
  });
}

/**
 * Validate that a filename is safe (no path traversal).
 */
function isSafeFilename(filename: string): boolean {
  if (filename.includes("..") || filename.includes("/") || filename.includes("\\")) {
    return false;
  }
  const resolved = path.resolve(PLANS_DIR, filename);
  return resolved.startsWith(path.resolve(PLANS_DIR));
}

// ---------------------------------------------------------------------------
// Express App
// ---------------------------------------------------------------------------

const app = express();
app.use(cors());
app.use(express.json());

// Rate limiting — prevent abuse
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 60,             // 60 requests per minute per IP
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Serve static CSS / JS assets
app.use("/static", express.static(path.join(ROOT_DIR, "static")));

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

/** Main page — serve the frontend HTML. */
app.get("/", (_req: Request, res: Response) => {
  const htmlPath = path.join(ROOT_DIR, "web", "public", "index.html");
  res.sendFile(htmlPath);
});

/** Submit a query and execute the full pipeline. */
app.post("/api/submit", async (req: Request, res: Response) => {
  try {
    const query = (req.body.query || "").trim();
    if (!query) {
      res.status(400).json({ success: false, error: "Query cannot be empty" });
      return;
    }

    console.log(`[web] Processing query: ${query}`);
    const result = await callPythonBridge("submit", { query });
    res.json(result);
  } catch (err) {
    console.error("[web] submit failed:", err);
    res.status(500).json({
      success: false,
      error: "An internal error occurred while processing the query.",
    });
  }
});

/** List saved execution plans. */
app.get("/api/plans", async (_req: Request, res: Response) => {
  try {
    const result = await callPythonBridge("list_plans");
    res.json(result);
  } catch (err) {
    console.error("[web] list_plans failed:", err);
    res.status(500).json({ success: false, error: "Failed to list plans." });
  }
});

/** Get a specific plan by filename. */
app.get("/api/plan/:filename", async (req: Request, res: Response) => {
  try {
    const filename = req.params.filename as string;
    if (!isSafeFilename(filename)) {
      res.status(400).json({ success: false, error: "Invalid filename" });
      return;
    }

    const result = await callPythonBridge("get_plan", { filename });
    if (!(result as { success: boolean }).success) {
      res.status(404).json(result);
      return;
    }
    res.json(result);
  } catch (err) {
    console.error("[web] get_plan failed:", err);
    res.status(500).json({ success: false, error: "Failed to retrieve plan." });
  }
});

/** System status. */
app.get("/api/status", async (_req: Request, res: Response) => {
  try {
    const result = await callPythonBridge("status");
    res.json(result);
  } catch (err) {
    console.error("[web] status failed:", err);
    res.status(500).json({
      success: false,
      error: "Failed to retrieve system status.",
    });
  }
});

/** List raw data files. */
app.get("/api/raw-data", async (_req: Request, res: Response) => {
  try {
    const result = await callPythonBridge("list_raw_data");
    res.json(result);
  } catch (err) {
    console.error("[web] raw-data failed:", err);
    res.status(500).json({ success: false, error: "Failed to list raw data." });
  }
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

app.listen(PORT, HOST, () => {
  console.log("=".repeat(60));
  console.log("TrustWise Web Interface (TypeScript)");
  console.log("=".repeat(60));
  console.log(`Server running at http://${HOST}:${PORT}`);
  console.log(`Debug mode: ${DEBUG}`);
  console.log("Press Ctrl+C to stop");
  console.log("=".repeat(60));
});
