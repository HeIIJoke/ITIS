export function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

let profileAbort = null;


function formatDegree(degree) {
  const map = { 1: "Кандидат наук", 2: "Доктор наук" };
  return map[degree] || "";
}

function formatTitle(title) {
  const map = { 1: "Доцент", 2: "Профессор" };
  return map[title] || "";
}

export async function initProfileTeacher(params) {
  const container = document.getElementById("profile-container");
  if (!container) return;

  const rawId = params?.id;
  const teacherId = Number(rawId);
  if (!rawId || !Number.isInteger(teacherId) || teacherId <= 0) {
    container.textContent = "Некорректный ID преподавателя.";
    return;
  }

  if (profileAbort) profileAbort.abort();
  profileAbort = new AbortController();
  const { signal } = profileAbort;

  container.textContent = "Загрузка...";

  try {
    const res = await fetch(`/api/teachers/${teacherId}`, {
      headers: { Accept: "application/json" },
      signal,
    });

    if (res.status === 404) {
      container.textContent = "Преподаватель не найден.";
      return;
    }
    if (!res.ok) throw new Error("HTTP " + res.status);

    const t = await res.json();
    if (!t || typeof t !== "object" || Array.isArray(t)) {
      throw new Error("Некорректный ответ сервера");
    }

    const fio = [t.last_name, t.first_name, t.middle_name]
      .filter(Boolean)
      .join(" ");

    const degreeText = formatDegree(t.degree);
    const titleText = formatTitle(t.academic_title);

    container.innerHTML = `
      <div class="teacher-profile" style="display: flex; gap: 20px; align-items: flex-start;">
        ${t.image_url ? `<img src="${escapeHtml(t.image_url)}" alt="${escapeHtml(fio)}" style="width: 150px; height: 180px; object-fit: cover; border-radius: 8px;">` : ""}
        
        <div>
          <h1>${escapeHtml(fio || "Без имени")}</h1>
          
          ${degreeText ? `<p><strong>Учёная степень:</strong> ${escapeHtml(degreeText)}</p>` : ""}
          ${titleText ? `<p><strong>Учёное звание:</strong> ${escapeHtml(titleText)}</p>` : ""}
          ${t.email ? `<p><strong>Email:</strong> <a href="mailto:${escapeHtml(t.email)}">${escapeHtml(t.email)}</a></p>` : ""}
          ${t.phone ? `<p><strong>Телефон:</strong> ${escapeHtml(t.phone)}</p>` : ""}
          ${t.hire_date ? `<p><strong>Дата приема на работу:</strong> ${escapeHtml(t.hire_date)}</p>` : ""}
        </div>
      </div>

      ${t.bio ? `<div style="margin-top: 20px;"><h3>Биография</h3><p>${escapeHtml(t.bio)}</p></div>` : ""}
    `;
  } catch (err) {
    if (err.name === "AbortError") return;
    console.error("[profile] ошибка:", err);
    container.textContent = "Не удалось загрузить профиль.";
  }
}