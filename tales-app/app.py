import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Стили с !important для принудительного применения ---
st.markdown("""
<style>
    /* Подключаем шрифты */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    /* Общий фон */
    .stApp {
        background-color: #fef9e7 !important;
    }
    
    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #2c1e0e !important;
        font-weight: 600 !important;
    }
    
    h1 {
        font-size: 3rem !important;
        border-bottom: 3px solid #d4b68a !important;
        padding-bottom: 15px !important;
    }
    
    /* Текст */
    p, li, .stMarkdown, .stText, .stChatMessage p {
        font-family: 'Open Sans', sans-serif !important;
        color: #1a1309 !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background-color: #f5e9d8 !important;
    }
    
    /* Кнопка доната */
    .stLinkButton a {
        background-color: #d4b68a !important;
        color: #2a1c0e !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        text-decoration: none !important;
        font-weight: bold !important;
        border: 2px solid #b5926a !important;
        display: inline-block !important;
        width: 100% !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }
    
    .stLinkButton a:hover {
        background-color: #b5926a !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Все кнопки */
    .stButton > button {
        background-color: #e6d5b8 !important;
        color: #2a1c0e !important;
        border: 2px solid #b5926a !important;
        border-radius: 40px !important;
        padding: 15px 20px !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        font-family: 'Open Sans', sans-serif !important;
        width: 100% !important;
        min-height: 60px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        background-color: #d4b68a !important;
        border-color: #8b6b4f !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* КАРТОЧКИ СКАЗОК - 1000px с !important */
    div[data-testid="column"] > div {
        background-color: #fffaf0 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        border: 2px solid #e9d9c4 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        height: 1000px !important;  /* ПРИНУДИТЕЛЬНО 1000px */
        min-height: 1000px !important;
        max-height: 1000px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="column"] > div:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
        border-color: #d4b68a !important;
    }
    
    /* Изображения - 500px с !important */
    div[data-testid="column"] img {
        width: 100% !important;
        height: 500px !important;  /* ПРИНУДИТЕЛЬНО 500px */
        min-height: 500px !important;
        max-height: 500px !important;
        object-fit: cover !important;
        border-radius: 15px !important;
        border: 2px solid #d4b68a !important;
        margin-bottom: 20px !important;
    }
    
    /* Заголовок сказки */
    div[data-testid="column"] h3 {
        font-size: 2.5rem !important;
        margin: 0 0 15px 0 !important;
        color: #2c1e0e !important;
    }
    
    /* Описание сказки */
    div[data-testid="column"] p {
        font-size: 1.2rem !important;
        margin: 0 0 25px 0 !important;
        flex-grow: 1 !important;
        color: #1a1309 !important;
        line-height: 1.5 !important;
        max-height: 200px !important;
        overflow-y: auto !important;
        padding-right: 10px !important;
    }
    
    /* Кнопка в карточке */
    div[data-testid="column"] .stButton {
        margin-top: auto !important;
        width: 100% !important;
    }
    
    /* Сообщения чата */
    .stChatMessage {
        background-color: #fffaf0 !important;
        border: 2px solid #e9d9c4 !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px !important;
    }
    
    .stChatMessage p {
        color: #1a1309 !important;
        font-size: 1.1rem !important;
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background-color: #e6d5b8 !important;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
        border-radius: 10px !important;
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 2.2rem !important;
        margin: 40px 0 20px 0 !important;
        padding-left: 15px !important;
        border-left: 5px solid #b5926a !important;
        color: #2c1e0e !important;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 600px) {
        div[data-testid="column"] > div {
            height: 800px !important;
            min-height: 800px !important;
            max-height: 800px !important;
            padding: 20px !important;
        }
        div[data-testid="column"] img {
            height: 400px !important;
            min-height: 400px !important;
            max-height: 400px !important;
        }
        div[data-testid="column"] h3 {
            font-size: 2rem !important;
        }
        div[data-testid="column"] p {
            font-size: 1rem !important;
        }
        h1 {
            font-size: 2rem !important;
        }
        .section-header {
            font-size: 1.8rem !important;
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
    st.markdown("Вы сами выбираете, как развернётся история. Все сказки абсолютно бесплатны.")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", width='stretch')
    
    if st.session_state.selected_tale:
        st.markdown("---")
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
        if st.button("🔄 Сменить сказку", width='stretch'):
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
                st.image("images/kolobok_cover.jpg", width='stretch')
            else:
                st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨+Колобок", width='stretch')
            st.markdown("### Колобок")
            st.markdown("Помоги Колобку убежать от всех зверей и найти настоящих друзей!")
            if st.button("✨ Начать", key="start_kolobok", width='stretch'):
                start_tale("Колобок")
                st.rerun()
        
        # Золотая рыбка
        with st.container():
            if os.path.exists("images/rybka_cover.jpg"):
                st.image("images/rybka_cover.jpg", width='stretch')
            else:
                st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨+Золотая+рыбка", width='stretch')
            st.markdown("### Золотая рыбка")
            st.markdown("Старик поймал золотую рыбку. Хватит ли мудрости не быть жадным?")
            if st.button("✨ Начать", key="start_rybka", width='stretch'):
                start_tale("Золотая рыбка")
                st.rerun()
    
    with col2:
        # Теремок
        with st.container():
            if os.path.exists("images/teremok_cover.jpg"):
                st.image("images/teremok_cover.jpg", width='stretch')
            else:
                st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨+Теремок", width='stretch')
            st.markdown("### Теремок")
            st.markdown("Построй свой теремок и реши, кого пускать, а кого нет.")
            if st.button("✨ Начать", key="start_teremok", width='stretch'):
                start_tale("Теремок")
                st.rerun()
        
        # Курочка Ряба
        with st.container():
            if os.path.exists("images/ryaba_cover.jpg"):
                st.image("images/ryaba_cover.jpg", width='stretch')
            else:
                st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨+Курочка+Ряба", width='stretch')
            st.markdown("### Курочка Ряба")
            st.markdown("Курочка снесла золотое яичко. Что делать с разбитым яйцом?")
            if st.button("✨ Начать", key="start_ryaba", width='stretch'):
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
                    st.image("images/forest_cover.jpg", width='stretch')
                else:
                    st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨+Волшебный+лес", width='stretch')
                st.markdown("### Путешествие в Волшебный лес")
                st.markdown("Отправляйся в загадочный лес, где живут говорящие звери и феи!")
                if st.button("✨ Начать", key="start_forest", width='stretch'):
                    start_tale("Путешествие в Волшебный лес")
                    st.rerun()

else:
    # Сама сказка
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    current = st.session_state.scenes.get(st.session_state.scene_id)
    if current:
        if not current.get("options"):
            if current.get("ending_type") and current.get("ending_number"):
                ending_id = f"{current['ending_type']}_{current['ending_number']}"
            else:
                ending_id = current["text"][:100]
            
            if st.session_state.selected_tale not in st.session_state.achieved_endings:
                st.session_state.achieved_endings[st.session_state.selected_tale] = set()
            
            if ending_id not in st.session_state.achieved_endings[st.session_state.selected_tale]:
                st.session_state.achieved_endings[st.session_state.selected_tale].add(ending_id)
                st.rerun()
            
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
            
            opened, total = get_ending_stats(st.session_state.selected_tale)
            st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if len(st.session_state.scene_history) > 1:
                    if st.button("↩️ Вернуться назад", width='stretch'):
                        go_back()
            with col2:
                if st.button("🔄 Начать заново", width='stretch'):
                    start_tale(st.session_state.selected_tale)
                    st.rerun()
        else:
            st.markdown("### Твой выбор:")
            for opt in current["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", width='stretch'):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад к выбору", width='stretch'):
                    go_back()
    else:
        st.error("⚠️ Сцена не найдена")
        if st.button("⬅️ К выбору сказок", width='stretch'):
            reset_to_main()
            st.rerun()
