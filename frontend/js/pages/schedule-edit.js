import { getGroupFromUrl, setGroupInUrl, goToSchedule } from "./schedule-nav.js";

export async function initScheduleEditPage() {
    const groupSelect = document.getElementById("edit-group");
    const scheduleBody = document.getElementById("edit-body");
    const addRowBtn = document.getElementById("add-row-btn");
    const saveBtn = document.getElementById("save-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    const saveStatus = document.getElementById("save-status");
    const backLink = document.getElementById("back-link");

    const DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
    const WEEKS = [
        { value: "all",  label: "Каждая неделя" },
        { value: "odd",  label: "Числитель" },
        { value: "even", label: "Знаменатель" }
    ];
    const LESSON_TYPES = ["", "Лекция", "Практика", "Лабораторная", "Семинар"];

    let groups = [];
    let teachers = [];
    let subjects = [];
    let classTimes = [];
    let isDirty = false;
    let isSaving = false;
    let lastGroupId = "";
    let statusTimer = null;

    if (!scheduleBody) return;

    await loadGroups();
    await loadTeachers();
    await loadSubjects();
    await loadClassTimes();

    /* ---------- ОБРАБОТЧИКИ КНОПОК ---------- */

    // Кнопка "+ Добавить занятие"
    if (addRowBtn) {
        addRowBtn.addEventListener("click", () => {
            if (
                scheduleBody.firstElementChild &&
                scheduleBody.firstElementChild.querySelector(".empty")
            ) {
                scheduleBody.replaceChildren();
            }

            const row = createEditRow(null);
            row.classList.add("is-new");
            scheduleBody.appendChild(row);
            setDirty(true);
            row.querySelector(".inp-subject")?.focus();

            // прокрутить к новой строке
            row.scrollIntoView({ behavior: "smooth", block: "nearest" });
        });
    }

    // Кнопка "Сохранить"
    if (saveBtn) {
        saveBtn.addEventListener("click", async () => {
            if (isSaving) return;
            await saveSchedule();
        });
    }

    // Кнопка "Отмена"
    if (cancelBtn) {
        cancelBtn.addEventListener("click", async () => {
            if (isDirty && !confirm("Отменить несохранённые изменения?")) return;

            resetForm();
            await loadSchedules();
        });
    }

    // Кнопка "← К расписанию" (открывать в новой вкладке через Ctrl/Cmd)
    if (backLink) {
        backLink.addEventListener("click", (event) => {
            if (event.ctrlKey || event.metaKey || event.shiftKey || event.button === 1) {
                return;
            }
            if (isDirty && !confirm("Уйти со страницы? Несохранённые изменения будут потеряны.")) {
                event.preventDefault();
                return;
            }

            event.preventDefault();
            goToSchedule(groupSelect ? groupSelect.value : getGroupFromUrl());
        });
    }

    // Смена группы
    if (groupSelect) {
        lastGroupId = groupSelect.value;

        groupSelect.addEventListener("change", async () => {
            if (isDirty) {
                const ok = confirm("Переключить группу? Несохранённые изменения будут потеряны.");
                if (!ok) {
                    groupSelect.value = lastGroupId;
                    return;
                }
            }

            lastGroupId = groupSelect.value;
            setGroupInUrl(groupSelect.value);

            resetForm();
            await loadSchedules();
        });
    }

    // Отслеживание изменений в таблице (любая правка → dirty)
    scheduleBody.addEventListener("input", () => setDirty(true));
    scheduleBody.addEventListener("change", () => setDirty(true));

    // Ctrl+S / Cmd+S — сохранить
    document.addEventListener("keydown", (event) => {
        const mod = event.ctrlKey || event.metaKey;

        if (mod && event.key.toLowerCase() === "s") {
            event.preventDefault();
            saveSchedule();
        } else if (mod && event.key === "Enter") {
            // Ctrl+Enter — добавить строку
            event.preventDefault();
            addRowBtn?.click();
        }
    });

    // Предупреждение при закрытии/уходе со страницы с несохранёнными изменениями
    window.addEventListener("beforeunload", (event) => {
        if (!isDirty) return;
        event.preventDefault();
        event.returnValue = "";
    });

    await loadSchedules();

    /* ---------- ЗАГРУЗКА СПРАВОЧНИКОВ ---------- */

    async function loadGroups() {
        try {
            const response = await fetch("/api/groups");
            if (!response.ok) throw new Error("Не удалось загрузить группы");

            groups = await response.json();
            if (!groupSelect) return;

            groups.forEach((group) => {
                const option = document.createElement("option");
                option.value = group.id;
                option.textContent = group.name;
                groupSelect.appendChild(option);
            });

            const groupFromUrl = getGroupFromUrl();
            if (groupFromUrl && groups.some((g) => String(g.id) === groupFromUrl)) {
                groupSelect.value = groupFromUrl;
            } else if (groups.length) {
                setGroupInUrl(groupSelect.value);
            }
        } catch (error) {
            console.error("Ошибка загрузки групп:", error);
        }
    }

    async function loadTeachers() {
        try {
            const response = await fetch("/api/teachers");
            if (!response.ok) throw new Error("Не удалось загрузить преподавателей");
            teachers = await response.json();
        } catch (error) {
            console.error("Ошибка загрузки преподавателей:", error);
        }
    }

    async function loadSubjects() {
        try {
            const response = await fetch("/api/subjects");
            if (!response.ok) throw new Error("Не удалось загрузить предметы");
            subjects = await response.json();
        } catch (error) {
            console.error("Ошибка загрузки предметов:", error);
        }
    }

    async function loadClassTimes() {
        try {
            const response = await fetch("/api/class-times");
            if (!response.ok) throw new Error("Не удалось загрузить время пар");
            classTimes = await response.json();
        } catch (error) {
            console.error("Ошибка загрузки времени пар:", error);
        }
    }

    /* ---------- ЗАГРУЗКА И ОТРИСОВКА ТАБЛИЦЫ ---------- */

    async function loadSchedules() {
        if (!groupSelect || !groupSelect.value) {
            scheduleBody.textContent = "Выберите группу";
            return;
        }

        scheduleBody.textContent = "Загрузка расписания...";

        try {
            const params = new URLSearchParams();
            params.append("group_id", groupSelect.value);

            const response = await fetch(`/api/schedules?${params.toString()}`);
            if (!response.ok) throw new Error("Не удалось загрузить расписание");

            const schedules = await response.json();
            renderScheduleTable(schedules);
            setDirty(false);
        } catch (error) {
            console.error("Ошибка загрузки расписания:", error);
            scheduleBody.textContent = "Не удалось загрузить расписание.";
        }
    }

    function renderScheduleTable(schedules) {
        scheduleBody.replaceChildren();

        if (backLink && groupSelect) {
            backLink.href = buildViewHref(groupSelect.value);
        }

        if (!schedules.length) {
            appendEmptyRow("Занятий пока нет. Нажмите «+ Добавить занятие».");
            return;
        }

        schedules.forEach((lesson) => {
            scheduleBody.appendChild(createEditRow(lesson));
        });
    }

    function appendEmptyRow(text) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 8;
        cell.className = "empty";
        cell.textContent = text;
        row.appendChild(cell);
        scheduleBody.appendChild(row);
    }

    function createEditRow(lesson) {
        lesson = lesson || {};

        const row = document.createElement("tr");
        if (lesson.id) row.dataset.id = lesson.id;

        // День недели
        const daySelect = document.createElement("select");
        daySelect.className = "inp-day";
        DAYS.forEach((day) => daySelect.add(new Option(day, day)));
        daySelect.value = lesson.day_of_week || DAYS[0];
        row.appendChild(wrapCell(daySelect));

        // Пара (время)
        const timeSelect = document.createElement("select");
        timeSelect.className = "inp-time";
        classTimes.forEach((time) => {
            timeSelect.add(new Option(formatTime(time), time.id));
        });
        if (lesson.class_time_id) timeSelect.value = String(lesson.class_time_id);
        row.appendChild(wrapCell(timeSelect));

        // Неделя
        const weekSelect = document.createElement("select");
        weekSelect.className = "inp-week";
        WEEKS.forEach((week) => weekSelect.add(new Option(week.label, week.value)));
        weekSelect.value = lesson.week_type || "all";
        row.appendChild(wrapCell(weekSelect));

        // Предмет
        const subjectSelect = document.createElement("select");
        subjectSelect.className = "inp-subject";
        subjectSelect.add(new Option("— предмет —", ""));
        subjects.forEach((subject) => {
            const label = subject.name +
                (subject.semester ? ` (${subject.semester} сем.)` : "");
            subjectSelect.add(new Option(label, subject.id));
        });
        if (lesson.subject_id) subjectSelect.value = String(lesson.subject_id);
        row.appendChild(wrapCell(subjectSelect));

        // Преподаватель
        const teacherSelect = document.createElement("select");
        teacherSelect.className = "inp-teacher";
        teacherSelect.add(new Option("— преподаватель —", ""));
        teachers.forEach((teacher) => {
            teacherSelect.add(new Option(formatTeacher(teacher), teacher.id));
        });
        if (lesson.teacher_id) teacherSelect.value = String(lesson.teacher_id);
        row.appendChild(wrapCell(teacherSelect));

        // Аудитория
        const roomInput = document.createElement("input");
        roomInput.type = "text";
        roomInput.className = "inp-room";
        roomInput.value = lesson.room || "";
        roomInput.placeholder = "ауд. 000";
        row.appendChild(wrapCell(roomInput));

        // Тип занятия
        const typeSelect = document.createElement("select");
        typeSelect.className = "inp-lesson-type";
        LESSON_TYPES.forEach((type) => {
            typeSelect.add(new Option(type || "—", type));
        });
        typeSelect.value = lesson.lesson_type || "";
        row.appendChild(wrapCell(typeSelect));

        // Кнопка "✕" — удалить строку
        const deleteCell = document.createElement("td");
        deleteCell.className = "actions-cell";

        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.className = "icon-btn del";
        deleteBtn.title = "Удалить занятие";
        deleteBtn.textContent = "✕";
        deleteBtn.addEventListener("click", () => {
            const subjectName =
                subjectSelect.options[subjectSelect.selectedIndex]?.text || "занятие";

            if (!confirm(`Удалить «${subjectName}»?`)) return;

            row.remove();
            setDirty(true);

            if (!scheduleBody.querySelector("tr")) {
                appendEmptyRow("Занятий пока нет.");
            }
        });

        deleteCell.appendChild(deleteBtn);
        row.appendChild(deleteCell);

        return row;
    }

    /* ---------- СОХРАНЕНИЕ ---------- */

    async function saveSchedule() {
        if (isSaving || !groupSelect) return;

        const rows = scheduleBody.querySelectorAll("tr");
        const lessons = [];
        const errors = [];

        rows.forEach((row, index) => {
            if (!row.querySelector("select")) return;

            const rowNumber = index + 1;
            const daySelect = row.querySelector(".inp-day");
            const timeSelect = row.querySelector(".inp-time");
            const weekSelect = row.querySelector(".inp-week");
            const subjectSelect = row.querySelector(".inp-subject");
            const teacherSelect = row.querySelector(".inp-teacher");
            const roomInput = row.querySelector(".inp-room");
            const typeSelect = row.querySelector(".inp-lesson-type");

            const subjectId = subjectSelect.value;
            const teacherId = teacherSelect.value;
            const timeId = timeSelect.value;
            const room = roomInput ? roomInput.value.trim() : "";

            if (!subjectId && !teacherId && !room) return;

            if (!subjectId) errors.push(`Строка ${rowNumber}: не выбран предмет`);
            if (!teacherId) errors.push(`Строка ${rowNumber}: не выбран преподаватель`);
            if (!timeId)    errors.push(`Строка ${rowNumber}: не выбрана пара`);

            lessons.push({
                id: row.dataset.id ? Number(row.dataset.id) : null,
                subject_id: Number(subjectId) || null,
                teacher_id: Number(teacherId) || null,
                class_time_id: Number(timeId) || null,
                day_of_week: daySelect.value,
                week_type: weekSelect.value,
                room: room || null,
                lesson_type: typeSelect ? typeSelect.value || null : null,
                notes: null
            });
        });

        if (errors.length) {
            alert("Проверьте данные:\n\n" + errors.join("\n"));
            return;
        }

        isSaving = true;
        setSaveButtonState("loading");

        try {
            const response = await fetch(
                `/api/schedules/save/${groupSelect.value}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ lessons })
                }
            );

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.error || "Не удалось сохранить расписание");
            }

            setDirty(false);
            showStatus("Сохранено ✓", "success");
            await loadSchedules();
        } catch (error) {
            console.error("Ошибка сохранения:", error);
            alert(error.message || "Ошибка соединения с сервером");
        } finally {
            isSaving = false;
            setSaveButtonState("idle");
        }
    }

    function setSaveButtonState(state) {
        if (!saveBtn) return;

        if (state === "loading") {
            saveBtn.disabled = true;
            saveBtn.dataset.originalText = saveBtn.textContent;
            saveBtn.textContent = "Сохранение…";
        } else {
            saveBtn.disabled = false;
            if (saveBtn.dataset.originalText) {
                saveBtn.textContent = saveBtn.dataset.originalText;
                delete saveBtn.dataset.originalText;
            }
        }
    }

    function resetForm() {
        setDirty(false);
        if (statusTimer) {
            clearTimeout(statusTimer);
            statusTimer = null;
        }
        if (saveStatus) {
            saveStatus.textContent = "";
            saveStatus.className = "save-status";
        }
    }

    /* ---------- ВСПОМОГАТЕЛЬНЫЕ ---------- */

    function wrapCell(element) {
        const cell = document.createElement("td");
        cell.appendChild(element);
        return cell;
    }

    function buildViewHref(groupId) {
        const params = new URLSearchParams();
        if (groupId) params.append("group", groupId);
        return `/schedule.html?${params.toString()}`;
    }

    function formatTeacher(teacher) {
        const initials =
            (teacher.first_name ? teacher.first_name[0] + "." : "") +
            (teacher.middle_name ? teacher.middle_name[0] + "." : "");
        return (teacher.last_name + " " + initials).trim();
    }

    function formatTime(classTime) {
        return classTime.start_time.slice(0, 5) + " – " + classTime.end_time.slice(0, 5);
    }

    function setDirty(value) {
        if (isDirty === value) return;
        isDirty = value;
        if (!saveStatus) return;

        if (isDirty) {
            saveStatus.textContent = "● Есть несохранённые изменения";
            saveStatus.className = "save-status save-status--dirty";
        } else {
            saveStatus.textContent = "";
            saveStatus.className = "save-status";
        }
    }

    function showStatus(text, type) {
        if (!saveStatus) return;
        if (statusTimer) clearTimeout(statusTimer);

        saveStatus.textContent = text;
        saveStatus.className = "save-status save-status--" + type;

        statusTimer = setTimeout(() => {
            statusTimer = null;
            setDirty(isDirty);
        }, 2500);
    }
}