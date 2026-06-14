// translate_tanakh.js
const fs = require("fs");
const path = require("path");

// 1. Define the 1-to-1 Mapping based on the provided Physics & Pneumatic definitions
// This includes the standard alphabet and the high-value final forms.
const hebrewToGreek = {
  א: "α", // Alpha (1)
  ב: "β", // Beta (2)
  ג: "γ", // Gamma (3)
  ד: "δ", // Delta (4)
  ה: "ε", // Epsilon (5)
  ו: "Ϝ", // Digamma (6) - SSOT match for 6
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
  צ: "ϙ", // Koppa (90) - SSOT match for 90
  ק: "ρ", // Rho (100)
  ר: "ς", // Final Sigma (200) - SSOT match for 200
  ש: "τ", // Tau (3) - SSOT match for Shin (3) in Biblical
  ת: "υ", // Upsilon (4) - SSOT match for Tav (4) in Biblical

  // Final Forms - Mapping to Biblical/Transposition values
  ך: "φ", // Final Kaph (20) -> Phi
  ם: "χ", // Final Mem (40) -> Chi
  ן: "ψ", // Final Nun (50) -> Psi
  ף: "ω", // Final Peh (80) -> Omega
  ץ: "ϡ", // Final Tsade (90) -> Sampi
};

// 2. Utility to strip Hebrew vowels (Niqqud and Cantillation marks)
function stripNiqqud(text) {
  // Replaces Unicode range for Hebrew points/accents with an empty string
  return text.replace(/[\u0591-\u05C7]/g, "");
}

// 3. Core Translation Logic
function translateToGreek(hebrewText) {
  const cleanText = stripNiqqud(hebrewText);
  let greekText = "";

  for (let char of cleanText) {
    // If the character is in our map, translate it. Otherwise, keep it (e.g., spaces, hyphens)
    greekText += hebrewToGreek[char] || char;
  }

  return greekText;
}

// 4. Recursive JSON Processor
function processJsonNode(node) {
  if (typeof node === "string") {
    return node;
  } else if (Array.isArray(node)) {
    return node.map(processJsonNode);
  } else if (typeof node === "object" && node !== null) {
    const result = {};
    for (const key in node) {
      const value = node[key];

      // Assign the original key-value pair
      result[key] = processJsonNode(value);

      // If the value is a string and contains Hebrew characters, generate the Greek twin
      if (typeof value === "string" && /[\u0590-\u05FF]/.test(value)) {
        result[`${key}_greek`] = translateToGreek(value);
      }
    }
    return result;
  }
  return node;
}

// 5. File System Traversal
function processDirectory(dirPath) {
  const files = fs.readdirSync(dirPath);

  for (const file of files) {
    const fullPath = path.join(dirPath, file);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      processDirectory(fullPath); // Recurse into subdirectories
    } else if (path.extname(fullPath) === ".json") {
      console.log(`Processing: ${fullPath}`);

      try {
        const rawData = fs.readFileSync(fullPath, "utf8");
        const jsonData = JSON.parse(rawData);

        const translatedData = processJsonNode(jsonData);

        // Write the updated JSON back to the file (formatted with 2 spaces)
        fs.writeFileSync(
          fullPath,
          JSON.stringify(translatedData, null, 2),
          "utf8",
        );
      } catch (error) {
        console.error(`Error processing file ${fullPath}:`, error.message);
      }
    }
  }
}

// Execute the script targeting the Tanakh directory
const targetDir = path.join(__dirname, "Tanakh");
if (fs.existsSync(targetDir)) {
  console.log(`Starting translation process in: ${targetDir}...`);
  processDirectory(targetDir);
  console.log(
    "Translation complete. All original Hebrew fields now have a parallel Greek field.",
  );
} else {
  console.error(`Could not find the target directory: ${targetDir}`);
}
