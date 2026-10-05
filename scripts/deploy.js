#!/usr/bin/env node

import { execSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
  magenta: '\x1b[35m',
};

function logStep(step, total, message) {
  console.log(`\n${colors.bold}${colors.cyan}[${step}/${total}] ${message}${colors.reset}`);
}

function logSuccess(message) {
  console.log(`${colors.green}✔ ${message}${colors.reset}`);
}

function logWarn(message) {
  console.log(`${colors.yellow}⚠ ${message}${colors.reset}`);
}

function logError(message) {
  console.log(`${colors.red}✖ ${message}${colors.reset}`);
}

function execText(cmd, cwd = rootDir) {
  return execSync(cmd, { cwd, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
}

function run(cmd, cwd = rootDir) {
  console.log(`${colors.dim}▶ ${cmd}${colors.reset}`);
  execSync(cmd, { cwd, stdio: 'inherit' });
}

function getRepoInfo() {
  try {
    const remoteUrl = execText('git remote get-url origin');
    const match = remoteUrl.match(/github\.com[:/]([^/]+)\/([^/.]+?)(?:\.git)?$/);
    if (match) {
      return { owner: match[1], repo: match[2] };
    }
  } catch {
    // fallback if remote info unavailable
  }
  return { owner: 'marcinOz', repo: 'OsakaRPG' };
}

function printHelp() {
  console.log(`
${colors.bold}OsakaRPG – GitHub Pages Deployment Script${colors.reset}

${colors.bold}Usage:${colors.reset}
  npm run deploy [options] [commit message]
  ./scripts/deploy.sh [options] [commit message]

${colors.bold}Options:${colors.reset}
  --skip-tests   Skip running local vitest suite
  --skip-build   Skip running local tsc and vite build
  --no-watch     Do not monitor the GitHub Actions workflow progress
  -f, --force    Force redeploy by pushing an empty commit if branch is up to date
  -h, --help     Show this help screen

${colors.bold}Examples:${colors.reset}
  npm run deploy
  npm run deploy -- "Fix campfire music loop and battle portraits"
  npm run deploy -- --skip-tests "Quick typo fix"
  npm run deploy -- --force
`);
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function watchDeployment(owner, repo, targetSha) {
  const actionsUrl = `https://github.com/${owner}/${repo}/actions`;
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/actions/runs`;

  console.log(`${colors.dim}Monitoring GitHub Actions (${actionsUrl})...${colors.reset}`);

  const maxAttempts = 36; // ~3 minutes (5s polling)
  let runId = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetch(apiUrl, {
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'OsakaRPG-Deploy-Script',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const runs = data.workflow_runs || [];

        // Match run either by target commit SHA or latest run on main
        const matchingRun = runs.find((r) => r.head_sha === targetSha)
          || runs.find((r) => r.head_branch === 'main' && (r.name.includes('Pages') || r.name.includes('Deploy')));

        if (matchingRun) {
          runId = matchingRun.id;
          const status = matchingRun.status; // queued, in_progress, completed
          const conclusion = matchingRun.conclusion; // success, failure, cancelled, null
          const runUrl = matchingRun.html_url;

          if (status === 'completed') {
            if (conclusion === 'success') {
              return { success: true, url: runUrl };
            } else {
              return { success: false, url: runUrl, conclusion };
            }
          }

          process.stdout.write(`\r${colors.yellow}⏳ GitHub Actions status: ${status} (attempt ${attempt}/${maxAttempts})...${colors.reset}`);
        } else {
          process.stdout.write(`\r${colors.dim}Waiting for workflow to start (attempt ${attempt}/${maxAttempts})...${colors.reset}`);
        }
      } else {
        // API rate limit or non-200
        process.stdout.write(`\r${colors.dim}Checking GitHub Actions (HTTP ${response.status})...${colors.reset}`);
      }
    } catch {
      // Offline or network restriction
      break;
    }

    await sleep(5000);
  }

  process.stdout.write('\n');
  return { timeout: true, runId };
}

async function main() {
  const rawArgs = process.argv.slice(2);

  if (rawArgs.includes('-h') || rawArgs.includes('--help')) {
    printHelp();
    process.exit(0);
  }

  const skipTests = rawArgs.includes('--skip-tests');
  const skipBuild = rawArgs.includes('--skip-build');
  const noWatch = rawArgs.includes('--no-watch');
  const force = rawArgs.includes('-f') || rawArgs.includes('--force');

  const commitMessageWords = rawArgs.filter(
    (arg) => !['--skip-tests', '--skip-build', '--no-watch', '-f', '--force'].includes(arg)
  );
  const customMessage = commitMessageWords.join(' ').trim();

  const { owner, repo } = getRepoInfo();
  const pagesUrl = `https://${owner.toLowerCase()}.github.io/${repo}/`;
  const totalSteps = (skipTests ? 0 : 1) + (skipBuild ? 0 : 1) + 3; // + git check/commit, push, actions
  let currentStep = 1;

  console.log(`\n${colors.bold}${colors.magenta}🎮 OsakaRPG – GitHub Pages Deployment${colors.reset}`);
  console.log(`${colors.dim}Target: ${pagesUrl}${colors.reset}\n`);

  // Step 1: Verify Git branch
  try {
    const currentBranch = execText('git branch --show-current');
    if (currentBranch !== 'main') {
      logError(`Current branch is '${currentBranch}'. GitHub Pages deploys from branch 'main'.`);
      console.log(`Switch to 'main' branch or merge your changes first:`);
      console.log(`  git checkout main && git merge ${currentBranch}`);
      process.exit(1);
    }
  } catch (err) {
    logError(`Git error: ${err.message}`);
    process.exit(1);
  }

  // Step 2: Tests
  if (!skipTests) {
    logStep(currentStep++, totalSteps, 'Running automated test suite (Vitest)...');
    try {
      run('npm test');
      logSuccess('All unit and integration tests passed.');
    } catch {
      logError('Tests failed! Aborting deployment to prevent deploying broken build.');
      process.exit(1);
    }
  } else {
    logWarn('Skipping test suite (--skip-tests).');
  }

  // Step 3: Build verification
  if (!skipBuild) {
    logStep(currentStep++, totalSteps, 'Building production bundle (tsc + vite build)...');
    try {
      run('npm run build');
      logSuccess('Production build generated successfully.');
    } catch {
      logError('Build failed! Aborting deployment.');
      process.exit(1);
    }
  } else {
    logWarn('Skipping local build (--skip-build).');
  }

  // Step 4: Git stage & commit
  logStep(currentStep++, totalSteps, 'Preparing Git commit & checking working tree...');
  const statusOutput = execText('git status --porcelain');
  const hasChanges = statusOutput.length > 0;

  if (hasChanges) {
    console.log(`${colors.dim}Changes detected in working tree. Staging all files...${colors.reset}`);
    run('git add -A');

    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const commitMsg = customMessage || `deploy: update OsakaRPG (${timestamp})`;

    console.log(`${colors.dim}Committing: "${commitMsg}"${colors.reset}`);
    run(`git commit -m "${commitMsg.replace(/"/g, '\\"')}"`);
    logSuccess('Changes committed to main.');
  } else {
    // Check if branch is ahead of origin/main
    let aheadCount = 0;
    try {
      const aheadStr = execText('git rev-list --count origin/main..main');
      aheadCount = parseInt(aheadStr, 10) || 0;
    } catch {
      // Remote branch check failed or origin not fetched
    }

    if (aheadCount > 0) {
      console.log(`${colors.dim}Working tree is clean, but local branch is ahead of origin/main by ${aheadCount} commit(s).${colors.reset}`);
    } else if (force) {
      console.log(`${colors.dim}Forcing deployment (--force): creating an empty commit to trigger CI/CD...${colors.reset}`);
      const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
      const commitMsg = customMessage || `deploy: force trigger deployment (${timestamp})`;
      run(`git commit --allow-empty -m "${commitMsg.replace(/"/g, '\\"')}"`);
      logSuccess('Created empty trigger commit.');
    } else {
      logSuccess('Working tree clean and already up to date with origin/main.');
      console.log(`\nTo trigger a redeploy without code changes, run:`);
      console.log(`  ${colors.bold}npm run deploy -- --force${colors.reset}\n`);
      console.log(`Live site: ${colors.green}${colors.bold}${pagesUrl}${colors.reset}\n`);
      process.exit(0);
    }
  }

  // Step 5: Push to GitHub
  logStep(currentStep++, totalSteps, 'Pushing commits to GitHub origin/main...');
  try {
    run('git push origin main');
    logSuccess('Successfully pushed to origin/main.');
  } catch (err) {
    logError(`Failed to push to GitHub: ${err.message}`);
    process.exit(1);
  }

  const headSha = execText('git rev-parse HEAD');
  const shortSha = headSha.substring(0, 7);

  // Step 6: Monitor GitHub Actions deployment
  logStep(currentStep++, totalSteps, `Triggering CI/CD deployment for commit ${shortSha}...`);

  if (noWatch) {
    console.log(`\n${colors.bold}${colors.green}✔ Push complete! GitHub Actions is deploying in the background.${colors.reset}`);
    console.log(`- GitHub Actions: ${colors.cyan}https://github.com/${owner}/${repo}/actions${colors.reset}`);
    console.log(`- Live Game URL:  ${colors.cyan}${pagesUrl}${colors.reset}\n`);
    return;
  }

  const result = await watchDeployment(owner, repo, headSha);

  process.stdout.write('\n');
  if (result.success) {
    console.log(`\n${colors.bold}${colors.green}====================================================${colors.reset}`);
    console.log(`${colors.bold}${colors.green}🎉 DEPLOYMENT SUCCEEDED!${colors.reset}`);
    console.log(`${colors.bold}${colors.green}====================================================${colors.reset}`);
    console.log(`\n🎮 Game is LIVE at:\n   ${colors.bold}${colors.cyan}${pagesUrl}${colors.reset}\n`);
    if (result.url) {
      console.log(`Workflow run: ${colors.dim}${result.url}${colors.reset}\n`);
    }
  } else if (result.success === false) {
    console.log(`\n${colors.bold}${colors.red}====================================================${colors.reset}`);
    console.log(`${colors.bold}${colors.red}✖ DEPLOYMENT FAILED ON GITHUB ACTIONS${colors.reset}`);
    console.log(`${colors.bold}${colors.red}====================================================${colors.reset}`);
    console.log(`Conclusion: ${result.conclusion}`);
    if (result.url) {
      console.log(`Inspect logs at: ${colors.cyan}${result.url}${colors.reset}\n`);
    }
    process.exit(1);
  } else {
    // Timeout or network notice
    console.log(`\n${colors.bold}${colors.yellow}Deployment is still processing or monitoring timed out.${colors.reset}`);
    console.log(`Check live progress at:`);
    console.log(`- GitHub Actions: ${colors.cyan}https://github.com/${owner}/${repo}/actions${colors.reset}`);
    console.log(`- Live Game URL:  ${colors.cyan}${pagesUrl}${colors.reset}\n`);
  }
}

main().catch((err) => {
  logError(`Unexpected deployment failure: ${err.message}`);
  process.exit(1);
});
