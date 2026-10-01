// Checks the theme's use of Firefox's own CSS custom properties against a
// Firefox build, so renamed or removed variables fail loudly instead of
// silently turning declarations into no-ops:
//   1. every var(--x) without a fallback names a property Firefox declares
//      in its CSS or sets from its JS
//   2. every --x the theme overrides is read by Firefox's own CSS
// --phoenix-* properties are covered by check-css.mjs and skipped here.
//
// Usage: node scripts/check-firefox-vars.mjs <firefox install dir>
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const firefoxDir = process.argv[2];
if (!firefoxDir) {
  console.error("usage: check-firefox-vars.mjs <firefox install dir>");
  process.exit(2);
}

const stripComments = (css) => css.replace(/\/\*[\s\S]*?\*\//g, (c) => c.replace(/[^\n]/g, " "));

// Firefox's chrome CSS and JS live in the two omni.ja archives (zip files).
const extract = (path, pattern) => {
  // omni.ja is an "optimized" jar with its central directory up front; unzip
  // warns about it and exits 2 but still extracts everything correctly.
  const unzip = spawnSync("unzip", ["-p", path, pattern], { maxBuffer: 1 << 30 });
  if (unzip.error || unzip.status > 2 || unzip.stdout.length === 0) {
    console.error(`could not read ${pattern} from ${path}: ${unzip.error ?? unzip.stderr.toString()}`);
    process.exit(2);
  }
  return unzip.stdout.toString("utf8");
};
let firefoxCss = "";
let firefoxJs = "";
for (const archive of ["omni.ja", "browser/omni.ja"]) {
  const path = join(firefoxDir, archive);
  if (!existsSync(path)) {
    console.error(`${path} not found`);
    process.exit(2);
  }
  firefoxCss += extract(path, "*.css");
  firefoxJs += extract(path, "*.*js");
}
firefoxCss = stripComments(firefoxCss);

const declared = new Set();
for (const m of firefoxCss.matchAll(/(--[\w-]+)\s*:/g)) declared.add(m[1]);
// Some properties are only ever set from chrome JS (style.setProperty, theme
// consumers), so count any "--name" string literal in Firefox's JS as declared.
for (const m of firefoxJs.matchAll(/["'`](--[\w-]+)["'`]/g)) declared.add(m[1]);
const read = new Set();
for (const m of firefoxCss.matchAll(/var\(\s*(--[\w-]+)/g)) read.add(m[1]);

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const chromeDir = join(root, "chrome");
const errors = [];
for (const name of readdirSync(chromeDir).filter((n) => n.endsWith(".css")).sort()) {
  const file = join(chromeDir, name);
  const css = stripComments(readFileSync(file, "utf8"));
  const where = (index) => `${relative(root, file)}:${css.slice(0, index).split("\n").length}`;

  // var(--x) with no fallback: --x must exist. var(--x, fallback) is a
  // deliberate compatibility chain and is only checked through its fallback.
  for (const m of css.matchAll(/var\(\s*(--[\w-]+)\s*\)/g)) {
    const prop = m[1];
    if (prop.startsWith("--phoenix-") || declared.has(prop)) continue;
    errors.push(`${where(m.index)}  ${prop} is not defined by Firefox`);
  }

  // Overrides: --x: value where Firefox never reads --x do nothing.
  for (const m of css.matchAll(/(?<![\w-])(--[\w-]+)\s*:/g)) {
    const prop = m[1];
    if (prop.startsWith("--phoenix-") || read.has(prop)) continue;
    errors.push(`${where(m.index)}  ${prop} is overridden but Firefox never reads it`);
  }
}

const version = readFileSync(join(firefoxDir, "application.ini"), "utf8").match(/^Version=(.*)$/m)?.[1];
if (errors.length > 0) {
  console.error(errors.join("\n"));
  console.error(`\n${errors.length} problem(s) found against Firefox ${version}`);
  process.exit(1);
}
console.log(`check-firefox-vars: OK against Firefox ${version}`);
