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
};
