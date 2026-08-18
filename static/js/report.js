/* Result dashboard: gauge animation, copy, print, PDF export */
(function () {
  function animateGauge() {
    const circle = document.getElementById("gauge-progress-circle");
    if (!circle) return;
    const percentage = parseFloat(circle.getAttribute("data-percentage") || "0");
    const radius = 80;
    const circumference = 2 * Math.PI * radius;
    circle.style.strokeDasharray = String(circumference);
    circle.style.strokeDashoffset = String(circumference);
    requestAnimationFrame(() => {
      const offset = circumference - (Math.min(Math.max(percentage, 0), 100) / 100) * circumference;
      circle.style.strokeDashoffset = String(offset);
    });
  }

  function buildReportText() {
    const root = document.getElementById("report-content");
    if (!root) return "";
    const title = document.querySelector(".result-toolbar h1")?.textContent || "HeartVision AI Report";
    const lines = [title, ""];
    root.querySelectorAll("h2, h3, h4, p, li, .metric").forEach((node) => {
      const text = node.textContent.replace(/\s+/g, " ").trim();
      if (text) lines.push(text);
    });
    return lines.join("\n");
  }

  async function copyReport() {
    const text = buildReportText();
    try {
      await navigator.clipboard.writeText(text);
      alert("Report copied to clipboard.");
    } catch (e) {
      const area = document.createElement("textarea");
      area.value = text;
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
      alert("Report copied to clipboard.");
    }
  }

  function exportPdf() {
    // Use native print-to-PDF for zero-dependency, high-fidelity clinical output
    window.print();
  }

  document.addEventListener("DOMContentLoaded", () => {
    animateGauge();

    const copyBtn = document.getElementById("copy-report-btn");
    const printBtn = document.getElementById("print-report-btn");
    const pdfBtn = document.getElementById("export-pdf-btn");

    if (copyBtn) copyBtn.addEventListener("click", copyReport);
    if (printBtn) printBtn.addEventListener("click", () => window.print());
    if (pdfBtn) pdfBtn.addEventListener("click", exportPdf);
  });
})();
