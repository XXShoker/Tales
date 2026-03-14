import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Простые стили ---
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
    
    h1 {
        color: #5d3a1a !important;
        font-size: 3rem;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background-color: #f5e9d8;
    }
    
    /* Кнопка доната */
    .stLinkButton a {
        background-color: #d4b68a;
        color: #2a1c0e !important;
        border-radius: 50px;
        padding: 15px 25px;
        text-decoration: none;
        font-weight: bold;
    }
    
    /* Кнопки */
    .stButton > button {
        background-color: #e6d5b8;
        color: #2a1c0e;
        border: 1px solid #b5926a;
        border-radius: 30px;
        font-family: 'Open Sans', sans-serif;
    }
    
    /* Карточки */
    div[data-testid="column"] > div {
        background-color: #fffaf0;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #e9d9c4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        height: 600px;
        display: flex;
        flex-direction: column;
    }
    
    div[data-testid="column"] img {
        width: 100%;
        height: 350px;
        object-fit: cover;
        border-radius: 15px;
        border: 1px solid #d4b68a;
        margin-bottom: 15px;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Инициализация ---
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
    for scene in tale["scenes"].values():
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
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown("Вы сами выбираете, как развернётся история")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    if st.session_state.selected_tale:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown("---")
        st.markdown(f"### {st.session_state.selected_tale}")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено: **{opened}/{total}**")
        if st.button("🔄 Сменить сказку"):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    # Просто две колонки с карточками
    col1, col2 = st.columns(2)
    
    with col1:
        # Колобок
        with st.container():
            if os.path.exists("images/kolobok_cover.jpg"):
                st.image("images/kolobok_cover.jpg", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨", use_container_width=True)
            st.markdown("### Колобок")
            st.markdown("Помоги Колобку убежать от всех зверей и найти настоящих друзей!")
            if st.button("✨ Начать", key="start_kolobok", use_container_width=True):
                start_tale("Колобок")
                st.rerun()
        
        # Золотая рыбка
        with st.container():
            if os.path.exists("images/rybka_cover.jpg"):
                st.image("images/rybka_cover.jpg", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨", use_container_width=True)
            st.markdown("### Золотая рыбка")
            st.markdown("Старик поймал золотую рыбку. Хватит ли мудрости не быть жадным?")
            if st.button("✨ Начать", key="start_rybka", use_container_width=True):
                start_tale("Золотая рыбка")
                st.rerun()
    
    with col2:
        # Теремок
        with st.container():
            if os.path.exists("images/teremok_cover.jpg"):
                st.image("images/teremok_cover.jpg", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨", use_container_width=True)
            st.markdown("### Теремок")
            st.markdown("Построй свой теремок и реши, кого пускать, а кого нет.")
            if st.button("✨ Начать", key="start_teremok", use_container_width=True):
                start_tale("Теремок")
                st.rerun()
        
        # Курочка Ряба
        with st.container():
            if os.path.exists("images/ryaba_cover.jpg"):
                st.image("images/ryaba_cover.jpg", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨", use_container_width=True)
            st.markdown("### Курочка Ряба")
            st.markdown("Курочка снесла золотое яичко. Что делать с разбитым яйцом?")
            if st.button("✨ Начать", key="start_ryaba", use_container_width=True):
                start_tale("Курочка Ряба")
                st.rerun()

else:
    # Сама сказка
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    current = st.session_state.scenes.get(st.session_state.scene_id)
    if current:
        if not current.get("options"):
            if current.get("ending_type"):
                ending_id = f"{current['ending_type']}_{current['ending_number']}"
                if ending_id not in st.session_state.achieved_endings.get(st.session_state.selected_tale, set()):
                    st.session_state.achieved_endings.setdefault(st.session_state.selected_tale, set()).add(ending_id)
                    st.rerun()
                st.success(f"🎉 Концовка #{current['ending_number']}")
            else:
                st.success("🎉 Конец!")
            
            if st.button("🔄 Начать заново"):
                start_tale(st.session_state.selected_tale)
                st.rerun()
        else:
            for opt in current["options"]:
                if st.button(opt["text"]):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Назад"):
                    go_back()
