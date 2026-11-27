import { getGroupFromUrl, setGroupInUrl, goToScheduleEdit } from "./schedule-nav.js";

export async function initSchedulePage() {
    const groupSelect = document.getElementById("schedule-group");
    const weekButtons = document.querySelectorAll(".week-btn");
    const scheduleBody = document.getElementById("schedule-body");
    const scheduleInfo = document.getElementById("schedule-info");
    const editLink = document.getElementById("edit-link");

    const DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
    const WEEK_LABEL = { odd: "числ.", even: "знам." };
    const WEEK_STORAGE_KEY = "scheduleView.week";

    let currentWeek = loadSavedWeek();
    let groups = [];
    let classTimes = [];

    if (!scheduleBody) return;

    // Восстановить активную кнопку недели из сохранённого значения
    weekButtons.forEach((btn) => {
        btn.classList.toggle("is-active", btn.dataset.week === currentWeek);
    });

    await loadGroups();
    await loadClassTimes();

    /* ---------- ОБРАБОТЧИКИ КНОПОК ---------- */

    // Переключение недели
    weekButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const nextWeek = btn.dataset.week;
            if (nextWeek === currentWeek) return;

            currentWeek = nextWeek;
            saveWeek(currentWeek);

            weekButtons.forEach((b) => {
                b.classList.toggle("is-active", b === btn);
            });

            loadSchedules();
        });
    });

    // Смена группы
    if (groupSelect) {
        groupSelect.addEventListener("change", () => {
            setGroupInUrl(groupSelect.value);
            loadSchedules();
        });
    }

    // Кнопка "Редактировать расписание"
    if (editLink) {
        editLink.addEventListener("click", (event) => {
            // Позволяем открыть в новой вкладке через Ctrl/Cmd/Shift/среднюю кнопку
            if (event.ctrlKey || event.metaKey || event.shiftKey || event.button === 1) {
                return;
            }

            event.preventDefault();
            goToScheduleEdit(groupSelect ? groupSelect.value : getGroupFromUrl());
        });
    }

    // Горячие клавиши: 1 — числитель, 2 — знаменатель, E — редактировать
    document.addEventListener("keydown", (event) => {
        if (event.target.matches("input, textarea, select")) return;

        if (event.key === "1") {
            document.querySelector('.week-btn[data-week="odd"]')?.click();
        } else if (event.key === "2") {
            document.querySelector('.week-btn[data-week="even"]')?.click();
        } else if (event.key.toLowerCase() === "e" && !event.ctrlKey && !event.metaKey) {
            goToScheduleEdit(groupSelect ? groupSelect.value : getGroupFromUrl());
        }
    });

    /* ---------- ЗАГРУЗКА ДАННЫХ ---------- */

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
                // по умолчанию первая группа в URL
                setGroupInUrl(groupSelect.value);
            }
        } catch (error) {
            console.error("Ошибка загрузки групп:", error);
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
            renderSchedule(schedules);
        } catch (error) {
            console.error("Ошибка загрузки расписания:", error);
            scheduleBody.textContent = "Не удалось загрузить расписание.";
        }
    }

    function renderSchedule(schedules) {
        scheduleBody.replaceChildren();

        classTimes.forEach((time) => {
            const row = document.createElement("tr");

            const timeCell = document.createElement("td");
            timeCell.className = "time-col";
            timeCell.textContent = formatTime(time);
            row.appendChild(timeCell);

            DAYS.forEach((day) => {
                const cell = document.createElement("td");

                const lessons = schedules.filter(
                    (item) =>
                        item.day_of_week === day &&
                        item.class_time_id === time.id &&
                        (item.week_type === "all" || item.week_type === currentWeek)
                );

                if (!lessons.length) {
                    const empty = document.createElement("span");
                    empty.className = "empty";
                    empty.textContent = "—";
                    cell.appendChild(empty);
                } else {
                    lessons.forEach((lesson) => {
                        cell.appendChild(createLessonCard(lesson));
                    });
                }

                row.appendChild(cell);
            });

            scheduleBody.appendChild(row);
        });

        if (scheduleInfo) {
            const group = groups.find((g) => String(g.id) === String(groupSelect.value));
            scheduleInfo.innerHTML =
                "Расписание для группы: <strong>" +
                escapeHtml(group ? group.name : "—") +
                "</strong>, неделя: <strong>" +
                (currentWeek === "odd" ? "числитель" : "знаменатель") +
                "</strong>";
        }

        if (editLink) {
            editLink.href = buildEditHref(groupSelect.value);
        }
    }

    function buildEditHref(groupId) {
        const params = new URLSearchParams();
        if (groupId) params.append("group", groupId);
        return `/schedule-edit.html?${params.toString()}`;
    }

    function createLessonCard(lesson) {
        const card = document.createElement("div");
        card.className = "lesson lesson--" + (lesson.week_type || "all");

        const head = document.createElement("div");
        head.className = "lesson-head";

        const subject = document.createElement("span");
        subject.className = "subject";
        subject.textContent = lesson.subject_name || "—";
        head.appendChild(subject);

        if (lesson.week_type !== "all" && WEEK_LABEL[lesson.week_type]) {
            const badge = document.createElement("span");
            badge.className = "week-badge week-badge--" + lesson.week_type;
            badge.textContent = WEEK_LABEL[lesson.week_type];
            head.appendChild(badge);
        }

        card.appendChild(head);

        if (lesson.teacher_name) {
            const teacher = document.createElement("span");
            teacher.className = "teacher";
            teacher.textContent = lesson.teacher_name;
            card.appendChild(teacher);
        }

        if (lesson.room) {
            const room = document.createElement("span");
            room.className = "room";
            room.textContent = lesson.room;
            card.appendChild(room);
        }

        if (lesson.lesson_type) {
            const type = document.createElement("span");
            type.className = "lesson-type";
            type.textContent = lesson.lesson_type;
            card.appendChild(type);
        }

        return card;
    }

    function formatTime(classTime) {
        return classTime.start_time.slice(0, 5) + " – " + classTime.end_time.slice(0, 5);
    }

    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
        }[c]));
    }

    function loadSavedWeek() {
        try {
            return sessionStorage.getItem(WEEK_STORAGE_KEY) || "odd";
        } catch {
            return "odd";
        }
    }

    function saveWeek(week) {
        try {
            sessionStorage.setItem(WEEK_STORAGE_KEY, week);
        } catch {
            /* ignore */
        }
    }
}