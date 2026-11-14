//import { initHome }           from "./pages/home.js";
import { initListTeachers } from "./pages/teachers/list_teachers.js";
import { initProfileTeacher } from "./pages/teachers/profile_teachers.js";
import { initAdminTeachers } from "./pages/teachers/admin_teachers.js";
import { initNewsPage } from "./pages/news.js";
import { initNewsDetailPage } from "./pages/news_detail.js";


const routes = [
  // { re: /^\/$/,                   load: () => initHome() },
  {
    re: /^\/teachers\/?$/,
  load: async () => {
    const res = await fetch("/pages/teachers/teachers.html");
    app.innerHTML = await res.text();
    await initListTeachers();
  }
 },
{
    re: /^\/teachers\/(\d+)\/?$/,
    load: async (m) => {
      const res = await fetch("/pages/teachers/profile_teachers.html");
      app.innerHTML = await res.text();
      await initProfileTeacher({ id: m[1] });
    }
  },

{
    re: /^\/news\/?$/, load: async (m) => {
    const res = await fetch("/pages/news/news.html");
    app.innerHTML = await res.text();
    await initNewsPage();
  }
},

  {
    re: /^\/news\/(\d+)\/?$/,   load: async (m) => {
    const res = await fetch("/pages/news/news_detail.html");
    app.innerHTML = await res.text();
    await initNewsDetailPage(m[1]);
  } },

  {
    re: /^\/teachers\/admin\/?$/,
    load: async () => {
      const res = await fetch("/pages/teachers/admin_teachers.html");
      app.innerHTML = await res.text();
      await initAdminTeachers();
    },
  },
];

const app = document.getElementById("app");

async function render(pathname) {
  for (const r of routes) {
    const m = pathname.match(r.re);
    if (m) {
      app.innerHTML = "";
      try {
        await r.load(m);
      } catch (e) {
        console.error(e);
        app.textContent = "Ошибка загрузки страницы.";
      }
      return;
    }
  }
  app.innerHTML = "<p>404</p>";
}

document.addEventListener("click", (e) => {
  const a = e.target.closest("a[data-link]");
  if (!a) return;
  e.preventDefault();
  history.pushState({}, "", a.href);
  render(location.pathname);
});
window.addEventListener("popstate", () => render(location.pathname));
render(location.pathname);
