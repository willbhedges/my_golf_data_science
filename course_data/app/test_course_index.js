/* node course_data/app/test_course_index.js: course_index.js unpack, search, slug and request (local + fake db) */
"use strict";
const fs = require("fs"), path = require("path"), zlib = require("zlib"), vm = require("vm"), assert = require("assert");
const src = fs.readFileSync(path.join(__dirname, "course_index.js"), "utf8");
const lines = ["Swope Memorial Golf Course|Kansas City|MO|39.0000|-94.5000|w123|18|B",
               "Pebble Beach Golf Links|Pebble Beach|CA|36.5680|-121.9500|w9|18|A",
               "Spirit Hollow Golf Course|Burlington|IA|40.8|-91.1|w5|18|A",
               "Tiny Nine|Ames|IA|42.0|-93.6|n7|9|D"];
const b64 = zlib.gzipSync(Buffer.from(lines.join("\n"))).toString("base64");
const code = src.replace("/*__COURSE_INDEX__*/null", JSON.stringify({n: lines.length, b64}));
const store = {};
const writes = [];
const fakeDb = {collection: n => ({onSnapshot: () => {}, doc: id => ({set: async d => { writes.push([n, id, d]); }})})};
const win = {claude: {use: async k => k === "db" ? fakeDb : {id: async () => "user-1"}}};
const ctx = {window: win, module: {exports: {}}, atob: s => Buffer.from(s, "base64").toString("binary"), Blob, Response,
             DecompressionStream, Uint8Array, setTimeout, Promise, console, isFinite, JSON, String, Math, Set,
             localStorage: {getItem: k => store[k] || null, setItem: (k, v) => { store[k] = v; }},
             D: {library: {entries: [{name: "Spirit Hollow Golf Course", state: "IA"}]}}};
vm.createContext(ctx);
vm.runInContext(code + "\n;this.CI = module.exports;", ctx);
const CI = ctx.CI;
(async () => {
  await CI.load();
  assert.strictEqual(CI.rows.length, 4);
  let r = CI.search("pebble", "all");
  assert.strictEqual(r.n, 1); assert.strictEqual(r.list[0].osm, "way/9");
  r = CI.search("ia golf", "IA");                     // Spirit Hollow is in the library: not repeated
  assert.strictEqual(r.list.length, 0); assert.strictEqual(CI.search("ames", "all").list[0].name, "Tiny Nine");
  r = CI.search("golf", "MO");
  assert.strictEqual(r.list[0].name, "Swope Memorial Golf Course");
  assert.strictEqual(CI.slugOf("Swope Memorial Golf Course"), "swope_memorial");
  assert.strictEqual(CI.slugOf("The Club at St. Andrew's"), "at_st_andrews");
  assert.ok(CI.section("swope", "all").includes("Request this course"));
  await new Promise(res => setTimeout(res, 20));       // the shared db connects
  assert.strictEqual(CI.state.mode, "shared");
  const how = await CI.request(CI.search("swope", "all").list[0]);
  assert.strictEqual(how, "shared");
  assert.strictEqual(writes.length, 1);
  const [coll, id, d] = writes[0];
  assert.strictEqual(coll, "requests"); assert.strictEqual(id, "mo_swope_memorial__user-1");
  for (const k of ["slug", "name", "city", "state", "osm", "requested_at", "user_id"]) assert.ok(d[k], k);
  assert.ok(CI.section("swope", "all").includes("Requested"));
  console.log("course_index.js: ok");
})().catch(e => { console.error(e); process.exit(1); });
