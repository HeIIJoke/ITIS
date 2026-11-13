

let teachersAbort = null;

export async function initListTeachers() {
  const container = document.getElementById("teachers-list");
  const status = document.getElementById("teachers-status");
  if (!container) return;

  if (teachersAbort) teachersAbort.abort();
  teachersAbort = new AbortController();
  const { signal } = teachersAbort;

  if (status) status.textContent = "Загрузка...";
  container.innerHTML = "";

  try {
    const res = await fetch("/api/teachers", {
      headers: { Accept: "application/json" },
      signal,
    });
    if (!res.ok) throw new Error("HTTP " + res.status);

    const teachers = await res.json();
    if (!Array.isArray(teachers)) throw new Error("Некорректный ответ сервера");

    if (!teachers.length) {
      if (status) status.textContent = "Пока нет преподавателей.";
      return;
    }

    if (status) status.textContent = "";
    container.innerHTML = teachers.map(renderCard).join("");
  } catch (err) {
    if (err.name === "AbortError") return;
    console.error(err);
    if (status) status.textContent = "Ошибка загрузки: " + err.message;
  }
}

function renderCard(t) {
  const fio = [t.last_name, t.first_name, t.middle_name]
    .filter(Boolean)
    .join(" ");
  const id = encodeURIComponent(t.id);
  
  const photoHtml = t.image_url 
    ? `<img src="${escapeHtml(t.image_url)}" alt="${escapeHtml(fio)}" class="teacher-avatar">` 
    : `<div class="teacher-avatar" style="background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #64748b;">👤</div>`;

  return `
    <div class="teacher-card">
      <div>
        ${photoHtml}
        <h3 style="margin: 10px 0 5px 0; font-size: 1.15rem;">${escapeHtml(fio)}</h3>
      </div>
      <div style="margin-top: 15px;">
        <a href="/teachers/${id}" data-link class="btn" style="display: inline-block; text-decoration: none; text-align: center;">Подробнее →</a>
      </div>
    </div>
  `;
}


function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}