// Project-specific static checks that stylelint cannot express:
//   1. every var(--phoenix-*) is declared somewhere in chrome/
//   2. @import targets exist and every chrome/*.css is imported
//   3. pref media queries that use both the legacy -moz-bool-pref form and
//      the -moz-pref() form list the same prefs with the same negation
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const chromeDir = join(root, "chrome");
const entries = ["userChrome.example.css", "chrome/phoenix.css"];

const files = readdirSync(chromeDir)
  .filter((name) => name.endsWith(".css"))
  .map((name) => join(chromeDir, name));
const sources = new Map(
  [...files, ...entries.map((e) => join(root, e))].map((file) => [
    file,
    readFileSync(file, "utf8").replace(/\/\*[\s\S]*?\*\//g, (c) => c.replace(/[^\n]/g, " ")),
  ]),
);

const errors = [];
const report = (file, index, message) => {
  const line = sources.get(file).slice(0, index).split("\n").length;
  errors.push(`${relative(root, file)}:${line}  ${message}`);
};

// 1. Custom properties
const declared = new Set();
for (const css of sources.values()) {
  for (const m of css.matchAll(/(--phoenix-[\w-]+)\s*:/g)) declared.add(m[1]);
}
for (const [file, css] of sources) {
  for (const m of css.matchAll(/var\(\s*(--phoenix-[\w-]+)/g)) {
    if (!declared.has(m[1])) report(file, m.index, `${m[1]} is used but never declared`);
  }
}

// 2. Imports
const imported = new Set();
for (const [file, css] of sources) {
  for (const m of css.matchAll(/@import\s+url\(\s*["']?([^"')]+)["']?\s*\)/g)) {
    const target = resolve(dirname(file), m[1]);
    imported.add(target);
    if (!existsSync(target)) report(file, m.index, `imported file ${m[1]} does not exist`);
  }
}
for (const file of files) {
  if (!imported.has(file)) errors.push(`${relative(root, file)}  is never imported`);
}

// 3. Pref media queries
const prefQuery = /((?:not\s*)?)\(\s*-moz-bool-pref\s*:\s*"([^"]+)"\s*\)|((?:not\s*)?)\(\s*-moz-pref\(\s*"([^"]+)"\s*\)\s*\)/g;
for (const [file, css] of sources) {
  for (const m of css.matchAll(/@(?:media|import)\b([^;{]*)/g)) {
    const legacy = [];
    const modern = [];
    for (const q of m[1].matchAll(prefQuery)) {
      if (q[2] !== undefined) legacy.push(`${q[1] ? "not " : ""}${q[2]}`);
      else modern.push(`${q[3] ? "not " : ""}${q[4]}`);
    }
    if (legacy.length === 0 || modern.length === 0) continue;
    const a = [...legacy].sort().join(", ");
    const b = [...modern].sort().join(", ");
    if (a !== b) {
      report(file, m.index, `-moz-bool-pref (${a}) and -moz-pref (${b}) disagree`);
    }
  }
}

if (errors.length > 0) {
  console.error(errors.join("\n"));
  console.error(`\n${errors.length} problem(s) found`);
  process.exit(1);
}
console.log(`check-css: ${files.length} files OK`);
