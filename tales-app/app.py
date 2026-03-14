import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Минимальные стили ---
st.markdown("""
<style>
    /* Базовые цвета */
    .stApp { background-color: #fef9e7; }
    section[data-testid="stSidebar"] { background-color: #f5e9d8; }
    
    /* Карточки - ФИКСИРОВАННАЯ ВЫСОТА */
    div[data-testid="column"] {
        height: 1000px !important;
    }
    
    div[data-testid="column"] > div {
        background-color: #fffaf0;
        border-radius: 20px;
        padding: 20px;
        border: 2px solid #e9d9c4;
        height: 1000px !important;
        display: flex;
        flex-direction: column;
    }
    
    /* Изображения - ФИКСИРОВАННАЯ ВЫСОТА */
    div[data-testid="column"] img {
        height: 500px !important;
        width: 100% !important;
        object-fit: cover;
        border-radius: 15px;
        border: 2px solid #d4b68a;
        margin-bottom: 15px;
    }
    
    /* Кнопка всегда внизу */
    div[data-testid="column"] .stButton {
        margin-top: auto;
    }
    
    /* Текст */
    h1, h2, h3 { color: #2c1e0e; }
    p { color: #1a1309; }
    
    /* Прогресс-бар */
    .stProgress > div > div { background-color: #b5926a; }
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
    st.markdown("Вы сами выбираете историю")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    if st.session_state.selected_tale:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown("---")
        st.markdown(f"### {st.session_state.selected_tale}")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено: **{opened}/{total}**")
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    col1, col2 = st.columns(2)
    
    with col1:
        # Колобок
        img = "images/kolobok_cover.jpg" if os.path.exists("images/kolobok_cover.jpg") else "https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨"
        st.image(img, use_container_width=True)
        st.markdown("### Колобок")
        st.markdown("Помоги Колобку убежать от всех зверей")
        if st.button("✨ Начать", key="k1", use_container_width=True):
            start_tale("Колобок")
            st.rerun()
        
        # Золотая рыбка
        img = "images/rybka_cover.jpg" if os.path.exists("images/rybka_cover.jpg") else "https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨"
        st.image(img, use_container_width=True)
        st.markdown("### Золотая рыбка")
        st.markdown("Старик поймал золотую рыбку")
        if st.button("✨ Начать", key="r1", use_container_width=True):
            start_tale("Золотая рыбка")
            st.rerun()
    
    with col2:
        # Теремок
        img = "images/teremok_cover.jpg" if os.path.exists("images/teremok_cover.jpg") else "https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨"
        st.image(img, use_container_width=True)
        st.markdown("### Теремок")
        st.markdown("Построй свой теремок")
        if st.button("✨ Начать", key="t1", use_container_width=True):
            start_tale("Теремок")
            st.rerun()
        
        # Курочка Ряба
        img = "images/ryaba_cover.jpg" if os.path.exists("images/ryaba_cover.jpg") else "https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨"
        st.image(img, use_container_width=True)
        st.markdown("### Курочка Ряба")
        st.markdown("Курочка снесла золотое яичко")
        if st.button("✨ Начать", key="kr1", use_container_width=True):
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
            if st.button("🔄 Начать заново", use_container_width=True):
                start_tale(st.session_state.selected_tale)
                st.rerun()
        else:
            for opt in current["options"]:
                if st.button(opt["text"], use_container_width=True):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Назад", use_container_width=True):
                    go_back()
