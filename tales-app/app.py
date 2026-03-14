import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Стили для Netflix-карусели ---
st.markdown("""
<style>
    /* Подключаем шрифты */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    /* Общий фон */
    .stApp {
        background-color: #fef9e7;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif;
        color: #5d3a1a;
    }
    
    /* Netflix-карусель */
    .carousel-row {
        display: flex;
        overflow-x: auto;
        gap: 20px;
        padding: 20px 0;
        margin: 0;
        scrollbar-width: thin;
        scrollbar-color: #b5926a #f5e9d8;
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
    
    /* Карточка сказки */
    .tale-card {
        flex: 0 0 auto;
        width: 280px;
        background: #fffaf0;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #e9d9c4;
        transition: transform 0.2s;
    }
    
    .tale-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
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
        font-size: 1.3rem;
    }
    
    .tale-card p {
        font-size: 0.9rem;
        color: #3e2c1b;
        margin: 0 0 16px 0;
        line-height: 1.4;
        height: 60px;
        overflow: hidden;
    }
    
    .start-btn {
        width: 100%;
        padding: 10px;
        background: #e6d5b8;
        border: 1px solid #b5926a;
        border-radius: 30px;
        color: #3e2c1b;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        text-align: center;
        transition: background 0.2s;
    }
    
    .start-btn:hover {
        background: #d4b68a;
    }
    
    /* Заголовки секций */
    .section-title {
        font-size: 2rem;
        margin: 40px 0 20px 0;
        padding-left: 15px;
        border-left: 4px solid #b5926a;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background-color: #f5e9d8;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background-color: #b5926a !important;
    }
    
    /* Скрываем стандартные колонки Streamlit */
    div[data-testid="column"] {
        display: none !important;
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

def reset_to_main():
    st.session_state.selected_tale = None
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown("Вы сами выбираете, как развернётся история")
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)

# --- Главный экран ---
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    # Советские сказки
    st.markdown('<div class="section-title">📚 Советские сказки</div>', unsafe_allow_html=True)
    
    # Рисуем карточки через HTML
    html = '<div class="carousel-row">'
    
    # Колобок
    html += '''
    <div class="tale-card">
        <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=🥖" alt="Колобок">
        <h3>Колобок</h3>
        <p>Помоги Колобку убежать от всех зверей и найти настоящих друзей!</p>
        <div class="start-btn" onclick="alert('Колобок запущен')">✨ Начать</div>
    </div>
    '''
    
    # Теремок
    html += '''
    <div class="tale-card">
        <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=🏠" alt="Теремок">
        <h3>Теремок</h3>
        <p>Построй свой теремок и реши, кого пускать, а кого нет.</p>
        <div class="start-btn" onclick="alert('Теремок запущен')">✨ Начать</div>
    </div>
    '''
    
    # Золотая рыбка
    html += '''
    <div class="tale-card">
        <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=🐠" alt="Золотая рыбка">
        <h3>Золотая рыбка</h3>
        <p>Старик поймал золотую рыбку. Хватит ли мудрости не быть жадным?</p>
        <div class="start-btn" onclick="alert('Золотая рыбка запущена')">✨ Начать</div>
    </div>
    '''
    
    # Курочка Ряба
    html += '''
    <div class="tale-card">
        <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=🐔" alt="Курочка Ряба">
        <h3>Курочка Ряба</h3>
        <p>Курочка снесла золотое яичко. Что делать с разбитым яйцом?</p>
        <div class="start-btn" onclick="alert('Курочка Ряба запущена')">✨ Начать</div>
    </div>
    '''
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    
    # Новые сказки
    st.markdown('<div class="section-title">🆕 Новые сказки</div>', unsafe_allow_html=True)
    
    html = '<div class="carousel-row">'
    html += '''
    <div class="tale-card">
        <img src="https://via.placeholder.com/280x160/ffe6f0/ff69b4?text=🌳" alt="Волшебный лес">
        <h3>Волшебный лес</h3>
        <p>Отправляйся в загадочный лес, где живут говорящие звери и феи!</p>
        <div class="start-btn" onclick="alert('Волшебный лес запущен')">✨ Начать</div>
    </div>
    '''
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

else:
    # Сама сказка
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    st.info("Здесь будет логика сказки")
