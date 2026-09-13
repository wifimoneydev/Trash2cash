document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("reward-form");
  if (!form) return;

  const materialField = document.getElementById("material");
  const weightField = document.getElementById("weight");
  const materialFieldWrap = document.getElementById("material-field");
  const weightFieldWrap = document.getElementById("weight-field");
  const resultPanel = document.getElementById("result-panel");
  const submitBtn = document.getElementById("reward-submit");

  function showResult(html, isError) {
    resultPanel.innerHTML = html;
    resultPanel.classList.add("is-visible");
    resultPanel.classList.toggle("is-error", !!isError);
  }

  function validate() {
    let ok = true;
    materialFieldWrap.classList.remove("has-error");
    weightFieldWrap.classList.remove("has-error");

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
    submitBtn.textContent = "Calculating…";

    fetch("/api/reward", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ material: materialField.value, weight: weightField.value }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.ok) {
          showResult(
            '<p class="result-label">Estimated reward</p>' +
            '<p class="result-value">₦' + data.reward.toFixed(2) + '</p>' +
            '<p class="result-note">Estimate for ' + data.weight + 'kg of ' + data.material +
            '. Based on a fixed rate table — not a live market price.</p>',
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
        submitBtn.textContent = "Calculate Reward";
      });
  });
});
