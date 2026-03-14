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
    return f'<img src="https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+{tale_name}" alt="{tale_name}">'

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown("Добро пожаловать в мир интерактивных сказок! Вы сами выбираете, как развернётся история. Все сказки абсолютно бесплатны.")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    if st.session_state.selected_tale:
        st.markdown("---")
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено: **{opened} / {total}**")
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    all_tales = list(tales.keys())
    soviet = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    new = ["Путешествие в Волшебный лес"]
    
    # Советские сказки
    st.markdown('<div class="section-title">📚 Советские сказки</div>', unsafe_allow_html=True)
    
    # СОЗДАЕМ ДВЕ КОЛОНКИ ЧЕРЕЗ HTML
    html = '<div class="row">'
    
    # Левая колонка
    html += '<div class="column">'
    for i, name in enumerate(soviet[:2]):  # первые две сказки
        if name in all_tales:
            html += f'''
            <div class="tale-card">
                {get_image_html(name)}
                <h3>{name}</h3>
                <p>{tales[name].get("description", "")}</p>
                <div class="start-btn" onclick="document.getElementById('btn_{name}').click()">✨ Начать</div>
            </div>
            '''
    html += '</div>'
    
    # Правая колонка
    html += '<div class="column">'
    for i, name in enumerate(soviet[2:4]):  # вторые две сказки
        if name in all_tales:
            html += f'''
            <div class="tale-card">
                {get_image_html(name)}
                <h3>{name}</h3>
                <p>{tales[name].get("description", "")}</p>
                <div class="start-btn" onclick="document.getElementById('btn_{name}').click()">✨ Начать</div>
            </div>
            '''
    html += '</div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Скрытые кнопки
    for name in soviet:
        if name in all_tales:
            if st.button("🎯", key=f"btn_{name}"):
                start_tale(name)
                st.rerun()
    
    # Новые сказки
    if new:
        st.markdown('<div class="section-title">🆕 Новые сказки</div>', unsafe_allow_html=True)
        html = '<div class="row"><div class="column">'
        for name in new:
            if name in all_tales:
                html += f'''
                <div class="tale-card">
                    {get_image_html(name)}
                    <h3>{name}</h3>
                    <p>{tales[name].get("description", "")}</p>
                    <div class="start-btn" onclick="document.getElementById('btn_new_{name}').click()">✨ Начать</div>
                </div>
                '''
        html += '</div><div class="column"></div></div>'
        st.markdown(html, unsafe_allow_html=True)
        
        for name in new:
            if name in all_tales:
                if st.button("✨", key=f"btn_new_{name}"):
                    start_tale(name)
                    st.rerun()

else:
    # Сама сказка
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    current = st.session_state.scenes.get(st.session_state.scene_id)
    if current:
        if not current.get("options"):
            # Концовка
            if current.get("ending_type"):
                ending_id = f"{current['ending_type']}_{current['ending_number']}"
                if ending_id not in st.session_state.achieved_endings.get(st.session_state.selected_tale, set()):
                    st.session_state.achieved_endings.setdefault(st.session_state.selected_tale, set()).add(ending_id)
                    st.rerun()
                st.success(f"🎉 Концовка #{current['ending_number']} ({current['ending_type']})")
            else:
                st.success("🎉 Конец сказки!")
            
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
