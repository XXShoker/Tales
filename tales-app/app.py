import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- HTML-карусель (Netflix стиль) ---
st.markdown("""
<style>
    /* Контейнер для горизонтальной прокрутки */
    .netflix-row {
        display: flex;
        overflow-x: auto;
        gap: 20px;
        padding: 20px 0;
        scrollbar-width: thin;
        scrollbar-color: #b5926a #f5e9d8;
        -webkit-overflow-scrolling: touch;
    }
    
    .netflix-row::-webkit-scrollbar {
        height: 8px;
    }
    
    .netflix-row::-webkit-scrollbar-track {
        background: #f5e9d8;
        border-radius: 10px;
    }
    
    .netflix-row::-webkit-scrollbar-thumb {
        background: #b5926a;
        border-radius: 10px;
    }
    
    /* Карточка сказки */
    .tale-card {
        flex: 0 0 auto;
        width: 280px;
        background: #fffaf0;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e9d9c4;
        transition: all 0.3s ease;
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
        margin-bottom: 12px;
    }
    
    .tale-card h3 {
        margin: 0 0 8px 0;
        font-size: 1.2rem;
        color: #5d3a1a;
    }
    
    .tale-card p {
        font-size: 0.9rem;
        color: #3e2c1b;
        margin: 0 0 12px 0;
        line-height: 1.4;
        height: 60px;
        overflow: hidden;
    }
    
    .tale-card button {
        width: 100%;
        background: #e6d5b8;
        color: #3e2c1b;
        border: 1px solid #b5926a;
        border-radius: 30px;
        padding: 8px 16px;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .tale-card button:hover {
        background: #d4b68a;
    }
    
    /* Заголовки секций */
    .section-title {
        font-size: 1.8rem;
        margin: 30px 0 10px 0;
        color: #5d3a1a;
        font-weight: 600;
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
    st.markdown("Добро пожаловать в мир **интерактивных сказок**!")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    if st.session_state.selected_tale is not None:
        st.markdown("---")
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        st.progress(opened / total if total > 0 else 0)
        st.markdown(f"Найдено: **{opened} / {total}**")
        
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    # Определяем группы сказок
    all_tales = list(tales.keys())
    soviet_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new_tales = ["Путешествие в Волшебный лес"]

    # Функция для создания HTML карточки
    def create_tale_card(tale_name, button_id):
        cover_path = tales[tale_name].get("cover", "")
        description = tales[tale_name].get("description", "")
        
        if cover_path and os.path.exists(cover_path):
            img_html = f'<img src="file/{cover_path}" alt="{tale_name}">'
        else:
            img_html = f'<img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨" alt="{tale_name}">'
        
        return f'''
        <div class="tale-card">
            {img_html}
            <h3>{tale_name}</h3>
            <p>{description}</p>
            <button onclick="document.getElementById('{button_id}').click()">✨ Начать</button>
        </div>
        '''

    # Советские сказки
    st.markdown('<div class="section-title">📚 Советские сказки</div>', unsafe_allow_html=True)
    
    # Создаем ряд с карточками
    with st.container():
        # Используем колонки для создания пространства, но сами карточки будут в HTML
        cols = st.columns(len(soviet_tales))
        
        # Для каждой сказки создаем скрытую кнопку Streamlit и HTML карточку
        for i, tale_name in enumerate(soviet_tales):
            if tale_name in all_tales:
                with cols[i]:
                    # Скрытая кнопка Streamlit
                    if st.button("✨", key=f"hidden_{tale_name}", help=tale_name):
                        start_tale(tale_name)
                        st.rerun()
                    
                    # HTML карточка (отображается поверх)
                    cover_path = tales[tale_name].get("cover", "")
                    description = tales[tale_name].get("description", "")
                    
                    html = f'''
                    <div class="tale-card" style="margin-top: -38px;">
                        <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨" alt="{tale_name}">
                        <h3>{tale_name}</h3>
                        <p>{description}</p>
                        <button style="pointer-events: none;">✨ Начать</button>
                    </div>
                    '''
                    st.markdown(html, unsafe_allow_html=True)

    # Новые сказки
    if new_tales:
        st.markdown('<div class="section-title">🆕 Новые сказки</div>', unsafe_allow_html=True)
        
        with st.container():
            cols = st.columns(len(new_tales))
            for i, tale_name in enumerate(new_tales):
                if tale_name in all_tales:
                    with cols[i]:
                        if st.button("✨", key=f"hidden_new_{tale_name}", help=tale_name):
                            start_tale(tale_name)
                            st.rerun()
                        
                        html = f'''
                        <div class="tale-card" style="margin-top: -38px;">
                            <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=✨" alt="{tale_name}">
                            <h3>{tale_name}</h3>
                            <p>{tales[tale_name].get("description", "")}</p>
                            <button style="pointer-events: none;">✨ Начать</button>
                        </div>
                        '''
                        st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🌟 *Все сказки бесплатны!*")

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
                    st.success("🎉 Поздравляем!")
                else:
                    st.info("😕 Попробуй ещё раз!")
                
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Найдено: **{opened} / {total}**.*")
            
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Назад", use_container_width=True):
                    go_back()
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
