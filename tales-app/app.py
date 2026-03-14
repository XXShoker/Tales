import streamlit as st
import os
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
}

/* Заголовки */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Cormorant Garamond', serif;
    color: #5d3a1a;
    font-weight: 600;
}

/* Боковая панель */
.css-1d391kg, section[data-testid="stSidebar"] {
    background-color: #f5e9d8 !important;
}

/* Карточки в карусели */
.carousel-container {
    display: flex;
    overflow-x: auto;
    gap: 20px;
    padding: 20px 0;
    scrollbar-width: thin;
}

.carousel-container .stButton > button {
    width: 280px;
    height: 380px;
    white-space: normal;
    word-wrap: break-word;
    background-color: #fffaf0;
    color: #3e2c1b;
    border: 1px solid #e9d9c4;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
    font-family: 'Open Sans', sans-serif;
}

.carousel-container .stButton > button:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    background-color: #fffaf0;
}

.carousel-container img {
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: 12px;
    margin-bottom: 10px;
}

.carousel-container h4 {
    margin: 0 0 5px 0;
    font-size: 1.3rem;
    color: #5d3a1a;
}

.carousel-container p {
    font-size: 0.9rem;
    margin: 0;
    flex-grow: 1;
}

/* Адаптация */
@media (max-width: 600px) {
    .carousel-container .stButton > button {
        width: 220px;
    }
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
    st.markdown("Добро пожаловать в мир **интерактивных сказок**! Вы сами выбираете, как развернётся история.")
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
        
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    # Определяем группы сказок
    all_tales = list(tales.keys())
    soviet_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new_tales = ["Путешествие в Волшебный лес"]

    # Советские сказки
    st.markdown("## 📚 Советские сказки")
    
    # Создаем горизонтальный скролл с помощью колонок
    cols = st.columns(len(soviet_tales))
    for i, tale_name in enumerate(soviet_tales):
        if tale_name in all_tales:
            with cols[i]:
                with st.container():
                    # Картинка
                    cover_path = tales[tale_name].get("cover", "")
                    if cover_path and os.path.exists(cover_path):
                        st.image(cover_path, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨", use_container_width=True)
                    
                    # Название и описание
                    st.markdown(f"#### {tale_name}")
                    st.markdown(tales[tale_name].get("description", ""))
                    
                    # Кнопка
                    if st.button("✨ Начать", key=f"choose_{tale_name}", use_container_width=True):
                        start_tale(tale_name)
                        st.rerun()

    # Новые сказки
    if new_tales:
        st.markdown("## 🆕 Новые сказки")
        cols = st.columns(len(new_tales))
        for i, tale_name in enumerate(new_tales):
            if tale_name in all_tales:
                with cols[i]:
                    with st.container():
                        cover_path = tales[tale_name].get("cover", "")
                        if cover_path and os.path.exists(cover_path):
                            st.image(cover_path, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨", use_container_width=True)
                        
                        st.markdown(f"#### {tale_name}")
                        st.markdown(tales[tale_name].get("description", ""))
                        
                        if st.button("✨ Начать", key=f"choose_{tale_name}_new", use_container_width=True):
                            start_tale(tale_name)
                            st.rerun()

    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны. Если хотите поддержать проект, воспользуйтесь кнопкой в боковой панели.*")

else:
    # Отображение сказки
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    current_scene = st.session_state.scenes.get(st.session_state.scene_id)

    if current_scene:
        if not current_scene.get("options"):
            if current_scene.get("ending_type") and current_scene.get("ending_number"):
                ending_type = current_scene["ending_type"]
                ending_num = current_scene["ending_number"]
                type_emoji = {"happy": "😊", "sad": "😢", "neutral": "😐"}.get(ending_type, "🌟")
                
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
                    st.info("😕 Это не счастливый конец. Попробуй пройти сказку снова!")
                
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Всего концовок: **{opened} / {total}**.*")
            else:
                st.markdown("---")
                st.markdown("🎉 **Конец сказки!**")
            
            st.markdown("---")
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Вернуться назад", use_container_width=True):
                    go_back()
            if st.button("🔄 Начать заново", use_container_width=True):
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
                if st.button("↩️ Назад", use_container_width=True):
                    go_back()
    else:
        st.error("⚠️ Сцена не найдена")
        if st.button("⬅️ К выбору сказок", use_container_width=True):
            reset_to_main()
            st.rerun()
