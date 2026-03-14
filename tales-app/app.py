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
        background: linear-gradient(135deg, #fef9e7 0%, #fcf3e0 100%);
    }
    
    /* Заголовки */
    h1, h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif;
        color: #5d3a1a;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    h1 {
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        border-bottom: 3px solid #d4b68a;
        padding-bottom: 15px;
        margin-bottom: 30px;
        color: #5d3a1a !important;  /* Тёмно-коричневый цвет, видно на светлом фоне */
    }
    
    /* Текст */
    p, li, .stMarkdown, .stText {
        font-family: 'Open Sans', sans-serif;
        color: #3e2c1b;
        line-height: 1.6;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5e9d8 0%, #ecdcc5 100%);
        border-right: 2px solid #d4b68a;
    }
    
    /* Кнопка доната - УЛУЧШЕНО */
    .donate-button {
        background: linear-gradient(135deg, #d4b68a 0%, #b5926a 100%);
        color: #2a1c0e !important;
        font-weight: 700;
        font-size: 1.2rem;
        border-radius: 50px;
        padding: 15px 25px;
        text-decoration: none;
        border: 2px solid #8b6b4f;
        transition: all 0.3s ease;
        display: inline-block;
        width: 100%;
        text-align: center;
        margin: 10px 0;
        font-family: 'Open Sans', sans-serif;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    .donate-button:hover {
        background: linear-gradient(135deg, #b5926a 0%, #9b7e62 100%);
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        border-color: #5d3a1a;
        color: #2a1c0e !important;
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 2.2rem;
        margin: 40px 0 20px 0;
        padding-left: 15px;
        border-left: 5px solid #b5926a;
        background: linear-gradient(90deg, rgba(213, 182, 138, 0.1) 0%, rgba(255,255,255,0) 100%);
        padding: 10px 20px;
    }
    
    /* Карточки сказок - УВЕЛИЧЕНА ВЫСОТА */
    .tale-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(93, 58, 26, 0.1);
        border: 2px solid #e9d9c4;
        transition: all 0.3s ease;
        height: 1200px;  /* Увеличено в 2 раза */
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(5px);
    }
    
    .tale-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 35px rgba(93, 58, 26, 0.2);
        border-color: #b5926a;
    }
    
    .tale-card img {
        width: 100%;
        height: 700px;  /* Увеличено для пропорциональности */
        object-fit: cover;
        border-radius: 15px;
        border: 2px solid #d4b68a;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .tale-card:hover img {
        transform: scale(1.02);
    }
    
    .tale-card h3 {
        font-size: 2rem;  /* Увеличен */
        margin: 0 0 15px 0;
        color: #5d3a1a;
    }
    
    .tale-card p {
        font-size: 1.1rem;  /* Увеличен */
        margin: 0 0 25px 0;
        flex-grow: 1;
        color: #3e2c1b;
        line-height: 1.5;
    }
    
    /* Кнопка "Начать" - УЛУЧШЕНО */
    .start-button {
        background: linear-gradient(135deg, #e6d5b8 0%, #d4b68a 100%);
        color: #2a1c0e;
        border: 2px solid #b5926a;
        border-radius: 40px;
        padding: 15px 30px;  /* Увеличен padding */
        font-size: 1.3rem;  /* Увеличен */
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        width: 100%;
        font-family: 'Open Sans', sans-serif;
        letter-spacing: 1px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .start-button:hover {
        background: linear-gradient(135deg, #d4b68a 0%, #b5926a 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-color: #8b6b4f;
    }
    
    /* Скрытые Streamlit кнопки */
    .stButton > button {
        display: none;
    }
    
    /* Сообщения чата */
    .stChatMessage {
        background: linear-gradient(135deg, #fffaf0 0%, #fcf3e0 100%) !important;
        border-radius: 20px !important;
        padding: 12px 20px !important;
        border: 2px solid #e9d9c4;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background: linear-gradient(135deg, #e6d5b8 0%, #d4b68a 100%) !important;
        border-color: #b5926a;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background: linear-gradient(90deg, #b5926a, #8b6b4f) !important;
        border-radius: 10px !important;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 600px) {
        h1 {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.8rem;
        }
        .tale-card {
            height: 500px;
        }
        .tale-card h3 {
            font-size: 1.5rem;
        }
        .tale-card img {
            height: 250px;
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
    for scene_id, scene in tale["scenes"].items():
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

def get_image_html(tale_name):
    cover_path = tales[tale_name].get("cover", "")
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as f:
                import base64
                img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{img_data}" alt="{tale_name}">'
        except:
            pass
    return f'<img src="https://via.placeholder.com/400x350/ffe6f0/ff69b4?text=✨+{tale_name}" alt="{tale_name}">'

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 🌟 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
    
    # Кнопка доната
    st.markdown("""
    <a href="https://donate.stream/donate_69b56f4953f16" target="_blank" class="donate-button">
        💖 Поддержать донатом
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.selected_tale is not None:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            progress_value = min(opened / total, 1.0)
            st.progress(progress_value)
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
        st.markdown("---")
        
        if st.button("🔄 Сменить сказку", use_container_width=True):
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
    
    # Советские сказки
    st.markdown('<div class="section-header">📚 Советские сказки</div>', unsafe_allow_html=True)
    
    # Создаем две колонки
    cols = st.columns(2)
    
    for i, tale_name in enumerate(soviet_tales):
        if tale_name in all_tales:
            with cols[i % 2]:
                # Генерируем уникальные ID для кнопок
                btn_id = f"btn_{tale_name.replace(' ', '_')}"
                
                # HTML карточка
                html = f'''
                <div class="tale-card">
                    {get_image_html(tale_name)}
                    <h3>{tale_name}</h3>
                    <p>{tales[tale_name].get("description", "")}</p>
                    <div class="start-button" onclick="document.getElementById('{btn_id}').click()">✨ Начать</div>
                </div>
                '''
                st.markdown(html, unsafe_allow_html=True)
                
                # Скрытая кнопка Streamlit
                if st.button("🎯", key=btn_id):
                    start_tale(tale_name)
                    st.rerun()
    
    # Новые сказки
    if new_tales:
        st.markdown('<div class="section-header">🆕 Новые сказки</div>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        for i, tale_name in enumerate(new_tales):
            if tale_name in all_tales:
                with cols[i % 2]:
                    btn_id = f"btn_new_{tale_name.replace(' ', '_')}"
                    
                    html = f'''
                    <div class="tale-card">
                        {get_image_html(tale_name)}
                        <h3>{tale_name}</h3>
                        <p>{tales[tale_name].get("description", "")}</p>
                        <div class="start-button" onclick="document.getElementById('{btn_id}').click()">✨ Начать</div>
                    </div>
                    '''
                    st.markdown(html, unsafe_allow_html=True)
                    
                    if st.button("✨", key=btn_id):
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
                tale = st.session_state.selected_tale
                ending_id = current_scene["text"][:100]
                
                if tale not in st.session_state.achieved_endings:
                    st.session_state.achieved_endings[tale] = set()
                if ending_id not in st.session_state.achieved_endings[tale]:
                    st.session_state.achieved_endings[tale].add(ending_id)
                    st.rerun()
                
                st.markdown("---")
                st.markdown("🎉 **Конец сказки!**")
                
                opened, total = get_ending_stats(tale)
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
