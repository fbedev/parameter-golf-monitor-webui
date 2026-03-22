const form = document.querySelector("#controls-form");
const tbody = document.querySelector("#leaderboard-body");
const statsGrid = document.querySelector("#stats-grid");
const generatedAt = document.querySelector("#generated-at");
const statusNote = document.querySelector("#status-note");

function fmtScore(value) {
  if (value === null || value === undefined) {
    return "?";
  }
  return Number(value).toFixed(5);
}

function fmtDate(value) {
  if (!value) {
    return "-";
  }
  return value;
}

function renderStats(stats) {
  const cards = [
    { label: "Total PRs", value: stats.total ?? 0 },
    { label: "With Scores", value: stats.scored ?? 0 },
    {
      label: "Best",
      value: stats.best ? `${fmtScore(stats.best.score)} (#${stats.best.number})` : "-",
    },
    {
      label: "Your Gap",
      value:
        stats.you && stats.you.gap_to_best !== null
          ? `${stats.you.gap_to_best > 0 ? "+" : ""}${stats.you.gap_to_best.toFixed(5)}`
          : "-",
    },
  ];

  statsGrid.innerHTML = cards
    .map(
      (card) => `
      <article class="stat-card">
        <p class="stat-label">${card.label}</p>
        <p class="stat-value">${card.value}</p>
      </article>
    `,
    )
    .join("");
}

function renderEntries(entries, me) {
  if (!entries.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8">No entries match the current filters.</td>
      </tr>
    `;
    return;
  }

  const meLower = me ? me.toLowerCase() : null;

  tbody.innerHTML = entries
    .map((entry) => {
      const isMe = meLower && entry.author.toLowerCase() === meLower;
      const status = entry.category === "non-record" ? "non-rec" : entry.status;
      const title = entry.suspect ? `${entry.title} [suspect]` : entry.title;
      const techniques = entry.techniques && entry.techniques.length ? entry.techniques.join(", ") : "unknown";
      return `
      <tr class="${isMe ? "by-me" : ""} ${entry.suspect ? "suspect" : ""}">
        <td class="rank">${entry.rank ?? "-"}</td>
        <td class="score">${fmtScore(entry.score)}</td>
        <td class="pr-number">#${entry.number}</td>
        <td><span class="status-pill">${status}</span></td>
        <td>${entry.author}${isMe ? " (you)" : ""}</td>
        <td>${fmtDate(entry.date)}</td>
        <td>${title}</td>
        <td>${techniques}</td>
      </tr>
    `;
    })
    .join("");
}

async function refreshLeaderboard() {
  const formData = new FormData(form);
  const params = new URLSearchParams();

  for (const [key, value] of formData.entries()) {
    if (value === "") {
      continue;
    }
    params.set(key, value);
  }

  ["records_only", "include_suspect"].forEach((name) => {
    const el = form.elements[name];
    if (el && el.checked) {
      params.set(name, "1");
    }
  });

  statusNote.textContent = "Loading";

  try {
    const response = await fetch(`/api/leaderboard?${params.toString()}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    renderStats(data.stats);
    renderEntries(data.entries, data.filters.me);
    generatedAt.textContent = new Date(data.generated_at).toLocaleString();
    statusNote.textContent = `Mode: ${data.mode.toUpperCase()} | Suspect hidden: ${Math.max((data.stats.suspect_count || 0) - data.entries.filter((e) => e.suspect).length, 0)}`;
  } catch (error) {
    statusNote.textContent = `Error: ${error.message}`;
    tbody.innerHTML = `
      <tr>
        <td colspan="8">${error.message}</td>
      </tr>
    `;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  refreshLeaderboard();
});

refreshLeaderboard();
