/**
 * Навигация между страницами расписания.
 * Все переходы сохраняют выбранную группу в query-строке,
 * чтобы при возврате назад пользователь увидел ту же группу.
 */

const ROUTES = {
    view: "/schedule.html",
    edit: "/schedule-edit.html"
};

export function getGroupFromUrl() {
    return new URLSearchParams(window.location.search).get("group");
}

export function setGroupInUrl(groupId) {
    const url = new URL(window.location.href);

    if (groupId) {
        url.searchParams.set("group", groupId);
    } else {
        url.searchParams.delete("group");
    }

    window.history.replaceState({}, "", url.toString());
}

export function buildScheduleUrl(groupId, page = "view") {
    const base = ROUTES[page] || ROUTES.view;
    if (!groupId) return base;

    const params = new URLSearchParams();
    params.append("group", groupId);

    return `${base}?${params.toString()}`;
}

/**
 * Переход на страницу просмотра расписания.
 * @param {string|number} [groupId]
 * @param {{ replace?: boolean }} [options] — replace:true заменит историю
 */
export function goToSchedule(groupId, options = {}) {
    const url = buildScheduleUrl(groupId, "view");

    if (options.replace) {
        window.location.replace(url);
    } else {
        window.location.href = url;
    }
}

/**
 * Переход на страницу редактирования расписания.
 */
export function goToScheduleEdit(groupId, options = {}) {
    const url = buildScheduleUrl(groupId, "edit");

    if (options.replace) {
        window.location.replace(url);
    } else {
        window.location.href = url;
    }
}