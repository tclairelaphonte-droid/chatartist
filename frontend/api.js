const API_BASE =
  location.hostname === "localhost" || location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://chatartist-backastage.vercel.app";

const AUTH_BASE = API_BASE + "/api/auth";

function getToken() {
  return localStorage.getItem("backstage_token");
}

function authHeaders() {
  const headers = {
    "Content-Type": "application/json",
  };

  const token = getToken();

  if (token) {
    headers.Authorization = "Bearer " + token;
  }

  // Admin qui consulte le dashboard d'un manager client
  const actAs = sessionStorage.getItem("backstage_act_as_manager");

  if (actAs) {
    headers["X-Act-As-Manager"] = actAs;
  }

  return headers;
}

async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();

  const headers = {
    ...authHeaders(),
    ...(options.headers || {}),
  };

  if (!options.body) {
    delete headers["Content-Type"];
  }

  const res = await fetch(API_BASE + path, {
    ...options,
    method,
    headers,
  });

  if (res.status === 204) {
    return null;
  }

  let data = null;

  try {
    data = await res.json();
  } catch (_) {
    data = {};
  }

  if (!res.ok) {
    const detail = data.detail;
    let message = "Erreur " + res.status;

    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail
        .map(function (d) {
          return d.msg || JSON.stringify(d);
        })
        .join(", ");
    }

    throw new Error(message);
  }

  return data;
}

async function apiAuth(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();

  const headers = {
    ...authHeaders(),
    ...(options.headers || {}),
  };

  if (!options.body) {
    delete headers["Content-Type"];
  }

  const res = await fetch(AUTH_BASE + path, {
    ...options,
    method,
    headers,
  });

  if (res.status === 204) {
    return null;
  }

  let data = null;

  try {
    data = await res.json();
  } catch (_) {
    data = {};
  }

  if (!res.ok) {
    const detail = data.detail;
    let message = "Erreur " + res.status;

    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail
        .map(function (d) {
          return d.msg || JSON.stringify(d);
        })
        .join(", ");
    }

    throw new Error(message);
  }

  return data;
}

function logout() {
  [
    "backstage_token",
    "backstage_username",
    "backstage_email",
    "backstage_role",
  ].forEach(function (key) {
    localStorage.removeItem(key);
  });

  sessionStorage.removeItem("backstage_act_as_manager");
  sessionStorage.removeItem("backstage_act_as_label");

  location.href = "login.html";
}

function requireAuth(role) {
  const token = getToken();

  if (!token) {
    const next = encodeURIComponent(
      location.pathname.split("/").pop() + location.search
    );

    location.replace("login.html?next=" + next);
    return false;
  }

  if (role) {
    const currentRole = localStorage.getItem("backstage_role");

    if (role === "manager") {
      if (currentRole !== "manager" && currentRole !== "admin") {
        location.replace("login.html");
        return false;
      }
    } else if (currentRole !== role) {
      location.replace(role === "admin" ? "login.html" : "index.html");
      return false;
    }
  }

  return true;
}