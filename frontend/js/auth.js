let accessToken = null;
let canRefresh = true;
let refreshRequest = null;
let sessionVersion = 0;

function updateSession(token) {
  accessToken = token;
  canRefresh = Boolean(token);
  sessionVersion++;
}

function refreshAccessToken() {
  if (!canRefresh) return Promise.resolve(null);
  if (refreshRequest) return refreshRequest;

  const version = sessionVersion;
  refreshRequest = (async () => {
    const response = await fetch("/api/auth/refresh", { method: "POST" });
    const data = response.ok ? await response.json() : null;
    if (version !== sessionVersion) return accessToken;

    if (response.status === 401) {
      updateSession(null);
      return null;
    }
    if (!response.ok) throw new Error("Не удалось обновить сеанс.");
    accessToken = data.access_token;
    return accessToken;
  })().finally(() => {
    refreshRequest = null;
  });
  return refreshRequest;
}

function sessionId(token) {
  const payload = token.split(".")[1].replaceAll("-", "+").replaceAll("_", "/");
  return JSON.parse(atob(payload)).sid;
}

export async function authenticatedFetch(url, options = {}) {
  const token = accessToken || await refreshAccessToken();
  const request = (bearerToken) => {
    const headers = new Headers(options.headers);
    if (bearerToken) headers.set("Authorization", `Bearer ${bearerToken}`);
    return fetch(url, { ...options, headers });
  };

  const response = await request(token);
  if (response.status !== 401 || !token) return response;

  const renewed = accessToken === token ? await refreshAccessToken() : accessToken;
  return renewed && sessionId(renewed) === sessionId(token) ? request(renewed) : response;
}

export async function readAccount() {
  if (!accessToken && !canRefresh) return null;
  const response = await authenticatedFetch("/api/auth/me");
  if (response.status === 401) return null;
  if (!response.ok) throw new Error("Не удалось загрузить данные аккаунта.");
  return response.json();
}

export async function readError(response, fallback) {
  const body = await response.json().catch(() => null);
  if (typeof body?.detail === "string") return body.detail;
  if (response.status === 422) return "Проверьте введённые данные.";
  return fallback;
}

export async function submitCredentials(credentials) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (!response.ok) throw new Error(await readError(response, "Не удалось отправить форму."));

  const data = await response.json();
  updateSession(data.access_token);
}

export async function signOut() {
  const headers = accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined;
  const response = await fetch("/api/auth/logout", { method: "POST", headers });
  if (!response.ok) throw new Error(await readError(response, "Не удалось выйти из системы."));
  updateSession(null);
}
