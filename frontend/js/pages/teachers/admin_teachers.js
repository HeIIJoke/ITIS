const ADMIN_AUTH = "Basic " + btoa("admin:admin123");

let adminInitialized = false;

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function formatDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => `${(e.loc || []).join(".")}: ${e.msg}`).join("; ");
  }
  return JSON.stringify(detail);
}

async function loadPositions() {
  const select = document.getElementById("select-position");
  if (!select) return;

  try {
    const res = await fetch("/api/teachers/positions", {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) throw new Error("HTTP " + res.status);

    const items = await res.json();
    for (const it of items) {
      const opt = document.createElement("option");
      opt.value = String(it.id);
      opt.textContent = it.name;
      select.appendChild(opt);
    }
  } catch (err) {
    console.error("[admin] refs positions:", err);
    select.disabled = true;
    select.innerHTML = '<option value="">Не удалось загрузить</option>';
  }
}

let teachersCache = [];

export async function initAdminTeachers() {
  const form = document.getElementById("add-teacher-form");
  const list = document.getElementById("admin-list");
  const status = document.getElementById("form-status");
  const submitBtn = document.getElementById("submit-btn");
  const cancelBtn = document.getElementById("cancel-edit-btn");
  const teacherIdInput = document.getElementById("teacher-id");

  if (!form || !list) return;

  if (adminInitialized) {
    await refreshList();
    return;
  }
  adminInitialized = true;

  await Promise.all([loadPositions(), refreshList()]);

  function resetFormMode() {
    form.reset();
    if (teacherIdInput) teacherIdInput.value = "";
    if (submitBtn) submitBtn.textContent = "Добавить";
    if (cancelBtn) cancelBtn.style.display = "none";
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      resetFormMode();
      if (status) {
        status.textContent = "";
        status.style.color = "";
      }
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fd = new FormData(form);
    const inputEmail = fd.get("email");
    const editingId = teacherIdInput ? teacherIdInput.value : "";
    const isEditing = Boolean(editingId);

    if (inputEmail) {
      const emailExists = teachersCache.some(
        (t) => t.email && t.email.toLowerCase() === inputEmail.toLowerCase() && String(t.id) !== String(editingId)
      );

      if (emailExists) {
        if (status) {
          status.style.color = "red";
          status.textContent = "Ошибка: Преподаватель с таким email уже существует в системе!";
        }
        return;
      }
    }

    const positionVal = fd.get("position_id");
    if (!positionVal) {
      fd.delete("position_id");
    }

    if (status) {
      status.style.color = "";
      status.textContent = "Отправка...";
    }

    try {
      const url = isEditing ? `/api/teachers/${editingId}` : "/api/teachers";
      const method = isEditing ? "PATCH" : "POST";

      const res = await fetch(url, {
        method: method,
        headers: {
          "Accept": "application/json",
          "Authorization": ADMIN_AUTH,
        },
        body: fd,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const msg = err.detail ? formatDetail(err.detail) : `HTTP ${res.status}`;
        throw new Error(msg);
      }

      if (status) {
        status.style.color = "green";
        status.textContent = isEditing ? "Изменено ✅" : "Добавлено ✅";
      }
      resetFormMode();
      await refreshList();
    } catch (err) {
      console.error("[admin] submit error:", err);
      if (status) {
        status.style.color = "red";
        status.textContent = "Ошибка: " + err.message;
      }
    }
  });


  list.addEventListener("click", async (e) => {
    const target = e.target;
    const id = Number(target.dataset.id);

    if (!Number.isInteger(id) || id <= 0) return;

    if (target.classList.contains("delete-btn")) {
      if (!confirm("Удалить преподавателя?")) return;
      target.disabled = true;
      try {
        const res = await fetch(`/api/teachers/${id}`, {
          method: "DELETE",
          headers: { "Authorization": ADMIN_AUTH, Accept: "application/json" },
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        await refreshList();
      } catch (err) {
        console.error("[admin] delete:", err);
        alert("Ошибка удаления: " + err.message);
      } finally {
        target.disabled = false;
      }
    }

    if (target.classList.contains("edit-btn")) {
      const teacher = teachersCache.find((t) => t.id === id);
      if (!teacher) return;

      if (teacherIdInput) teacherIdInput.value = teacher.id;
      if (form.last_name) form.last_name.value = teacher.last_name || "";
      if (form.first_name) form.first_name.value = teacher.first_name || "";
      if (form.middle_name) form.middle_name.value = teacher.middle_name || "";
      if (form.email) form.email.value = teacher.email || "";
      if (form.phone) form.phone.value = teacher.phone || "";
      if (form.bio) form.bio.value = teacher.bio || "";
      if (form.image_url) form.image_url.value = teacher.image_url || "";
      if (form.hire_date) form.hire_date.value = teacher.hire_date || "";
      if (form.dismissal_date) form.dismissal_date.value = teacher.dismissal_date || ""; 
      
      if (teacher.degree !== undefined && form.degree) form.degree.value = teacher.degree;
      if (teacher.academic_title !== undefined && form.academic_title) form.academic_title.value = teacher.academic_title;
      if (teacher.position_id !== null && form.position_id) form.position_id.value = teacher.position_id;
      
      if (submitBtn) submitBtn.textContent = "Сохранить изменения";
      if (cancelBtn) cancelBtn.style.display = "inline-block";
      if (status) {
        status.textContent = "";
        status.style.color = "";
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });

  async function refreshList() {
    list.innerHTML = "<li>Загрузка...</li>";
    try {
      const res = await fetch("/api/teachers", {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      teachersCache = await res.json();
      if (!Array.isArray(teachersCache)) throw new Error("Некорректный ответ сервера");

      if (!teachersCache.length) {
        list.innerHTML = "<li>Пока пусто</li>";
        return;
      }

      list.innerHTML = teachersCache.map((t) => {
        const fio = [t.last_name, t.first_name, t.middle_name]
          .filter(Boolean)
          .join(" ");

        const safeId = String(t.id);

        return `<li style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
          <span>${escapeHtml(fio || "Без имени")}</span>
          <div>
            <button data-id="${escapeHtml(safeId)}" class="edit-btn" style="margin-right: 5px;">Редактировать</button>
            <button data-id="${escapeHtml(safeId)}" class="delete-btn">Удалить</button>
          </div>
        </li>`;
      }).join("");
    } catch (err) {
      console.error("[admin] list:", err);
      list.innerHTML = `<li>Ошибка загрузки: ${escapeHtml(err.message)}</li>`;
    }
  }
}

window.initAdminTeachers = initAdminTeachers;