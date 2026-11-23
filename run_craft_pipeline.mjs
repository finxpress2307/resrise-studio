process.env.FLOW_MCP_PAUSE_MIN_S = "1";
process.env.FLOW_MCP_PAUSE_MAX_S = "2";

import { getFlowPage } from "file:///C:/Users/zeb/flow-mcp/dist/chrome.js";
import { LocalCore } from "file:///C:/Users/zeb/flow-mcp/dist/core.js";
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { execSync } from "node:child_process";

console.log("=== Initializing 7-Day CRAFT Pipeline for All Accounts ===");

const matrixPath = "D:/social media/resrise-studio/craft_prompts.json";
const queuePath = "D:/social media/resrise-studio/swarm_queue.json";

const craftMatrix = JSON.parse(readFileSync(matrixPath, "utf-8"));
const queueData = JSON.parse(readFileSync(queuePath, "utf-8"));

// Connect to Google Flow
const page = await getFlowPage();
const projectUrl = "https://flow.google.com/project/a0abfc84-6358-4f63-8190-fcb7c7246e5b";
await page.goto(projectUrl, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(4000);
console.log("Connected to Google Flow Project:", page.url());

const core = new LocalCore();

function cropTo4_5(srcPath, dstPath) {
  // Execute clean python 4:5 crop with zero blur
  const pyCode = `
from PIL import Image
im = Image.open(r"${srcPath}")
w, h = im.size
cw = int(w * (846.0 / 896.0)) if w != 846 else 846
ch = int(h * (1057.0 / 1200.0)) if h != 1200 else 1057
x0 = (w - cw) // 2
y0 = int(h * (35.0 / 1200.0))
cropped = im.crop((x0, y0, x0 + cw, y0 + ch))
cropped.save(r"${dstPath}", quality=96)
`;
  execSync(`python -c "${pyCode.replace(/\n/g, ' ')}"`);
}

for (let idx = 0; idx < craftMatrix.length; idx++) {
  const item = craftMatrix[idx];
  const { draft_id, day_index, account, character_asset, scenes } = item;
  const dayStr = String(day_index).padStart(2, "0");

  const accountDir = join("D:/social media/resrise-studio/draft_media", account);
  if (!existsSync(accountDir)) mkdirSync(accountDir, { recursive: true });

  const targetPaths = scenes.map((s, i) => {
    const slideNum = String(i + 1).padStart(2, "0");
    return join(accountDir, `day${dayStr}_${account}_${slideNum}.jpg`);
  });

  console.log(`\n------------------------------------------------------------`);
  console.log(`[Day ${day_index}/7 - ${account}] Target: ${targetPaths.length} slides`);
  console.log(`------------------------------------------------------------`);

  // Check if all slides already exist and are valid
  const allExist = targetPaths.every(p => existsSync(p));
  if (allExist) {
    console.log(`✓ All slides already exist for Day ${day_index} (${account}). Skipping generation.`);
  } else {
    const projectName = `craft_day${dayStr}_${account}`;
    const flowScenes = scenes.map(s => ({
      prompt: s.prompt,
      type: "image",
      aspect_ratio: "3:4",
      max_credits: 0,
      reference_images: [character_asset],
      download_quality: "original"
    }));

    console.log(`Queueing ${flowScenes.length} scenes in Flow project: [${projectName}] with character [${character_asset}]...`);
    try {
      const genResult = await core.generate({
        project: projectName,
        scenes: flowScenes
      });
      const jobIds = genResult.jobs.map(j => j.id);
      console.log(`Waiting for jobs:`, jobIds);

      const waitResult = await core.wait({ job_ids: jobIds, timeout_seconds: 600 });
      console.log(`Generation finished. Ready files: ${waitResult.finished.length}`);

      const outDir = join("C:/Users/zeb/flow-mcp-out", projectName);
      if (existsSync(outDir)) {
        const genFiles = readdirSync(outDir)
          .filter(f => f.match(/\.(jpg|jpeg|png)$/i))
          .sort()
          .map(f => join(outDir, f));

        genFiles.forEach((gf, fIdx) => {
          if (fIdx < targetPaths.length) {
            const dest = targetPaths[fIdx];
            cropTo4_5(gf, dest);
            console.log(`✓ Cropped (4:5 Clean) & Saved: ${dest}`);
          }
        });
      }
    } catch (err) {
      console.error(`Error generating Day ${day_index} for ${account}:`, err.message);
    }
  }

  // Update swarm_queue.json for this draft immediately
  const queueItem = queueData.find(q => q.id === draft_id);
  if (queueItem) {
    const existingMedia = targetPaths.filter(p => existsSync(p));
    queueItem.media_paths = existingMedia;
    writeFileSync(queuePath, JSON.stringify(queueData, null, 2), "utf-8");
    console.log(`✓ Synced draft ${draft_id} in swarm_queue.json with ${existingMedia.length} paths!`);
  }
}

await page.close();
console.log("\n============================================================");
console.log("=== 7-Day CRAFT Pipeline Completed for All 3 Accounts! ===");
console.log("============================================================");
