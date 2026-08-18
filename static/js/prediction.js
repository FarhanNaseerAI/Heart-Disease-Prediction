/* Clinical form validation, presets, loading choreography, AJAX predict */
(function () {
  const PRESETS = {
    notebook: {
      age: 63, sex: 1, cp: 3, trestbps: 145, chol: 233, fbs: 1,
      restecg: 0, thalach: 150, exang: 0, oldpeak: 2.3, slope: 0, ca: 0, thal: 1,
    },
    healthy: {
      age: 41, sex: 0, cp: 1, trestbps: 130, chol: 204, fbs: 0,
      restecg: 0, thalach: 172, exang: 0, oldpeak: 1.4, slope: 2, ca: 0, thal: 2,
    },
    cardiac: {
      age: 67, sex: 1, cp: 0, trestbps: 160, chol: 286, fbs: 0,
      restecg: 0, thalach: 108, exang: 1, oldpeak: 1.5, slope: 1, ca: 3, thal: 3,
    },
  };

  const RULES = {
    age: { min: 1, max: 120, type: "int", label: "Age" },
    sex: { allowed: [0, 1], type: "int", label: "Gender" },
    cp: { allowed: [0, 1, 2, 3], type: "int", label: "Chest Pain Type" },
    trestbps: { min: 80, max: 250, type: "float", label: "Blood Pressure" },
    chol: { min: 100, max: 600, type: "float", label: "Cholesterol" },
    fbs: { allowed: [0, 1], type: "int", label: "Fasting Blood Sugar" },
    restecg: { allowed: [0, 1, 2], type: "int", label: "Resting ECG" },
    thalach: { min: 60, max: 220, type: "float", label: "Maximum Heart Rate" },
    exang: { allowed: [0, 1], type: "int", label: "Exercise Angina" },
    oldpeak: { min: 0, max: 10, type: "float", label: "Oldpeak" },
    slope: { allowed: [0, 1, 2], type: "int", label: "ST Slope" },
    ca: { allowed: [0, 1, 2, 3, 4], type: "int", label: "Major Vessels" },
    thal: { allowed: [0, 1, 2, 3], type: "int", label: "Thalassemia" },
  };

  const LOADING_STEPS = [
    { text: "Analyzing Patient Data...", detail: "Validating clinical inputs", progress: 12 },
    { text: "Extracting Clinical Features...", detail: "Building feature vector in notebook order", progress: 32 },
    { text: "Running Machine Learning Model...", detail: "Random Forest inference (unscaled)", progress: 58 },
    { text: "Calculating Risk...", detail: "Estimating class probabilities", progress: 78 },
    { text: "Generating Medical Report...", detail: "Assembling recommendations & explanations", progress: 92 },
    { text: "Prediction Complete.", detail: "Preparing dashboard", progress: 100 },
  ];

  function setFieldValue(name, value) {
    const el = document.getElementById(name);
    const range = document.getElementById(`${name}-range`);
    if (el) el.value = value;
    if (range) range.value = value;
  }

  function fillPreset(key) {
    const data = PRESETS[key];
    if (!data) return;
    Object.keys(data).forEach((k) => setFieldValue(k, data[k]));
    clearAllErrors();
  }

  function resetForm(form) {
    form.reset();
    ["age", "trestbps", "chol", "thalach", "oldpeak"].forEach((name) => {
      const num = document.getElementById(name);
      const range = document.getElementById(`${name}-range`);
      if (num && range) range.value = num.value || range.defaultValue || range.min;
    });
    clearAllErrors();
  }

  function syncRanges() {
    const pairs = [
      ["age-range", "age"],
      ["trestbps-range", "trestbps"],
      ["chol-range", "chol"],
      ["thalach-range", "thalach"],
      ["oldpeak-range", "oldpeak"],
    ];
    pairs.forEach(([rangeId, numId]) => {
      const rangeEl = document.getElementById(rangeId);
      const numEl = document.getElementById(numId);
      if (!rangeEl || !numEl) return;
      rangeEl.addEventListener("input", () => {
        numEl.value = rangeEl.value;
        validateField(numId);
      });
      numEl.addEventListener("input", () => {
        if (numEl.value !== "") rangeEl.value = numEl.value;
        validateField(numId);
      });
    });
  }

  function showError(name, message) {
    const field = document.getElementById(name)?.closest(".field");
    const err = document.getElementById(`${name}-error`);
    if (field) field.classList.add("is-invalid");
    if (err) err.textContent = message;
  }

  function clearError(name) {
    const field = document.getElementById(name)?.closest(".field");
    const err = document.getElementById(`${name}-error`);
    if (field) field.classList.remove("is-invalid");
    if (err) err.textContent = "";
  }

  function clearAllErrors() {
    Object.keys(RULES).forEach(clearError);
  }

  function validateField(name) {
    const rule = RULES[name];
    const el = document.getElementById(name);
    if (!rule || !el) return true;

    if (el.value === "" || el.value === null) {
      showError(name, `${rule.label} is required.`);
      return false;
    }

    const raw = el.value;
    const val = rule.type === "int" ? parseInt(raw, 10) : parseFloat(raw);
    if (Number.isNaN(val)) {
      showError(name, `${rule.label} must be a valid number.`);
      return false;
    }
    if (rule.min != null && val < rule.min) {
      showError(name, `${rule.label} cannot be less than ${rule.min}.`);
      return false;
    }
    if (rule.max != null && val > rule.max) {
      showError(name, `${rule.label} cannot exceed ${rule.max}.`);
      return false;
    }
    if (rule.allowed && !rule.allowed.includes(val)) {
      showError(name, `Invalid selection for ${rule.label}.`);
      return false;
    }
    clearError(name);
    return true;
  }

  function validateForm() {
    let ok = true;
    Object.keys(RULES).forEach((name) => {
      if (!validateField(name)) ok = false;
    });
    return ok;
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function runLoadingSequence() {
    const overlay = document.getElementById("loading-overlay");
    const title = document.getElementById("loading-title");
    const detail = document.getElementById("loading-step-text");
    const fill = document.getElementById("progress-bar-fill");
    if (!overlay) return;

    overlay.hidden = false;
    overlay.classList.add("active");
    document.body.style.overflow = "hidden";

    for (const step of LOADING_STEPS) {
      if (title) title.textContent = step.text;
      if (detail) detail.textContent = step.detail;
      if (fill) fill.style.width = `${step.progress}%`;
      await sleep(520);
    }
  }

  function hideLoading() {
    const overlay = document.getElementById("loading-overlay");
    if (!overlay) return;
    overlay.classList.remove("active");
    overlay.hidden = true;
    document.body.style.overflow = "";
    const fill = document.getElementById("progress-bar-fill");
    if (fill) fill.style.width = "0%";
  }

  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("prediction-form");
    if (!form) return;

    syncRanges();

    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => fillPreset(btn.getAttribute("data-preset")));
    });

    const resetBtn = document.getElementById("reset-form-btn");
    if (resetBtn) resetBtn.addEventListener("click", () => resetForm(form));

    Object.keys(RULES).forEach((name) => {
      const el = document.getElementById(name);
      if (el) {
        el.addEventListener("change", () => validateField(name));
        el.addEventListener("blur", () => validateField(name));
      }
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!validateForm()) {
        const firstInvalid = form.querySelector(".field.is-invalid");
        if (firstInvalid) firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }

      const loadingPromise = runLoadingSequence();
      const formData = new FormData(form);

      try {
        const response = await fetch(form.action || "/predict", {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await response.json();
        await loadingPromise;

        if (data.success) {
          window.location.href = "/result";
          return;
        }

        hideLoading();
        if (Array.isArray(data.errors)) {
          data.errors.forEach((msg) => {
            // Map common labels back to fields when possible
            const entry = Object.entries(RULES).find(([, r]) => msg.toLowerCase().includes(r.label.toLowerCase()));
            if (entry) showError(entry[0], msg);
          });
          alert(data.errors.join("\n"));
        } else {
          alert("Prediction failed. Please review your inputs.");
        }
      } catch (err) {
        await loadingPromise;
        hideLoading();
        console.error(err);
        form.submit();
      }
    });
  });
})();
