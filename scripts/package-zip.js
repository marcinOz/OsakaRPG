#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';
import zlib from 'node:zlib';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const distDir = path.resolve(rootDir, 'dist');
const zipFileName = 'the-pack-rpg.zip';
const outputZip = path.resolve(distDir, zipFileName);

// 1. Validate that dist directory and index.html exist
if (!fs.existsSync(distDir) || !fs.existsSync(path.join(distDir, 'index.html'))) {
  console.error('Error: dist/ directory or dist/index.html not found.');
  console.error('Please run "npm run build" before packaging the zip archive.');
  process.exit(1);
}

// 2. Remove existing archive if present
if (fs.existsSync(outputZip)) {
  fs.unlinkSync(outputZip);
}

console.log(`Packaging ${distDir} into ${outputZip}...`);

// Pure Node ZIP implementation fallback
function packageWithNode(sourceDir, targetZip) {
  const crcTable = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    }
    crcTable[i] = c;
  }
  function crc32(buf) {
    let crc = 0 ^ (-1);
    for (let i = 0; i < buf.length; i++) {
      crc = (crc >>> 8) ^ crcTable[(crc ^ buf[i]) & 0xFF];
    }
    return (crc ^ (-1)) >>> 0;
  }

  const files = [];
  function walk(dir, relPath = '') {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name === '.DS_Store' || entry.name.endsWith('.zip')) continue;
      const full = path.join(dir, entry.name);
      const rel = relPath ? (relPath + '/' + entry.name) : entry.name;
      if (entry.isDirectory()) {
        walk(full, rel);
      } else if (entry.isFile()) {
        files.push({ full, rel });
      }
    }
  }
  walk(sourceDir);

  const localParts = [];
  const cdParts = [];
  let offset = 0;

  for (const file of files) {
    const content = fs.readFileSync(file.full);
    const uncompressedSize = content.length;
    const fileCrc = crc32(content);
    const compressed = zlib.deflateRawSync(content);
    const compressedSize = compressed.length;
    const nameBuf = Buffer.from(file.rel, 'utf8');

    // Local file header: 30 bytes
    const lh = Buffer.alloc(30);
    lh.writeUInt32LE(0x04034b50, 0); // signature
    lh.writeUInt16LE(20, 4);         // version needed (2.0)
    lh.writeUInt16LE(0x0800, 6);     // flags (UTF-8)
    lh.writeUInt16LE(8, 8);          // compression (deflate)
    lh.writeUInt16LE(0, 10);         // time
    lh.writeUInt16LE(0, 12);         // date
    lh.writeUInt32LE(fileCrc, 14);   // crc32
    lh.writeUInt32LE(compressedSize, 18);
    lh.writeUInt32LE(uncompressedSize, 22);
    lh.writeUInt16LE(nameBuf.length, 26);
    lh.writeUInt16LE(0, 28);         // extra len

    localParts.push(lh, nameBuf, compressed);

    // Central directory header: 46 bytes
    const cd = Buffer.alloc(46);
    cd.writeUInt32LE(0x02014b50, 0); // signature
    cd.writeUInt16LE(20, 4);         // version made by
    cd.writeUInt16LE(20, 6);         // version needed
    cd.writeUInt16LE(0x0800, 8);     // flags
    cd.writeUInt16LE(8, 10);         // compression
    cd.writeUInt16LE(0, 12);         // time
    cd.writeUInt16LE(0, 14);         // date
    cd.writeUInt32LE(fileCrc, 16);   // crc32
    cd.writeUInt32LE(compressedSize, 20);
    cd.writeUInt32LE(uncompressedSize, 24);
    cd.writeUInt16LE(nameBuf.length, 28);
    cd.writeUInt16LE(0, 30);         // extra len
    cd.writeUInt16LE(0, 32);         // comment len
    cd.writeUInt16LE(0, 34);         // disk start
    cd.writeUInt16LE(0, 36);         // internal attrs
    cd.writeUInt32LE(0, 38);         // external attrs
    cd.writeUInt32LE(offset, 42);    // relative offset of local header

    cdParts.push(cd, nameBuf);

    offset += lh.length + nameBuf.length + compressed.length;
  }

  const cdOffset = offset;
  let cdSize = 0;
  for (const part of cdParts) cdSize += part.length;

  // End of central directory: 22 bytes
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0); // signature
  eocd.writeUInt16LE(0, 4);          // disk number
  eocd.writeUInt16LE(0, 6);          // cd disk
  eocd.writeUInt16LE(files.length, 8); // records on disk
  eocd.writeUInt16LE(files.length, 10); // total records
  eocd.writeUInt32LE(cdSize, 12);     // cd size
  eocd.writeUInt32LE(cdOffset, 16);   // cd offset
  eocd.writeUInt16LE(0, 20);         // comment length

  const allParts = [...localParts, ...cdParts, eocd];
  fs.writeFileSync(targetZip, Buffer.concat(allParts));
  return files.length;
}

let packaged = false;

// 3. Try child_process zip on Unix/macOS or powershell/tar on Windows
if (process.platform !== 'win32') {
  try {
    execSync(`zip -r -q "${zipFileName}" . -x "*.DS_Store" -x "*.zip"`, {
      cwd: distDir,
      stdio: 'pipe',
    });
    packaged = true;
  } catch (err) {
    // zip command not available or failed; fallback to Node
  }
} else {
  // Try tar or powershell Compress-Archive
  try {
    execSync(`tar -a -c -f "${zipFileName}" *`, {
      cwd: distDir,
      stdio: 'pipe',
    });
    packaged = true;
  } catch {
    try {
      execSync(`powershell -NoProfile -Command "Compress-Archive -Path '${distDir}/*' -DestinationPath '${outputZip}' -Force"`, {
        stdio: 'pipe',
      });
      packaged = true;
    } catch {
      // Fallback to pure Node
    }
  }
}

// 4. Fallback to pure Node if system utility was not used
if (!packaged || !fs.existsSync(outputZip)) {
  packageWithNode(distDir, outputZip);
}

const stats = fs.statSync(outputZip);
const sizeMb = (stats.size / (1024 * 1024)).toFixed(2);
console.log(`Successfully created: ${outputZip} (${sizeMb} MB)`);
