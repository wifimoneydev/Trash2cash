document.addEventListener("DOMContentLoaded", function () {
  const tabs = document.getElementById("city-tabs");
  const results = document.getElementById("location-results");
  if (!tabs || !results) return;

  function pinIcon() {
    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M12 21s7-6.5 7-11.5a7 7 0 1 0-14 0C5 14.5 12 21 12 21Z"/>' +
      '<circle cx="12" cy="9.5" r="2.4"/></svg>';
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function renderRecords(records) {
    if (!records || records.length === 0) {
      results.innerHTML = '<div class="empty-state" id="location-grid"><p>We don\'t currently have any listed areas for that city.</p></div>';
      return;
    }
    const cards = records.map(function (r) {
      return '<div class="location-card">' +
        '<h3>' + pinIcon() + ' ' + escapeHtml(r.lga) + '</h3>' +
        '<p class="location-city">' + escapeHtml(r.city) + '</p>' +
        '<p class="location-note">Exact outlet address not yet available — this is a static reference area.</p>' +
        '</div>';
    }).join("");
    results.innerHTML = '<div class="location-grid" id="location-grid">' + cards + '</div>';
  }

  tabs.addEventListener("click", function (event) {
    const btn = event.target.closest(".city-tab");
    if (!btn) return;

    tabs.querySelectorAll(".city-tab").forEach(function (t) { t.setAttribute("aria-pressed", "false"); });
    btn.setAttribute("aria-pressed", "true");

    const city = btn.dataset.city;
    results.setAttribute("aria-busy", "true");

    fetch("/api/locations?city=" + encodeURIComponent(city))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        renderRecords(data.records || []);
      })
      .catch(function () {
        results.innerHTML = '<div class="empty-state"><p>Couldn\'t load locations right now. Please try again.</p></div>';
      })
      .finally(function () {
        results.setAttribute("aria-busy", "false");
      });
  });
});
