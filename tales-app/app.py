import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="centered")

# --- Стили (только базовые, без каруселей) ---
st.markdown("""
<style>
    /* Подключаем шрифты */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    /* Общий фон */
    .stApp {
        background-color: #fef9e7;
    }
    
    /* Заголовки */
    h1, h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif;
        color: #5d3a1a;
    }
    
    /* Текст */
    p, li, .stMarkdown {
        font-family: 'Open Sans', sans-serif;
        color: #3e2c1b;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background-color: #f5e9d8 !important;
    }
    
    /* Кнопки */
    .stButton > button {
        font-family: 'Open Sans', sans-serif;
        background-color: #e6d5b8;
        color: #3e2c1b;
        border: 1px solid #b5926a;
        border-radius: 30px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #d4b68a;
        border-color: #8b6b4f;
    }
    
    /* Карточки сказок */
    div[data-testid="column"] > div {
        background-color: #fffaf0;
        border-radius: 20px;
        padding: 15px;
        border: 1px solid #e9d9c4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    /* Изображения */
    div[data-testid="column"] img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        border: 1px solid #d4b68a;
        margin-bottom: 10px;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
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
        "Вы сами выбираете, как развернётся история."
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
        
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    all_tales = list(tales.keys())
    
    # Две колонки для карточек
    cols = st.columns(2)
    
    for idx, tale_name in enumerate(all_tales):
        with cols[idx % 2]:
            with st.container():
                # Обложка
                cover_path = tales[tale_name].get("cover", "")
                if cover_path and os.path.exists(cover_path):
                    st.image(cover_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+Сказка", use_container_width=True)
                
                # Название и описание
                st.markdown(f"#### {tale_name}")
                if tales[tale_name].get("description"):
                    st.markdown(tales[tale_name]["description"])
                
                # Кнопка начала
                if st.button(f"✨ Начать", key=f"choose_{tale_name}", use_container_width=True):
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
            col1, col2 = st.columns(2)
            with col1:
                if len(st.session_state.scene_history) > 1:
                    if st.button("↩️ Назад", use_container_width=True):
                        go_back()
            with col2:
                if st.button("🔄 Заново", use_container_width=True):
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
