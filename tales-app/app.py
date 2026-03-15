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
        background: linear-gradient(135deg, #fcf3e0 0%, #fef9e7 100%);
    }
    
    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif;
        color: #2c1e0e !important;
        font-weight: 600;
    }
    
    h1 {
        font-size: 3rem;
        border-bottom: 3px solid #d4b68a;
        padding-bottom: 15px;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Заголовки секций */
    .section-header {
        font-size: 2.2rem;
        margin: 40px 0 20px 0;
        padding-left: 15px;
        border-left: 5px solid #b5926a;
        background: linear-gradient(90deg, rgba(181,146,106,0.1) 0%, rgba(255,255,255,0) 100%);
        padding: 10px 20px;
        border-radius: 0 20px 20px 0;
    }
    
    /* Текст */
    p, li, .stMarkdown, .stText, .stChatMessage p {
        font-family: 'Open Sans', sans-serif;
        color: #1a1309 !important;
        font-size: clamp(1rem, 2vw, 1.2rem);
        line-height: 1.6;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5e9d8 0%, #ecdcc5 100%);
        border-right: 2px solid #d4b68a;
    }
    
    /* Кнопка доната */
    .stLinkButton a {
        background: linear-gradient(135deg, #d4b68a, #b5926a);
        color: #2a1c0e !important;
        border-radius: 50px;
        padding: 15px 25px;
        text-decoration: none;
        font-weight: bold;
        border: 2px solid #8b6b4f;
        display: inline-block;
        width: 100%;
        text-align: center;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stLinkButton a:hover {
        background: linear-gradient(135deg, #b5926a, #9b7e62);
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.2);
    }
    
    /* Все кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #e6d5b8, #d4b68a);
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
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #d4b68a, #b5926a);
        border-color: #8b6b4f;
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }
    
    /* КАРТОЧКИ */
    div[data-testid="column"] > div {
        background: white;
        border-radius: 24px;
        padding: 25px;
        border: 2px solid #e9d9c4;
        box-shadow: 0 10px 25px rgba(93,58,26,0.1);
        height: 1000px !important;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    
    div[data-testid="column"] > div:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 35px rgba(93,58,26,0.15);
        border-color: #d4b68a;
    }
    
    /* Изображения */
    div[data-testid="column"] img {
        width: 100%;
        height: 500px !important;
        object-fit: cover;
        border-radius: 16px;
        border: 2px solid #d4b68a;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="column"] > div:hover img {
        transform: scale(1.02);
    }
    
    /* Прогресс на карточке */
    .card-progress {
        font-size: 0.9rem;
        color: #8b6b4f;
        margin: 5px 0 15px 0;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .card-progress-bar {
        height: 6px;
        background: #e6d5b8;
        border-radius: 3px;
        flex-grow: 1;
        overflow: hidden;
    }
    
    .card-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #b5926a, #8b6b4f);
        border-radius: 3px;
    }
    
    /* Достижения */
    .achievement-badge {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #e6d5b8;
        color: #2a1c0e;
        text-align: center;
        line-height: 30px;
        margin-right: 5px;
        font-size: 1.2rem;
    }
    
    .achievement-unlocked {
        background: linear-gradient(135deg, #d4b68a, #b5926a);
        box-shadow: 0 0 10px gold;
    }
    
    /* Анимация появления текста */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage {
        animation: fadeIn 0.3s ease-out;
        background: white !important;
        border: 2px solid #e9d9c4;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background: linear-gradient(135deg, #e6d5b8, #d4b68a) !important;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background: linear-gradient(90deg, #b5926a, #8b6b4f) !important;
        border-radius: 10px;
    }
    
    /* ===== МОБИЛЬНАЯ АДАПТАЦИЯ ===== */
    @media (max-width: 600px) {
        div[data-testid="column"] > div {
            height: 800px !important;
            padding: 15px;
        }
        div[data-testid="column"] img {
            height: 350px !important;
        }
        h1 {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.5rem;
        }
        
        /* Плавающие кнопки */
        .floating-home-button {
            position: fixed;
            bottom: 20px;
            left: 10px;
            z-index: 999;
            background: #e6d5b8;
            border: 2px solid #b5926a;
            border-radius: 40px;
            padding: 10px 20px;
            font-size: 1rem;
            font-weight: 600;
            color: #2a1c0e;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            cursor: pointer;
            backdrop-filter: blur(5px);
        }
        
        .stLinkButton {
            position: fixed;
            bottom: 20px;
            right: 10px;
            z-index: 999;
            width: auto;
            max-width: 200px;
        }
        
        .stLinkButton a {
            padding: 10px 20px;
            font-size: 1rem;
            white-space: nowrap;
        }
        
        section[data-testid="stSidebar"] .stLinkButton {
            position: static;
            max-width: none;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- JavaScript для плавающих кнопок ---
st.markdown("""
<script>
    function createFloatingButtons() {
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('tale')) return;
        
        // Кнопка "К сказкам"
        const homeBtn = document.createElement('div');
        homeBtn.className = 'floating-home-button';
        homeBtn.innerHTML = '🏠 К сказкам';
        homeBtn.onclick = () => window.location.href = window.location.pathname;
        document.body.appendChild(homeBtn);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createFloatingButtons);
    } else {
        createFloatingButtons();
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

# --- Достижения ---
if "achievements" not in st.session_state:
    st.session_state.achievements = {
        # Классика
        "kolobok_5": False, "kolobok_all": False,
        "teremok_5": False, "teremok_all": False,
        "rybka_3_greedy": False, "rybka_all": False,
        "ryaba_3_save": False, "ryaba_all": False,
        # Приключения
        "forest_10_locations": False, "forest_all_friends": False, "forest_all": False,
        # Детектив
        "detective_10": False, "detective_time_5": False, "detective_save_3": False, "detective_all": False,
        # Романтика
        "romance_3_love": False, "romance_5_happy": False, "romance_all": False,
        # Секретные
        "teremok_fairy": False, "teremok_bees": False,
        "ryaba_wish": False, "ryaba_drink": False,
        "crossover": False,
        # Мета
        "total_50": False, "total_80": False, "total_all": False,
        "speedrun": False, "explorer": False, "talisman": False, "death_10": False,
    }

if "achievement_progress" not in st.session_state:
    st.session_state.achievement_progress = {
        "kolobok_count": 0,
        "teremok_count": 0,
        "rybka_greedy": 0,
        "ryaba_save": 0,
        "forest_locations": set(),
        "forest_friends": set(),
        "detective_count": 0,
        "detective_time": 0,
        "detective_save": 0,
        "romance_love": 0,
        "romance_happy": 0,
        "total_endings_found": 0,
        "death_count": 0,
        "speedrun_tales": set(),
    }

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

def check_achievements(tale_name, ending_type=None, ending_data=None):
    """Проверяет и разблокирует достижения"""
    progress = st.session_state.achievement_progress
    ach = st.session_state.achievements
    
    # --- Колобок ---
    if tale_name == "Колобок":
        progress["kolobok_count"] = len(st.session_state.achieved_endings.get("Колобок", set()))
        if progress["kolobok_count"] >= 5 and not ach["kolobok_5"]:
            ach["kolobok_5"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Колобок-беглец» (5 концовок)")
        if progress["kolobok_count"] >= 16 and not ach["kolobok_all"]:
            ach["kolobok_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Ни одна лиса не страшна» (все концовки Колобка)")
    
    # --- Теремок ---
    if tale_name == "Теремок":
        progress["teremok_count"] = len(st.session_state.achieved_endings.get("Теремок", set()))
        if progress["teremok_count"] >= 5 and not ach["teremok_5"]:
            ach["teremok_5"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Терем-теремок» (5 концовок)")
        if progress["teremok_count"] >= 14 and not ach["teremok_all"]:
            ach["teremok_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Всем дом» (все концовки Теремка)")
        
        # Секретные достижения Теремка
        if ending_data:
            ending_num = ending_data.get("ending_number")
            
            # Фея (концовки 6 и 7)
            if ending_num in [6, 7] and not ach["teremok_fairy"]:
                ach["teremok_fairy"] = True
                st.balloons()
                st.success("🏆 Достижение разблокировано: «Постучи три раза» (секретная фея)")
            
            # Пчёлы (концовки 9, 10, 11)
            if ending_num in [9, 10, 11] and not ach["teremok_bees"]:
                ach["teremok_bees"] = True
                st.balloons()
                st.success("🏆 Достижение разблокировано: «Пчелиный король» (секретные пчёлы)")
    
    # --- Золотая рыбка ---
    if tale_name == "Золотая рыбка":
        if ending_type == "sad" and ending_data:
            if ending_data.get("ending_number") in [1,2,3]:
                progress["rybka_greedy"] += 1
                if progress["rybka_greedy"] >= 3 and not ach["rybka_3_greedy"]:
                    ach["rybka_3_greedy"] = True
                    st.balloons()
                    st.success("🏆 Достижение разблокировано: «Золотая жадность» (3 жадные концовки)")
        
        progress["rybka_count"] = len(st.session_state.achieved_endings.get("Золотая рыбка", set()))
        if progress["rybka_count"] >= 10 and not ach["rybka_all"]:
            ach["rybka_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Мудрец» (все концовки Золотой рыбки)")
    
    # --- Курочка Ряба ---
    if tale_name == "Курочка Ряба":
        if ending_type == "happy" and ending_data:
            if ending_data.get("ending_number") in [1,2,3,4,5,6,7]:
                progress["ryaba_save"] += 1
                if progress["ryaba_save"] >= 3 and not ach["ryaba_3_save"]:
                    ach["ryaba_3_save"] = True
                    st.balloons()
                    st.success("🏆 Достижение разблокировано: «Курочка-спасительница» (3 спасения)")
        
        progress["ryaba_count"] = len(st.session_state.achieved_endings.get("Курочка Ряба", set()))
        if progress["ryaba_count"] >= 12 and not ach["ryaba_all"]:
            ach["ryaba_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Золотой урожай» (все концовки Курочки Рябы)")
        
        # Секретные Рябы
        if ending_data and ending_data.get("ending_type") == "secret":
            ending_num = ending_data.get("ending_number")
            if ending_num in [5,6] and not ach["ryaba_wish"]:
                ach["ryaba_wish"] = True
                st.balloons()
                st.success("🏆 Достижение разблокировано: «Хрустальный шар» (загадать желание)")
            if ending_num == 7 and not ach["ryaba_drink"]:
                ach["ryaba_drink"] = True
                st.balloons()
                st.success("🏆 Достижение разблокировано: «Гулянка» (выпить с дедом)")
    
    # --- Путешествие в Волшебный лес ---
    if tale_name == "Путешествие в Волшебный лес":
        progress["forest_count"] = len(st.session_state.achieved_endings.get("Путешествие в Волшебный лес", set()))
        if progress["forest_count"] >= 12 and not ach["forest_all"]:
            ach["forest_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Повелитель леса» (все концовки)")
    
    # --- Хроники разбитых часов ---
    if tale_name == "Хроники разбитых часов: Детектив времени":
        progress["detective_count"] = len(st.session_state.achieved_endings.get(tale_name, set()))
        if progress["detective_count"] >= 10 and not ach["detective_10"]:
            ach["detective_10"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Следопыт» (10 концовок)")
        if progress["detective_count"] >= 25 and not ach["detective_all"]:
            ach["detective_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Идеальное преступление» (все концовки)")
    
    # --- Мелодия дождя ---
    if tale_name == "Мелодия дождя":
        progress["romance_count"] = len(st.session_state.achieved_endings.get(tale_name, set()))
        if progress["romance_count"] >= 5 and not ach["romance_5_happy"]:
            ach["romance_5_happy"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Романтик» (5 концовок)")
        if progress["romance_count"] >= 20 and not ach["romance_all"]:
            ach["romance_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Идеальная пара» (все концовки)")
    
    # --- Новая сказка: Проклятие крови ЛИКСА ---
    if tale_name == "Проклятие крови ЛИКСА":
        progress["lyx_count"] = len(st.session_state.achieved_endings.get(tale_name, set()))
        if progress["lyx_count"] >= 5 and not ach.get("lyx_5", False):
            ach["lyx_5"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Выжившая» (5 концовок ЛИКСЫ)")
        if progress["lyx_count"] >= 9 and not ach.get("lyx_all", False):
            ach["lyx_all"] = True
            st.balloons()
            st.success("🏆 Достижение разблокировано: «Проклятие снято» (все концовки ЛИКСЫ)")
    
    # --- Общая статистика ---
    total = 0
    for tale in tales.keys():
        total += len(st.session_state.achieved_endings.get(tale, set()))
    progress["total_endings_found"] = total
    
    if total >= 50 and not ach["total_50"]:
        ach["total_50"] = True
        st.balloons()
        st.success("🏆 Достижение разблокировано: «Коллекционер» (50 концовок)")
    if total >= 80 and not ach["total_80"]:
        ach["total_80"] = True
        st.balloons()
        st.success("🏆 Достижение разблокировано: «Профессионал» (80 концовок)")
    
    # Подсчёт всех возможных концовок
    total_possible = 16 + 14 + 20 + 12 + 12 + 25 + 20 + 9  # добавил 9 концовок ЛИКСЫ
    if total >= total_possible and not ach["total_all"]:
        ach["total_all"] = True
        st.balloons()
        st.balloons()
        st.success("👑 ДОСТИЖЕНИЕ ПЛАТИНОВОЕ: «Библиотекарь» (ВСЕ концовки!)")

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
    
    # Достижения (только на главном экране)
    if st.session_state.selected_tale is None:
        with st.expander("🏆 Достижения"):
            ach = st.session_state.achievements
            
            # Считаем сколько всего
            total_achieved = sum(1 for v in ach.values() if v)
            st.markdown(f"**Прогресс: {total_achieved}/33**")  # обновил счётчик
            st.progress(total_achieved / 33)
            
            st.markdown("---")
            
            # Группируем по категориям
            cols = st.columns(2)
            
            with cols[0]:
                st.markdown("**📚 Классика**")
                st.markdown(f"{'✅' if ach['kolobok_5'] else '⬜'} Колобок-беглец (5/16)")
                st.markdown(f"{'✅' if ach['kolobok_all'] else '⬜'} Ни одна лиса не страшна")
                st.markdown(f"{'✅' if ach['teremok_5'] else '⬜'} Терем-теремок (5/14)")
                st.markdown(f"{'✅' if ach['teremok_all'] else '⬜'} Всем дом")
                st.markdown(f"{'✅' if ach['rybka_3_greedy'] else '⬜'} Золотая жадность")
                st.markdown(f"{'✅' if ach['rybka_all'] else '⬜'} Мудрец")
                st.markdown(f"{'✅' if ach['ryaba_3_save'] else '⬜'} Курочка-спасительница")
                st.markdown(f"{'✅' if ach['ryaba_all'] else '⬜'} Золотой урожай")
            
            with cols[1]:
                st.markdown("**🧚 Приключения**")
                st.markdown(f"{'✅' if ach['forest_10_locations'] else '⬜'} Лесной исследователь")
                st.markdown(f"{'✅' if ach['forest_all_friends'] else '⬜'} Друг зверей")
                st.markdown(f"{'✅' if ach['forest_all'] else '⬜'} Повелитель леса")
                
                st.markdown("**🔞 16+**")
                st.markdown(f"{'✅' if ach['detective_10'] else '⬜'} Следопыт")
                st.markdown(f"{'✅' if ach['detective_time_5'] else '⬜'} Мастер времени")
                st.markdown(f"{'✅' if ach['detective_save_3'] else '⬜'} Спаситель")
                st.markdown(f"{'✅' if ach['detective_all'] else '⬜'} Идеальное преступление")
                st.markdown(f"{'✅' if ach['romance_3_love'] else '⬜'} Сердцеед")
                st.markdown(f"{'✅' if ach['romance_5_happy'] else '⬜'} Романтик")
                st.markdown(f"{'✅' if ach['romance_all'] else '⬜'} Идеальная пара")
                st.markdown(f"{'✅' if ach.get('lyx_5', False) else '⬜'} Выжившая (5/9)")
                st.markdown(f"{'✅' if ach.get('lyx_all', False) else '⬜'} Проклятие снято (9/9)")
            
            st.markdown("---")
            st.markdown("**🔮 Секретные**")
            cols2 = st.columns(3)
            with cols2[0]:
                st.markdown(f"{'✅' if ach['teremok_fairy'] else '⬜'} Фея")
                st.markdown(f"{'✅' if ach['teremok_bees'] else '⬜'} Пчёлы")
            with cols2[1]:
                st.markdown(f"{'✅' if ach['ryaba_wish'] else '⬜'} Желание")
                st.markdown(f"{'✅' if ach['ryaba_drink'] else '⬜'} Гулянка")
            with cols2[2]:
                st.markdown(f"{'✅' if ach['crossover'] else '⬜'} Хранитель")
            
            st.markdown("---")
            st.markdown("**🏆 Мета**")
            st.markdown(f"{'✅' if ach['total_50'] else '⬜'} Коллекционер (50)")
            st.markdown(f"{'✅' if ach['total_80'] else '⬜'} Профессионал (80)")
            st.markdown(f"{'✅' if ach['total_all'] else '⬜'} Библиотекарь (все)")
            st.markdown(f"{'✅' if ach['speedrun'] else '⬜'} Скороход")
            st.markdown(f"{'✅' if ach['explorer'] else '⬜'} Исследователь")
            st.markdown(f"{'✅' if ach['talisman'] else '⬜'} Талисман")
            st.markdown(f"{'✅' if ach['death_10'] else '⬜'} Бессмертный")

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    all_tales = list(tales.keys())
    
    # Категории - ИСПРАВЛЕНО
    classic_tales = ["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"]
    adventure_tales = ["Путешествие в Волшебный лес"]
    adult_tales = [
        "Хроники разбитых часов: Детектив времени", 
        "Мелодия дождя",
        "Проклятие крови ЛИКСА"
    ]
    
    def render_category(title, tale_list):
        tales_in_cat = [t for t in tale_list if t in all_tales]
        if not tales_in_cat:
            return
        
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        
        # Две колонки
        cols = st.columns(2)
        for idx, tale_name in enumerate(tales_in_cat):
            with cols[idx % 2]:
                with st.container():
                    # Обложка
                    cover_path = tales[tale_name].get("cover", "")
                    if cover_path and os.path.exists(cover_path):
                        st.image(cover_path, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨", use_container_width=True)
                    
                    st.markdown(f"### {tale_name}")
                    
                    # Прогресс на карточке
                    opened, total = get_ending_stats(tale_name)
                    if total > 0:
                        progress_pct = opened / total if total > 0 else 0
                        st.markdown(f"""
                        <div class="card-progress">
                            <span>📊 {opened}/{total}</span>
                            <div class="card-progress-bar">
                                <div class="card-progress-fill" style="width: {progress_pct*100}%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(tales[tale_name].get("description", ""))
                    if st.button("✨ Начать", key=f"{tale_name}", use_container_width=True):
                        start_tale(tale_name)
                        st.rerun()
    
    render_category("📚 Классические сказки", classic_tales)
    render_category("🧚 Приключения и фэнтези", adventure_tales)
    render_category("🔞 16+ Детективы и романтика", adult_tales)
    
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
                
                # Проверяем достижения
                check_achievements(st.session_state.selected_tale, 
                                 current.get("ending_type"), 
                                 current)
                
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
