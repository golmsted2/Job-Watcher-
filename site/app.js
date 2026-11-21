const DEMO_HISTORY = [
  {posting_key:"jpmorgan-chase:101", employer:"JPMorgan Chase", source:"jpmorgan-chase", source_id:"101", title:"2027 Investment Banking Analyst", location:"New York, NY", team:"Investment Banking", employment_type:"Full-time", workplace_type:"Hybrid", salary_min:95000, salary_max:115000, salary_currency:"USD", salary_text:"$95,000–$115,000", is_internship:false, is_new_grad:true, sponsorship:"mentioned", degree_requirement:"mentioned", duplicate_key:"jpmorgan chase 2027 investment banking analyst new york ny", first_seen:"2026-11-20", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/jpmorgan/101"},
  {posting_key:"bank-of-america:102", employer:"Bank of America", source:"bank-of-america", source_id:"102", title:"Credit Analyst - Early Career", location:"Charlotte, NC", team:"Credit", employment_type:"Full-time", workplace_type:"Hybrid", salary_min:70000, salary_max:85000, salary_currency:"USD", salary_text:"$70,000–$85,000", is_internship:false, is_new_grad:true, sponsorship:"unknown", degree_requirement:"mentioned", duplicate_key:"bank of america credit analyst early career charlotte nc", first_seen:"2026-11-19", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/bofa/102"},
  {posting_key:"stifel:103", employer:"Stifel", source:"stifel", source_id:"103", title:"Client Service Associate", location:"St. Louis, MO", team:"Wealth Management", employment_type:"Full-time", workplace_type:"On-site", salary_min:null, salary_max:null, salary_currency:"", salary_text:"", is_internship:false, is_new_grad:false, sponsorship:"unknown", degree_requirement:"not-listed", duplicate_key:"stifel client service associate st louis mo", first_seen:"2026-11-18", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/stifel/103"},
  {posting_key:"pnc:104", employer:"PNC", source:"pnc", source_id:"104", title:"Financial Analyst I", location:"Pittsburgh, PA", team:"Finance", employment_type:"Full-time", workplace_type:"Hybrid", salary_min:62000, salary_max:76000, salary_currency:"USD", salary_text:"$62,000–$76,000", is_internship:false, is_new_grad:true, sponsorship:"no", degree_requirement:"mentioned", duplicate_key:"pnc financial analyst i pittsburgh pa", first_seen:"2026-11-17", last_seen:"2026-11-20", removed_date:"", in_role:true, is_us:true, first_run:false, apply_url:"https://example.com/pnc/104"}
];
const DEMO_STATUS = {run_utc:"2026-11-20T13:00:00Z", latest_run_date:"2026-11-20", earliest_raw_date:"2026-11-01", successful_run_days:20, open_postings:4, new_today:1, removed_today:0, first_run_postings:2, sources:[]};
const APPLICATION_STATUSES = ["Not started", "Saved", "Applied", "Interview", "Offer", "Closed"];
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
  return applications[key] || {status:"Not started", note:""};
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

function postingCard(row, state, latestDate) {
  const app = applicationFor(state.applications, row.posting_key);
  const fresh = freshness(row, latestDate);
  const salary = salaryLabel(row);
  const stage = row.is_internship ? "Internship" : row.is_new_grad ? "New grad / early career" : "Entry-level signal";
  const sponsorship = row.sponsorship === "mentioned" ? "Sponsorship mentioned" : row.sponsorship === "no" ? "No sponsorship" : "Sponsorship not listed";
  const degree = row.degree_requirement === "mentioned" ? "Degree mentioned" : "Degree not listed";
  return `<article class="posting-card">
    <div class="posting-main">
      <div class="posting-topline"><span class="match-score">${fitScore(row)}% match</span><span class="freshness ${fresh.className}">${fresh.label}</span><span class="posted-label">seen ${fmtDate(row.last_seen || row.first_seen)}</span></div>
      <div class="posting-title"><a href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.title)}</a></div>
      <div class="posting-detail"><strong>${escapeHtml(row.employer)}</strong> · ${escapeHtml(row.location || "Location not listed")} · first seen ${fmtDate(row.first_seen)}</div>
      <div class="posting-tags"><span class="tag">${escapeHtml(row.team || "Finance")}</span><span class="tag muted">${escapeHtml(workplace(row))}</span><span class="tag muted">${escapeHtml(stage)}</span><span class="tag muted">${escapeHtml(sponsorship)}</span><span class="tag muted">${escapeHtml(degree)}</span></div>
      <div class="posting-meta"><span class="posting-salary ${salary === "Salary not listed" ? "salary-missing" : ""}">${escapeHtml(salary)}</span><span>Source: ${escapeHtml(row.source || "employer feed")}</span></div>
      <div class="tracker-box"><label>Application status<select class="app-status" data-key="${escapeHtml(row.posting_key)}">${APPLICATION_STATUSES.map((status) => `<option ${status === app.status ? "selected" : ""}>${status}</option>`).join("")}</select></label><label>Private note<textarea class="app-note" data-key="${escapeHtml(row.posting_key)}" rows="1" placeholder="Add a reminder…">${escapeHtml(app.note)}</textarea></label></div>
    </div>
    <div class="posting-actions"><button class="star ${state.favorites.has(row.posting_key) ? "saved" : ""}" data-key="${escapeHtml(row.posting_key)}" aria-label="Save ${escapeHtml(row.title)}">★</button><a class="apply-button" href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">View role</a></div>
  </article>`;
}

function renderBrowse({history, status}) {
  const openRows = history.filter((row) => !row.removed_date && row.is_us);
  const employerSelect = $("#employer-filter");
  const locationSelect = $("#location-filter");
  [...new Set(openRows.map((row) => row.employer).filter(Boolean))].sort().forEach((value) => employerSelect.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
  [...new Set(openRows.map((row) => row.location).filter(Boolean))].sort().forEach((value) => locationSelect.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
  const params = new URLSearchParams(window.location.search);
  const state = {roleOnly: storage.get("roleOnly", true), favorites: new Set(storage.get("jobFavorites", [])), applications: storage.get("jobApplications", {})};
  if (params.get("employer")) employerSelect.value = params.get("employer");
  $("#role-toggle").checked = state.roleOnly;
  const latestDate = status.latest_run_date || openRows.reduce((latest, row) => dateOnly(row.last_seen) > latest ? dateOnly(row.last_seen) : latest, "");
  const render = () => {
    const titleQuery = $("#title-search").value.trim().toLowerCase();
    const stage = $("#stage-filter").value;
    const model = $("#work-model-filter").value;
    const sponsorship = $("#sponsorship-filter").value;
    const degree = $("#degree-filter").value;
    const salary = $("#salary-filter").value;
    const tracking = $("#tracking-filter").value;
    let rows = openRows.filter((row) => {
      const app = applicationFor(state.applications, row.posting_key);
      const rowModel = workplace(row).toLowerCase();
      const salaryKnown = row.salary_min || row.salary_max;
      return (!state.roleOnly || row.in_role) && (!employerSelect.value || row.employer === employerSelect.value) && (!locationSelect.value || row.location === locationSelect.value) && (!titleQuery || String(row.title).toLowerCase().includes(titleQuery)) && (!stage || (stage === "internship" ? row.is_internship : stage === "new-grad" ? row.is_new_grad : row.in_role)) && (!model || rowModel === model) && (!sponsorship || row.sponsorship === sponsorship) && (!degree || row.degree_requirement === degree) && (!salary || (salary === "listed" ? salaryKnown : Number(row.salary_min || row.salary_max || 0) >= 100000)) && (!tracking || (tracking === "saved" ? state.favorites.has(row.posting_key) : tracking === "not-started" ? app.status === "Not started" : app.status === tracking));
    });
    const age = Number($("#days-filter").value || 0);
    if (age) rows = rows.filter((row) => daysBetween(row.first_seen, latestDate) >= age);
    rows = dedupeRows(rows);
    const sort = $("#sort-filter").value;
    rows.sort((a, b) => sort === "oldest" ? dateOnly(a.first_seen).localeCompare(dateOnly(b.first_seen)) : sort === "employer" ? a.employer.localeCompare(b.employer) : sort === "match" ? fitScore(b) - fitScore(a) : sort === "salary" ? Number(b.salary_max || b.salary_min || 0) - Number(a.salary_max || a.salary_min || 0) : dateOnly(b.first_seen).localeCompare(dateOnly(a.first_seen)));
    $("#browse-count").textContent = rows.length;
    $("#browse-summary").textContent = `${rows.length} ${rows.length === 1 ? "posting" : "postings"} · ${state.roleOnly ? "finance / early-career match" : "all US postings"} · duplicates hidden`;
    $("#posting-list").innerHTML = rows.length ? rows.map((row) => postingCard(row, state, latestDate)).join("") : `<div class="panel"><p class="empty">No postings match these filters.</p></div>`;
    $$(".star").forEach((button) => button.addEventListener("click", () => { const key = button.dataset.key; state.favorites.has(key) ? state.favorites.delete(key) : state.favorites.add(key); storage.set("jobFavorites", [...state.favorites]); render(); }));
    $$(".app-status").forEach((select) => select.addEventListener("change", () => { const key = select.dataset.key; state.applications[key] = {...applicationFor(state.applications, key), status:select.value, updatedAt:new Date().toISOString()}; storage.set("jobApplications", state.applications); }));
    $$(".app-note").forEach((note) => note.addEventListener("blur", () => { const key = note.dataset.key; state.applications[key] = {...applicationFor(state.applications, key), note:note.value, updatedAt:new Date().toISOString()}; storage.set("jobApplications", state.applications); }));
  };
  [$("#role-toggle"), employerSelect, locationSelect, $("#days-filter"), $("#title-search"), $("#sort-filter"), $("#stage-filter"), $("#work-model-filter"), $("#sponsorship-filter"), $("#degree-filter"), $("#salary-filter"), $("#tracking-filter")].forEach((element) => element.addEventListener(element.type === "checkbox" ? "change" : "input", () => { if (element === $("#role-toggle")) { state.roleOnly = element.checked; storage.set("roleOnly", state.roleOnly); } render(); }));
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
  $("#company-detail").innerHTML = `<div class="company-detail-heading"><div class="company-monogram">${escapeHtml(selected.slice(0, 2).toUpperCase())}</div><div><p class="eyebrow">Company profile</p><h2>${escapeHtml(selected)}</h2><p>${escapeHtml(profile.focus)}</p></div></div><div class="company-metrics"><span><strong>${rows.length}</strong> open matches</span><span><strong>${rows.filter((row) => row.is_new_grad || row.is_internship).length}</strong> new-grad / internship signals</span><span><strong>${latest ? fmtDate(latest) : "—"}</strong> last seen</span></div><p class="company-source">Feed: ${escapeHtml(profile.ats)} · <a href="./browse.html?employer=${encodeURIComponent(selected)}">Browse this company’s roles →</a></p>`;
  $("#company-list").innerHTML = employers.map((employer) => { const employerRows = byEmployer[employer] || []; const profileData = COMPANY_PROFILES[employer]; return `<a class="company-card ${employer === selected ? "selected" : ""}" href="./companies.html?company=${encodeURIComponent(employer)}"><div class="company-heading"><span class="company-monogram">${escapeHtml(employer.slice(0, 2).toUpperCase())}</span><span><strong>${escapeHtml(employer)}</strong><small>${escapeHtml(profileData.ats)}</small></span></div><p>${escapeHtml(profileData.focus)}</p><div class="company-roles"><span>${employerRows.length} open matches</span><span>${employerRows.filter((row) => row.is_new_grad || row.is_internship).length} early-career</span></div></a>`; }).join("");
  $("#company-summary").textContent = `${employers.length} tracked finance employers · ${openRows.length} open early-career matches · refreshed ${fmtDate(status.latest_run_date)}`;
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
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
}

init();
