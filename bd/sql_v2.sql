-- ==========================================
-- 1. СПРАВОЧНИКИ (Словари)
-- ==========================================

-- Роли пользователей (Админ, Студент, Преподаватель и т.д.)
CREATE TABLE IF NOT EXISTS public.roles (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE
);

-- Уровни образования (Бакалавриат, Магистратура и т.д.)
CREATE TABLE IF NOT EXISTS public.education_levels (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE
);

-- Должности преподавателей (Ассистент, Старший преподаватель, Зав. кафедрой)
CREATE TABLE IF NOT EXISTS public.teacher_positions (
    id serial PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE
);

-- Категории новостей
CREATE TABLE IF NOT EXISTS public.news_categories (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE
);

-- Справочник времени пар (звонки)
CREATE TABLE IF NOT EXISTS public.class_times (
    id serial PRIMARY KEY,
    lesson_number integer NOT NULL UNIQUE, -- Номер пары (1, 2, 3...)
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL
);


-- ==========================================
-- 2. СТРУКТУРА ВУЗА
-- ==========================================

-- Кафедры
CREATE TABLE IF NOT EXISTS public.departments (
    id serial PRIMARY KEY,
    name varchar(150) NOT NULL,
    description text,
    phone varchar(20),
    email varchar(100),
    social_network_link varchar(255)
);

-- Направления подготовки (Специальности)
CREATE TABLE IF NOT EXISTS public.majors (
    id serial PRIMARY KEY,
    department_id integer REFERENCES public.departments(id) ON DELETE SET NULL,
    education_level_id integer REFERENCES public.education_levels(id),
    name varchar(150) NOT NULL,
    description text
);

-- Учебные группы
CREATE TABLE IF NOT EXISTS public.student_groups (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE,
    course_year integer NOT NULL
);


-- ==========================================
-- 3. ЛЮДИ И ПОЛЬЗОВАТЕЛИ
-- ==========================================

-- Преподаватели
CREATE TABLE IF NOT EXISTS public.teachers (
    id serial PRIMARY KEY,
    position_id integer REFERENCES public.teacher_positions(id) ON DELETE SET NULL,
    
    -- Ученая степень и звание (например: 0 - нет, 1 - кандидат/доцент, 2 - доктор/профессор)
    degree smallint DEFAULT 0,
    academic_title smallint DEFAULT 0,
    
    -- Личные и контактные данные
    last_name varchar(50) NOT NULL,
    first_name varchar(50) NOT NULL,
    middle_name varchar(50),
    email varchar(100) UNIQUE,
    phone varchar(20),
    bio text,
    
    -- Системные данные и кадровая информация
    slug varchar(100) UNIQUE,
    hire_date date,
    dismissal_date date
);

ALTER TABLE public.teachers ADD COLUMN image_url VARCHAR(255);

-- Студенты
CREATE TABLE IF NOT EXISTS public.students (
    id serial PRIMARY KEY,
    group_id integer REFERENCES public.student_groups(id) ON DELETE CASCADE,
    last_name varchar(50) NOT NULL,
    first_name varchar(50) NOT NULL,
    middle_name varchar(50),
    record_book_number varchar(20) UNIQUE NOT NULL, -- Номер зачетки / студбилета
    study_form varchar(50),                         -- Очная, заочная, очно-заочная
    financing_type varchar(50),                     -- Бюджет, контракт, целевое
    status varchar(50) DEFAULT 'Учится'             -- Учится, Отчислен, Академ, Выпускник
);

-- Аккаунты пользователей (для входа в систему)
CREATE TABLE IF NOT EXISTS public.users (
    id serial PRIMARY KEY,
    role_id integer REFERENCES public.roles(id) ON DELETE RESTRICT,
    teacher_id integer REFERENCES public.teachers(id) ON DELETE CASCADE UNIQUE,
    student_id integer REFERENCES public.students(id) ON DELETE CASCADE UNIQUE,
    login varchar(50) NOT NULL UNIQUE,
    password_hash varchar(255) NOT NULL, 
    is_active boolean DEFAULT true,
    CONSTRAINT check_user_type CHECK (
        (teacher_id IS NOT NULL AND student_id IS NULL) OR 
        (student_id IS NOT NULL AND teacher_id IS NULL) OR
        (teacher_id IS NULL AND student_id IS NULL)
    )
);


-- ==========================================
-- 4. УЧЕБНЫЙ ПРОЦЕСС
-- ==========================================

-- Дисциплины (Предметы)
CREATE TABLE IF NOT EXISTS public.subjects (
    id serial PRIMARY KEY,
    major_id integer REFERENCES public.majors(id) ON DELETE CASCADE,
    name varchar(150) NOT NULL,
    description text,
    semester integer NOT NULL,
    control_type varchar(50), -- Экзамен, Зачет, Диф.зачет, Курсовая
    total_hours integer       -- Объем предмета в часах
);

-- Связь: какие преподаватели ведут какие предметы (Многие ко Многим)
CREATE TABLE IF NOT EXISTS public.teacher_subjects (
    id serial PRIMARY KEY,
    subject_id integer REFERENCES public.subjects(id) ON DELETE CASCADE,
    teacher_id integer REFERENCES public.teachers(id) ON DELETE CASCADE,
    UNIQUE (subject_id, teacher_id)
);

-- Постоянное расписание
CREATE TABLE IF NOT EXISTS public.schedules (
    id serial PRIMARY KEY,
    group_id integer REFERENCES public.student_groups(id) ON DELETE CASCADE,
    teacher_id integer REFERENCES public.teachers(id),
    subject_id integer REFERENCES public.subjects(id),
    class_time_id integer REFERENCES public.class_times(id),
    day_of_week varchar(15) NOT NULL,
    week_type varchar(15) NOT NULL DEFAULT 'all', -- 'all', 'even', 'odd'
    room varchar(20),
    lesson_type varchar(50), -- Лекция, практика, лаба
    notes varchar(255)
);

-- Замены и отмены пар (Изменения в расписании)
CREATE TABLE IF NOT EXISTS public.schedule_changes (
    id serial PRIMARY KEY,
    schedule_id integer REFERENCES public.schedules(id) ON DELETE CASCADE, 
    change_date date NOT NULL, 
    new_teacher_id integer REFERENCES public.teachers(id), 
    new_room varchar(20),                                  
    is_cancelled boolean DEFAULT false,                    
    reason text                                            
);


-- ==========================================
-- 5. ИНФРАСТРУКТУРА (Новости и обращения)
-- ==========================================

-- Новости
CREATE TABLE IF NOT EXISTS public.news (
    id serial PRIMARY KEY,
    category_id integer REFERENCES public.news_categories(id),
    author_id integer REFERENCES public.users(id) ON DELETE SET NULL,
    title varchar(150) NOT NULL,
    content text NOT NULL,
    publish_date timestamp DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.news ADD COLUMN image_url VARCHAR(255);
ALTER TABLE public.news ADD COLUMN is_event BOOLEAN;

-- Обращения пользователей (Техподдержка/Деканат)
CREATE TABLE IF NOT EXISTS public.support_tickets (
    id serial PRIMARY KEY,
    user_id integer REFERENCES public.users(id) ON DELETE CASCADE,
    topic varchar(100) NOT NULL,
    message text NOT NULL,
    status varchar(30) DEFAULT 'Новое',
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);