import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="centered")

# --- Стили ---
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
        font-weight: 600;
    }
    
    /* Текст */
    p, li, .stMarkdown, .stText {
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
    
    /* Кнопка доната */
    .stLinkButton a {
        background-color: #d4b68a !important;
        color: #2a1c0e !important;
        font-weight: 600 !important;
        border-radius: 30px !important;
        padding: 0.5rem 1rem !important;
        text-decoration: none !important;
        border: 1px solid #b5926a !important;
        transition: all 0.3s ease !important;
        display: inline-block !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    .stLinkButton a:hover {
        background-color: #b89e7c !important;
        color: #2a1c0e !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* Карточки сказок */
    div[data-testid="column"] > div {
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
    
    div[data-testid="column"] > div:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    /* Изображения обложек */
    div[data-testid="column"] img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        border: 1px solid #d4b68a;
        margin-bottom: 10px;
    }
    
    /* Заголовок сказки */
    div[data-testid="column"] h4 {
        margin: 0 0 5px 0;
        font-size: 1.2rem;
    }
    
    /* Описание */
    div[data-testid="column"] p {
        font-size: 0.9rem;
        line-height: 1.4;
        margin: 0 0 10px 0;
        flex-grow: 1;
    }
    
    /* Кнопка в карточке */
    div[data-testid="column"] .stButton {
        margin-top: auto;
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
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 600px) {
        div[data-testid="column"] img {
            height: 150px;
        }
        h1 {
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
    st.session_state.achieved_endings = {}  # {tale_name: set(endings_ids)}

# --- ИСПРАВЛЕННАЯ функция подсчета концовок ---
def count_total_endings(tale_name):
    """Подсчитывает количество концовок (сцен с options=[]) в сказке"""
    tale = tales.get(tale_name)
    if not tale:
        return 0
    count = 0
    for scene_id, scene in tale["scenes"].items():
        # Концовка - это сцена без options
        if scene.get("options") == []:
            count += 1
    print(f"Сказка {tale_name}: найдено {count} концовок")  # Для отладки
    return count

def get_ending_stats(tale_name):
    """Возвращает (количество открытых, всего)"""
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
    st.markdown("## 🌟 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
    
    # Кнопка доната
    st.markdown("""
    <a href="https://donate.stream/donate_69b56f4953f16" target="_blank" style="
        background-color: #d4b68a;
        color: #2a1c0e !important;
        font-weight: 600;
        border-radius: 30px;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border: 1px solid #b5926a;
        transition: all 0.3s ease;
        display: inline-block;
        width: 100%;
        text-align: center;
        margin: 0.5rem 0;
        font-family: 'Open Sans', sans-serif;
    " onmouseover="this.style.backgroundColor='#b89e7c'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)';" 
       onmouseout="this.style.backgroundColor='#d4b68a'; this.style.transform='translateY(0)'; this.style.boxShadow='none';">
        💖 Поддержать донатом
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Статистика концовок для текущей сказки
    if st.session_state.selected_tale is not None:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(opened / total)
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
    # Экран выбора сказки
    st.markdown("### Выберите сказку для чтения")
    
    # Получаем все сказки
    tale_names = list(tales.keys())
    
    # Создаем две колонки
    cols = st.columns(2)
    
    for i, tale_name in enumerate(tale_names):
        with cols[i % 2]:
            with st.container(border=True):
                # Обложка
                cover_path = tales[tale_name].get("cover", "")
                if cover_path and os.path.exists(cover_path):
                    st.image(cover_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+Сказка", use_container_width=True)
                
                # Название
                st.markdown(f"#### {tale_name}")
                
                # Описание
                if tales[tale_name].get("description"):
                    st.markdown(tales[tale_name]["description"])
                
                # Кнопка начала
                if st.button(f"✨ Начать", key=f"choose_{tale_name}", use_container_width=True):
                    start_tale(tale_name)
                    st.rerun()
    
    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны. Если хотите поддержать проект, воспользуйтесь кнопкой в боковой панели.*")

else:
    # Отображаем историю сообщений
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    current_scene = st.session_state.scenes.get(st.session_state.scene_id)

    if current_scene:
        # Если это концовка (нет options)
        if not current_scene.get("options"):
            # Проверяем, есть ли ending_type и ending_number
            if current_scene.get("ending_type") and current_scene.get("ending_number"):
                ending_type = current_scene["ending_type"]
                ending_num = current_scene["ending_number"]
                
                # Определяем эмодзи для типа
                type_emoji = {
                    "happy": "😊",
                    "sad": "😢",
                    "neutral": "😐",
                    "secret": "🤫"
                }.get(ending_type, "🌟")
                
                # Запоминаем, что концовка открыта
                tale = st.session_state.selected_tale
                ending_id = f"{ending_type}_{ending_num}"
                if tale not in st.session_state.achieved_endings:
                    st.session_state.achieved_endings[tale] = set()
                st.session_state.achieved_endings[tale].add(ending_id)
                
                # Показываем информацию о концовке
                st.markdown("---")
                st.markdown(f"## {type_emoji} **Концовка #{ending_num}**")
                st.markdown(f"**Тип:** {ending_type.capitalize()}")
                
                if ending_type == "happy":
                    st.success("🎉 Поздравляем! Это счастливый конец!")
                else:
                    st.info("😕 Это не счастливый конец. Попробуй пройти сказку снова, возможно, ты найдёшь счастливый конец!")
                
                # Показываем общий прогресс
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            else:
                # Старая сказка без типов концовок
                tale = st.session_state.selected_tale
                # Создаем уникальный ID для концовки на основе текста
                ending_id = f"end_{len(st.session_state.achieved_endings.get(tale, set())) + 1}_{hash(current_scene['text'][:50])}"
                if tale not in st.session_state.achieved_endings:
                    st.session_state.achieved_endings[tale] = set()
                if ending_id not in st.session_state.achieved_endings[tale]:
                    st.session_state.achieved_endings[tale].add(ending_id)
                    st.rerun()  # Важно: обновляем страницу для отображения нового счетчика
                
                st.markdown("---")
                st.markdown("🎉 **Конец сказки!**")
                
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            
            # Кнопки после концовки
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
            # Обычная сцена с вариантами
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
