// .github/scripts/publish-hashnode.js
// Publishes markdown articles from the articles/ folder to Hashnode via GraphQL API.
// On first publish: creates the post and saves its ID to .github/hashnode-ids.json
// On subsequent pushes: updates the existing post instead of creating a duplicate.

const fs   = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');

const HASHNODE_PAT            = process.env.HASHNODE_PAT;
const HASHNODE_PUBLICATION_ID = process.env.HASHNODE_PUBLICATION_ID;
const GITHUB_TOKEN            = process.env.GITHUB_TOKEN;
const GITHUB_REPOSITORY       = process.env.GITHUB_REPOSITORY;
const WORKSPACE               = process.env.GITHUB_WORKSPACE || process.cwd();
const IDS_FILE                = path.join(WORKSPACE, '.github', 'hashnode-ids.json');
const ARTICLES_DIR            = path.join(WORKSPACE, 'articles');

// ── Frontmatter Parser ────────────────────────────────────────────────────────
function parseFrontmatter(raw) {
  const match = raw.match(/^---[\r\n]+([\s\S]*?)[\r\n]+---[\r\n]+([\s\S]*)$/);
  if (!match) return null;

  const data = {};
  match[1].split('\n').forEach(line => {
    const colon = line.indexOf(':');
    if (colon < 1) return;
    const key = line.slice(0, colon).trim();
    const val = line.slice(colon + 1).trim().replace(/^['"]|['"]$/g, '');
    data[key] = val;
  });

  return { data, content: match[2].trim() };
}

// ── GraphQL Request ───────────────────────────────────────────────────────────
function graphql(query, variables) {
  const body = JSON.stringify({ query, variables });

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'gql.hashnode.com',
      method:   'POST',
      path:     '/',
      headers: {
        'Content-Type':   'application/json',
        'Authorization':  HASHNODE_PAT,
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      let raw = '';
      res.on('data', chunk => raw += chunk);
      res.on('end', () => {
        const result = JSON.parse(raw);
        if (result.errors) return reject(new Error(JSON.stringify(result.errors)));
        resolve(result.data);
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ── Publish (create) ──────────────────────────────────────────────────────────
function publishPost(title, contentMarkdown, tags, coverImage) {
  const tagList = (tags || '').split(',').map(t => ({ name: t.trim() })).filter(t => t.name);
  const input = {
    title,
    publicationId:   HASHNODE_PUBLICATION_ID,
    contentMarkdown,
    tags:            tagList,
    ...(coverImage ? { coverImageOptions: { coverImageURL: coverImage } } : {}),
  };
  return graphql(
    `mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) { post { id title url } }
    }`,
    { input }
  ).then(d => d.publishPost.post);
}

// ── Update (patch) ────────────────────────────────────────────────────────────
function updatePost(id, title, contentMarkdown, tags, coverImage) {
  const tagList = (tags || '').split(',').map(t => ({ name: t.trim() })).filter(t => t.name);
  const input = {
    id,
    title,
    contentMarkdown,
    tags: tagList,
    ...(coverImage ? { coverImageOptions: { coverImageURL: coverImage } } : {}),
  };
  return graphql(
    `mutation UpdatePost($input: UpdatePostInput!) {
      updatePost(input: $input) { post { id title url } }
    }`,
    { input }
  ).then(d => d.updatePost.post);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (!HASHNODE_PAT || !HASHNODE_PUBLICATION_ID) {
    console.error('Missing HASHNODE_PAT or HASHNODE_PUBLICATION_ID secrets!');
    process.exit(1);
  }

  if (!fs.existsSync(ARTICLES_DIR)) {
    console.error(`articles/ directory not found at: ${ARTICLES_DIR}`);
    process.exit(1);
  }

  // Load saved ID map
  let idsMap = {};
  if (fs.existsSync(IDS_FILE)) {
    idsMap = JSON.parse(fs.readFileSync(IDS_FILE, 'utf8'));
  }

  const files  = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.md'));
  let   newIds = false;

  for (const file of files) {
    const raw    = fs.readFileSync(path.join(ARTICLES_DIR, file), 'utf8');
    const parsed = parseFrontmatter(raw);

    if (!parsed) { console.log(`SKIP ${file} — no frontmatter`); continue; }

    const { data, content } = parsed;
    if (data.published !== 'true') { console.log(`SKIP ${file} — draft`); continue; }

    const existingId = idsMap[file];

    try {
      if (existingId) {
        console.log(`UPDATING: ${data.title}`);
        const post = await updatePost(existingId, data.title, content, data.tags, data.cover_image);
        console.log(`  -> Updated: ${post.url}`);
      } else {
        console.log(`PUBLISHING: ${data.title}`);
        const post = await publishPost(data.title, content, data.tags, data.cover_image);
        console.log(`  -> Published: ${post.url}`);
        idsMap[file] = post.id;
        newIds = true;
      }
    } catch (err) {
      console.error(`ERROR on ${file}: ${err.message}`);
      process.exit(1);
    }
  }

  // Save new IDs and commit back to repo
  if (newIds) {
    fs.writeFileSync(IDS_FILE, JSON.stringify(idsMap, null, 2));
    execSync('git config user.name "github-actions[bot]"');
    execSync('git config user.email "github-actions[bot]@users.noreply.github.com"');
    const remoteUrl = `https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git`;
    execSync(`git remote set-url origin ${remoteUrl}`);
    execSync(`git add ${IDS_FILE}`);
    execSync('git commit -m "chore: save hashnode post ids [skip ci]"');
    execSync('git push origin main');
    console.log('Saved Hashnode post IDs to .github/hashnode-ids.json');
  }
}

main().catch(err => { console.error(err); process.exit(1); });
