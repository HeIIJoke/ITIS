const routes = {
  "/": {
    title: "Главная",
    file: "/pages/home.html",
  },

  "/teachers": {
    title: "Преподаватели",
    file: "/pages/teacher/teacher_list.html",
  },

  "/news": {
    title: "Новости кафедры",
    file: "/pages/news.html",
  },
};

async function navigate(path) {
  const app = document.getElementById("app");
  const route = routes[path];

  if (!route) {
    app.innerHTML = "<h2>Страница не найдена</h2>";
    document.title = "Страница не найдена | Кафедра ВТИСиТ";
    return;
  }

  try {
    const response = await fetch(route.file);

    if (!response.ok) throw new Error(`Ошибка загрузки: ${response.status}`);

    app.innerHTML = await response.text();

    document.title = `${route.title} | Кафедра ВТИСиТ`;

    if (route.init) await route.init();
  } catch (error) {
    console.error(error);
    app.innerHTML = "<h2>Не удалось загрузить страницу</h2>";
  }
}

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-link]");

  if (
    !link ||
    event.ctrlKey ||
    event.metaKey ||
    event.shiftKey ||
    event.altKey ||
    event.button !== 0
  )
    return;

  const url = new URL(link.href);

  if (url.origin !== location.origin) return;

  event.preventDefault();

  if (url.pathname === location.pathname) return;

  history.pushState({}, "", url.pathname);
  navigate(url.pathname);
});

window.addEventListener("popstate", () => {
  navigate(location.pathname);
});

document.addEventListener("DOMContentLoaded", () => {
  navigate(location.pathname);
});
