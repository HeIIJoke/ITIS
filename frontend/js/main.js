/**
 * main.js — общая логика, не привязанная к конкретной странице.
 *
 * Здесь единственное место, где фронтенд общается с бэкендом: apiGet().
 * Появится авторизация или базовый URL — правим только этот файл.
 */

const API_PREFIX = "/api";

/**
 * GET-запрос к API с единой обработкой ошибок.
 * @param {string} path путь без префикса, например "/department"
 * @returns {Promise<any>} разобранный JSON
 */
async function apiGet(path) {
  const response = await fetch(`${API_PREFIX}${path}`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`API ${path}: HTTP ${response.status}`);
  }

  return response.json();
}

