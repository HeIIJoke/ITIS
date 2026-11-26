export async function initNewsPage() {
    const toggleBtn = document.getElementById("toggle-form-btn");
    const cancelBtn = document.getElementById("cancel-form-btn");
    const formCard = document.getElementById("publish-form-card");
    const newsForm = document.getElementById("news-form");
    const newsList = document.getElementById("news-list");
    const categoryFilter = document.getElementById("news-category-filter");
    const pagination = document.getElementById("news-pagination");

    let currentPage = 1;
    const pageSize = 6;

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

    if (categoryFilter) {
        categoryFilter.addEventListener("change", () => {
            currentPage = 1;
            loadNews();
        });
    }

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
                
                currentPage = 1;
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
                // Категории для формы публикации
                if (categorySelect) {
                    const option = document.createElement("option");
    
                    option.value = category.id;
                    option.textContent = category.name;
    
                    categorySelect.appendChild(option);
                }
    
                // Категории для фильтра
                if (categoryFilter) {
                    const option = document.createElement("option");
    
                    option.value = category.id;
                    option.textContent = category.name;
    
                    categoryFilter.appendChild(option);
                }
            });
    
        } catch (error) {
            console.error("Ошибка загрузки категорий:", error);
        }
    }

    async function loadNews() {
        newsList.textContent = "Загрузка новостей...";
    
        try {
            const params = new URLSearchParams();
    
            params.append("page", currentPage);
            params.append("page_size", pageSize);
    
            // Добавляем категорию, если она выбрана
            if (categoryFilter && categoryFilter.value) {
                params.append("category_id", categoryFilter.value);
            }
    
            const response = await fetch(`/api/news?${params.toString()}`);
    
            if (!response.ok) {
                throw new Error("Не удалось загрузить новости");
            }
    
            const data = await response.json();
            const news = data.items;
    
            newsList.replaceChildren();
    
            if (news.length === 0) {
                newsList.textContent = "В этой категории пока нет новостей.";
    
                pagination.replaceChildren();
                return;
            }
    
            news.forEach((item) => {
                const isFeatured =
                    currentPage === 1 &&
                    item.id === data.featured_event_id;
            
                newsList.appendChild(createNewsCard(item, isFeatured));
            });
    
            // Обновляем кнопки страниц
            renderPagination(data.total_pages);
    
        } catch (error) {
            console.error("Ошибка загрузки новостей:", error);
            newsList.textContent = "Не удалось загрузить новости.";
            pagination.replaceChildren();
        }
    }

    function renderPagination(totalPages) {
        pagination.replaceChildren();
    
        if (totalPages <= 1) {
            return;
        }
    
        const prevButton = document.createElement("button");
        prevButton.textContent = "←";
        prevButton.disabled = currentPage === 1;
    
        prevButton.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                loadNews();
            }
        });
    
        pagination.appendChild(prevButton);
    
        let pages = [];
    
        if (totalPages <= 7) {
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            pages.push(1);
    
            if (currentPage <= 3) {
                pages.push(2, 3, "...", totalPages - 2, totalPages - 1, totalPages);
            } else if (currentPage >= totalPages - 2) {
                pages.push(
                    "...",
                    totalPages - 2,
                    totalPages - 1,
                    totalPages
                );
            } else {
                pages.push(
                    "...",
                    currentPage - 1,
                    currentPage,
                    currentPage + 1,
                    "...",
                    totalPages
                );
            }
        }
    
        pages.forEach((page) => {
            if (page === "...") {
                const dots = document.createElement("span");
                dots.textContent = "...";
                dots.className = "pagination-dots";
    
                pagination.appendChild(dots);
                return;
            }
    
            const pageButton = document.createElement("button");
            pageButton.textContent = page;
    
            if (page === currentPage) {
                pageButton.classList.add("active");
            }
    
            pageButton.addEventListener("click", () => {
                currentPage = page;
                loadNews();
            });
    
            pagination.appendChild(pageButton);
        });
    
        const nextButton = document.createElement("button");
        nextButton.textContent = "→";
        nextButton.disabled = currentPage === totalPages;
    
        nextButton.addEventListener("click", () => {
            if (currentPage < totalPages) {
                currentPage++;
                loadNews();
            }
        });
    
        pagination.appendChild(nextButton);
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