import streamlit as st
import os
import base64
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Единые стили для всего приложения ---
st.markdown("""
<style>
    /* Общие стили */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    .stApp {
        background-color: #fef9e7;
    }
    
    h1, h2, h3, .section-title {
        font-family: 'Cormorant Garamond', serif;
        color: #5d3a1a;
    }
    
    /* Netflix-карусель - ГЛАВНОЕ ИСПРАВЛЕНИЕ */
    .carousel-row {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important;
        gap: 20px !important;
        padding: 20px 5px 30px 5px !important;
        margin: 0 !important;
        scrollbar-width: thin;
        scrollbar-color: #b5926a #f5e9d8;
        -webkit-overflow-scrolling: touch;
        width: 100%;
    }
    
    .carousel-row::-webkit-scrollbar {
        height: 8px;
    }
    
    .carousel-row::-webkit-scrollbar-track {
        background: #f5e9d8;
        border-radius: 10px;
    }
    
    .carousel-row::-webkit-scrollbar-thumb {
        background: #b5926a;
        border-radius: 10px;
    }
    
    /* Карточка сказки - фиксированный размер */
    .tale-card {
        flex: 0 0 auto !important;
        width: 280px !important;
        background: #fffaf0;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e9d9c4;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        height: fit-content;
    }
    
    .tale-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }
    
    .tale-card img {
        width: 100%;
        height: 160px;
        object-fit: cover;
        border-radius: 12px;
        border: 1px solid #d4b68a;
        margin-bottom: 12px;
    }
    
    .tale-card h3 {
        margin: 0 0 8px 0;
        font-size: 1.3rem;
        color: #5d3a1a;
        font-family: 'Cormorant Garamond', serif;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .tale-card p {
        font-size: 0.9rem;
        line-height: 1.4;
        color: #3e2c1b;
        margin: 0 0 12px 0;
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        font-family: 'Open Sans', sans-serif;
    }
    
    .tale-card button {
        width: 100%;
        background-color: #e6d5b8;
        color: #3e2c1b;
        border: 1px solid #b5926a;
        border-radius: 30px;
        padding: 10px 16px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Open Sans', sans-serif;
        margin-top: auto;
    }
    
    .tale-card button:hover {
        background-color: #d4b68a;
        transform: scale(1.02);
    }
    
    /* Заголовки секций */
    .section-title {
        font-size: 2rem;
        margin: 30px 0 10px 0;
        padding-left: 15px;
        border-left: 4px solid #b5926a;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background-color: #f5e9d8;
    }
    
    /* Скрываем стандартные Streamlit элементы */
    div[data-testid="stHorizontalBlock"] {
        display: none !important;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 600px) {
        .tale-card {
            width: 220px !important;
        }
        .tale-card img {
            height: 130px;
        }
        .section-title {
            font-size: 1.5rem;
        }
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
    }
    
    /* Кнопки в сайдбаре */
    .sidebar .stButton button {
        background-color: #cbb89e;
        border-color: #9b7e62;
    }
    
    .sidebar .stButton button:hover {
        background-color: #b89e7c;
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

def get_image_html(tale_name):
    """Возвращает HTML для изображения сказки"""
    cover_path = tales[tale_name].get("cover", "")
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{img_data}" alt="{tale_name}">'
        except:
            pass
    return f'<img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨" alt="{tale_name}">'

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown("Добро пожаловать в мир **интерактивных сказок**! Вы сами выбираете, как развернётся история.")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    if st.session_state.selected_tale is not None:
        st.markdown("---")
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
    # Определяем группы сказок
    all_tales = list(tales.keys())
    soviet_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new_tales = ["Путешествие в Волшебный лес"]

    # ВАЖНО: Убираем стандартные Streamlit колонки, используем чистый HTML
    
    # Советские сказки
    st.markdown('<div class="section-title">📚 Советские сказки</div>', unsafe_allow_html=True)
    
    # Создаем карусель с карточками
    carousel_html = '<div class="carousel-row">'
    for tale_name in soviet_tales:
        if tale_name in all_tales:
            description = tales[tale_name].get("description", "")
            # Создаем уникальный ID для кнопки
            btn_id = f"btn_{tale_name.replace(' ', '_')}"
            carousel_html += f'''
            <div class="tale-card">
                {get_image_html(tale_name)}
                <h3>{tale_name}</h3>
                <p>{description}</p>
                <button onclick="document.getElementById('{btn_id}').click()">✨ Начать</button>
            </div>
            '''
    carousel_html += '</div>'
    
    st.markdown(carousel_html, unsafe_allow_html=True)

    # Скрытые кнопки Streamlit (для обработки кликов)
    for tale_name in soviet_tales:
        if tale_name in all_tales:
            btn_id = f"btn_{tale_name.replace(' ', '_')}"
            if st.button("🎯", key=btn_id, help=tale_name):
                start_tale(tale_name)
                st.rerun()

    # Новые сказки
    if new_tales and any(t in all_tales for t in new_tales):
        st.markdown('<div class="section-title">🆕 Новые сказки</div>', unsafe_allow_html=True)
        
        carousel_html = '<div class="carousel-row">'
        for tale_name in new_tales:
            if tale_name in all_tales:
                description = tales[tale_name].get("description", "")
                btn_id = f"btn_new_{tale_name.replace(' ', '_')}"
                carousel_html += f'''
                <div class="tale-card">
                    {get_image_html(tale_name)}
                    <h3>{tale_name}</h3>
                    <p>{description}</p>
                    <button onclick="document.getElementById('{btn_id}').click()">✨ Начать</button>
                </div>
                '''
        carousel_html += '</div>'
        
        st.markdown(carousel_html, unsafe_allow_html=True)

        # Скрытые кнопки для новых сказок
        for tale_name in new_tales:
            if tale_name in all_tales:
                btn_id = f"btn_new_{tale_name.replace(' ', '_')}"
                if st.button("✨", key=btn_id, help=tale_name):
                    start_tale(tale_name)
                    st.rerun()

    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны. Если хотите поддержать проект, воспользуйтесь кнопкой в боковой панели.*")

else:
    # --- Отображение сказки (без изменений) ---
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
