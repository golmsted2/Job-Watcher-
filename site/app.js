const DEMO_HISTORY = [
  {posting_key:"jpmorgan-chase:101", employer:"JPMorgan Chase", source:"jpmorgan-chase", source_id:"101", title:"2027 Investment Banking Analyst", location:"New York, NY", team:"Investment Banking", employment_type:"Full-time", workplace_type:"Hybrid", salary_min:95000, salary_max:115000, salary_currency:"USD", salary_text:"$95,000–$115,000", is_internship:false, is_new_grad:true, sponsorship:"mentioned", degree_requirement:"mentioned", duplicate_key:"jpmorgan chase 2027 investment banking analyst new york ny", first_seen:"2026-11-20", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/jpmorgan/101"},
  {posting_key:"bank-of-america:102", employer:"Bank of America", source:"bank-of-america", source_id:"102", title:"Credit Analyst - Early Career", location:"Charlotte, NC", team:"Credit", employment_type:"Full-time", workplace_type:"Hybrid", salary_min:70000, salary_max:85000, salary_currency:"USD", salary_text:"$70,000–$85,000", is_internship:false, is_new_grad:true, sponsorship:"unknown", degree_requirement:"mentioned", duplicate_key:"bank of america credit analyst early career charlotte nc", first_seen:"2026-11-19", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/bofa/102"},
  {posting_key:"stifel:103", employer:"Stifel", source:"stifel", source_id:"103", title:"Client Service Associate", location:"St. Louis, MO", team:"Wealth Management", employment_type:"Full-time", workplace_type:"On-site", salary_min:null, salary_max:null, salary_currency:"", salary_text:"", is_internship:false, is_new_grad:false, sponsorship:"unknown", degree_requirement:"not-listed", duplicate_key:"stifel client service associate st louis mo", first_seen:"2026-11-18", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/stifel/103"},
  {posting_key:"pnc:104", employer:"PNC", source:"pnc", source_id:"104", title:"Financial Analyst I", location:"Pittsburgh, PA", team:"Finance", employment_type:"Full-time", workplace_type:"Hybrid", salary_min:62000, salary_max:76000, salary_currency:"USD", salary_text:"$62,000–$76,000", is_internship:false, is_new_grad:true, sponsorship:"no", degree_requirement:"mentioned", duplicate_key:"pnc financial analyst i pittsburgh pa", first_seen:"2026-11-17", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/pnc/104"}
];
const DEMO_STATUS = {run_utc:"2026-11-20T13:00:00Z", latest_run_date:"2026-11-20", earliest_raw_date:"2026-11-01", successful_run_days:20, open_postings:4, new_today:1, removed_today:0, first_run_postings:2, sources:[]};
const APPLICATION_STATUSES = ["Not started", "Saved", "Applied", "Interview", "Offer", "Closed"];
const PROGRAM_TYPES = ["Internship / campus", "New graduate program", "Rotational / leadership", "Entry-level"];
const COST_BANDS = {
  "NY": {label:"New York area", band:"High", index:145}, "CA": {label:"California", band:"High", index:139},
  "MA": {label:"Boston area", band:"High", index:132}, "DC": {label:"Washington, DC", band:"High", index:128},
  "WA": {label:"Seattle area", band:"High", index:126}, "IL": {label:"Chicago area", band:"Medium-high", index:108},
  "TX": {label:"Texas", band:"Medium", index:96}, "NC": {label:"North Carolina", band:"Medium", index:94},
  "MO": {label:"Missouri", band:"Medium-low", index:89}, "PA": {label:"Pennsylvania", band:"Medium-low", index:90},
  "OH": {label:"Ohio", band:"Medium-low", index:88}, "FL": {label:"Florida", band:"Medium", index:101},
  "MN": {label:"Minnesota", band:"Medium", index:98}, "CO": {label:"Colorado", band:"Medium-high", index:112},
  "VA": {label:"Virginia", band:"Medium-high", index:108}, "GA": {label:"Georgia", band:"Medium-low", index:92}
};
const MAP_POINTS = {NY:[83,67], CA:[20,116], MA:[88,53], DC:[78,84], WA:[18,28], IL:[57,78], TX:[46,135], NC:[75,103], MO:[52,91], PA:[72,72], OH:[67,77], FL:[76,151], MN:[50,48], CO:[40,91], VA:[75,91], GA:[68,122]};
const SKILL_ALIASES = {
  excel:"Excel", sql:"SQL", python:"Python", tableau:"Tableau", powerbi:"Power BI", "power bi":"Power BI",
  accounting:"Accounting", fpya:"FP&A", "fp&a":"FP&A", finance:"Finance", financial:"Finance",
  valuation:"Valuation", modeling:"Financial modeling", "financial modeling":"Financial modeling",
  risk:"Risk", credit:"Credit", investment:"Investments", banking:"Banking", payments:"Payments",
  bloomberg:"Bloomberg", salesforce:"Salesforce", communication:"Communication", leadership:"Leadership"
};
const COMPANY_PROFILES = {
  "Edward Jones": {focus:"Branch, wealth management, operations, and financial planning careers.", ats:"MCloud"},
  "Stifel": {focus:"Wealth management, investment banking, capital markets, and client service.", ats:"Jibe"},
  "JPMorgan Chase": {focus:"Banking, markets, risk, finance, and early-career analyst programs.", ats:"Oracle"},
  "Bank of America": {focus:"Consumer banking, corporate finance, risk, credit, and wealth management.", ats:"Workday"},
  "Citi": {focus:"Banking, treasury, risk, markets, and global financial services.", ats:"Eightfold"},
  "Wells Fargo": {focus:"Consumer and commercial banking, risk, lending, and finance operations.", ats:"Workday"},
  "Goldman Sachs": {focus:"Investment banking, asset management, markets, and engineering for finance.", ats:"Workday"},
  "Morgan Stanley": {focus:"Wealth management, investment banking, research, and capital markets.", ats:"Workday"},
  "PNC": {focus:"Retail and commercial banking, credit, treasury, and financial analysis.", ats:"Workday"},
  "U.S. Bank": {focus:"Banking, payments, risk, finance, and relationship management.", ats:"Workday"},
  "State Street": {focus:"Asset servicing, investment management, fund accounting, and risk.", ats:"Workday"},
  "BNY": {focus:"Asset management, custody, investment operations, and finance technology.", ats:"Workday"},
  "American Express": {focus:"Payments, credit, risk, finance, and customer-facing analyst roles.", ats:"Workday"},
  "Capital One": {focus:"Consumer finance, credit, risk, product, and financial analysis.", ats:"Workday"},
  "Northern Trust": {focus:"Asset servicing, wealth management, banking, and investment operations.", ats:"Workday"}
};
const COMPANY_LOGOS = {
  "Edward Jones":"./assets/logos/edward-jones.png",
  "Stifel":"./assets/logos/stifel.png",
  "JPMorgan Chase":"./assets/logos/jpmorgan-chase.png",
  "Bank of America":"./assets/logos/bank-of-america.png",
  "Citi":"./assets/logos/citi.png",
  "Wells Fargo":"./assets/logos/wells-fargo.png",
  "Goldman Sachs":"./assets/logos/goldman-sachs.png",
  "Morgan Stanley":"./assets/logos/morgan-stanley.png",
  "PNC":"./assets/logos/pnc.png",
  "U.S. Bank":"./assets/logos/us-bank.png",
  "State Street":"./assets/logos/state-street.png",
  "BNY":"./assets/logos/bny.png",
  "American Express":"./assets/logos/american-express.png",
  "Capital One":"./assets/logos/capital-one.png",
  "Northern Trust":"./assets/logos/northern-trust.png"
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));
const fmtDate = (value) => value ? new Intl.DateTimeFormat("en-US", {month:"short", day:"numeric", year:"numeric", timeZone:"UTC"}).format(new Date(`${String(value).slice(0, 10)}T00:00:00Z`)) : "—";
const dateOnly = (value) => String(value || "").slice(0, 10);
const daysBetween = (a, b) => {
  if (!a || !b) return 0;
  return Math.max(0, Math.round((new Date(`${dateOnly(b)}T00:00:00Z`) - new Date(`${dateOnly(a)}T00:00:00Z`)) / 86400000));
};
const groupBy = (rows, keyFn) => rows.reduce((groups, row) => { const key = keyFn(row); (groups[key] ||= []).push(row); return groups; }, {});
const storage = {
  get(key, fallback) { try { const value = localStorage.getItem(key); return value === null ? fallback : JSON.parse(value); } catch (_error) { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (_error) {} }
};

async function loadData() {
  try {
    const version = Date.now();
    const [historyResponse, statusResponse] = await Promise.all([
      fetch(`./data/history.json?v=${version}`, {cache: "no-store"}),
      fetch(`./data/status.json?v=${version}`, {cache: "no-store"}),
    ]);
    if (!historyResponse.ok || !statusResponse.ok) throw new Error("data unavailable");
    return {history: await historyResponse.json(), status: await statusResponse.json()};
  } catch (_error) {
    return {history: DEMO_HISTORY, status: DEMO_STATUS};
  }
}

function showNetworkState() {
  const element = $("#network-status");
  if (element) element.textContent = navigator.onLine ? "Online-ready" : "Offline · cached data";
}

function renderToday({history, status}) {
  $("#run-date").textContent = fmtDate(status.latest_run_date);
  $("#run-time").textContent = status.run_utc ? new Intl.DateTimeFormat("en-US", {hour:"numeric", minute:"2-digit", timeZone:"UTC", timeZoneName:"short"}).format(new Date(status.run_utc)) : "UTC run time unavailable";
  $("#stat-days").textContent = status.successful_run_days ?? "—";
  $("#stat-open").textContent = status.open_postings ?? history.filter((row) => !row.removed_date && row.is_us && row.in_role).length;
  $("#stat-new").textContent = status.new_today ?? 0;
  $("#stat-removed").textContent = status.removed_today ?? 0;
  $("#source-status").innerHTML = (status.sources || []).map((source) => `<div class="source-row"><div class="source-name"><span class="status-dot ${source.ok ? "" : "bad"}"></span><span>${escapeHtml(source.employer || source.id)}</span></div><span class="source-meta">${source.ok ? `${source.item_count} postings` : "source failed"}</span></div>`).join("") || `<p class="empty">No source status has been published yet.</p>`;
  const newRows = history.filter((row) => row.first_seen === status.latest_run_date && !row.first_run && row.is_us && row.in_role).slice(0, 5);
  const removedRows = history.filter((row) => row.removed_date === status.latest_run_date && row.is_us && row.in_role).slice(0, 5);
  const changeMarkup = (rows, removed = false) => rows.length ? rows.map((row) => `<div class="change-item ${removed ? "removed" : ""}"><a href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.title)}</a><span>${escapeHtml(row.employer)} · ${escapeHtml(row.location || "Location not listed")}</span></div>`).join("") : `<p class="empty">Nothing recorded.</p>`;
  $("#new-list").innerHTML = changeMarkup(newRows);
  $("#removed-list").innerHTML = changeMarkup(removedRows, true);
}

function workplace(row) {
  const value = String(row.workplace_type || "").toLowerCase();
  if (value.includes("remote")) return "Remote";
  if (value.includes("hybrid")) return "Hybrid";
  if (value.includes("on-site") || value.includes("onsite") || value.includes("on site")) return "On-site";
  return row.workplace_type || "Work model not listed";
}

function freshness(row, latestDate) {
  const age = daysBetween(dateOnly(row.last_seen || row.first_seen), latestDate);
  return {label: age <= 1 ? "Fresh" : age <= 7 ? "Recent" : `${age}d old`, className: age <= 1 ? "fresh" : age <= 7 ? "recent" : "older"};
}

function salaryLabel(row) {
  if (row.salary_text) return row.salary_text;
  const currency = row.salary_currency === "USD" || !row.salary_currency ? "$" : `${row.salary_currency} `;
  const low = row.salary_min ? `${currency}${Number(row.salary_min).toLocaleString("en-US", {maximumFractionDigits:0})}` : "";
  const high = row.salary_max ? `${currency}${Number(row.salary_max).toLocaleString("en-US", {maximumFractionDigits:0})}` : "";
  return low && high && low !== high ? `${low}–${high}` : low || high || "Salary not listed";
}

function annualSalary(row) {
  const low = Number(row.salary_annual_min || row.salary_min || 0);
  const high = Number(row.salary_annual_max || row.salary_max || 0);
  return {low, high, period:row.salary_period || (low || high ? "year" : "unknown")};
}

function salaryMatches(row, selection) {
  if (!selection) return true;
  const salary = annualSalary(row);
  if (selection === "listed") return Boolean(salary.low || salary.high);
  const low = salary.low || salary.high;
  const high = salary.high || salary.low;
  if (!low && !high) return false;
  if (/^\d+$/.test(selection)) return high >= Number(selection);
  if (selection.endsWith("+")) return high >= Number(selection.slice(0, -1));
  const [minimum, maximum] = selection.split("-").map(Number);
  return high >= minimum && low < maximum;
}

function normalizedSalaryLabel(row) {
  const salary = annualSalary(row);
  if (!salary.low && !salary.high) return "Salary not listed";
  const low = salary.low ? `$${Math.round(salary.low).toLocaleString("en-US")}` : "";
  const high = salary.high ? `$${Math.round(salary.high).toLocaleString("en-US")}` : "";
  return low && high && low !== high ? `${low}–${high} annualized` : `${low || high} annualized`;
}

function programType(row) {
  return row.program_type || (row.is_internship ? "Internship / campus" : row.is_new_grad ? "New graduate program" : "Entry-level");
}

function locationProfile(location) {
  const value = String(location || "");
  const match = value.match(/(?:,|\s)\s*([A-Z]{2})(?:\b|\s|,)/);
  const profile = match && COST_BANDS[match[1]] ? COST_BANDS[match[1]] : null;
  return profile ? {...profile, state:match[1]} : {label:"US location", band:"Not available", index:null, state:""};
}

function profileData() {
  return storage.get("jobProfile", {name:"", skills:[], resumeText:"", weeklyDigest:true, browserAlerts:true});
}

function extractSkills(text) {
  const value = String(text || "").toLowerCase();
  return [...new Set(Object.keys(SKILL_ALIASES).filter((skill) => value.includes(skill)).map((skill) => SKILL_ALIASES[skill]))];
}

function profileMatch(row, profile = profileData()) {
  const skills = new Set([...(profile.skills || []), ...extractSkills(profile.resumeText || "")]);
  if (!skills.size) return null;
  const haystack = `${row.title} ${row.team} ${row.program_type || ""} ${row.salary_text || ""}`.toLowerCase();
  const hits = [...skills].filter((skill) => haystack.includes(skill.toLowerCase()));
  return {score:Math.min(99, Math.round(45 + hits.length / Math.max(skills.size, 1) * 55)), hits};
}

function searchMatches(row, search) {
  const title = String(row.title || "").toLowerCase();
  const employer = String(row.employer || "").toLowerCase();
  const query = String(search.query || "").toLowerCase();
  return (!query || title.includes(query) || employer.includes(query)) && (!search.employer || row.employer === search.employer) && (!search.location || row.location === search.location) && (!search.program || programType(row) === search.program) && (!search.stage || (search.stage === "internship" ? row.is_internship : search.stage === "new-grad" ? row.is_new_grad : row.in_role)) && (!search.workplace || workplace(row).toLowerCase() === search.workplace) && (!search.sponsorship || row.sponsorship === search.sponsorship) && (!search.degree || row.degree_requirement === search.degree) && salaryMatches(row, search.salary) && (!search.remoteOnly || workplace(row) === "Remote");
}

function currentSearch() {
  return {
    query:$("#title-search")?.value || "",
    employer:$("#employer-filter")?.value || "",
    location:$("#location-filter")?.value || "",
    stage:$("#stage-filter")?.value || "",
    program:$("#program-filter")?.value || "",
    workplace:$("#work-model-filter")?.value || "",
    sponsorship:$("#sponsorship-filter")?.value || "",
    degree:$("#degree-filter")?.value || "",
    salary:$("#salary-filter")?.value || "",
    remoteOnly:false,
  };
}

function fitScore(row) {
  let score = row.in_role ? 48 : 20;
  if (row.is_new_grad) score += 18;
  if (row.is_internship) score += 10;
  if (row.is_us) score += 10;
  if (["Remote", "Hybrid"].includes(workplace(row))) score += 4;
  if (row.salary_min || row.salary_max) score += 4;
  if (row.degree_requirement === "mentioned") score += 3;
  if (row.sponsorship === "mentioned") score += 3;
  return Math.min(99, score);
}

function applicationFor(applications, key) {
  return applications[key] || {status:"Not started", note:"", deadline:""};
}

function dedupeRows(rows) {
  const unique = new Map();
  rows.forEach((row) => {
    const key = row.duplicate_key || row.posting_key;
    const previous = unique.get(key);
    if (!previous || (row.in_role && !previous.in_role) || dateOnly(row.last_seen) > dateOnly(previous.last_seen)) unique.set(key, row);
  });
  return [...unique.values()];
}

function companyLogo(employer, detail = false) {
  const initials = employer.slice(0, 2).toUpperCase();
  const source = COMPANY_LOGOS[employer];
  const detailClass = detail ? " detail-logo" : "";
  const fallbackStyle = source ? ' style="display:none"' : "";
  const image = source ? `<img class="company-logo" src="${source}" alt="" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='grid';">` : "";
  return `<span class="company-logo-shell${detailClass}">${image}<span class="company-monogram company-logo-fallback"${fallbackStyle}>${escapeHtml(initials)}</span></span>`;
}

function postingCard(row, state, latestDate) {
  const app = applicationFor(state.applications, row.posting_key);
  const fresh = freshness(row, latestDate);
  const salary = salaryLabel(row);
  const annualizedSalary = normalizedSalaryLabel(row);
  const match = profileMatch(row, state.profile);
  const verified = dateOnly(row.last_seen) === dateOnly(latestDate);
  const stage = row.is_internship ? "Internship" : row.is_new_grad ? "New grad / early career" : "Entry-level signal";
  const sponsorship = row.sponsorship === "mentioned" ? "Sponsorship mentioned" : row.sponsorship === "no" ? "No sponsorship" : "Sponsorship not listed";
  const degree = row.degree_requirement === "mentioned" ? "Degree mentioned" : "Degree not listed";
  return `<article class="posting-card">
    <div class="posting-main">
      <div class="posting-topline"><span class="match-score">${fitScore(row)}% fit</span>${match ? `<span class="profile-score">${match.score}% profile</span>` : ""}<span class="freshness ${fresh.className}">${verified ? "Verified today" : fresh.label}</span><span class="posted-label">seen ${fmtDate(row.last_seen || row.first_seen)}</span></div>
      <div class="posting-title"><a href="./job.html?job=${encodeURIComponent(row.posting_key)}">${escapeHtml(row.title)}</a></div>
      <div class="posting-detail"><strong>${escapeHtml(row.employer)}</strong> · ${escapeHtml(row.location || "Location not listed")} · ${escapeHtml(locationProfile(row.location).band)} cost band · first seen ${fmtDate(row.first_seen)}</div>
      <div class="posting-tags"><span class="tag">${escapeHtml(row.team || "Finance")}</span><span class="tag muted">${escapeHtml(workplace(row))}</span><span class="tag muted">${escapeHtml(programType(row))}</span><span class="tag muted">${escapeHtml(sponsorship)}</span><span class="tag muted">${escapeHtml(degree)}</span></div>
      <div class="posting-meta"><span class="posting-salary ${salary === "Salary not listed" ? "salary-missing" : ""}">${escapeHtml(salary)}</span>${salary !== annualizedSalary ? `<span class="salary-normalized">${escapeHtml(annualizedSalary)}</span>` : ""}<span>Source: ${escapeHtml(row.source || "employer feed")}</span></div>
      <div class="tracker-box"><label>Application status<select class="app-status" data-key="${escapeHtml(row.posting_key)}">${APPLICATION_STATUSES.map((status) => `<option ${status === app.status ? "selected" : ""}>${status}</option>`).join("")}</select></label><label>Deadline<input class="app-deadline" data-key="${escapeHtml(row.posting_key)}" type="date" value="${escapeHtml(app.deadline || "")}"></label><label>Private note<textarea class="app-note" data-key="${escapeHtml(row.posting_key)}" rows="1" placeholder="Add a reminder…">${escapeHtml(app.note)}</textarea></label></div>
    </div>
    <div class="posting-actions"><label class="compare-check"><input type="checkbox" class="compare-toggle" data-key="${escapeHtml(row.posting_key)}" ${state.compare.has(row.posting_key) ? "checked" : ""}> Compare</label><button class="star ${state.favorites.has(row.posting_key) ? "saved" : ""}" data-key="${escapeHtml(row.posting_key)}" aria-label="Save ${escapeHtml(row.title)}">★</button><a class="apply-button" href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">Apply</a></div>
  </article>`;
}

function renderBrowse({history, status}) {
  const openRows = history.filter((row) => !row.removed_date && row.is_us);
  const employerSelect = $("#employer-filter");
  const locationSelect = $("#location-filter");
  [...new Set(openRows.map((row) => row.employer).filter(Boolean))].sort().forEach((value) => employerSelect.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
  [...new Set(openRows.map((row) => row.location).filter(Boolean))].sort().forEach((value) => locationSelect.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
  const params = new URLSearchParams(window.location.search);
  const state = {roleOnly: storage.get("roleOnly", true), favorites: new Set(storage.get("jobFavorites", [])), compare: new Set(storage.get("compareJobs", [])), applications: storage.get("jobApplications", {}), profile: profileData()};
  if (params.get("employer")) employerSelect.value = params.get("employer");
  $("#role-toggle").checked = state.roleOnly;
  const latestDate = status.latest_run_date || openRows.reduce((latest, row) => dateOnly(row.last_seen) > latest ? dateOnly(row.last_seen) : latest, "");
  const render = () => {
    const titleQuery = $("#title-search").value.trim().toLowerCase();
    const stage = $("#stage-filter").value;
    const model = $("#work-model-filter").value;
    const sponsorship = $("#sponsorship-filter").value;
    const degree = $("#degree-filter").value;
    const program = $("#program-filter").value;
    const salary = $("#salary-filter").value;
    const tracking = $("#tracking-filter").value;
    let rows = openRows.filter((row) => {
      const app = applicationFor(state.applications, row.posting_key);
      const rowModel = workplace(row).toLowerCase();
      return (!state.roleOnly || row.in_role) && (!employerSelect.value || row.employer === employerSelect.value) && (!locationSelect.value || row.location === locationSelect.value) && (!titleQuery || String(row.title).toLowerCase().includes(titleQuery)) && (!stage || (stage === "internship" ? row.is_internship : stage === "new-grad" ? row.is_new_grad : row.in_role)) && (!program || programType(row) === program) && (!model || rowModel === model) && (!sponsorship || row.sponsorship === sponsorship) && (!degree || row.degree_requirement === degree) && salaryMatches(row, salary) && (!tracking || (tracking === "saved" ? state.favorites.has(row.posting_key) : tracking === "not-started" ? app.status === "Not started" : app.status === tracking));
    });
    const age = Number($("#days-filter").value || 0);
    if (age) rows = rows.filter((row) => daysBetween(row.first_seen, latestDate) >= age);
    rows = dedupeRows(rows);
    const sort = $("#sort-filter").value;
    rows.sort((a, b) => sort === "oldest" ? dateOnly(a.first_seen).localeCompare(dateOnly(b.first_seen)) : sort === "employer" ? a.employer.localeCompare(b.employer) : sort === "match" ? fitScore(b) - fitScore(a) : sort === "salary" ? Number(b.salary_max || b.salary_min || 0) - Number(a.salary_max || a.salary_min || 0) : dateOnly(b.first_seen).localeCompare(dateOnly(a.first_seen)));
    $("#browse-count").textContent = rows.length;
    $("#browse-summary").textContent = `${rows.length} ${rows.length === 1 ? "posting" : "postings"} · ${state.roleOnly ? "finance / early-career match" : "all US postings"} · duplicates hidden`;
    if ($("#compare-count")) $("#compare-count").textContent = state.compare.size;
    if ($("#compare-link")) $("#compare-link").href = `./compare.html?jobs=${encodeURIComponent([...state.compare].join(","))}`;
    $("#posting-list").innerHTML = rows.length ? rows.map((row) => postingCard(row, state, latestDate)).join("") : `<div class="panel"><p class="empty">No postings match these filters.</p></div>`;
    $$(".star").forEach((button) => button.addEventListener("click", () => { const key = button.dataset.key; state.favorites.has(key) ? state.favorites.delete(key) : state.favorites.add(key); storage.set("jobFavorites", [...state.favorites]); render(); }));
    $$(".compare-toggle").forEach((checkbox) => checkbox.addEventListener("change", () => { const key = checkbox.dataset.key; if (checkbox.checked && state.compare.size >= 3) { checkbox.checked = false; return; } checkbox.checked ? state.compare.add(key) : state.compare.delete(key); storage.set("compareJobs", [...state.compare]); render(); }));
    $$(".app-status").forEach((select) => select.addEventListener("change", () => { const key = select.dataset.key; state.applications[key] = {...applicationFor(state.applications, key), status:select.value, updatedAt:new Date().toISOString()}; storage.set("jobApplications", state.applications); }));
    $$(".app-deadline").forEach((input) => input.addEventListener("change", () => { const key = input.dataset.key; state.applications[key] = {...applicationFor(state.applications, key), deadline:input.value, updatedAt:new Date().toISOString()}; storage.set("jobApplications", state.applications); }));
    $$(".app-note").forEach((note) => note.addEventListener("blur", () => { const key = note.dataset.key; state.applications[key] = {...applicationFor(state.applications, key), note:note.value, updatedAt:new Date().toISOString()}; storage.set("jobApplications", state.applications); }));
  };
  [$("#role-toggle"), employerSelect, locationSelect, $("#days-filter"), $("#title-search"), $("#sort-filter"), $("#stage-filter"), $("#program-filter"), $("#work-model-filter"), $("#sponsorship-filter"), $("#degree-filter"), $("#salary-filter"), $("#tracking-filter")].filter(Boolean).forEach((element) => element.addEventListener(element.type === "checkbox" ? "change" : "input", () => { if (element === $("#role-toggle")) { state.roleOnly = element.checked; storage.set("roleOnly", state.roleOnly); } render(); }));
  $("#save-search")?.addEventListener("click", () => {
    const searches = storage.get("savedSearches", []);
    const name = $("#search-name")?.value.trim() || `Search ${searches.length + 1}`;
    searches.unshift({id:`search-${Date.now()}`, name, ...currentSearch(), createdAt:new Date().toISOString()});
    storage.set("savedSearches", searches.slice(0, 12));
    if ($("#search-feedback")) $("#search-feedback").textContent = "Saved to your Workspace.";
  });
  render();
}

function barChart(element, pairs, color = "blue") {
  if (!pairs.length) { element.innerHTML = `<span class="empty">Not enough history yet.</span>`; return; }
  const max = Math.max(...pairs.map((pair) => pair[1]), 1);
  element.innerHTML = pairs.map(([label, value]) => `<div class="bar-wrap" title="${escapeHtml(label)}: ${value}"><div class="bar ${color}" style="height:${Math.max(4, value / max * 100)}%"></div><span class="bar-label">${escapeHtml(label)}</span></div>`).join("");
}

function horizontalChart(element, pairs) {
  const max = Math.max(...pairs.map((pair) => pair[1]), 1);
  element.innerHTML = pairs.length ? pairs.map(([label, value]) => `<div class="hbar-row"><span>${escapeHtml(label || "Not listed")}</span><span class="hbar-track"><span class="hbar-fill" style="width:${value / max * 100}%"></span></span><span class="hbar-value">${value}</span></div>`).join("") : `<span class="empty">Not enough history yet.</span>`;
}

function renderMarket({history, status}) {
  const usHistory = history.filter((row) => row.is_us && row.in_role);
  const dates = [...new Set(usHistory.flatMap((row) => [row.first_seen, row.removed_date].filter(Boolean)))].sort();
  $("#market-days").textContent = dates.length;
  const newByDay = Object.entries(groupBy(usHistory.filter((row) => row.first_seen && !row.first_run), (row) => row.first_seen)).map(([date, rows]) => [date.slice(5), rows.length]).sort();
  const removedByDay = Object.entries(groupBy(usHistory.filter((row) => row.removed_date), (row) => row.removed_date)).map(([date, rows]) => [date.slice(5), rows.length]).sort();
  barChart($("#new-chart"), newByDay, "teal");
  barChart($("#removed-chart"), removedByDay, "coral");
  const newCount = newByDay.reduce((sum, pair) => sum + pair[1], 0);
  const removedCount = removedByDay.reduce((sum, pair) => sum + pair[1], 0);
  $("#new-finding").textContent = `${newCount} postings entered the market.`;
  $("#new-explain").textContent = "The chart excludes the first-run inventory, so this is the flow observed after watching began.";
  $("#removed-finding").textContent = `${removedCount} postings have left the watch list.`;
  $("#removed-explain").textContent = "A removal is only recorded when that employer returned a successful, fresh board response.";
  const openByEmployer = Object.entries(groupBy(usHistory.filter((row) => !row.removed_date), (row) => row.employer)).map(([key, rows]) => [key, rows.length]).sort((a, b) => b[1] - a[1]);
  horizontalChart($("#employer-chart"), openByEmployer);
  const removedEligible = usHistory.filter((row) => row.removed_date && !row.first_run && row.first_seen);
  const durations = removedEligible.map((row) => daysBetween(row.first_seen, row.removed_date)).sort((a, b) => a - b);
  const median = durations.length ? durations[Math.floor(durations.length / 2)] : 0;
  $("#days-finding").textContent = `The median role lasted ${median} days.`;
  $("#days-explain").textContent = "First-run roles are left out because their true start date predates the tracker.";
  $("#days-stat").textContent = `${median}d`;
  const atLeastSevenDaysOld = removedEligible.filter((row) => daysBetween(row.first_seen, status.latest_run_date) >= 7);
  const withinSeven = atLeastSevenDaysOld.filter((row) => daysBetween(row.first_seen, row.removed_date) <= 7);
  const share = atLeastSevenDaysOld.length ? Math.round(withinSeven.length / atLeastSevenDaysOld.length * 100) : 0;
  $("#share-finding").textContent = `${share}% were removed within seven days.`;
  $("#share-explain").textContent = "The denominator is limited to non-first-run roles old enough to qualify for the comparison.";
  $("#share-stat").textContent = `${share}%`;
  const locations = Object.entries(groupBy(usHistory.filter((row) => !row.removed_date), (row) => row.location || "Not listed")).map(([key, rows]) => [key, rows.length]).sort((a, b) => b[1] - a[1]).slice(0, 5);
  horizontalChart($("#location-chart"), locations);
}

function renderCompanies({history, status}) {
  const openRows = history.filter((row) => !row.removed_date && row.is_us && row.in_role);
  const byEmployer = groupBy(dedupeRows(openRows), (row) => row.employer);
  const employers = Object.keys(COMPANY_PROFILES).sort();
  const selected = new URLSearchParams(window.location.search).get("company") || employers[0];
  const rows = byEmployer[selected] || [];
  const profile = COMPANY_PROFILES[selected] || {focus:"Finance roles from the current watch list.", ats:"Employer feed"};
  const latest = rows.reduce((value, row) => dateOnly(row.last_seen) > value ? dateOnly(row.last_seen) : value, "");
  $("#company-detail").innerHTML = `<div class="company-detail-heading">${companyLogo(selected, true)}<div><p class="eyebrow">Company profile</p><h2>${escapeHtml(selected)}</h2><p>${escapeHtml(profile.focus)}</p></div></div><div class="company-metrics"><span><strong>${rows.length}</strong> open matches</span><span><strong>${rows.filter((row) => row.is_new_grad || row.is_internship).length}</strong> new-grad / internship signals</span><span><strong>${latest ? fmtDate(latest) : "—"}</strong> last seen</span></div><p class="company-source">Feed: ${escapeHtml(profile.ats)} · <a href="./browse.html?employer=${encodeURIComponent(selected)}">Browse this company’s roles →</a></p>`;
  $("#company-list").innerHTML = employers.map((employer) => { const employerRows = byEmployer[employer] || []; const profileData = COMPANY_PROFILES[employer]; return `<a class="company-card ${employer === selected ? "selected" : ""}" href="./companies.html?company=${encodeURIComponent(employer)}"><div class="company-heading">${companyLogo(employer)}<span><strong>${escapeHtml(employer)}</strong><small>${escapeHtml(profileData.ats)}</small></span></div><p>${escapeHtml(profileData.focus)}</p><div class="company-roles"><span>${employerRows.length} open matches</span><span>${employerRows.filter((row) => row.is_new_grad || row.is_internship).length} early-career</span></div></a>`; }).join("");
  $("#company-summary").textContent = `${employers.length} tracked finance employers · ${openRows.length} open early-career matches · refreshed ${fmtDate(status.latest_run_date)}`;
}

function saveApplication(key, patch) {
  const applications = storage.get("jobApplications", {});
  applications[key] = {...applicationFor(applications, key), ...patch, updatedAt:new Date().toISOString()};
  storage.set("jobApplications", applications);
  return applications[key];
}

function jobUrl(key) {
  return `./job.html?job=${encodeURIComponent(key)}`;
}

function renderJobDetail({history, status}) {
  const key = new URLSearchParams(window.location.search).get("job");
  const row = history.find((item) => item.posting_key === key) || history.find((item) => item.posting_key === decodeURIComponent(key || ""));
  const container = $("#job-detail");
  if (!row) { container.innerHTML = `<div class="panel"><h2>Job not found</h2><p class="empty">This role may have been removed from the current public index.</p><a class="apply-button" href="./browse.html">Back to Browse</a></div>`; return; }
  const applications = storage.get("jobApplications", {});
  const favorites = new Set(storage.get("jobFavorites", []));
  const app = applicationFor(applications, row.posting_key);
  const profile = profileMatch(row);
  const cost = locationProfile(row.location);
  const salary = salaryLabel(row);
  const annualized = normalizedSalaryLabel(row);
  const verified = dateOnly(row.last_seen) === dateOnly(status.latest_run_date);
  container.innerHTML = `<div class="detail-kicker"><a href="./browse.html">← Browse roles</a><span class="${verified ? "verified-label" : "stale-label"}">${verified ? "Verified in latest source run" : `Last seen ${fmtDate(row.last_seen)}`}</span></div><div class="job-detail-heading"><div><p class="eyebrow">${escapeHtml(row.employer)} · ${escapeHtml(row.source || "employer feed")}</p><h1>${escapeHtml(row.title)}</h1><p class="job-subtitle">${escapeHtml(row.location || "US location not listed")} · ${escapeHtml(workplace(row))} · ${escapeHtml(programType(row))}</p></div><div class="detail-score"><strong>${fitScore(row)}%</strong><span>role fit</span>${profile ? `<small>${profile.score}% profile fit</small>` : ""}</div></div><div class="job-detail-grid"><div><section class="detail-section"><p class="eyebrow">Role snapshot</p><div class="detail-facts"><span><strong>${escapeHtml(salary)}</strong><small>${salary === "Salary not listed" ? "Employer did not publish a range" : escapeHtml(annualized)}</small></span><span><strong>${escapeHtml(cost.band)}</strong><small>${escapeHtml(cost.label)} cost band</small></span><span><strong>${verified ? "Verified today" : freshness(row, status.latest_run_date).label}</strong><small>source freshness</small></span></div></section><section class="detail-section"><p class="eyebrow">About the role</p>${row.description_excerpt ? `<p class="description-copy">${escapeHtml(row.description_excerpt)}</p>` : `<p class="description-copy">The public index has the role metadata but not a description for this source. Use the employer posting for the full responsibilities and qualifications.</p>`}</section><section class="detail-section"><p class="eyebrow">Candidate signals</p><div class="signal-grid"><span>${escapeHtml(programType(row))}</span><span>${row.sponsorship === "mentioned" ? "Sponsorship mentioned" : row.sponsorship === "no" ? "No sponsorship listed" : "Sponsorship not listed"}</span><span>${row.degree_requirement === "mentioned" ? "Degree mentioned" : "Degree not listed"}</span><span>${row.is_internship ? "Internship signal" : row.is_new_grad ? "New graduate signal" : "Entry-level signal"}</span></div></section></div><aside class="detail-aside"><section class="panel tracker-panel"><p class="eyebrow">Your application</p><label>Status<select id="detail-status">${APPLICATION_STATUSES.map((value) => `<option ${value === app.status ? "selected" : ""}>${value}</option>`).join("")}</select></label><label>Deadline<input id="detail-deadline" type="date" value="${escapeHtml(app.deadline || "")}"></label><label>Private note<textarea id="detail-note" rows="4" placeholder="Interview prep, contact, follow-up…">${escapeHtml(app.note || "")}</textarea></label><button class="button button-dark" id="save-detail">Save application</button><span class="form-feedback" id="detail-feedback"></span><button class="secondary-button" id="favorite-detail">${favorites.has(row.posting_key) ? "★ Saved" : "☆ Save job"}</button><a class="apply-button detail-apply" href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">Apply on employer site</a></section></aside></div>`;
  $("#save-detail").addEventListener("click", () => { saveApplication(row.posting_key, {status:$("#detail-status").value, deadline:$("#detail-deadline").value, note:$("#detail-note").value}); $("#detail-feedback").textContent = "Saved locally."; });
  $("#favorite-detail").addEventListener("click", () => { const next = new Set(storage.get("jobFavorites", [])); next.has(row.posting_key) ? next.delete(row.posting_key) : next.add(row.posting_key); storage.set("jobFavorites", [...next]); $("#favorite-detail").textContent = next.has(row.posting_key) ? "★ Saved" : "☆ Save job"; });
}

function renderCompare({history}) {
  const queryKeys = new URLSearchParams(window.location.search).get("jobs");
  const keys = queryKeys ? queryKeys.split(",").map((key) => decodeURIComponent(key)).filter(Boolean) : storage.get("compareJobs", []);
  const rows = keys.map((key) => history.find((row) => row.posting_key === key)).filter(Boolean).slice(0, 3);
  const container = $("#compare-table");
  if (!rows.length) { container.innerHTML = `<div class="panel"><h2>No jobs selected</h2><p class="empty">Choose up to three roles on Browse, then compare them here.</p><a class="apply-button" href="./browse.html">Choose jobs</a></div>`; return; }
  const fields = [["Employer", (row) => row.employer], ["Location", (row) => row.location || "Not listed"], ["Work model", workplace], ["Program", programType], ["Salary", normalizedSalaryLabel], ["Role fit", (row) => `${fitScore(row)}%`], ["Profile fit", (row) => profileMatch(row)?.score ? `${profileMatch(row).score}%` : "Add profile"], ["Cost band", (row) => locationProfile(row.location).band], ["Freshness", (row) => dateOnly(row.last_seen) === dateOnly(new Date().toISOString()) ? "Verified today" : fmtDate(row.last_seen)], ["First seen", (row) => fmtDate(row.first_seen)]];
  container.innerHTML = `<div class="compare-scroll"><table class="compare-table"><thead><tr><th>Signal</th>${rows.map((row) => `<th><a href="${jobUrl(row.posting_key)}">${escapeHtml(row.title)}</a><button class="remove-compare" data-key="${escapeHtml(row.posting_key)}">Remove</button></th>`).join("")}</tr></thead><tbody>${fields.map(([label, value]) => `<tr><th>${escapeHtml(label)}</th>${rows.map((row) => `<td>${escapeHtml(value(row))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  $$(".remove-compare").forEach((button) => button.addEventListener("click", () => { const next = storage.get("compareJobs", []).filter((key) => key !== button.dataset.key); storage.set("compareJobs", next); button.closest("th").remove(); renderCompare({history}); }));
}

function applicationStats(history) {
  const applications = storage.get("jobApplications", {});
  const values = Object.values(applications);
  const count = (status) => values.filter((item) => item.status === status).length;
  const applied = count("Applied") + count("Interview") + count("Offer") + count("Closed");
  return {saved:storage.get("jobFavorites", []).length, tracked:values.length, applied, interview:count("Interview"), offers:count("Offer"), responseRate:applied ? Math.round((count("Interview") + count("Offer")) / applied * 100) : 0};
}

function renderWorkspace({history, status}) {
  let profile = profileData();
  const applications = storage.get("jobApplications", {});
  const stats = applicationStats(history);
  const today = new Date().toISOString().slice(0, 10);
  const deadlines = Object.entries(applications).filter(([, item]) => item.deadline && item.deadline >= today).sort((a, b) => a[1].deadline.localeCompare(b[1].deadline)).slice(0, 8).map(([key, item]) => ({row:history.find((row) => row.posting_key === key), item})).filter((item) => item.row);
  const savedSearches = storage.get("savedSearches", []);
  const latestRows = history.filter((row) => row.first_seen === status.latest_run_date && row.is_us && row.in_role);
  $("#workspace-summary").textContent = `${stats.tracked} tracked applications · ${savedSearches.length} saved searches · data refreshed ${fmtDate(status.latest_run_date)}`;
  $("#workspace-stats").innerHTML = [[stats.saved,"Saved jobs"],[stats.tracked,"Tracked roles"],[stats.applied,"Applications"],[stats.interview,"Interviews"],[stats.offers,"Offers"],[`${stats.responseRate}%`,"Interview / offer rate"]].map(([value,label]) => `<article class="metric-card"><span>${label}</span><strong>${value}</strong><small>stored in this browser</small></article>`).join("");
  $("#deadline-list").innerHTML = deadlines.length ? deadlines.map(({row,item}) => `<div class="deadline-row"><div><a href="${jobUrl(row.posting_key)}">${escapeHtml(row.title)}</a><span>${escapeHtml(row.employer)} · ${escapeHtml(item.status)}</span></div><time datetime="${escapeHtml(item.deadline)}">${fmtDate(item.deadline)}</time></div>`).join("") : `<p class="empty">No upcoming deadlines saved yet.</p>`;
  $("#saved-search-list").innerHTML = savedSearches.length ? savedSearches.map((search) => { const matches = latestRows.filter((row) => searchMatches(row, search)).length; return `<div class="saved-search-row"><div><strong>${escapeHtml(search.name)}</strong><span>${escapeHtml(search.query || "All finance roles")} · ${matches} new match${matches === 1 ? "" : "es"} today</span></div><button class="secondary-button delete-search" data-id="${escapeHtml(search.id)}">Remove</button></div>`; }).join("") : `<p class="empty">Save a search from Browse to get a quick new-role check here.</p>`;
  const locations = Object.entries(groupBy(history.filter((row) => !row.removed_date && row.is_us && row.in_role), (row) => locationProfile(row.location).label)).map(([label, rows]) => { const profile = locationProfile(rows[0].location); const salaries = rows.map((row) => annualSalary(row).low).filter(Boolean); return {label, band:profile.band, count:rows.length, salary:salaries.length ? Math.round(salaries.reduce((a, b) => a + b, 0) / salaries.length) : 0}; }).sort((a, b) => b.count - a.count).slice(0, 8);
  const byState = groupBy(history.filter((row) => !row.removed_date && row.is_us && row.in_role), (row) => locationProfile(row.location).state);
  $("#location-map").innerHTML = `<div class="map-legend"><span><i class="map-dot small"></i> fewer roles</span><span><i class="map-dot large"></i> more roles</span></div><svg viewBox="0 0 110 175" role="img" aria-label="Relative concentration of tracked roles by state">${Object.entries(MAP_POINTS).map(([state, [x, y]]) => { const count = (byState[state] || []).length; const radius = Math.max(2, Math.min(9, 2 + count / 40)); const band = COST_BANDS[state]?.band || "Not available"; return `<circle cx="${x}" cy="${y}" r="${radius}" class="map-point" data-state="${state}"><title>${state}: ${count} roles · ${band} cost band</title></circle>`; }).join("")}<path class="map-outline" d="M9 32L26 17L42 22L58 15L78 27L95 40L89 56L99 71L89 86L95 102L86 118L79 139L64 153L48 162L33 151L20 140L11 116L14 91L7 76Z"/></svg>`;
  $("#location-insights").innerHTML = locations.length ? locations.map((item) => `<div class="location-row"><span><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.band)} cost band</small></span><b>${item.count}</b><span>${item.salary ? `$${item.salary.toLocaleString()} avg listed` : "Salary data limited"}</span></div>`).join("") : `<p class="empty">Location insights will appear as US roles accumulate.</p>`;
  $("#profile-name").value = profile.name || "";
  $("#profile-skills").value = (profile.skills || []).join(", ");
  $("#resume-text").value = profile.resumeText || "";
  $("#notification-toggle").checked = profile.browserAlerts !== false;
  $("#digest-toggle").checked = profile.weeklyDigest !== false;
  $("#profile-match-summary").textContent = profile.skills?.length || profile.resumeText ? `${[...(profile.skills || []), ...extractSkills(profile.resumeText || "")].filter((value, index, values) => values.indexOf(value) === index).length} skills ready for profile matching.` : "Add skills or a resume text file to personalize match scores.";
  $$(".delete-search").forEach((button) => button.addEventListener("click", () => { storage.set("savedSearches", storage.get("savedSearches", []).filter((search) => search.id !== button.dataset.id)); renderWorkspace({history, status}); }));
  $("#save-profile").addEventListener("click", () => { const skills = $("#profile-skills").value.split(",").map((value) => value.trim()).filter(Boolean); profile = {...profile, name:$("#profile-name").value.trim(), skills, resumeText:$("#resume-text").value, browserAlerts:$("#notification-toggle").checked, weeklyDigest:$("#digest-toggle").checked}; storage.set("jobProfile", profile); $("#profile-feedback").textContent = "Profile saved locally."; });
  $("#enable-notifications").addEventListener("click", async () => { if (!("Notification" in window)) { $("#profile-feedback").textContent = "This browser does not support notifications."; return; } const permission = await Notification.requestPermission(); profile = {...profile, browserAlerts:permission === "granted"}; storage.set("jobProfile", profile); $("#profile-feedback").textContent = permission === "granted" ? "Browser alerts enabled." : "Browser alerts remain off."; });
  $("#resume-file").addEventListener("change", (event) => { const file = event.target.files[0]; if (!file) return; const reader = new FileReader(); reader.onload = () => { $("#resume-text").value = String(reader.result || ""); $("#profile-feedback").textContent = `${file.name} loaded. Save your profile to use it for matching.`; }; reader.readAsText(file); });
  $("#export-profile").addEventListener("click", () => { const payload = {profile:storage.get("jobProfile", {}), favorites:storage.get("jobFavorites", []), applications:storage.get("jobApplications", {}), searches:storage.get("savedSearches", [])}; const blob = new Blob([JSON.stringify(payload, null, 2)], {type:"application/json"}); const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = "job-watcher-profile.json"; link.click(); URL.revokeObjectURL(link.href); });
  $("#import-profile").addEventListener("change", (event) => { const file = event.target.files[0]; if (!file) return; const reader = new FileReader(); reader.onload = () => { try { const payload = JSON.parse(String(reader.result)); if (payload.profile) storage.set("jobProfile", payload.profile); if (payload.favorites) storage.set("jobFavorites", payload.favorites); if (payload.applications) storage.set("jobApplications", payload.applications); if (payload.searches) storage.set("savedSearches", payload.searches); renderWorkspace({history, status}); } catch (_error) { $("#profile-feedback").textContent = "That file could not be imported."; } }; reader.readAsText(file); });
}

async function init() {
  showNetworkState();
  window.addEventListener("online", showNetworkState);
  window.addEventListener("offline", showNetworkState);
  const data = await loadData();
  const page = document.body.dataset.page;
  if (page === "today") renderToday(data);
  if (page === "browse") renderBrowse(data);
  if (page === "market") renderMarket(data);
  if (page === "companies") renderCompanies(data);
  if (page === "job") renderJobDetail(data);
  if (page === "compare") renderCompare(data);
  if (page === "workspace") renderWorkspace(data);
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
}

init();
