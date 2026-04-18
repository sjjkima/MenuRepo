(function () {
  window.TABLEORDER_API_BASE = window.TABLEORDER_API_BASE || "https://menurepo.onrender.com";

  const isLocalFrontend =
    ["localhost", "127.0.0.1"].includes(window.location.hostname) &&
    window.location.port === "8080";

  const configuredApiBase = window.API_BASE || window.TABLEORDER_API_BASE;

  const defaultApiBase = isLocalFrontend
    ? "http://127.0.0.1:8000"
    : configuredApiBase || "https://your-render-backend.onrender.com";

  window.API_BASE = configuredApiBase || defaultApiBase;
})();
