import fs from 'fs';
import os from 'os';
import path from 'path';

export default async function eventSpy(event) {
  const logDir = path.join(os.homedir(), '.openclaw/logs');
  const logFile = path.join(logDir, 'spy.log');
  
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logLine = `[${new Date().toISOString()}] Type: ${event.type}\n${JSON.stringify(event, null, 2)}\n\n`;
  fs.appendFileSync(logFile, logLine);
}
