document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("reward-form");
  if (!form) return;

  const dataEl = document.getElementById("materials-data");
  const materials = dataEl ? JSON.parse(dataEl.textContent) : [];
  const materialsById = {};
  materials.forEach(function (m) { materialsById[m.id] = m; });

  const categoryField = document.getElementById("category");
  const materialField = document.getElementById("material");
  const examplesHint = document.getElementById("material-examples-hint");
  const categoryFieldWrap = document.getElementById("category-field");
  const materialFieldWrap = document.getElementById("material-field");
  const weightField = document.getElementById("weight");
  const weightFieldWrap = document.getElementById("weight-field");
  const resultPanel = document.getElementById("result-panel");
  const submitBtn = document.getElementById("reward-submit");

  function updateMaterialOptions(preserveSelection) {
    const selectedCategory = categoryField.value;
    const previousMaterial = materialField.value;
    let hasVisibleSelection = false;

    Array.from(materialField.options).forEach(function (opt) {
      if (!opt.value) return; // the "Select a material…" placeholder
      const matches = opt.dataset.category === selectedCategory;
      opt.hidden = !matches;
      if (matches && opt.value === previousMaterial) hasVisibleSelection = true;
    });

    materialField.disabled = !selectedCategory;

    if (!preserveSelection || !hasVisibleSelection) {
      materialField.value = "";
      updateExamplesHint();
    }
  }

  function updateExamplesHint() {
    const material = materialsById[materialField.value];
    examplesHint.textContent = material ? material.examples.join(", ") : "";
  }

  categoryField.addEventListener("change", function () {
    updateMaterialOptions(false);
  });
  materialField.addEventListener("change", updateExamplesHint);

  // On first load (e.g. a deep link from the Materials page with both
  // category and material pre-selected), keep the pre-selected material
  // visible instead of clearing it.
  updateMaterialOptions(true);

  function showResult(html, isError) {
    resultPanel.innerHTML = html;
    resultPanel.classList.add("is-visible");
    resultPanel.classList.toggle("is-error", !!isError);

    const rect = resultPanel.getBoundingClientRect();
    const fullyVisible = rect.top >= 0 && rect.bottom <= window.innerHeight;
    if (!fullyVisible) {
      resultPanel.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "nearest",
      });
    }
  }

  function validate() {
    let ok = true;
    categoryFieldWrap.classList.remove("has-error");
    materialFieldWrap.classList.remove("has-error");
    weightFieldWrap.classList.remove("has-error");

    if (!categoryField.value) {
      categoryFieldWrap.classList.add("has-error");
      ok = false;
    }
    if (!materialField.value) {
      materialFieldWrap.classList.add("has-error");
      ok = false;
    }

    const weightVal = parseFloat(weightField.value);
    if (weightField.value === "" || Number.isNaN(weightVal) || weightVal < 0) {
      weightFieldWrap.classList.add("has-error");
      ok = false;
    }

    return ok;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!validate()) return;

    submitBtn.disabled = true;
    submitBtn.textContent = "Estimating…";

    fetch("/api/reward", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ material_id: materialField.value, weight: weightField.value }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.ok) {
          showResult(
            '<p class="result-label">' + data.material_name + '</p>' +
            '<p class="result-value">₦' + data.reward.toFixed(2) + '</p>' +
            '<p class="result-note">' + data.weight + 'kg × ₦' + data.rate_per_kg + '/kg. ' + data.disclaimer + '</p>' +
            '<p class="material-not-sure"><a href="/locations?material=' + encodeURIComponent(data.material_id) + '">Find a drop-off →</a></p>',
            false
          );
        } else {
          showResult(
            '<p class="result-label">Couldn\'t calculate that</p><p class="result-note">' + data.message + '</p>',
            true
          );
        }
      })
      .catch(function () {
        showResult('<p class="result-label">Something went wrong</p><p class="result-note">Please try again in a moment, or use the form without JavaScript.</p>', true);
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = "Estimate Reward";
      });
  });
});
