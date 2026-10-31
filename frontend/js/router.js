const routes = {
  "/": {
    title: "Главная",
    file: "/pages/home.html",
  },

  "/teachers": {
    title: "Преподаватели",
    file: "/pages/teachers.html",
    init: loadTeachers,
  },

  "/news": {
    title: "Новости кафедры",
    file: "/pages/news.html",
    init: initNewsPage,
  },
};
