// @ts-nocheck
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';

describe('Deploy Script & Configuration', () => {
  const rootDir = path.resolve(__dirname, '..');
  const packageJsonPath = path.join(rootDir, 'package.json');
  const deployJsPath = path.join(rootDir, 'scripts', 'deploy.js');
  const deployShPath = path.join(rootDir, 'scripts', 'deploy.sh');

  it('scripts/deploy.js exists and is marked executable', () => {
    expect(fs.existsSync(deployJsPath)).toBe(true);
    const content = fs.readFileSync(deployJsPath, 'utf8');
    expect(content.startsWith('#!/usr/bin/env node')).toBe(true);
    expect(content).toContain('OsakaRPG – GitHub Pages Deployment Script');
    expect(content).toContain('watchDeployment');
  });

  it('scripts/deploy.sh exists and references deploy.js', () => {
    expect(fs.existsSync(deployShPath)).toBe(true);
    const content = fs.readFileSync(deployShPath, 'utf8');
    expect(content.startsWith('#!/usr/bin/env bash')).toBe(true);
    expect(content).toContain('node scripts/deploy.js');
  });

  it('package.json contains "deploy" npm script', () => {
    const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    expect(pkg.scripts).toBeDefined();
    expect(pkg.scripts.deploy).toBe('node scripts/deploy.js');
  });
});
