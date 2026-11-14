export async function initNewsDetailPage(newsId) {
  const newsDetail = document.getElementById("news_detail");

  try {
      const response = await fetch(`/api/news/${newsId}`);

      if (response.status === 404) {
          newsDetail.innerHTML = "<h2>Новость не найдена</h2>";
          return;
      }

      if (!response.ok) {
          throw new Error("Не удалось загрузить новость");
      }

      const item = await response.json();

      newsDetail.replaceChildren();

      if (item.image_url) {
          const image = document.createElement("img");
          image.className = "news-detail-image";
          image.src = item.image_url;
          image.alt = item.title;

          newsDetail.appendChild(image);
      }

      if (item.is_event) {
          const badge = document.createElement("span");
          badge.className = "news-badge news-detail-badge";
          badge.textContent = "СОБЫТИЕ";

          newsDetail.appendChild(badge);
      }

      const header = document.createElement("div");
      header.className = "news-detail-header";

      const date = document.createElement("span");
      date.className = "news-date";
      date.textContent = item.publish_date
          ? new Date(item.publish_date).toLocaleDateString("ru-RU")
          : "";

      const category = document.createElement("span");
      category.className = "news-category";
      category.textContent = item.category || "Без категории";

      header.append(date, category);

      const title = document.createElement("h1");
      title.textContent = item.title;

      const content = document.createElement("p");
      content.className = "news-detail-content";
      content.textContent = item.content;

      newsDetail.append(header, title, content);

      document.title = `${item.title} | Кафедра ВТИСиТ`;

  } catch (error) {
      console.error("Ошибка загрузки новости:", error);
      newsDetail.textContent = "Не удалось загрузить новость.";
  }
}