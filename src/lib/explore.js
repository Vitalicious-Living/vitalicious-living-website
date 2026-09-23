// Explore Food demo support: deterministic sample data and a small
// markdown-ish renderer for private-reference recipe bodies.
// Sample vendors, reviewers, comments and metrics are illustrative only.

export const SAMPLE_VENDORS = [
  { name: "Lotus & Maple Kitchen", type: "Pan-Asian bowls", tags: ["soup", "grain", "vegetable", "noodle", "congee", "mains", "porridge", "appetizer"] },
  { name: "Unionville Greens", type: "Salads and grain bowls", tags: ["salad", "greens", "grain", "vegetable", "dressing"] },
  { name: "Milliken Soup Bar", type: "Soups and congee", tags: ["soup", "stock", "congee", "stew", "porridge"] },
  { name: "Markham Veg House", type: "Vegetarian Chinese", tags: ["tofu", "bean", "vegetable", "rice", "steaming", "wok", "mains", "appetizer"] },
  { name: "Rutherford Roast Co.", type: "Roasts and braises", tags: ["roast", "chicken", "turkey", "meat", "steak", "pork", "fish"] },
  { name: "Cathedraltown Bake Lab", type: "Breads and baking", tags: ["breakfast", "bread", "bun", "pancake", "waffle", "dessert", "sweet", "egg"] },
  { name: "Enterprise Noodle Room", type: "Noodle dishes", tags: ["noodle", "pasta", "macaroni", "soup"] },
  { name: "Buttonville Brunch Co.", type: "Daytime cafe", tags: ["breakfast", "egg", "pancake", "beverage", "smoothie", "fruit"] },
  { name: "Cornell Community Kitchen", type: "Community non-profit", tags: ["stew", "soup", "bean", "grain", "chili", "vegetable"] },
  { name: "Thornhill Fitness Fuel", type: "Gym cafe", tags: ["beverage", "smoothie", "snack", "protein", "breakfast", "sweet"] },
];

export const SAMPLE_REVIEWERS = [
  { name: "A. Chen", cred: "Registered Dietitian", scope: "nutrition information review", color: "#1f7a4d" },
  { name: "M. Okafor", cred: "Registered Dietitian", scope: "menu nutrition alignment", color: "#0f5c8c" },
  { name: "S. Kaur", cred: "Holistic Nutritionist", scope: "whole-food pattern review", color: "#8a4fbd" },
  { name: "J. Tremblay", cred: "Certified Personal Trainer", scope: "active-lifestyle fit", color: "#b45309" },
  { name: "L. Wang", cred: "Professional Dietitian (P.Dt.)", scope: "allergen and substitutions review", color: "#be3e5d" },
];

export const SAMPLE_COMMENTS = [
  { why: "whether it is good", text: "Made this last weekend and it disappeared fast. Will double the batch next time." },
  { why: "whether it is good", text: "The texture is the winner here. Crispy edges, tender middle." },
  { why: "why it is healthy", text: "Legumes plus greens in one bowl makes this an easy weekday default for me." },
  { why: "why it is healthy", text: "Love that the richness comes from whole ingredients instead of cream." },
  { why: "why it is healthy", text: "Keeps me full through an afternoon of coaching sessions." },
  { why: "where it is from", text: "Reminds me of the version my grandmother made in autumn. The smell alone is nostalgia." },
  { why: "where it is from", text: "Great to see this tradition represented instead of fused into nothing." },
  { why: "where the inspirations are", text: "You can trace the technique back to the cookbook cited above. They explain the why, not just the how." },
  { why: "where the inspirations are", text: "The headnote in the source book is worth the price alone. This dish follows it faithfully." },
  { why: "local availability", text: "Tried the sample listing at the demo vendor. Close to the home version." },
  { why: "local availability", text: "Please bring this to a real Markham spot. I would order it weekly." },
  { why: "whether it is good", text: "Simple, honest food. Nothing fancy and that is exactly the point." },
];

export const SAMPLE_HANDLES = [
  "greensfork.mk", "dumpling.dad", "yhn.chen", "runnerbean", "chefpai_",
  "wellness.sue", "markham.foodie", "kitchen.w5", "_lotuslane", "gary.eats",
  "mkveggie", "soupseason",
];

export const AVATAR_COLORS = ["#1f7a4d", "#0f5c8c", "#8a4fbd", "#b45309", "#be3e5d", "#2f6f8f", "#4d7c0f", "#7c2d12"];

/** @type {Record<string, string>} */
export const BOOK_NOTES = {
  "tao-of-nutrition": "A Taoist-informed Chinese nutrition reference: food energetics, seasonal balance and simple vegetarian cooking.",
  "the-five-elements-cookbook": "A modern Chinese food-therapy cookbook pairing Five Elements framing with everyday plant-forward recipes.",
  "the-food-lab": "Kenji Lopez-Alt's kitchen-science opus: tested techniques and the reasoning behind each recipe.",
  "the-wisdom-of-the-chinese-kitchen": "Grace Young's Cantonese family cooking: market wisdom, wok breath, celebration foods and healing soups.",
  "vegetable-kingdom": "Bryant Terry's vegetable-led vegan cooking with wide cultural breadth and a soundtrack for every chapter.",
  "the-how-not-to-age-cookbook": "Michael Greger's evidence-screened longevity cookbook built on whole-food plant-based patterns.",
  "the-blue-zones-kitchen-one-pot-meals": "Dan Buettner's one-pot format applying Blue Zones longevity food patterns to low-friction home cooking.",
};

export function hash32(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function rand(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function initials(name) {
  return name.split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
}

export function sampleData(r) {
  const h = hash32(r.id);
  const rng = rand(h);
  const famKey = `${r.family || ""}`.toLowerCase();

  let pool = SAMPLE_VENDORS.filter(v => v.tags.some(t => famKey.includes(t)));
  if (pool.length < 2) pool = [...SAMPLE_VENDORS];
  const nVendors = h % 5 === 0 ? 0 : 1 + (h % 3);
  const vendors = [];
  for (let i = 0; i < nVendors && pool.length; i++) {
    const idx = Math.floor(rng() * pool.length) % pool.length;
    vendors.push(pool.splice(idx, 1)[0]);
  }

  const nRev = h % 3 === 0 ? 0 : 1 + (h % 2);
  const reviewers = [];
  const revPool = [...SAMPLE_REVIEWERS];
  for (let i = 0; i < nRev; i++) {
    reviewers.push(revPool.splice(Math.floor(rng() * revPool.length) % revPool.length, 1)[0]);
  }

  const likes = 14 + Math.floor(rng() * 230);
  const saves = Math.floor(likes * (0.3 + rng() * 0.35));

  const nComments = 2 + (h % 4);
  const comments = [];
  const cPool = SAMPLE_COMMENTS.map((c, i) => ({ ...c, i }));
  for (let i = 0; i < nComments && cPool.length; i++) {
    const idx = Math.floor(rng() * cPool.length) % cPool.length;
    const c = cPool.splice(idx, 1)[0];
    const handle = SAMPLE_HANDLES[(h + c.i * 7 + i * 3) % SAMPLE_HANDLES.length];
    const color = AVATAR_COLORS[(h + i * 5) % AVATAR_COLORS.length];
    comments.push({ handle, color, why: c.why, text: c.text });
  }

  return { vendors, reviewers, likes, saves, comments };
}

export function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function inline(s) {
  return esc(s)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

const META_RE = /^(NOTES?|VARIATIONS?|NOTE|TIP|TIPS|SERVES|MAKES|TOTAL TIME|ACTIVE TIME|PREP TIME)$/i;

export function renderBody(body) {
  const lines = String(body).split("\n");
  const out = [];
  let list = null;
  const closeList = () => { if (list) { out.push(`</${list}>`); list = null; } };
  for (const raw of lines) {
    const t = raw.trim();
    if (!t) { closeList(); continue; }
    if (/^[-•*]\s+/.test(t)) {
      if (list !== "ul") { closeList(); out.push("<ul>"); list = "ul"; }
      out.push(`<li>${inline(t.replace(/^[-•*]\s+/, ""))}</li>`);
      continue;
    }
    const om = t.match(/^(\d{1,2})[.)]\s+(.*)$/);
    if (om) {
      if (list !== "ol") { closeList(); out.push("<ol>"); list = "ol"; }
      out.push(`<li value="${om[1]}">${inline(om[2])}</li>`);
      continue;
    }
    closeList();
    if (META_RE.test(t) && t.length < 40) {
      out.push(`<p class="rhead">${esc(t)}</p>`);
      continue;
    }
    out.push(`<p>${inline(t)}</p>`);
  }
  closeList();
  return out.join("\n");
}
