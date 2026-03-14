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
        color: #2c1e0e !important;
        text-align: center;
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 2.2rem;
        margin: 40px 0 20px 0;
        padding-left: 15px;
        border-left: 5px solid #b5926a;
        color: #2c1e0e !important;
        font-family: 'Cormorant Garamond', serif;
    }
    
    /* Текст - тёмный */
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
        font-size: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stLinkButton a:hover {
        background-color: #b5926a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
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
    
    /* КАРТОЧКИ - используем Streamlit container вместо HTML div */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #fffaf0;
        border-radius: 20px;
        padding: 25px;
        border: 2px solid #e9d9c4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        width: 100%;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Изображения */
    div[data-testid="stVerticalBlock"] img {
        width: 100%;
        height: 500px;
        object-fit: cover;
        border-radius: 15px;
        border: 2px solid #d4b68a;
        margin-bottom: 20px;
    }
    
    /* Заголовок сказки */
    div[data-testid="stVerticalBlock"] h3 {
        font-size: 2rem;
        margin: 0 0 15px 0;
        color: #2c1e0e !important;
    }
    
    /* Описание сказки */
    div[data-testid="stVerticalBlock"] p {
        font-size: 1.1rem;
        margin: 0 0 20px 0;
        color: #1a1309 !important;
    }
    
    /* Кнопка в карточке */
    div[data-testid="stVerticalBlock"] .stButton {
        margin-top: 20px;
    }
    
    /* Центрирование контейнера */
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Сообщения чата */
    .stChatMessage {
        background-color: #fffaf0 !important;
        border: 2px solid #e9d9c4;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px;
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background-color: #e6d5b8 !important;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
        border-radius: 10px;
    }
    
    /* Плавающая кнопка для возврата */
    .floating-home-button {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
        background-color: #e6d5b8;
        border: 2px solid #b5926a;
        border-radius: 40px;
        padding: 10px 20px;
        font-size: 1rem;
        font-weight: 600;
        color: #2a1c0e;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .floating-home-button:hover {
        background-color: #d4b68a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 600px) {
        div[data-testid="stVerticalBlock"] img {
            height: 350px;
        }
        div[data-testid="stVerticalBlock"] h3 {
            font-size: 1.5rem;
        }
        div[data-testid="stVerticalBlock"] p {
            font-size: 0.95rem;
        }
        h1 {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- JavaScript для плавающей кнопки ---
st.markdown("""
<script>
    function createFloatingHomeButton() {
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('tale')) {
            return;
        }
        
        const btn = document.createElement('div');
        btn.className = 'floating-home-button';
        btn.innerHTML = '🏠 К списку сказок';
        btn.onclick = function() {
            window.location.href = window.location.pathname;
        };
        document.body.appendChild(btn);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createFloatingHomeButton);
    } else {
        createFloatingHomeButton();
    }
</script>
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
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
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
    # Центрированный контейнер
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Определяем категории
    all_tales = list(tales.keys())
    
    # Категория 1: Классические сказки
    classic_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    
    # Категория 2: Приключения и фэнтези
    adventure_tales = ["Путешествие в Волшебный лес"]
    
    # Категория 3: 16+ (для взрослых)
    adult_tales = ["Хроники разбитых часов: Детектив времени", "Мелодия дождя"]
    
    # Отображаем категории по одной карточке
    if classic_tales:
        st.markdown('<div class="section-header">📚 Классические сказки</div>', unsafe_allow_html=True)
        classic_list = [t for t in classic_tales if t in all_tales]
        for tale_name in classic_list:
            with st.container():
                cover_path = tales[tale_name].get("cover", "")
                if cover_path and os.path.exists(cover_path):
                    st.image(cover_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨", use_container_width=True)
                st.markdown(f"### {tale_name}")
                st.markdown(tales[tale_name].get("description", ""))
                if st.button("✨ Начать", key=f"classic_{tale_name}", use_container_width=True):
                    start_tale(tale_name)
                    st.rerun()
    
    if adventure_tales:
        st.markdown('<div class="section-header">🧚 Приключения и фэнтези</div>', unsafe_allow_html=True)
        adventure_list = [t for t in adventure_tales if t in all_tales]
        for tale_name in adventure_list:
            with st.container():
                cover_path = tales[tale_name].get("cover", "")
                if cover_path and os.path.exists(cover_path):
                    st.image(cover_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨", use_container_width=True)
                st.markdown(f"### {tale_name}")
                st.markdown(tales[tale_name].get("description", ""))
                if st.button("✨ Начать", key=f"adventure_{tale_name}", use_container_width=True):
                    start_tale(tale_name)
                    st.rerun()
    
    if adult_tales:
        st.markdown('<div class="section-header">🔞 16+ Детективы и романтика</div>', unsafe_allow_html=True)
        adult_list = [t for t in adult_tales if t in all_tales]
        for tale_name in adult_list:
            with st.container():
                cover_path = tales[tale_name].get("cover", "")
                if cover_path and os.path.exists(cover_path):
                    st.image(cover_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨", use_container_width=True)
                st.markdown(f"### {tale_name}")
                st.markdown(tales[tale_name].get("description", ""))
                if st.button("✨ Начать", key=f"adult_{tale_name}", use_container_width=True):
                    start_tale(tale_name)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны. Если хотите поддержать проект, воспользуйтесь кнопкой в боковой панели.*")

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
                emoji = {"happy": "😊", "sad": "😢", "neutral": "😐", "secret": "🤫"}.get(current["ending_type"], "🎉")
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
                    if st.button("↩️ Вернуться назад", use_container_width=True):
                        go_back()
            with col2:
                if st.button("🔄 Начать заново", use_container_width=True):
                    start_tale(st.session_state.selected_tale)
                    st.rerun()
        else:
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
