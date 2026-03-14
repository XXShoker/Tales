import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="centered")

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

/* Кнопки */
.stButton > button {
    font-family: 'Open Sans', sans-serif;
    background-color: #e6d5b8;
    color: #3e2c1b;
    border: 1px solid #b5926a;
    border-radius: 30px;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.stButton > button:hover {
    background-color: #d4b68a;
    color: #2a1c0e;
    border-color: #8b6b4f;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

/* Кнопки в сайдбаре */
.sidebar .stButton > button {
    background-color: #cbb89e;
    border-color: #9b7e62;
}

.sidebar .stButton > button:hover {
    background-color: #b89e7c;
}

/* --- Карусель (горизонтальная прокрутка) --- */
.scrollable-container {
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: 10px;
    margin-bottom: 20px;
    scrollbar-width: thin;
    scrollbar-color: #b5926a #f5e9d8;
}

.scrollable-container::-webkit-scrollbar {
    height: 8px;
}

.scrollable-container::-webkit-scrollbar-track {
    background: #f5e9d8;
    border-radius: 10px;
}

.scrollable-container::-webkit-scrollbar-thumb {
    background: #b5926a;
    border-radius: 10px;
}

/* Колонки внутри карусели */
.scrollable-container [data-testid="column"] {
    display: inline-block;
    float: none;
    white-space: normal;
    width: 260px !important;
    margin-right: 20px;
    vertical-align: top;
}

/* Карточка сказки (внутри колонки) */
.carousel-card {
    background-color: #fffaf0;
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e9d9c4;
    transition: box-shadow 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.carousel-card:hover {
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.carousel-card img {
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: 12px;
    border: 1px solid #d4b68a;
    margin-bottom: 10px;
}

.carousel-card h4 {
    margin: 0 0 5px 0;
    font-size: 1.2rem;
    white-space: normal;
}

.carousel-card p {
    font-size: 0.9rem;
    line-height: 1.4;
    margin: 0 0 10px 0;
    white-space: normal;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}

.carousel-card .stButton {
    width: 100%;
    margin-top: auto;
}

.carousel-card .stButton button {
    width: 100%;
    padding: 0.4rem;
    font-size: 0.9rem;
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
    .scrollable-container [data-testid="column"] {
        width: 200px !important;
    }
    .carousel-card img {
        height: 120px;
    }
    h1 {
        font-size: 1.8rem;
    }
}

/* Прогресс-бар */
.stProgress > div > div {
    background-color: #b5926a !important;
}

/* Ссылка доната (fallback) */
.stLinkButton a, a button {
    background-color: #d4b68a;
    color: #2a1c0e;
    border-radius: 30px;
    padding: 0.5rem 1rem;
    text-decoration: none;
    font-weight: 600;
    transition: background-color 0.3s;
    border: none;
    cursor: pointer;
}

.stLinkButton a:hover, a button:hover {
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

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
    try:
        st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    except AttributeError:
        st.markdown(
            '<a href="https://donate.stream/donate_69b56f4953f16" target="_blank">'
            '<button style="background-color:#d4b68a; color:#2a1c0e; padding:0.5rem 1rem; '
            'border:none; border-radius:30px; width:100%; font-size:1rem; '
            'cursor:pointer; font-weight:600;">💖 Поддержать донатом</button></a>',
            unsafe_allow_html=True
        )
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

if st.session_state.selected_tale is None:
    # Определяем группы сказок
    all_tales = list(tales.keys())
    soviet_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new_tales = ["Путешествие в Волшебный лес"]

    def show_tale_card(tale_name):
        cover_path = tales[tale_name].get("cover", "")
        if cover_path and os.path.exists(cover_path):
            st.image(cover_path, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/240x150/ffe6f0/ff69b4?text=✨+Сказка", use_container_width=True)
        st.markdown(f"#### {tale_name}")
        if tales[tale_name].get("description"):
            st.markdown(tales[tale_name]["description"])
        if st.button(f"✨ Начать", key=f"choose_{tale_name}", use_container_width=True):
            start_tale(tale_name)
            st.rerun()

    # Секция "Советские сказки"
    st.markdown("## 📚 Советские сказки")
    st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
    cols = st.columns(len(soviet_tales))
    for i, tale_name in enumerate(soviet_tales):
        if tale_name in all_tales:
            with cols[i]:
                st.markdown('<div class="carousel-card">', unsafe_allow_html=True)
                show_tale_card(tale_name)
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Секция "Новые сказки"
    st.markdown("## 🆕 Новые сказки")
    st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
    cols = st.columns(len(new_tales))
    for i, tale_name in enumerate(new_tales):
        if tale_name in all_tales:
            with cols[i]:
                st.markdown('<div class="carousel-card">', unsafe_allow_html=True)
                show_tale_card(tale_name)
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны. Если хотите поддержать проект, воспользуйтесь кнопкой в боковой панели.*")

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
