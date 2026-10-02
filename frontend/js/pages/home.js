/**
 * Страница «Главная».
 *
 * Эталонная страница: берёт данные фичи GET /api/department и рисует их.
 * Копируй этот файл как шаблон для своих страниц.
 */

async function initHome() {
  const container = document.getElementById("department-info");
  if (!container) return;

  try {
    const info = await apiGet("/department");

    container.innerHTML = `
      <h2>${info.full_name}</h2>
      <p>${info.about}</p>
      <ul class="info-list">
        <li><strong>Заведующий кафедрой:</strong> ${info.head}</li>
        <li><strong>Факультет:</strong> ${info.faculty}</li>
        <li><strong>Год основания:</strong> ${info.founded}</li>
        <li><strong>Почта:</strong> <a href="mailto:${info.contacts.email}">${info.contacts.email}</a></li>
        <li><strong>Телефон:</strong> ${info.contacts.phone}</li>
        <li><strong>Адрес:</strong> ${info.contacts.address}</li>
      </ul>
    `;
  } catch (error) {
    console.error(error);
    container.innerHTML =
      '<p class="error">Не удалось загрузить информацию о кафедре.</p>';
  }
}

