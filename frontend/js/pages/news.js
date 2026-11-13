async function initNewsPage() {
    const toggleBtn = document.getElementById("toggle-form-btn");
    const cancelBtn = document.getElementById("cancel-form-btn");
    const formCard = document.getElementById("publish-form-card");
    const newsForm = document.getElementById("news-form");
    const newsList = document.getElementById("news-list");

    const imageInput = document.getElementById("news-image");
    const imagePreview = document.getElementById("image-preview");
    const imagePreviewContainer = document.getElementById("image-preview-container");
    const removeImageBtn = document.getElementById("remove-image-btn");
    const selectedFileName = document.getElementById("selected-file-name");
    
    let selectedImage = null;

    if (imageInput) {
        imageInput.addEventListener("change", () => {
            const file = imageInput.files[0];
    
            if (!file) {
                return;
            }
    
            if (!file.type.startsWith("image/")) {
                alert("Выберите изображение");
                imageInput.value = "";
                return;
            }
    
            if (file.size > 5 * 1024 * 1024) {
                alert("Размер изображения не должен превышать 5 МБ");
                imageInput.value = "";
                return;
            }
    
            selectedImage = file;
    
            imagePreview.src = URL.createObjectURL(file);
            selectedFileName.textContent = file.name;
    
            imagePreviewContainer.classList.remove("hidden");
        });
    }
    
    if (removeImageBtn) {
        removeImageBtn.addEventListener("click", () => {
            selectedImage = null;
            imageInput.value = "";
            imagePreview.src = "";
            selectedFileName.textContent = "Файл не выбран";
    
            imagePreviewContainer.classList.add("hidden");
        });
    }

    if (!newsList) return;
    await loadCategories();

    if (toggleBtn && formCard) {
        toggleBtn.addEventListener("click", (event) => {
            event.preventDefault();
            formCard.classList.toggle("hidden");
        });
    }

    if (cancelBtn && formCard) {
        cancelBtn.addEventListener("click", (event) => {
            event.preventDefault();
            formCard.classList.add("hidden");
            newsForm?.reset();
        });
    }

    loadNews();

    if (newsForm) {
        newsForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const title = document.getElementById("news-title").value.trim();
            const content = document.getElementById("news-content").value.trim();

            const categoryInput = document.getElementById("news-category");
            const eventInput = document.getElementById("news-is-event");

            if (title.length < 5) {
                alert("Заголовок должен содержать минимум 5 символов");
                return;
            }

            if (title.length > 150) {
                alert("Заголовок не должен превышать 150 символов");
                return;
            }

            if (content.length < 10) {
                alert("Описание должно содержать минимум 10 символов");
                return;
            }

            if (!categoryInput.value) {
                alert("Выберите категорию новости");
                return;
            }

            const formData = new FormData();

            formData.append("title", title);
            formData.append("content", content);
            formData.append("category_id", categoryInput.value);
            formData.append("is_event", String(eventInput?.checked || false));
            
            if (selectedImage) {
                formData.append("image", selectedImage);
            }

            try {
                const response = await fetch("/api/news", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(
                        error.detail || "Не удалось опубликовать новость"
                    );
                }

                newsForm.reset();

                selectedImage = null;
                imageInput.value = "";
                imagePreview.src = "";
                selectedFileName.textContent = "Файл не выбран";
                imagePreviewContainer.classList.add("hidden");
                
                formCard?.classList.add("hidden");
                
                await loadNews();
            } catch (error) {
                console.error("Ошибка публикации:", error);
                alert(error.message || "Ошибка соединения с сервером");
            }
        });
    }

    async function loadCategories() {
        const categorySelect = document.getElementById("news-category");
    
        try {
            const response = await fetch("/api/news/categories");
    
            if (!response.ok) {
                throw new Error("Не удалось загрузить категории");
            }
    
            const categories = await response.json();
    
            categories.forEach((category) => {
                const option = document.createElement("option");
    
                option.value = category.id;
                option.textContent = category.name;
    
                categorySelect.appendChild(option);
            });
    
        } catch (error) {
            console.error("Ошибка загрузки категорий:", error);
            categorySelect.innerHTML =
                '<option value="">Не удалось загрузить категории</option>';
        }
    }

    async function loadNews() {
        newsList.textContent = "Загрузка новостей...";

        try {
            const response = await fetch("/api/news");

            if (!response.ok) {
                throw new Error("Не удалось загрузить новости");
            }

            const news = await response.json();

            newsList.replaceChildren();

            if (news.length === 0) {
                newsList.textContent = "Пока новостей нет.";
                return;
            }

            const latestEvent = news.find((item) => item.is_event === true);
            const sortedNews = [...news];

            if (latestEvent) {
                const eventIndex = sortedNews.findIndex(
                    (item) => item.id === latestEvent.id
                );

                if (eventIndex !== -1) {
                    sortedNews.splice(eventIndex, 1);
                    sortedNews.unshift(latestEvent);
                }
            }

            sortedNews.forEach((item, index) => {
                const isFeatured = latestEvent && item.id === latestEvent.id;

                newsList.appendChild(createNewsCard(item, isFeatured));
            });

        } catch (error) {
            console.error("Ошибка загрузки новостей:", error);
            newsList.textContent = "Не удалось загрузить новости.";
        }
    }

    function createNewsCard(item, isFeatured) {
        const isEvent = item.is_event === true;

        const card = document.createElement("article");
        card.className = isFeatured
            ? "news-card news-featured"
            : "news-card";

        const imageContainer = document.createElement("div");
        imageContainer.className = "news-image";

        if (item.image_url) {
            const image = document.createElement("img");
            image.src = item.image_url;
            image.alt = item.title;
            image.loading = "lazy";

            image.addEventListener("error", () => {
                console.error("Не удалось загрузить изображение:", image.src);
            });

            imageContainer.appendChild(image);
        }

        if (isEvent) {
            const badge = document.createElement("span");
            badge.className = "news-badge";
            badge.textContent = "СОБЫТИЕ";
            imageContainer.appendChild(badge);
        }

        const content = document.createElement("div");
        content.className = "news-content";

        const header = document.createElement("div");
        header.className = "news-card-header";
        
        const date = document.createElement("span");
        date.className = "news-date";
        date.textContent = item.publish_date
            ? new Date(item.publish_date).toLocaleDateString("ru-RU")
            : "";
        
        const category = document.createElement("span");
        category.className = "news-category";
        category.textContent = item.category || "Без категории";
        
        header.append(date, category);

        const title = document.createElement("h2");
        title.textContent = item.title;

        const text = document.createElement("p");
        text.className = "news-text";
        text.textContent = item.content;

        content.append(header, title, text);
        card.append(imageContainer, content);

        card.addEventListener("click", () => {
            window.location.href = `/news/${item.id}`;
        });
        
        card.style.cursor = "pointer";
        
        return card;
    }
}