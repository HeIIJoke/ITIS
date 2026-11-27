import { readAccount, signOut } from "./auth.js";
import { renderCredentials, renderProfile, renderUserAdmin } from "./pages/auth.js";
import { initListTeachers } from "./pages/teachers/list_teachers.js";
import { initProfileTeacher } from "./pages/teachers/profile_teachers.js";
import { initAdminTeachers } from "./pages/teachers/admin_teachers.js";
import { initNewsPage } from "./pages/news.js";
import { initNewsDetailPage } from "./pages/news_detail.js";
import { initSchedulePage } from "./pages/schedule.js";
import { initScheduleEditPage } from "./pages/schedule-edit.js";


const routes = [
  { path: /^\/$/, template: "/pages/home.html" },
  { path: /^\/teachers\/?$/, template: "/pages/teachers/teachers.html", init: initListTeachers },
  {
    path: /^\/teachers\/(\d+)\/?$/,
    template: "/pages/teachers/profile_teachers.html",
    init: (match) => initProfileTeacher({ id: match[1] }),
  },
  {
    path: /^\/news\/?$/,
    template: "/pages/news/news.html",
    init: (_, account) => initNewsPage(account?.role === "admin"),
  },
  {
    path: /^\/news\/(\d+)\/?$/,
    template: "/pages/news/news_detail.html",
    init: (match) => initNewsDetailPage(match[1]),
  },
  {
    path: /^\/teachers\/admin\/?$/,
    template: "/pages/teachers/admin_teachers.html",
    fragment: "#teachers-admin-template",
    access: "admin",
    init: initAdminTeachers,
  },
  { path: /^\/admin\/users\/?$/, access: "admin", init: () => renderUserAdmin(app) },
  { path: /^\/profile\/?$/, access: "account", init: (_, account) => renderProfile(app, account) },
  {
    path: /^\/(login|register)\/?$/,
    init: ([, mode], account) => {
      if (account) {
        navigate("/profile", { replace: true });
      } else {
        renderCredentials(app, mode, navigate, history.state?.registered);
      }
    },
  },

  {
    re: /^\/schedule\/edit\/?$/,
    load: async () => {
      const res = await fetch("/pages/schedule/schedule-edit.html");
      app.innerHTML = await res.text();
      return await initScheduleEditPage();   
    },
  },

  {
     re: /^\/schedule\/?$/,
    load: async () => {
      const res = await fetch("/pages/schedule/schedule.html");
      app.innerHTML = await res.text();
      return await initSchedulePage();      
    },
  },
];

const app = document.getElementById("app");
const logoutButton = document.getElementById("sign-out");
const authStatus = document.getElementById("auth-status");
let renderVersion = 0;

function updateNavigation(account) {
  document.querySelectorAll("[data-auth]").forEach((element) => {
    const access = element.dataset.auth;
    const visible = {
      guest: !account,
      account: Boolean(account),
      admin: account?.role === "admin",
    };
    element.hidden = !visible[access];
  });
}

function navigate(path, { replace = false, registered = false } = {}) {
  const update = replace ? "replaceState" : "pushState";
  history[update]({ registered }, "", path);
  render(location.pathname);
}

async function render(pathname) {
  const version = ++renderVersion;
  const route = routes.find(({ path }) => path.test(pathname));
  authStatus.textContent = "";
  app.textContent = "Загрузка...";

  try {
    const account = await readAccount().catch((error) => {
      if (route?.access) throw error;
      return null;
    });
    if (version !== renderVersion) return;
    updateNavigation(account);

    if (!route) {
      app.textContent = "404";
      return;
    }
    if (route.access && !account) {
      navigate("/login", { replace: true });
      return;
    }
    if (route.access === "admin" && account.role !== "admin") {
      app.textContent = "Этот раздел доступен только администратору.";
      return;
    }

    if (route.template) {
      const response = await fetch(route.template);
      if (!response.ok) throw new Error("Шаблон страницы недоступен");
      const html = await response.text();
      if (version !== renderVersion) return;
      if (route.fragment) {
        const document = new DOMParser().parseFromString(html, "text/html");
        app.replaceChildren(document.querySelector(route.fragment).content.cloneNode(true));
      } else {
        app.innerHTML = html;
      }
    }
    await route.init?.(pathname.match(route.path), account);
  } catch (error) {
    if (version === renderVersion) app.textContent = "Ошибка загрузки страницы.";
    console.error(error);
  }
}

logoutButton.addEventListener("click", async () => {
  logoutButton.disabled = true;
  try {
    await signOut();
    navigate("/login", { replace: true });
  } catch (error) {
    authStatus.textContent = error.message;
  } finally {
    logoutButton.disabled = false;
  }
});

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-link]");
  if (!link || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  navigate(link.href);
});
window.addEventListener("popstate", () => render(location.pathname));
render(location.pathname);
