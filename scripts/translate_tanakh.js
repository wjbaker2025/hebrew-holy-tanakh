// translate_tanakh.js
const fs = require("fs");
const path = require("path");

// 1. Existing corpus-specific Hebrew-to-Greek glyph substitutions.
// These are NOT a historically attested Greek translation or value isomorphism.
const hebrewToGreek = {
  א: "α", // Alpha (1)
  ב: "β", // Beta (2)
  ג: "γ", // Gamma (3)
  ד: "δ", // Delta (4)
  ה: "ε", // Epsilon (5)
  ו: "υ", // Legacy corpus convention; NOT equal to model Vav=6 (υ=4 in model)
  ז: "ζ", // Zeta (7)
  ח: "η", // Eta (8)
  ט: "θ", // Theta (9)
  י: "ι", // Iota (10)
  כ: "κ", // Kappa (20)
  ל: "λ", // Lambda (30)
  מ: "μ", // Mu (40)
  נ: "ν", // Nu (50)
  ס: "ξ", // Xi (60)
  ע: "ο", // Omicron (70)
  פ: "π", // Pi (80)
  צ: "ϡ", // Legacy glyph convention; experimental ϡ=90 versus standard Greek ϡ=900
  ק: "ρ", // Rho (100)
  ר: "σ", // Ordinary Greek sigma used throughout corpus legacy fields
  ש: "τ", // Tau (3) - SSOT match for Shin (3) in Biblical
  ת: "υ", // Upsilon (4) - SSOT match for Tav (4) in Biblical

  // Final Forms - Mapping to Biblical/Transposition values
  ך: "φ", // Final Kaph (20) -> Phi
  ם: "χ", // Final Mem (40) -> Chi
  ן: "ψ", // Final Nun (50) -> Psi
  ף: "ω", // Final Peh (80) -> Omega
  ץ: "ϡ", // Final Tsade (90) -> Sampi
};

// This is a LEGACY GLYPH substitution that reproduces existing corpus fields,
// NOT a Greek translation, Septuagint reading, or always value-preserving cipher.
// Score original Hebrew letters with scripts/gematria_core.py instead.
function stripNiqqud(text) {
  return text.replace(/[\u0591-\u05C7]/g, "");
}

function renderLegacyGreek(hebrewText) {
  return [...stripNiqqud(hebrewText)]
    .map((char) => hebrewToGreek[char] || char)
    .join("");
}

function checkOrUpdate(node, report, write) {
  if (Array.isArray(node)) {
    for (const item of node) checkOrUpdate(item, report, write);
    return;
  }
  if (!node || typeof node !== "object") return;
  if (typeof node.hebrew === "string") {
    report.tokens++;
    const expected = renderLegacyGreek(node.hebrew);
    if (node.hebrew_greek !== expected) {
      report.mismatches++;
      if (report.examples.length < 10) {
        report.examples.push({ hebrew: node.hebrew, actual: node.hebrew_greek ?? null, expected });
      }
      if (write) node.hebrew_greek = expected;
    }
  }
  for (const [key, value] of Object.entries(node)) {
    if (key !== "hebrew") checkOrUpdate(value, report, write);
  }
}

function main() {
  const args = new Set(process.argv.slice(2));
  const known = new Set(["--write", "--check", "--help"]);
  if ([...args].some((x) => !known.has(x)) || (args.has("--write") && args.has("--check"))) {
    console.error("Usage: node scripts/translate_tanakh.js [--check | --write]");
    process.exitCode = 2;
    return;
  }
  if (args.has("--help")) {
    console.log("--check: report mismatches and exit nonzero; --write: explicitly update only affected files; no flag: report only.");
    return;
  }
  const write = args.has("--write");
  const dir = path.resolve(__dirname, "..", "Tanakh");
  const report = { files: 0, tokens: 0, mismatches: 0, examples: [], updatedFiles: 0 };
  function walk(folder) {
    for (const entry of fs.readdirSync(folder, { withFileTypes: true })) {
      const full = path.join(folder, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile() && /^[0-9]{2}_.+[.]json$/.test(entry.name)) {
        report.files++;
        const doc = JSON.parse(fs.readFileSync(full, "utf8"));
        const before = report.mismatches;
        checkOrUpdate(doc, report, write);
        if (write && report.mismatches > before) {
          fs.writeFileSync(full, JSON.stringify(doc, null, 2) + "\n", "utf8");
          report.updatedFiles++;
        }
      }
    }
  }
  walk(dir);
  if (report.files !== 39) {
    throw new Error(`Expected 39 numbered Tanakh JSON books, found ${report.files}`);
  }
  console.log(JSON.stringify(report, null, 2));
  if (args.has("--check") && report.mismatches) process.exitCode = 1;
}
if (require.main === module) main();
module.exports = { stripNiqqud, renderLegacyGreek, checkOrUpdate };
