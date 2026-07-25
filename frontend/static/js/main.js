/* Shared helpers used across every page: token storage, authenticated
   fetch wrapper, and navbar state. */

const HFE = (() => {
  const TOKEN_KEY = "hfe_token";
  const USER_KEY = "hfe_user";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user || {}));
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || "{}");
    } catch {
      return {};
    }
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function isAuthed() {
    return !!getToken();
  }

  async function apiFetch(path, options = {}) {
    const token = getToken();
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      options.headers || {}
    );
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(path, { ...options, headers });
    let body = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    if (res.status === 401 || res.status === 422) {
      clearSession();
      if (!location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    if (!res.ok) {
      const message = (body && body.error) || `Request failed (${res.status})`;
      throw new Error(message);
    }
    return body;
  }

  function requireAuth() {
    if (!isAuthed()) {
      window.location.href = "/login";
    }
  }

  function riskColor(label) {
    return { Low: "#1ea672", Moderate: "#e8a23d", High: "#d9584b" }[label] || "#5b7480";
  }

  return { getToken, setSession, getUser, clearSession, isAuthed, apiFetch, requireAuth, riskColor };
})();

document.addEventListener("DOMContentLoaded", () => {
  const guestNav = document.getElementById("nav-auth-guest");
  const userNav = document.getElementById("nav-auth-user");
  const dashLink = document.getElementById("nav-dashboard-link");

  if (HFE.isAuthed()) {
    if (guestNav) guestNav.style.display = "none";
    if (userNav) userNav.style.display = "inline-flex";
    if (dashLink) dashLink.style.display = "list-item";
  }

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      HFE.clearSession();
      window.location.href = "/";
    });
  }
});
