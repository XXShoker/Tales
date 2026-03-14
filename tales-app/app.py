import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Стили ---
st.markdown("""
<style>
    /* Подключаем шрифты */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    /* Общий фон */
    .stApp {
        background-color: #fef9e7;
    }
    
    /* Заголовки - тёмные и читаемые */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif;
        color: #2c1e0e !important;
        font-weight: 600;
    }
    
    h1 {
        font-size: 3rem;
        border-bottom: 3px solid #d4b68a;
        padding-bottom: 15px;
    }
    
    /* Текст */
    p, li, .stMarkdown, .stText, .stChatMessage p {
        font-family: 'Open Sans', sans-serif;
        color: #1a1309 !important;
        font-size: 1.1rem;
        line-height: 1.6;
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
        border: 2px solid #b5926a;
        display: inline-block;
        width: 100%;
        text-align: center;
    }
    
    /* Все кнопки */
    .stButton > button {
        background-color: #e6d5b8;
        color: #2a1c0e;
        border: 2px solid #b5926a;
        border-radius: 40px;
        padding: 15px 20px !important;
        font-size: 1.2rem !important;
        font-weight: 600;
        font-family: 'Open Sans', sans-serif;
        width: 100%;
        min-height: 60px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: #d4b68a;
        border-color: #8b6b4f;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Карточки сказок */
    div[data-testid="column"] > div {
        background-color: #fffaf0;
        border-radius: 20px;
        padding: 25px;
        border: 2px solid #e9d9c4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        height: 650px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"] > div:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        border-color: #d4b68a;
    }
    
    /* Изображения */
    div[data-testid="column"] img {
        width: 100%;
        height: 350px;
        object-fit: cover;
        border-radius: 15px;
        border: 2px solid #d4b68a;
        margin-bottom: 15px;
    }
    
    /* Заголовок сказки */
    div[data-testid="column"] h3 {
        font-size: 2rem;
        margin: 0 0 10px 0;
        color: #2c1e0e !important;
    }
    
    /* Описание сказки */
    div[data-testid="column"] p {
        font-size: 1rem;
        margin: 0 0 20px 0;
        flex-grow: 1;
        color: #1a1309 !important;
        line-height: 1.5;
    }
    
    /* Кнопка в карточке */
    div[data-testid="column"] .stButton {
        margin-top: auto;
        width: 100%;
    }
    
    /* Сообщения чата */
    .stChatMessage {
        background-color: #fffaf0 !important;
        border: 2px solid #e9d9c4;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px;
    }
    
    .stChatMessage p {
        color: #1a1309 !important;
        font-size: 1.1rem;
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background-color: #e6d5b8 !important;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
        border-radius: 10px;
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 2.2rem;
        margin: 40px 0 20px 0;
        padding-left: 15px;
        border-left: 5px solid #b5926a;
        color: #2c1e0e !important;
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
    st.session_state.achieved_endings = {}  # СЧЕТЧИК ЗДЕСЬ!

def count_total_endings(tale_name):
    """Подсчитывает общее количество концовок в сказке"""
    tale = tales.get(tale_name)
    if not tale:
        return 0
    count = 0
    for scene in tale["scenes"].values():
        if scene.get("options") == []:
            count += 1
    return count

def get_ending_stats(tale_name):
    """Возвращает (сколько открыто, сколько всего)"""
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
    st.markdown("Вы сами выбираете, как развернётся история. Все сказки абсолютно бесплатны.")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    # СЧЕТЧИК - отображается только когда выбрана сказка
    if st.session_state.selected_tale:
        st.markdown("---")
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    # Две колонки
    col1, col2 = st.columns(2)
    
    with col1:
        # Колобок
        with st.container():
            if os.path.exists("images/kolobok_cover.jpg"):
                st.image("images/kolobok_cover.jpg", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨+Колобок", use_container_width=True)
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
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨+Золотая+рыбка", use_container_width=True)
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
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨+Теремок", use_container_width=True)
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
                st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨+Курочка+Ряба", use_container_width=True)
            st.markdown("### Курочка Ряба")
            st.markdown("Курочка снесла золотое яичко. Что делать с разбитым яйцом?")
            if st.button("✨ Начать", key="start_ryaba", use_container_width=True):
                start_tale("Курочка Ряба")
                st.rerun()

    # Новая сказка
    if "Путешествие в Волшебный лес" in tales:
        st.markdown("---")
        st.markdown("## 🆕 Новые сказки")
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                if os.path.exists("images/forest_cover.jpg"):
                    st.image("images/forest_cover.jpg", use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨+Волшебный+лес", use_container_width=True)
                st.markdown("### Путешествие в Волшебный лес")
                st.markdown("Отправляйся в загадочный лес, где живут говорящие звери и феи!")
                if st.button("✨ Начать", key="start_forest", use_container_width=True):
                    start_tale("Путешествие в Волшебный лес")
                    st.rerun()

else:
    # Сама сказка
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    current = st.session_state.scenes.get(st.session_state.scene_id)
    if current:
        if not current.get("options"):  # Это концовка
            # Запоминаем концовку
            if current.get("ending_type") and current.get("ending_number"):
                ending_id = f"{current['ending_type']}_{current['ending_number']}"
            else:
                ending_id = current["text"][:100]  # для старых сказок
            
            if st.session_state.selected_tale not in st.session_state.achieved_endings:
                st.session_state.achieved_endings[st.session_state.selected_tale] = set()
            
            if ending_id not in st.session_state.achieved_endings[st.session_state.selected_tale]:
                st.session_state.achieved_endings[st.session_state.selected_tale].add(ending_id)
                st.rerun()
            
            # Показываем сообщение о концовке
            st.markdown("---")
            if current.get("ending_type"):
                emoji = {"happy": "😊", "sad": "😢", "neutral": "😐"}.get(current["ending_type"], "🎉")
                st.markdown(f"## {emoji} **Концовка #{current['ending_number']}**")
                if current["ending_type"] == "happy":
                    st.success("🎉 Поздравляем! Это счастливый конец!")
                else:
                    st.info("😕 Это не счастливый конец. Попробуй пройти сказку снова!")
            else:
                st.markdown("## 🎉 **Конец сказки!**")
            
            # Показываем прогресс
            opened, total = get_ending_stats(st.session_state.selected_tale)
            st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            
            # Кнопки
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if len(st.session_state.scene_history) > 1:
                    if st.button("↩️ Вернуться назад", use_container_width=True):
                        go_back()
            with col2:
                if st.button("🔄 Начать заново", use_container_width=True):
                    start_tale(st.session_state.selected_tale)
                    st.rerun()
        else:
            # Обычный выбор
            st.markdown("### Твой выбор:")
            for opt in current["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", use_container_width=True):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад к выбору", use_container_width=True):
                    go_back()
    else:
        st.error("⚠️ Сцена не найдена")
        if st.button("⬅️ К выбору сказок", use_container_width=True):
            reset_to_main()
            st.rerun()
