const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'bible_app.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const data = JSON.parse(fs.readFileSync(path.join(root, 'gemantria/mappings/gemantria_ciphers.json'), 'utf8'));

function app() {
  const requests = [];
  const context = vm.createContext({
    console,
    document: { addEventListener() {} },
    fetch: async url => {
      requests.push(url);
      return url === 'gemantria/mappings/gemantria_ciphers.json'
        ? { ok: true, json: async () => data }
        : { ok: false };
    },
  });
  vm.runInContext(script, context);
  return { context, requests };
}

test('app loads the real cipher file and counts final Hebrew forms', async () => {
  const { context, requests } = app();
  await vm.runInContext('fetchCipherData()', context);
  assert.ok(requests.includes('gemantria/mappings/gemantria_ciphers.json'));
  vm.runInContext('state.activeCipher = "standard"', context);
  assert.equal(vm.runInContext('calculateGematria("אֱלֹהִים")', context), 86);
  assert.equal(vm.runInContext('calculateGematria("מלך")', context), 90);
  assert.equal(vm.runInContext('calculateGematria("אמת")', context), 441);
  assert.equal(vm.runInContext('calculateGematria("בראשית")', context), 913);
  vm.runInContext('state.activeCipher = "biblical"', context);
  assert.equal(vm.runInContext('calculateGematria("אמת")', context), 45);
  assert.equal(vm.runInContext('calculateGematria("בראשית")', context), 220);
});

test('fallback and loaded maps agree on Hebrew final forms for each Hebrew cipher', async () => {
  const { context } = app();
  const inputs = ['כך', 'מם', 'נן', 'פף', 'צץ', 'יהי אור'];
  for (const cipher of ['standard', 'biblical', 'reversal', 'genesis_order']) {
    vm.runInContext(`state.activeCipher = ${JSON.stringify(cipher)}; state.cipherData = {}`, context);
    const fallback = inputs.map(text => vm.runInContext(`calculateGematria(${JSON.stringify(text)})`, context));
    await vm.runInContext('fetchCipherData()', context);
    const loaded = inputs.map(text => vm.runInContext(`calculateGematria(${JSON.stringify(text)})`, context));
    assert.deepEqual(loaded, fallback, cipher);
  }
});

test('the Greek fallback works without a loaded JSON file', () => {
  const { context } = app();
  vm.runInContext('state.activeCipher = "greek_transposition"; state.scriptMode = "greek"', context);
  assert.equal(vm.runInContext('calculateGematria("αβγ")', context), 6);
});

test('circle-of-fifths ratios match each pitch relative to C', () => {
  const csv = fs.readFileSync(path.join(root, 'audio/harmonic+circle_map.csv'), 'utf8');
  const rows = csv.replace(/^\uFEFF/, '').trim().split(/\r?\n/).slice(1);
  const expected = ['1/1', '2⁷/¹²', '2²/¹²', '2⁹/¹²', '2⁴/¹²', '2¹¹/¹²', '2⁶/¹²', '2¹/¹²', '2⁸/¹²', '2³/¹²', '2¹⁰/¹²', '2⁵/¹²'];
  assert.deepEqual(rows.map(row => row.split(',')[1]), expected);
});
