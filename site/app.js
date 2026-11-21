const DEMO_HISTORY = [
  {posting_key:"stripe:101", employer:"Stripe", source:"stripe", source_id:"101", title:"Senior Financial Analyst", location:"New York, NY", team:"Finance", employment_type:"Full-time", workplace_type:"Hybrid", description:"", apply_url:"https://example.com/stripe/101", posted_at:"2026-11-20", first_seen:"2026-11-20", last_seen:"2026-11-20", removed_date:"", in_role:true, first_run:false},
  {posting_key:"stripe:102", employer:"Stripe", source:"stripe", source_id:"102", title:"Data Analyst, Risk", location:"Remote", team:"Risk", employment_type:"Full-time", workplace_type:"Remote", description:"", apply_url:"https://example.com/stripe/102", posted_at:"2026-11-17", first_seen:"2026-11-17", last_seen:"2026-11-20", removed_date:"", in_role:true, first_run:false},
  {posting_key:"airbnb:201", employer:"Airbnb", source:"airbnb", source_id:"201", title:"Product Manager", location:"San Francisco, CA", team:"Product", employment_type:"Full-time", workplace_type:"Hybrid", description:"", apply_url:"https://example.com/airbnb/201", posted_at:"2026-11-15", first_seen:"2026-11-15", last_seen:"2026-11-20", removed_date:"", in_role:false, first_run:false},
  {posting_key:"airbnb:202", employer:"Airbnb", source:"airbnb", source_id:"202", title:"Senior Analytics Engineer", location:"Seattle, WA", team:"Data", employment_type:"Full-time", workplace_type:"Hybrid", description:"", apply_url:"https://example.com/airbnb/202", posted_at:"2026-11-12", first_seen:"2026-11-12", last_seen:"2026-11-20", removed_date:"", in_role:true, first_run:false},
  {posting_key:"figma:301", employer:"Figma", source:"figma", source_id:"301", title:"Data Scientist, Growth", location:"New York, NY", team:"Data", employment_type:"Full-time", workplace_type:"Hybrid", description:"", apply_url:"https://example.com/figma/301", posted_at:"2026-11-10", first_seen:"2026-11-10", last_seen:"2026-11-20", removed_date:"", in_role:true, first_run:false},
  {posting_key:"notion:401", employer:"Notion", source:"notion", source_id:"401", title:"Brand Designer", location:"San Francisco, CA", team:"Design", employment_type:"Full-time", workplace_type:"On-site", description:"", apply_url:"https://example.com/notion/401", posted_at:"2026-11-03", first_seen:"2026-11-03", last_seen:"2026-11-18", removed_date:"2026-11-19", in_role:false, first_run:false},
  {posting_key:"brex:501", employer:"Brex", source:"brex", source_id:"501", title:"Credit Risk Analyst", location:"Salt Lake City, UT", team:"Credit", employment_type:"Full-time", workplace_type:"Hybrid", description:"", apply_url:"https://example.com/brex/501", posted_at:"2026-11-01", first_seen:"2026-11-01", last_seen:"2026-11-20", removed_date:"", in_role:true, first_run:true},
  {posting_key:"gitlab:601", employer:"GitLab", source:"gitlab", source_id:"601", title:"Senior Software Engineer", location:"Remote", team:"Engineering", employment_type:"Full-time", workplace_type:"Remote", description:"", apply_url:"https://example.com/gitlab/601", posted_at:"2026-10-29", first_seen:"2026-10-29", last_seen:"2026-11-20", removed_date:"", in_role:false, first_run:true}
];
const DEMO_STATUS = {run_utc:"2026-11-20T13:00:00Z", latest_run_date:"2026-11-20", earliest_raw_date:"2026-11-01", successful_run_days:20, open_postings:7, new_today:1, removed_today:0, first_run_postings:2, sources:[
  {id:"airbnb",employer:"Airbnb",ats:"Greenhouse",ok:true,item_count:112}, {id:"stripe",employer:"Stripe",ats:"Greenhouse",ok:true,item_count:94}, {id:"datadog",employer:"Datadog",ats:"Greenhouse",ok:true,item_count:80}, {id:"coinbase",employer:"Coinbase",ats:"Greenhouse",ok:true,item_count:76}, {id:"figma",employer:"Figma",ats:"Greenhouse",ok:true,item_count:48}, {id:"lyft",employer:"Lyft",ats:"Greenhouse",ok:false,item_count:0,error:"HTTPError: 503"}
]};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));
const fmtDate = (value) => value ? new Intl.DateTimeFormat("en-US", {month:"short", day:"numeric", year:"numeric", timeZone:"UTC"}).format(new Date(`${value}T00:00:00Z`)) : "—";
const daysBetween = (a, b) => Math.max(0, Math.round((new Date(`${b}T00:00:00Z`) - new Date(`${a}T00:00:00Z`)) / 86400000));
const groupBy = (rows, keyFn) => rows.reduce((groups, row) => { const key = keyFn(row); (groups[key] ||= []).push(row); return groups; }, {});

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
  $("#source-status").innerHTML = (status.sources || []).map((source) => `<div class="source-row"><div class="source-name"><span class="status-dot ${source.ok ? "" : "bad"}"></span><span>${escapeHtml(source.employer)}</span></div><span class="source-meta">${source.ok ? `${source.item_count} postings` : "source failed"}</span></div>`).join("") || `<p class="empty">No source status has been published yet.</p>`;
  const newRows = history.filter((row) => row.first_seen === status.latest_run_date && !row.first_run && row.is_us && row.in_role).slice(0, 5);
  const removedRows = history.filter((row) => row.removed_date === status.latest_run_date && row.is_us && row.in_role).slice(0, 5);
  const changeMarkup = (rows, removed = false) => rows.length ? rows.map((row) => `<div class="change-item ${removed ? "removed" : ""}"><a href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.title)}</a><span>${escapeHtml(row.employer)} · ${escapeHtml(row.location || "Location not listed")}</span></div>`).join("") : `<p class="empty">Nothing recorded.</p>`;
  $("#new-list").innerHTML = changeMarkup(newRows);
  $("#removed-list").innerHTML = changeMarkup(removedRows, true);
}

function renderBrowse({history}) {
  const openRows = history.filter((row) => !row.removed_date && row.is_us);
  const employerSelect = $("#employer-filter");
  const locationSelect = $("#location-filter");
  [...new Set(openRows.map((row) => row.employer))].sort().forEach((value) => employerSelect.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
  [...new Set(openRows.map((row) => row.location).filter(Boolean))].sort().forEach((value) => locationSelect.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
  const state = {roleOnly: localStorage.getItem("roleOnly") !== "false", favorites: new Set(JSON.parse(localStorage.getItem("jobFavorites") || "[]"))};
  $("#role-toggle").checked = state.roleOnly;
  const render = () => {
    let rows = openRows.filter((row) => (!state.roleOnly || row.in_role) && (!employerSelect.value || row.employer === employerSelect.value) && (!locationSelect.value || row.location === locationSelect.value) && (!$("#title-search").value.trim() || row.title.toLowerCase().includes($("#title-search").value.trim().toLowerCase())));
    const age = Number($("#days-filter").value || 0);
    const latestDate = rows.reduce((latest, row) => row.last_seen > latest ? row.last_seen : latest, "");
    if (age && latestDate) rows = rows.filter((row) => daysBetween(row.first_seen, latestDate) >= age);
    const sort = $("#sort-filter").value;
    rows.sort((a, b) => sort === "oldest" ? a.first_seen.localeCompare(b.first_seen) : sort === "employer" ? a.employer.localeCompare(b.employer) : b.first_seen.localeCompare(a.first_seen));
    $("#browse-count").textContent = rows.length;
    $("#browse-summary").textContent = `${rows.length} ${rows.length === 1 ? "posting" : "postings"} · ${state.roleOnly ? "finance / early-career match" : "all US postings"}`;
    $("#posting-list").innerHTML = rows.length ? rows.map((row) => `<article class="posting-card"><div><div class="posting-title"><a href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.title)}</a></div><div class="posting-detail">${escapeHtml(row.employer)} · ${escapeHtml(row.location || "Location not listed")} · first seen ${fmtDate(row.first_seen)}</div><div class="posting-tags"><span class="tag">${escapeHtml(row.team || "Team not listed")}</span><span class="tag muted">${escapeHtml(row.workplace_type || row.employment_type || "Details unavailable")}</span></div></div><div class="posting-actions"><button class="star ${state.favorites.has(row.posting_key) ? "saved" : ""}" data-key="${escapeHtml(row.posting_key)}" aria-label="Save ${escapeHtml(row.title)}">★</button><a class="apply-button" href="${escapeHtml(row.apply_url)}" target="_blank" rel="noreferrer">View role</a></div></article>`).join("") : `<div class="panel"><p class="empty">No postings match these filters.</p></div>`;
    $$(".star").forEach((button) => button.addEventListener("click", () => { const key = button.dataset.key; state.favorites.has(key) ? state.favorites.delete(key) : state.favorites.add(key); localStorage.setItem("jobFavorites", JSON.stringify([...state.favorites])); render(); }));
  };
  [$("#role-toggle"), employerSelect, locationSelect, $("#days-filter"), $("#title-search"), $("#sort-filter")].forEach((element) => element.addEventListener(element.type === "checkbox" ? "change" : "input", () => { if (element === $("#role-toggle")) { state.roleOnly = element.checked; localStorage.setItem("roleOnly", String(state.roleOnly)); } render(); }));
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

async function init() {
  showNetworkState();
  window.addEventListener("online", showNetworkState);
  window.addEventListener("offline", showNetworkState);
  const data = await loadData();
  const page = document.body.dataset.page;
  if (page === "today") renderToday(data);
  if (page === "browse") renderBrowse(data);
  if (page === "market") renderMarket(data);
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
}

init();

