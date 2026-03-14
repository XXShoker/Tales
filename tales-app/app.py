import streamlit as st
import os
import base64
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Стили ---
st.markdown("""
<style>
/* Подключаем шрифты */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');

/* Общий фон – старая бумага */
.stApp {
    background-color: #fef9e7;
    background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MCIgaGVpZ2h0PSI4MCIgdmlld0JveD0iMCAwIDQwIDQwIj48cGF0aCBkPSJNMjAgMjBhMTAgMTAgMCAwIDEgMjAgMCAxMCAxMCAwIDAgMS0yMCAweiIgZmlsbD0iI2UwZDVjMCIgb3BhY2l0eT0iMC4yIi8+PC9zdmc+');
    background-repeat: repeat;
}

/* Заголовки */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Cormorant Garamond', serif;
    color: #5d3a1a;
    font-weight: 600;
}

/* Основной текст */
p, li, .stMarkdown, .stText {
    font-family: 'Open Sans', sans-serif;
    color: #3e2c1b;
}

/* Боковая панель */
.css-1d391kg, .css-1wrcr25, section[data-testid="stSidebar"] {
    background-color: #f5e9d8 !important;
}

/* --- Карусель как в Netflix --- */
.carousel-title {
    font-size: 1.8rem;
    margin: 20px 0 10px 0;
    padding-left: 5px;
    font-family: 'Cormorant Garamond', serif;
    color: #5d3a1a;
}

.carousel-container {
    display: flex;
    overflow-x: auto;
    gap: 20px;
    padding: 10px 5px 20px 5px;
    scrollbar-width: thin;
    scrollbar-color: #b5926a #f5e9d8;
    -webkit-overflow-scrolling: touch;
    margin-bottom: 30px;
}

.carousel-container::-webkit-scrollbar {
    height: 8px;
}

.carousel-container::-webkit-scrollbar-track {
    background: #f5e9d8;
    border-radius: 10px;
}

.carousel-container::-webkit-scrollbar-thumb {
    background: #b5926a;
    border-radius: 10px;
}

/* Карточка сказки */
.tale-card {
    flex: 0 0 auto;
    width: 280px;
    background-color: #fffaf0;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e9d9c4;
    transition: all 0.3s ease;
    cursor: pointer;
    text-decoration: none;
    color: inherit;
    display: block;
}

.tale-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.12);
}

.tale-card img {
    width: 100%;
    height: 160px;
    object-fit: cover;
    border-radius: 12px;
    border: 1px solid #d4b68a;
    margin-bottom: 12px;
}

.tale-card h3 {
    margin: 0 0 8px 0;
    font-size: 1.3rem;
    color: #5d3a1a;
    font-family: 'Cormorant Garamond', serif;
}

.tale-card p {
    font-size: 0.9rem;
    line-height: 1.4;
    color: #3e2c1b;
    margin: 0 0 12px 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.tale-card .start-button {
    width: 100%;
    background-color: #e6d5b8;
    color: #3e2c1b;
    border: 1px solid #b5926a;
    border-radius: 30px;
    padding: 8px 16px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    font-weight: 600;
}

.tale-card .start-button:hover {
    background-color: #d4b68a;
}

/* Сообщения чата */
.stChatMessage {
    background-color: #fffaf0 !important;
    border-radius: 18px !important;
    padding: 8px 16px !important;
    border: 1px solid #e9d9c4;
    margin-bottom: 8px;
}

.stChatMessage[data-testid="chatMessageUser"] {
    background-color: #e6d5b8 !important;
}

/* Адаптация для мобильных */
@media (max-width: 600px) {
    .tale-card {
        width: 220px;
    }
    .tale-card img {
        height: 130px;
    }
    h1 {
        font-size: 1.8rem;
    }
}

/* Прогресс-бар */
.stProgress > div > div {
    background-color: #b5926a !important;
}

/* Ссылка доната */
.stLinkButton a {
    background-color: #d4b68a;
    color: #2a1c0e;
    border-radius: 30px;
    padding: 0.5rem 1rem;
    text-decoration: none;
    font-weight: 600;
    transition: background-color 0.3s;
}

.stLinkButton a:hover {
    background-color: #b89e7c;
}
</style>
""", unsafe_allow_html=True)

# --- Инициализация состояния ---
if "selected_tale" not in st.session_state:
    st.session_state.selected_tale = None
if "scene_id" not in st.session_state:
    st.session_state.scene_id = "start"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "scenes" not in st.session_state:
    st.session_state.scenes = {}
if "scene_history" not in st.session_state:
    st.session_state.scene_history = []
if "achieved_endings" not in st.session_state:
    st.session_state.achieved_endings = {}
if "clicked_tale" not in st.session_state:
    st.session_state.clicked_tale = None

def count_total_endings(tale_name):
    tale = tales.get(tale_name)
    if not tale:
        return 0
    count = 0
    for scene_id, scene in tale["scenes"].items():
        if scene.get("options") == []:
            count += 1
    return count

def get_ending_stats(tale_name):
    opened = len(st.session_state.achieved_endings.get(tale_name, set()))
    total = count_total_endings(tale_name)
    return opened, total

def start_tale(tale_name):
    st.session_state.selected_tale = tale_name
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    st.session_state.scene_history = ["start"]
    tale_data = tales.get(tale_name)
    if tale_data:
        st.session_state.scenes = tale_data["scenes"]
        first_scene = st.session_state.scenes["start"]
        st.session_state.messages.append({"role": "assistant", "content": first_scene["text"]})
    if tale_name not in st.session_state.achieved_endings:
        st.session_state.achieved_endings[tale_name] = set()

def handle_choice(choice_text, next_scene_id):
    st.session_state.messages.append({"role": "user", "content": choice_text})
    st.session_state.scene_id = next_scene_id
    st.session_state.scene_history.append(next_scene_id)
    next_scene = st.session_state.scenes.get(next_scene_id)
    if next_scene:
        st.session_state.messages.append({"role": "assistant", "content": next_scene["text"]})
    else:
        st.error(f"Сцена {next_scene_id} не найдена")

def go_back():
    if len(st.session_state.scene_history) > 1:
        st.session_state.scene_history.pop()
        st.session_state.scene_id = st.session_state.scene_history[-1]
        if len(st.session_state.messages) >= 2:
            st.session_state.messages.pop()
            st.session_state.messages.pop()
        st.rerun()

def reset_to_main():
    st.session_state.selected_tale = None
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []

def get_image_base64(image_path):
    """Конвертирует изображение в base64 для вставки в HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    st.markdown("---")
    
    if st.session_state.selected_tale is not None:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        st.progress(opened / total if total > 0 else 0)
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
        st.markdown("---")
    
    if st.session_state.selected_tale is not None:
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()
        if st.button("❌ Завершить и выйти", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

# Проверяем, не была ли выбрана сказка через кнопку
if st.session_state.clicked_tale:
    start_tale(st.session_state.clicked_tale)
    st.session_state.clicked_tale = None
    st.rerun()

if st.session_state.selected_tale is None:
    # Определяем группы сказок
    all_tales = list(tales.keys())
    soviet_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new_tales = ["Путешествие в Волшебный лес"]

    # Функция для создания HTML карточки
    def create_tale_card(tale_name):
        cover_path = tales[tale_name].get("cover", "")
        description = tales[tale_name].get("description", "")
        
        if cover_path and os.path.exists(cover_path):
            img_base64 = get_image_base64(cover_path)
            if img_base64:
                img_html = f'<img src="data:image/jpeg;base64,{img_base64}" alt="{tale_name}">'
            else:
                img_html = f'<img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨+{tale_name}" alt="{tale_name}">'
        else:
            img_html = f'<img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨+{tale_name}" alt="{tale_name}">'
        
        return f'''
        <a href="?tale={tale_name}" target="_self" style="text-decoration: none; color: inherit;">
            <div class="tale-card">
                {img_html}
                <h3>{tale_name}</h3>
                <p>{description}</p>
                <div class="start-button">✨ Начать</div>
            </div>
        </a>
        '''

    # Секция "Советские сказки"
    st.markdown("## 📚 Советские сказки")
    
    # Создаем карусель
    carousel_html = '<div class="carousel-container">'
    for tale_name in soviet_tales:
        if tale_name in all_tales:
            carousel_html += create_tale_card(tale_name)
    carousel_html += '</div>'
    
    st.markdown(carousel_html, unsafe_allow_html=True)

    # Секция "Новые сказки"
    if new_tales and any(t in all_tales for t in new_tales):
        st.markdown("## 🆕 Новые сказки")
        
        carousel_html = '<div class="carousel-container">'
        for tale_name in new_tales:
            if tale_name in all_tales:
                carousel_html += create_tale_card(tale_name)
        carousel_html += '</div>'
        
        st.markdown(carousel_html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны. Если хотите поддержать проект, воспользуйтесь кнопкой в боковой панели.*")

    # Обработка URL параметра
    query_params = st.query_params
    if "tale" in query_params:
        tale_name = query_params["tale"]
        if tale_name in all_tales:
            st.session_state.clicked_tale = tale_name
            st.query_params.clear()
            st.rerun()

else:
    # Отображение сказки (история сообщений)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    current_scene = st.session_state.scenes.get(st.session_state.scene_id)

    if current_scene:
        if not current_scene.get("options"):
            if current_scene.get("ending_type") and current_scene.get("ending_number"):
                ending_type = current_scene["ending_type"]
                ending_num = current_scene["ending_number"]
                type_emoji = {
                    "happy": "😊",
                    "sad": "😢",
                    "neutral": "😐",
                    "secret": "🤫"
                }.get(ending_type, "🌟")
                
                tale = st.session_state.selected_tale
                ending_id = f"{ending_type}_{ending_num}"
                if tale not in st.session_state.achieved_endings:
                    st.session_state.achieved_endings[tale] = set()
                st.session_state.achieved_endings[tale].add(ending_id)
                
                st.markdown("---")
                st.markdown(f"## {type_emoji} **Концовка #{ending_num}**")
                st.markdown(f"**Тип:** {ending_type.capitalize()}")
                
                if ending_type == "happy":
                    st.success("🎉 Поздравляем! Это счастливый конец!")
                else:
                    st.info("😕 Это не счастливый конец. Попробуй пройти сказку снова, возможно, ты найдёшь счастливый конец!")
                
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            else:
                st.markdown("---")
                st.markdown("🎉 **Конец сказки!**")
            
            st.markdown("---")
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Вернуться к предыдущему выбору", use_container_width=True):
                    go_back()
            if st.button("🔄 Начать эту сказку заново", use_container_width=True):
                start_tale(st.session_state.selected_tale)
                st.rerun()
        else:
            st.markdown("### Твой выбор:")
            for opt in current_scene["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", use_container_width=True):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад к предыдущему выбору", use_container_width=True):
                    go_back()
    else:
        st.error("⚠️ Сцена не найдена. Вернитесь к выбору сказок.")
        if st.button("⬅️ К выбору сказок", use_container_width=True):
            reset_to_main()
            st.rerun()
