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
    
    /* Общий фон */
    .stApp {
        background: linear-gradient(135deg, #fef9e7 0%, #fcf3e0 100%);
    }
    
    /* Заголовки */
    h1, h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif;
        color: #5d3a1a;
        font-weight: 600;
    }
    
    h1 {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5e9d8 0%, #ecdcc5 100%);
        border-right: 2px solid #d4b68a;
        padding: 20px;
    }
    
    /* Кнопка доната */
    .stLinkButton a {
        background: linear-gradient(135deg, #d4b68a, #b5926a) !important;
        color: #2a1c0e !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        text-decoration: none !important;
        border: 2px solid #8b6b4f !important;
        transition: all 0.3s ease !important;
        display: inline-block !important;
        width: 100% !important;
        text-align: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    .stLinkButton a:hover {
        background: linear-gradient(135deg, #b5926a, #9b7e62) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Заголовки секций */
    .section-title {
        font-size: 2.2rem;
        margin: 40px 0 20px 0;
        padding-left: 15px;
        border-left: 5px solid #b5926a;
        background: linear-gradient(90deg, rgba(213,182,138,0.2) 0%, rgba(255,255,255,0) 100%);
        padding: 15px 25px;
        font-family: 'Cormorant Garamond', serif;
        color: #5d3a1a;
    }
    
    /* Контейнер для колонок */
    .row {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    /* Колонка */
    .column {
        flex: 1;
        min-width: 0;
    }
    
    /* Карточка сказки */
    .tale-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 25px rgba(93,58,26,0.1);
        border: 2px solid #e9d9c4;
        transition: all 0.3s ease;
        height: 100%;
        margin-bottom: 20px;
    }
    
    .tale-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(93,58,26,0.2);
        border-color: #b5926a;
    }
    
    .tale-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 15px;
        border: 2px solid #d4b68a;
        margin-bottom: 15px;
    }
    
    .tale-card h3 {
        font-size: 1.8rem;
        margin: 0 0 10px 0;
        color: #5d3a1a;
    }
    
    .tale-card p {
        font-size: 1rem;
        color: #3e2c1b;
        margin: 0 0 20px 0;
        line-height: 1.5;
        min-height: 60px;
    }
    
    /* Кнопка "Начать" */
    .start-btn {
        background: linear-gradient(135deg, #e6d5b8, #d4b68a);
        color: #2a1c0e;
        border: 2px solid #b5926a;
        border-radius: 40px;
        padding: 12px 20px;
        font-size: 1.2rem;
        font-weight: 700;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        font-family: 'Open Sans', sans-serif;
    }
    
    .start-btn:hover {
        background: linear-gradient(135deg, #d4b68a, #b5926a);
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.1);
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background: linear-gradient(90deg, #b5926a, #8b6b4f) !important;
        border-radius: 10px !important;
    }
    
    /* Сообщения чата */
    .stChatMessage {
        background: white !important;
        border-radius: 20px !important;
        padding: 12px 20px !important;
        border: 2px solid #e9d9c4 !important;
        margin-bottom: 10px !important;
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background: linear-gradient(135deg, #e6d5b8, #d4b68a) !important;
        border-color: #b5926a !important;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 600px) {
        .row {
            flex-direction: column;
        }
        h1 {
            font-size: 2rem;
        }
        .section-title {
            font-size: 1.8rem;
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
if "total_endings" not in st.session_state:
    st.session_state.total_endings = {}

def count_total_endings(tale_name):
    if tale_name in st.session_state.total_endings:
        return st.session_state.total_endings[tale_name]
    tale = tales.get(tale_name)
    if not tale:
        return 0
    count = 0
    for scene in tale["scenes"].values():
        if scene.get("options") == []:
            count += 1
    st.session_state.total_endings[tale_name] = count
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
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []

def get_image_html(tale_name):
    cover_path = tales[tale_name].get("cover", "")
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{img_data}" alt="{tale_name}">'
        except:
            pass
    return f'<img src="https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+{tale_name}" alt="{tale_name}">'

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown("Добро пожаловать в мир интерактивных сказок! Вы сами выбираете, как развернётся история. Все сказки абсолютно бесплатны.")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", width='stretch')
    
    if st.session_state.selected_tale:
        st.markdown("---")
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено: **{opened} / {total}**")
        if st.button("🔄 Сменить сказку", width='stretch'):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    all_tales = list(tales.keys())
    soviet = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new = ["Путешествие в Волшебный лес"]
    
    # Советские сказки
    st.markdown('<div class="section-title">📚 Советские сказки</div>', unsafe_allow_html=True)
    
    # Левая колонка
    col1, col2 = st.columns(2)
    
    with col1:
        for name in soviet[:2]:
            if name in all_tales:
                with st.container():
                    st.markdown(f'<div class="tale-card">', unsafe_allow_html=True)
                    cover_path = tales[name].get("cover", "")
                    if cover_path and os.path.exists(cover_path):
                        st.image(cover_path, width='stretch')
                    else:
                        st.image("https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+Сказка", width='stretch')
                    st.markdown(f"### {name}")
                    st.markdown(tales[name].get("description", ""))
                    if st.button("✨ Начать", key=f"btn_{name}", width='stretch'):
                        start_tale(name)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        for name in soviet[2:4]:
            if name in all_tales:
                with st.container():
                    st.markdown(f'<div class="tale-card">', unsafe_allow_html=True)
                    cover_path = tales[name].get("cover", "")
                    if cover_path and os.path.exists(cover_path):
                        st.image(cover_path, width='stretch')
                    else:
                        st.image("https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+Сказка", width='stretch')
                    st.markdown(f"### {name}")
                    st.markdown(tales[name].get("description", ""))
                    if st.button("✨ Начать", key=f"btn_{name}_2", width='stretch'):
                        start_tale(name)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Новые сказки
    if new:
        st.markdown('<div class="section-title">🆕 Новые сказки</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            for name in new:
                if name in all_tales:
                    with st.container():
                        st.markdown(f'<div class="tale-card">', unsafe_allow_html=True)
                        cover_path = tales[name].get("cover", "")
                        if cover_path and os.path.exists(cover_path):
                            st.image(cover_path, width='stretch')
                        else:
                            st.image("https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+Сказка", width='stretch')
                        st.markdown(f"### {name}")
                        st.markdown(tales[name].get("description", ""))
                        if st.button("✨ Начать", key=f"btn_new_{name}", width='stretch'):
                            start_tale(name)
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

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
                type_emoji = {"happy": "😊", "sad": "😢", "neutral": "😐", "secret": "🤫"}.get(ending_type, "🌟")
                
                tale = st.session_state.selected_tale
                ending_id = f"{ending_type}_{ending_num}"
                
                if tale not in st.session_state.achieved_endings:
                    st.session_state.achieved_endings[tale] = set()
                if ending_id not in st.session_state.achieved_endings[tale]:
                    st.session_state.achieved_endings[tale].add(ending_id)
                    st.rerun()
                
                st.markdown("---")
                st.markdown(f"## {type_emoji} **Концовка #{ending_num}**")
                st.markdown(f"**Тип:** {ending_type.capitalize()}")
                
                if ending_type == "happy":
                    st.success("🎉 Поздравляем! Это счастливый конец!")
                else:
                    st.info("😕 Это не счастливый конец. Попробуй пройти сказку снова!")
                
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            else:
                st.markdown("---")
                st.markdown("🎉 **Конец сказки!**")
            
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
            for opt in current_scene["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", width='stretch'):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад", width='stretch'):
                    go_back()
    else:
        st.error("⚠️ Сцена не найдена. Вернитесь к выбору сказок.")
        if st.button("⬅️ К выбору сказок", width='stretch'):
            reset_to_main()
            st.rerun()
