import streamlit as st
import os
import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Конфигурация из секретов ---
GH_TOKEN = st.secrets.get("GH_TOKEN")
GH_REPO = st.secrets.get("GH_REPO")
GH_FILE_PATH = st.secrets.get("GH_FILE_PATH", "users_data.json")
SESSION_SECRET = st.secrets.get("SESSION_SECRET", "default_secret_change_me")

# --- ВСТРОЕННАЯ АУТЕНТИФИКАЦИЯ STREAMLIT ---
# --- ИСПРАВЛЕННАЯ ФУНКЦИЯ ПРОВЕРКИ АВТОРИЗАЦИИ ---
def check_password():
    """Проверяет авторизацию пользователя"""
    
    # Если пользователь уже в session_state - всё ок
    if st.session_state.get("user"):
        return True
    
    # Проверяем несколько возможных источников авторизации
    try:
        # Вариант 1: experimental_user (Streamlit Community Cloud)
        if hasattr(st, 'experimental_user'):
            user_info = st.experimental_user
            if user_info and user_info.get('email'):
                email = user_info['email']
                name = user_info.get('name', email.split('@')[0])
                
                st.session_state.user = {
                    'email': email,
                    'name': name,
                    'user_id': hashlib.md5(email.encode()).hexdigest()[:10]
                }
                
                # Загружаем прогресс пользователя
                users = get_github_data()
                if email in users:
                    st.session_state.achieved_endings = users[email].get("achieved_endings", {})
                    user_achievements = users[email].get("achievements", {})
                    if user_achievements:
                        for key, value in user_achievements.items():
                            if key in st.session_state.achievements:
                                st.session_state.achievements[key] = value
                return True
        
        # Вариант 2: query_params (для обратной совместимости)
        if 'user_email' in st.query_params:
            email = st.query_params['user_email']
            st.session_state.user = {
                'email': email,
                'name': email.split('@')[0],
                'user_id': hashlib.md5(email.encode()).hexdigest()[:10]
            }
            return True
            
        # Вариант 3: тестовый режим (если APP_URL содержит localhost)
        if 'localhost' in st.query_params.get('app_url', '') or 'streamlit.app' in st.query_params.get('app_url', ''):
            # Для отладки создаем тестового пользователя
            if 'debug_mode' not in st.session_state:
                st.session_state.debug_mode = True
                st.session_state.user = {
                    'email': 'debug@example.com',
                    'name': 'Debug User',
                    'user_id': 'debug_123'
                }
                return True
                
    except Exception as e:
        # В случае ошибки просто продолжаем
        pass
    
    return False

# --- Инициализация состояния ---
def init_session_state():
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
    if "user" not in st.session_state:
        st.session_state.user = None
    if "achievements" not in st.session_state:
        st.session_state.achievements = {
            "kolobok_5": False, "kolobok_all": False,
            "teremok_5": False, "teremok_all": False,
            "rybka_3_greedy": False, "rybka_all": False,
            "ryaba_3_save": False, "ryaba_all": False,
            "forest_10_locations": False, "forest_all_friends": False, "forest_all": False,
            "detective_10": False, "detective_time_5": False, "detective_save_3": False, "detective_all": False,
            "romance_3_love": False, "romance_5_happy": False, "romance_all": False,
            "teremok_fairy": False, "teremok_bees": False,
            "ryaba_wish": False, "ryaba_drink": False,
            "crossover": False,
            "total_50": False, "total_80": False, "total_all": False,
            "speedrun": False, "explorer": False, "talisman": False, "death_10": False,
            "lyx_5": False, "lyx_all": False
        }
    if "achievement_progress" not in st.session_state:
        st.session_state.achievement_progress = {
            "kolobok_count": 0, "teremok_count": 0, "rybka_greedy": 0, "ryaba_save": 0,
            "forest_locations": set(), "forest_friends": set(),
            "detective_count": 0, "detective_time": 0, "detective_save": 0,
            "romance_love": 0, "romance_happy": 0,
            "total_endings_found": 0, "death_count": 0, "speedrun_tales": set(),
            "lyx_count": 0
        }

init_session_state()

# --- ПРОВЕРКА АВТОРИЗАЦИИ ---
if not check_password():

# --- Функции для работы с GitHub ---
@st.cache_resource(ttl=60)
def get_github_data():
    if not GH_TOKEN:
        return {}
    
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_FILE_PATH}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content["content"]).decode("utf-8")
            users_data = json.loads(decoded)
            
            for email, user_data in users_data.items():
                if "achieved_endings" in user_data:
                    endings_dict = user_data["achieved_endings"]
                    for tale_name, endings in endings_dict.items():
                        if isinstance(endings, list):
                            endings_dict[tale_name] = set(endings)
            return users_data
        elif response.status_code == 404:
            return {}
        else:
            return {}
    except Exception as e:
        return {}

def save_users_to_github(users_data):
    if not GH_TOKEN:
        return False
    
    serializable_data = {}
    for email, user_data in users_data.items():
        serializable_data[email] = {}
        for key, value in user_data.items():
            if key == "achieved_endings":
                serializable_data[email][key] = {}
                if value:
                    for tale_name, endings in value.items():
                        if isinstance(endings, set):
                            serializable_data[email][key][tale_name] = list(endings)
                        else:
                            serializable_data[email][key][tale_name] = endings
                else:
                    serializable_data[email][key] = {}
            elif key == "achievements":
                serializable_data[email][key] = value.copy() if value else {}
            else:
                serializable_data[email][key] = value
    
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_FILE_PATH}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        sha = response.json().get("sha") if response.status_code == 200 else None
    except:
        sha = None
    
    content_json = json.dumps(serializable_data, ensure_ascii=False, indent=2)
    content_bytes = content_json.encode("utf-8")
    content_base64 = base64.b64encode(content_bytes).decode("utf-8")
    
    data = {
        "message": f"Update users data - {datetime.now().isoformat()}",
        "content": content_base64,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=data)
        st.cache_resource.clear()
        return response.status_code in [200, 201]
    except Exception as e:
        return False

def save_user_progress():
    """Сохраняет прогресс пользователя"""
    if st.session_state.user:
        try:
            email = st.session_state.user["email"]
            users = get_github_data()
            
            # Создаем или обновляем запись пользователя
            users[email] = {
                "user_id": st.session_state.user["user_id"],
                "name": st.session_state.user["name"],
                "email": email,
                "last_login": datetime.now().isoformat(),
                "achieved_endings": st.session_state.achieved_endings,
                "achievements": st.session_state.achievements
            }
            
            save_users_to_github(users)
        except Exception as e:
            pass

# --- Функции для работы с URL (сохранение состояния сказки) ---
def save_tale_state_to_url():
    """Сохраняет состояние сказки в URL"""
    params = {}
    
    if st.session_state.get('selected_tale'):
        params['tale'] = st.session_state.selected_tale
    
    if st.session_state.get('scene_id') and st.session_state.scene_id != "start":
        params['scene'] = st.session_state.scene_id
    
    # Сохраняем историю (не более 5 сцен)
    if len(st.session_state.get('scene_history', [])) > 1:
        recent_history = st.session_state.scene_history[-5:]
        params['history'] = ','.join(recent_history)
    
    # Обновляем URL
    if params:
        st.query_params.update(params)

def restore_tale_state_from_url():
    """Восстанавливает состояние сказки из URL"""
    if 'tale_restored' not in st.session_state:
        tale_name = st.query_params.get('tale')
        scene_id = st.query_params.get('scene', 'start')
        history_str = st.query_params.get('history', '')
        
        if tale_name and tale_name in tales and not st.session_state.get('selected_tale'):
            st.session_state.selected_tale = tale_name
            tale_data = tales.get(tale_name)
            if tale_data:
                st.session_state.scenes = tale_data["scenes"]
                
                # Проверяем существование сцены
                if scene_id not in st.session_state.scenes:
                    scene_id = "start"
                
                # Восстанавливаем историю
                if history_str:
                    history = history_str.split(',')
                    valid_history = [h for h in history if h in st.session_state.scenes]
                    if valid_history:
                        st.session_state.scene_history = valid_history
                    else:
                        st.session_state.scene_history = [scene_id]
                else:
                    st.session_state.scene_history = [scene_id]
                
                st.session_state.scene_id = scene_id
                
                # Восстанавливаем сообщения
                st.session_state.messages = []
                for i, hist_scene_id in enumerate(st.session_state.scene_history):
                    scene = st.session_state.scenes.get(hist_scene_id)
                    if scene:
                        if i == 0:
                            st.session_state.messages.append({"role": "assistant", "content": scene["text"]})
                        else:
                            prev_scene = st.session_state.scenes.get(st.session_state.scene_history[i-1])
                            if prev_scene and prev_scene.get("options"):
                                choice_text = "→ Далее"
                                for opt in prev_scene["options"]:
                                    if opt["next"] == hist_scene_id:
                                        choice_text = opt["text"]
                                        break
                                st.session_state.messages.append({"role": "user", "content": choice_text})
                            st.session_state.messages.append({"role": "assistant", "content": scene["text"]})
        
        st.session_state.tale_restored = True

# --- Восстанавливаем состояние сказки ---
restore_tale_state_from_url()

# --- Функции для сказок ---
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
    
    save_tale_state_to_url()

def handle_choice(choice_text, next_scene_id):
    st.session_state.messages.append({"role": "user", "content": choice_text})
    st.session_state.scene_id = next_scene_id
    st.session_state.scene_history.append(next_scene_id)
    next_scene = st.session_state.scenes.get(next_scene_id)
    if next_scene:
        st.session_state.messages.append({"role": "assistant", "content": next_scene["text"]})
    
    save_tale_state_to_url()

def go_back():
    if len(st.session_state.scene_history) > 1:
        st.session_state.scene_history.pop()
        st.session_state.scene_id = st.session_state.scene_history[-1]
        
        # Перестраиваем сообщения
        st.session_state.messages = []
        for i, hist_scene_id in enumerate(st.session_state.scene_history):
            scene = st.session_state.scenes.get(hist_scene_id)
            if scene:
                if i == 0:
                    st.session_state.messages.append({"role": "assistant", "content": scene["text"]})
                else:
                    prev_scene = st.session_state.scenes.get(st.session_state.scene_history[i-1])
                    if prev_scene and prev_scene.get("options"):
                        choice_text = "→ Далее"
                        for opt in prev_scene["options"]:
                            if opt["next"] == hist_scene_id:
                                choice_text = opt["text"]
                                break
                        st.session_state.messages.append({"role": "user", "content": choice_text})
                    st.session_state.messages.append({"role": "assistant", "content": scene["text"]})
        
        save_tale_state_to_url()
        st.rerun()

def reset_to_main():
    st.session_state.selected_tale = None
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []
    
    if 'tale' in st.query_params:
        del st.query_params['tale']
    if 'scene' in st.query_params:
        del st.query_params['scene']
    if 'history' in st.query_params:
        del st.query_params['history']

def check_achievements(tale_name, ending_type=None, ending_data=None):
    """Проверка и разблокировка достижений"""
    progress = st.session_state.achievement_progress
    ach = st.session_state.achievements
    
    if tale_name == "Колобок":
        progress["kolobok_count"] = len(st.session_state.achieved_endings.get("Колобок", set()))
        if progress["kolobok_count"] >= 5 and not ach["kolobok_5"]:
            ach["kolobok_5"] = True
            st.balloons()
            st.success("🏆 Достижение: «Колобок-беглец» (5 концовок)")
        if progress["kolobok_count"] >= 16 and not ach["kolobok_all"]:
            ach["kolobok_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Ни одна лиса не страшна»")
    
    # Сохраняем прогресс после каждого достижения
    save_user_progress()

# --- Стили ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #fcf3e0 0%, #fef9e7 100%);
    }
    
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
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #e6d5b8, #d4b68a);
        color: #2a1c0e !important;
        border: 2px solid #b5926a;
        border-radius: 40px;
        padding: 15px 20px !important;
        font-size: 1.2rem !important;
        font-weight: 600;
        width: 100%;
        min-height: 60px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #d4b68a, #b5926a);
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }
    
    div[data-testid="column"] > div {
        background: white;
        border-radius: 24px;
        padding: 25px;
        border: 2px solid #e9d9c4;
        box-shadow: 0 10px 25px rgba(93,58,26,0.1);
        height: auto !important;
        min-height: 500px;
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"] > div:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 35px rgba(93,58,26,0.15);
        border-color: #d4b68a;
    }
    
    div[data-testid="column"] img {
        width: 100%;
        height: auto !important;
        max-height: 300px;
        object-fit: cover;
        border-radius: 16px;
        border: 2px solid #d4b68a;
        margin-bottom: 20px;
    }
    
    .stChatMessage {
        animation: fadeIn 0.3s ease-out;
        background: white !important;
        border: 2px solid #e9d9c4;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @media (max-width: 600px) {
        h1 { font-size: 2rem; }
        div[data-testid="column"] > div { min-height: 400px; }
    }
</style>
""", unsafe_allow_html=True)

# --- Боковая панель ---
with st.sidebar:
    st.markdown(f"👋 Привет, **{st.session_state.user['name']}**!")
    st.markdown(f"📧 {st.session_state.user['email']}")
    st.markdown("---")
    st.markdown("## 📖 О проекте")
    st.markdown("Вы сами выбираете, как развернётся история.")
    
    # --- Прогресс текущей сказки ---
    if st.session_state.selected_tale:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
        if st.button("🔄 Сменить сказку", width='stretch'):
            reset_to_main()
            st.rerun()
    
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", width='stretch')

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    # Отображаем список сказок
    all_tales = list(tales.keys())
    
    # Категории
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
        
        st.markdown(f"### {title}")
        
        # Две колонки
        cols = st.columns(2)
        for idx, tale_name in enumerate(tales_in_cat):
            with cols[idx % 2]:
                with st.container():
                    # Обложка
                    cover_path = tales[tale_name].get("cover", "")
                    if cover_path and os.path.exists(cover_path):
                        st.image(cover_path, width='stretch')
                    else:
                        st.image("https://via.placeholder.com/800x500/ffe6f0/ff69b4?text=✨", width='stretch')
                    
                    st.markdown(f"### {tale_name}")
                    
                    # Прогресс
                    opened, total = get_ending_stats(tale_name)
                    if total > 0:
                        st.markdown(f"📊 Прогресс: {opened}/{total}")
                    
                    st.markdown(tales[tale_name].get("description", ""))
                    if st.button("✨ Начать", key=f"{tale_name}", width='stretch'):
                        start_tale(tale_name)
                        st.rerun()
    
    render_category("📚 Классические сказки", classic_tales)
    render_category("🧚 Приключения и фэнтези", adventure_tales)
    render_category("🔞 16+ Детективы и романтика", adult_tales)

else:
    # Отображаем сказку
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    current = st.session_state.scenes.get(st.session_state.scene_id)
    if current:
        if not current.get("options"):
            # Концовка
            if current.get("ending_type") and current.get("ending_number"):
                ending_id = f"{current['ending_type']}_{current['ending_number']}"
            else:
                ending_id = current["text"][:100]
            
            if st.session_state.selected_tale not in st.session_state.achieved_endings:
                st.session_state.achieved_endings[st.session_state.selected_tale] = set()
            
            if ending_id not in st.session_state.achieved_endings[st.session_state.selected_tale]:
                st.session_state.achieved_endings[st.session_state.selected_tale].add(ending_id)
                check_achievements(st.session_state.selected_tale, current.get("ending_type"), current)
                save_user_progress()
                st.rerun()
            
            st.markdown("---")
            if current.get("ending_type"):
                emoji = {"happy": "😊", "sad": "😢", "neutral": "😐", "secret": "🤫"}.get(current["ending_type"], "🎉")
                st.markdown(f"## {emoji} **Концовка #{current['ending_number']}**")
                if current["ending_type"] == "happy":
                    st.success("🎉 Счастливый конец!")
                else:
                    st.info("😕 Попробуйте другой путь!")
            
            opened, total = get_ending_stats(st.session_state.selected_tale)
            st.markdown(f"*Найдено концовок: **{opened}/{total}***")
            
            col1, col2 = st.columns(2)
            with col1:
                if len(st.session_state.scene_history) > 1:
                    if st.button("↩️ Назад", width='stretch'):
                        go_back()
            with col2:
                if st.button("🔄 Заново", width='stretch'):
                    start_tale(st.session_state.selected_tale)
                    st.rerun()
        else:
            # Выборы
            st.markdown("### Твой выбор:")
            for opt in current["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", width='stretch'):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад", width='stretch'):
                    go_back()
    else:
        st.error("⚠️ Сцена не найдена")
        if st.button("⬅️ К выбору сказок", width='stretch'):
            reset_to_main()
            st.rerun()
