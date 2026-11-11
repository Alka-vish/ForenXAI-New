
import express from 'express';
import cors from 'cors';
import multer from 'multer';
import crypto from 'crypto';
import path from 'path';
import http from 'http';
import { spawn } from 'child_process';

export const app = express();

const PORT = process.env.PORT || 3000;
const PYTHON_PORT = Number(process.env.FORENSIC_ENGINE_PORT || 5050);

// Project paths
const PROJECT_ROOT = 'D:\\ForenXAI3';
const FORENSIC_ENGINE_DIR = path.join(PROJECT_ROOT, 'forensic-engine');
const PYTHON_EXECUTABLE = path.join(
  PROJECT_ROOT,
  '.venv',
  'Scripts',
  'python.exe'
);

const PYTHON_PATH = FORENSIC_ENGINE_DIR;

let pythonProcess = null;
let isSpawning = false;
let engineIsReady = false;

// Check whether the Python forensic engine is responding
function isEngineRunning() {
  return new Promise((resolve) => {
    const req = http.get(
      `http://127.0.0.1:${PYTHON_PORT}/health`,
      (res) => {
        const ok = res.statusCode === 200;

        if (ok) {
          engineIsReady = true;
        }

        res.resume();
        resolve(ok);
      }
    );

    req.on('error', () => {
      engineIsReady = false;
      resolve(false);
    });

    req.setTimeout(1500, () => {
      req.destroy();
      engineIsReady = false;
      resolve(false);
    });
  });
}

// Start or verify the Python forensic engine
async function ensureForensicEngine() {
  if (await isEngineRunning()) {
    engineIsReady = true;
    return true;
  }

  engineIsReady = false;

  if (!isSpawning) {
    isSpawning = true;

    console.log(
      `[ForenXAI] Starting Python forensic engine on port ${PYTHON_PORT}...`
    );

    console.log(`[ForenXAI] Python executable: ${PYTHON_EXECUTABLE}`);

    pythonProcess = spawn(
      PYTHON_EXECUTABLE,
      [
        '-m',
        'uvicorn',
        'main:app',
        '--app-dir',
        FORENSIC_ENGINE_DIR,
        '--port',
        String(PYTHON_PORT),
        '--host',
        '127.0.0.1',
      ],
      {
        cwd: PROJECT_ROOT,
        env: {
          ...process.env,
          PYTHONPATH: PYTHON_PATH,
        },
        stdio: 'inherit',
        windowsHide: true,
      }
    );

    pythonProcess.on('error', (err) => {
      console.error(
        '[ForenXAI] Failed to launch Python forensic engine:',
        err.message
      );

      pythonProcess = null;
      isSpawning = false;
      engineIsReady = false;
    });

    pythonProcess.on('exit', (code, signal) => {
      console.log(
        `[ForenXAI] Forensic engine exited. Code: ${code}, Signal: ${signal}`
      );

      pythonProcess = null;
      isSpawning = false;
      engineIsReady = false;
    });
  }

  // Wait up to approximately 15 seconds for startup
  for (let i = 0; i < 30; i++) {
    await new Promise((resolve) => setTimeout(resolve, 500));

    if (await isEngineRunning()) {
      engineIsReady = true;
      isSpawning = false;

      console.log(
        `[ForenXAI] Python forensic engine verified ready on port ${PYTHON_PORT}`
      );

      return true;
    }

    if (!pythonProcess && !isSpawning) {
      break;
    }
  }

  console.error(
    '[ForenXAI] Python forensic engine did not become ready.'
  );

  return false;
}

// Start the engine when this server starts
ensureForensicEngine().catch((err) => {
  console.error('[ForenXAI] Startup error:', err.message);
});

// Enable CORS
app.use(cors());

// Headers that must not be forwarded by the proxy
const HOP_BY_HOP_HEADERS = new Set([
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
]);

// Proxy requests to the Python forensic engine
async function proxyToForensicEngine(req, res, targetPath) {
  if (!(await isEngineRunning())) {
    const ready = await ensureForensicEngine();

    if (!ready) {
      return res.status(503).json({
        error: 'Forensic engine service unavailable',
        detail: 'The Python forensic engine failed to start or respond.',
      });
    }
  }

  const forwardHeaders = {};

  for (const [key, value] of Object.entries(req.headers)) {
    if (
      !HOP_BY_HOP_HEADERS.has(key.toLowerCase()) &&
      key.toLowerCase() !== 'host'
    ) {
      forwardHeaders[key] = value;
    }
  }

  forwardHeaders.host = `127.0.0.1:${PYTHON_PORT}`;

  const options = {
    hostname: '127.0.0.1',
    port: PYTHON_PORT,
    path: targetPath,
    method: req.method,
    headers: forwardHeaders,
  };

  const proxyReq = http.request(options, (proxyRes) => {
    const responseHeaders = {};

    for (const [key, value] of Object.entries(proxyRes.headers)) {
      if (
        !HOP_BY_HOP_HEADERS.has(key.toLowerCase()) &&
        value !== undefined
      ) {
        responseHeaders[key] = value;
      }
    }

    res.writeHead(proxyRes.statusCode || 200, responseHeaders);
    proxyRes.pipe(res);

    proxyRes.on('error', (err) => {
      console.error(
        `[ForenXAI Proxy Error] Response stream for ${targetPath}:`,
        err.message
      );

      if (!res.headersSent) {
        res.status(502).json({
          error: 'Forensic engine stream error',
          detail: err.message,
        });
      } else {
        res.end();
      }
    });
  });

  proxyReq.on('error', (err) => {
    console.error(
      `[ForenXAI Proxy Error] Failed forwarding to ${targetPath}:`,
      err.message
    );

    if (!res.headersSent) {
      res.status(502).json({
        error: 'Forensic engine service unavailable',
        detail: err.message,
      });
    }
  });

  req.on('error', (err) => {
    console.error(
      '[ForenXAI Proxy Error] Incoming request stream error:',
      err.message
    );

    proxyReq.destroy(err);
  });

  res.on('close', () => {
    if (!proxyReq.destroyed) {
      proxyReq.destroy();
    }
  });

  req.pipe(proxyReq);
}

// Forensic engine routes
// Mounted before express.json to support streaming requests
app.use('/debate', (req, res) =>
  proxyToForensicEngine(req, res, '/debate')
);

app.use('/api/debate', (req, res) =>
  proxyToForensicEngine(req, res, '/debate')
);

app.use('/analyze', (req, res) =>
  proxyToForensicEngine(req, res, '/analyze')
);

app.use('/api/analyze', (req, res) =>
  proxyToForensicEngine(req, res, '/analyze')
);

app.use('/debate-evidence', (req, res) =>
  proxyToForensicEngine(req, res, '/debate-evidence')
);

app.use('/api/debate-evidence', (req, res) =>
  proxyToForensicEngine(req, res, '/debate-evidence')
);

app.use('/maps/:filename', (req, res) =>
  proxyToForensicEngine(req, res, `/maps/${req.params.filename}`)
);

app.use('/api/maps/:filename', (req, res) =>
  proxyToForensicEngine(req, res, `/maps/${req.params.filename}`)
);

// Parse JSON for other routes
app.use(express.json());

// Allowed image types
const ALLOWED_MIME_TYPES = new Set([
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/webp',
]);

const ALLOWED_EXTENSIONS = new Set([
  '.jpg',
  '.jpeg',
  '.png',
  '.webp',
]);

// Multer configuration
const storage = multer.memoryStorage();

const upload = multer({
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024,
  },
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    const mimeType = file.mimetype.toLowerCase();

    if (
      ALLOWED_EXTENSIONS.has(ext) ||
      ALLOWED_MIME_TYPES.has(mimeType)
    ) {
      return cb(null, true);
    }

    return cb(
      new Error(
        'Unsupported file type. Only JPG, JPEG, PNG, and WEBP files are allowed.'
      )
    );
  },
});

// Backend health endpoint
app.get('/api/health', async (req, res) => {
  const healthy = await isEngineRunning();

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'ok' : 'degraded',
    service: 'ForenXAI Backend',
    pythonEngine: healthy ? 'connected' : 'unavailable',
  });
});

// Image upload API
app.post('/api/upload', (req, res) => {
  upload.single('image')(req, res, (err) => {
    if (err) {
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(400).json({
          error: 'File size exceeds 10MB limit.',
        });
      }

      return res.status(400).json({
        error: err.message || 'Invalid file upload.',
      });
    }

    if (!req.file) {
      return res.status(400).json({
        error: 'No image file provided.',
      });
    }

    const ext = path.extname(req.file.originalname).toLowerCase();
    const mimeType = req.file.mimetype.toLowerCase();

    if (
      !ALLOWED_EXTENSIONS.has(ext) &&
      !ALLOWED_MIME_TYPES.has(mimeType)
    ) {
      return res.status(400).json({
        error:
          'Unsupported file type. Only JPG, JPEG, PNG, and WEBP files are allowed.',
      });
    }

    try {
      const hash = crypto
        .createHash('sha256')
        .update(req.file.buffer)
        .digest('hex');

      return res.status(200).json({
        message: 'Image uploaded successfully.',
        filename: req.file.originalname,
        fileType: req.file.mimetype,
        fileSize: req.file.size,
        sha256: hash,
      });
    } catch (hashError) {
      console.error(
        '[ForenXAI] Error calculating SHA-256 hash:',
        hashError
      );

      return res.status(500).json({
        error: 'Failed to process image and calculate hash.',
      });
    }
  });
});

export default app;

// Run directly when RUN_STANDALONE=true
if (process.env.RUN_STANDALONE === 'true') {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(
      `ForenXAI Backend server running on http://0.0.0.0:${PORT}`
    );
  });
}
