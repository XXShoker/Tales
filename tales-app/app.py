import streamlit as st
import os
import requests
import json
import hashlib
import hmac
import base64
import random
import string
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Конфигурация из секретов ---
GH_TOKEN = st.secrets.get("GH_TOKEN")
GH_REPO = st.secrets.get("GH_REPO")
GH_FILE_PATH = st.secrets.get("GH_FILE_PATH", "users_data.json")
SESSION_SECRET = st.secrets.get("SESSION_SECRET", "default_secret_change_me")

def send_reset_code(email, code):
    """Отправка кода восстановления на email"""
    try:
        # Настройки почты из secrets
        EMAIL_HOST = st.secrets.get("EMAIL_HOST", "smtp.gmail.com")
        EMAIL_PORT = st.secrets.get("EMAIL_PORT", 587)
        EMAIL_USER = st.secrets.get("EMAIL_USER")
        EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD")
        FROM_EMAIL = st.secrets.get("FROM_EMAIL", EMAIL_USER)
        
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = email
        msg["Subject"] = "Восстановление пароля - Интерактивные сказки"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Восстановление пароля</h2>
            <p>Ваш код для восстановления пароля:</p>
            <h1 style="font-size: 32px; background: #f0f0f0; padding: 10px; text-align: center;">{code}</h1>
            <p>Код действителен в течение 15 минут.</p>
            <p>Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, "html"))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Ошибка отправки email: {e}")
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

# --- ПРОСТАЯ АВТОРИЗАЦИЯ ЧЕРЕЗ SESSION_STATE ---
# --- РАБОТА С COOKIES ЧЕРЕЗ JAVASCRIPT ---
def set_cookie(name, value, days=30):
    """Устанавливает cookie через JavaScript"""
    js = f"""
    <script>
    function setCookie(name, value, days) {{
        let expires = "";
        if (days) {{
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }}
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
    }}
    setCookie('{name}', '{value}', {days});
    </script>
    """
    st.components.v1.html(js, height=0)

def get_cookie_js():
    """JavaScript для получения cookies и передачи в URL"""
    return """
    <script>
    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }
    
    // Получаем cookies и добавляем в URL
    const userEmail = getCookie('user_email');
    const userName = getCookie('user_name');
    
    if (userEmail && userName) {
        const url = new URL(window.location.href);
        url.searchParams.set('cookie_email', userEmail);
        url.searchParams.set('cookie_name', userName);
        window.history.replaceState({}, '', url);
    }
    </script>
    """

def clear_cookie(name):
    """Удаляет cookie"""
    js = f"""
    <script>
    document.cookie = '{name}=; Max-Age=-99999999; path=/';
    </script>
    """
    st.components.v1.html(js, height=0)

# --- АВТОРИЗАЦИЯ ЧЕРЕЗ SESSIONSTORAGE (РАБОТАЕТ 100%) ---
def init_auth():
    """Инициализация авторизации - УПРОЩЕННАЯ И РАБОЧАЯ"""
    
    # Прямая проверка URL параметров (БЕЗ ВСЯКОЙ JAVASCRIPT МАГИИ)
    if 'user' not in st.session_state:
        # Просто берем данные из URL - они уже есть!
        email = st.query_params.get('user_email')
        name = st.query_params.get('user_name')
        username = st.query_params.get('user_username')
        
        print(f"🔍 Проверка URL: email={email}, name={name}, username={username}")
        
        if email and name:
            print(f"✅ Восстанавливаем пользователя: {email}")
            st.session_state.user = {
                'email': email,
                'name': name,
                'username': username or email.split('@')[0],
                'user_id': hashlib.md5(email.encode()).hexdigest()[:10]
            }
            
            # Загружаем прогресс
            try:
                users = get_github_data()
                if email in users:
                    st.session_state.achieved_endings = users[email].get("achieved_endings", {})
                    user_achievements = users[email].get("achievements", {})
                    if user_achievements:
                        for key, value in user_achievements.items():
                            if key in st.session_state.achievements:
                                st.session_state.achievements[key] = value
            except Exception as e:
                print(f"Ошибка загрузки прогресса: {e}")
        else:
            st.session_state.user = None
            print("ℹ️ Нет данных в URL")

def login_user(email, name, username):
    """Вход пользователя"""
    print(f"✅ Вход: {email}")
    
    st.session_state.user = {
        'email': email,
        'name': name,
        'username': username,
        'user_id': hashlib.md5(email.encode()).hexdigest()[:10]
    }
    
    # Сохраняем в URL (это все, что нужно!)
    st.query_params['user_email'] = email
    st.query_params['user_name'] = name
    st.query_params['user_username'] = username
    
    # Загружаем прогресс
    try:
        users = get_github_data()
        if email in users:
            st.session_state.achieved_endings = users[email].get("achieved_endings", {})
            user_achievements = users[email].get("achievements", {})
            if user_achievements:
                for key, value in user_achievements.items():
                    if key in st.session_state.achievements:
                        st.session_state.achievements[key] = value
    except Exception as e:
        print(f"Ошибка загрузки прогресса: {e}")
    
    st.rerun()

def logout_user():
    """Выход пользователя"""
    print("👋 Выход")
    
    st.session_state.user = None
    st.session_state.achieved_endings = {}
    
    # Удаляем из URL
    if 'user_email' in st.query_params:
        del st.query_params['user_email']
    if 'user_name' in st.query_params:
        del st.query_params['user_name']
    if 'user_username' in st.query_params:
        del st.query_params['user_username']
    
    st.rerun()

# Инициализация
init_auth()

# --- ДИАГНОСТИКА (временно) ---
st.sidebar.markdown("### 🔍 Отладка")
st.sidebar.write("User в session_state:", st.session_state.get('user'))
st.sidebar.write("Параметры URL:", dict(st.query_params))

# --- ПРОВЕРКА АВТОРИЗАЦИИ ---
if not st.session_state.get('user'):
    st.title("🔐 Интерактивные сказки")
    
    # Создаем вкладки для входа и регистрации
    tab1, tab2, tab3 = st.tabs(["🔑 Вход", "📝 Регистрация", "❓ Забыли пароль"])
    
    with tab1:
        st.markdown("### Вход в существующий аккаунт")
        
        with st.form("login_form"):
            login_email = st.text_input("Email или Логин", placeholder="your@email.com или username")
            login_password = st.text_input("Пароль", type="password", placeholder="••••••••")
            
            submitted_login = st.form_submit_button("🔑 Войти", width='stretch')
            
            if submitted_login:
                if login_email and login_password:
                    users = get_github_data()
                    
                    # Ищем пользователя по email или логину
                    found_user = None
                    found_email = None
                    
                    for email, user_data in users.items():
                        if (email == login_email or 
                            user_data.get('username') == login_email):
                            found_user = user_data
                            found_email = email
                            break
                    
                    if found_user:
                        # Проверяем пароль
                        stored_password = found_user.get('password')
                        
                        # Добавляем соль как в старом коде
                        salt = "interactive_tales_salt"
                        input_hash = hashlib.sha256((login_password + salt).encode()).hexdigest()
                        
                        if input_hash == stored_password:
                            name = found_user.get('name', found_email.split('@')[0])
                            username = found_user.get('username', found_email.split('@')[0])
                            login_user(found_email, name, username)
                            st.success("✅ Вход выполнен!")
                            st.rerun()
                        else:
                            st.error("❌ Неверный пароль!")
                            # Для отладки
                            with st.expander("🔧 Отладка"):
                                st.write("Ваш хеш:", input_hash)
                                st.write("Хеш в БД:", stored_password) 
                    else:
                        st.error("❌ Пользователь не найден!")
                else:
                    st.error("❌ Заполните все поля")  
    
    with tab2:
        st.markdown("### Создание нового аккаунта")
        
        with st.form("register_form"):
            reg_email = st.text_input("Email", placeholder="your@email.com")
            reg_username = st.text_input("Логин (уникальный)", placeholder="username123")
            reg_name = st.text_input("Ваше имя", placeholder="Иван Петров")
            reg_password = st.text_input("Пароль", type="password", placeholder="••••••••")
            reg_password2 = st.text_input("Подтвердите пароль", type="password", placeholder="••••••••")
            
            st.markdown("---")
            st.markdown("### 📜 Пользовательское соглашение")
            agree = st.checkbox("Я принимаю условия пользовательского соглашения")
            
            submitted_reg = st.form_submit_button("📝 Зарегистрироваться", width='stretch')
            
            if submitted_reg:
                # Проверка заполнения полей
                if not reg_email:
                    st.error("❌ Введите email")
                elif not reg_username:
                    st.error("❌ Введите логин")
                elif not reg_name:
                    st.error("❌ Введите имя")
                elif not reg_password:
                    st.error("❌ Введите пароль")
                elif reg_password != reg_password2:
                    st.error("❌ Пароли не совпадают")
                elif len(reg_password) < 6:
                    st.error("❌ Пароль должен быть не менее 6 символов")
                elif not agree:
                    st.error("❌ Примите пользовательское соглашение")
                else:
                    users = get_github_data()
                    
                    # Проверяем, нет ли уже такого email
                    if reg_email in users:
                        st.error("❌ Пользователь с таким email уже существует")
                    else:
                        # Проверяем, нет ли уже такого логина
                        username_exists = False
                        for email, user_data in users.items():
                            if user_data.get('username') == reg_username:
                                username_exists = True
                                break
                        
                        if username_exists:
                            st.error("❌ Этот логин уже занят. Придумайте другой")
                        else:
                            # Регистрируем нового пользователя
# Добавляем соль как в старом коде
                            salt = "interactive_tales_salt"
                            password_hash = hashlib.sha256((reg_password + salt).encode()).hexdigest()
                            
                            users[reg_email] = {
                                'username': reg_username,
                                'name': reg_name,
                                'password': password_hash,
                                'created_at': datetime.now().isoformat(),
                                'achieved_endings': {},
                                'achievements': {}
                            }
                            
                            if save_users_to_github(users):
                                login_user(reg_email, reg_name, reg_username)
                                st.success("✅ Регистрация успешна!")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка сохранения данных")
    
    with tab3:
        st.markdown("### 🔑 Восстановление пароля")
        
        with st.form("reset_form"):
            reset_email = st.text_input("Ваш Email", placeholder="your@email.com")
            submitted_reset = st.form_submit_button("📧 Отправить код", width='stretch')
            
            if submitted_reset:
                if reset_email:
                    users = get_github_data()
                    if reset_email in users:
                        # Генерируем временный код
                        reset_code = ''.join(random.choices(string.digits, k=6))
                        expiry = datetime.now() + timedelta(minutes=15)
                        
                        st.session_state.reset_data = {
                            'email': reset_email,
                            'code': reset_code,
                            'expiry': expiry.isoformat()
                        }
                        
                        st.info(f"🔐 Код подтверждения: **{reset_code}**")
                        st.session_state.reset_code_sent = True
                        st.rerun()
                    else:
                        st.error("❌ Пользователь с таким email не найден")
                else:
                    st.error("❌ Введите email")
        
        # Если код отправлен, показываем форму ввода
        if st.session_state.get('reset_code_sent'):
            with st.form("verify_reset_form"):
                verify_code = st.text_input("Введите код из письма", max_chars=6)
                new_password = st.text_input("Новый пароль", type="password")
                new_password2 = st.text_input("Подтвердите пароль", type="password")
                
                submitted_verify = st.form_submit_button("🔄 Сменить пароль", width='stretch')
                
                if submitted_verify:
                    reset_data = st.session_state.get('reset_data', {})
                    
                    if not reset_data:
                        st.error("❌ Сессия восстановления истекла")
                    elif datetime.now() > datetime.fromisoformat(reset_data['expiry']):
                        st.error("❌ Код истек. Запросите новый")
                        del st.session_state.reset_data
                        del st.session_state.reset_code_sent
                        st.rerun()
                    elif verify_code != reset_data['code']:
                        st.error("❌ Неверный код")
                    elif not new_password or len(new_password) < 6:
                        st.error("❌ Пароль должен быть не менее 6 символов")
                    elif new_password != new_password2:
                        st.error("❌ Пароли не совпадают")
                    else:
                        # Обновляем пароль
                        users = get_github_data()
                        email = reset_data['email']
                        
                        if email in users:
                            salt = "interactive_tales_salt"
                            new_password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
                            users[email]['password'] = new_password_hash
                            
                            if save_users_to_github(users):
                                st.success("✅ Пароль успешно изменен!")
                                del st.session_state.reset_data
                                del st.session_state.reset_code_sent
                                st.rerun()
                            else:
                                st.error("❌ Ошибка сохранения")
    
    st.markdown("---")
    st.info("ℹ️ Ваш прогресс будет автоматически сохраняться")
    st.stop()

# --- Восстанавливаем состояние сказки из URL ---
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
    
    if tale_name == "Теремок":
        progress["teremok_count"] = len(st.session_state.achieved_endings.get("Теремок", set()))
        if progress["teremok_count"] >= 5 and not ach["teremok_5"]:
            ach["teremok_5"] = True
            st.balloons()
            st.success("🏆 Достижение: «Терем-теремок» (5 концовок)")
        if progress["teremok_count"] >= 14 and not ach["teremok_all"]:
            ach["teremok_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Всем дом»")
        
        if ending_data:
            ending_num = ending_data.get("ending_number")
            if ending_num in [6, 7] and not ach["teremok_fairy"]:
                ach["teremok_fairy"] = True
                st.balloons()
                st.success("🏆 Достижение: «Постучи три раза»")
            if ending_num in [9, 10, 11] and not ach["teremok_bees"]:
                ach["teremok_bees"] = True
                st.balloons()
                st.success("🏆 Достижение: «Пчелиный король»")
    
    if tale_name == "Золотая рыбка":
        if ending_type == "sad" and ending_data:
            if ending_data.get("ending_number") in [1,2,3]:
                progress["rybka_greedy"] += 1
                if progress["rybka_greedy"] >= 3 and not ach["rybka_3_greedy"]:
                    ach["rybka_3_greedy"] = True
                    st.balloons()
                    st.success("🏆 Достижение: «Золотая жадность» (3 жадные концовки)")
        
        progress["rybka_count"] = len(st.session_state.achieved_endings.get("Золотая рыбка", set()))
        if progress["rybka_count"] >= 10 and not ach["rybka_all"]:
            ach["rybka_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Мудрец» (все концовки Золотой рыбки)")
    
    if tale_name == "Курочка Ряба":
        if ending_type == "happy" and ending_data:
            if ending_data.get("ending_number") in [1,2,3,4,5,6,7]:
                progress["ryaba_save"] += 1
                if progress["ryaba_save"] >= 3 and not ach["ryaba_3_save"]:
                    ach["ryaba_3_save"] = True
                    st.balloons()
                    st.success("🏆 Достижение: «Курочка-спасительница» (3 спасения)")
        
        progress["ryaba_count"] = len(st.session_state.achieved_endings.get("Курочка Ряба", set()))
        if progress["ryaba_count"] >= 12 and not ach["ryaba_all"]:
            ach["ryaba_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Золотой урожай» (все концовки Курочки Рябы)")
        
        if ending_data and ending_data.get("ending_type") == "secret":
            ending_num = ending_data.get("ending_number")
            if ending_num in [5,6] and not ach["ryaba_wish"]:
                ach["ryaba_wish"] = True
                st.balloons()
                st.success("🏆 Достижение: «Хрустальный шар» (загадать желание)")
            if ending_num == 7 and not ach["ryaba_drink"]:
                ach["ryaba_drink"] = True
                st.balloons()
                st.success("🏆 Достижение: «Гулянка» (выпить с дедом)")
    
    if tale_name == "Путешествие в Волшебный лес":
        progress["forest_count"] = len(st.session_state.achieved_endings.get("Путешествие в Волшебный лес", set()))
        if progress["forest_count"] >= 12 and not ach["forest_all"]:
            ach["forest_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Повелитель леса» (все концовки)")
    
    if tale_name == "Хроники разбитых часов: Детектив времени":
        progress["detective_count"] = len(st.session_state.achieved_endings.get(tale_name, set()))
        if progress["detective_count"] >= 10 and not ach["detective_10"]:
            ach["detective_10"] = True
            st.balloons()
            st.success("🏆 Достижение: «Следопыт» (10 концовок)")
        if progress["detective_count"] >= 25 and not ach["detective_all"]:
            ach["detective_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Идеальное преступление» (все концовки)")
    
    if tale_name == "Мелодия дождя":
        progress["romance_count"] = len(st.session_state.achieved_endings.get(tale_name, set()))
        if progress["romance_count"] >= 5 and not ach["romance_5_happy"]:
            ach["romance_5_happy"] = True
            st.balloons()
            st.success("🏆 Достижение: «Романтик» (5 концовок)")
        if progress["romance_count"] >= 20 and not ach["romance_all"]:
            ach["romance_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Идеальная пара» (все концовки)")
    
    if tale_name == "Проклятие крови ЛИКСА":
        progress["lyx_count"] = len(st.session_state.achieved_endings.get(tale_name, set()))
        if progress["lyx_count"] >= 5 and not ach.get("lyx_5", False):
            ach["lyx_5"] = True
            st.balloons()
            st.success("🏆 Достижение: «Выжившая» (5 концовок ЛИКСЫ)")
        if progress["lyx_count"] >= 9 and not ach.get("lyx_all", False):
            ach["lyx_all"] = True
            st.balloons()
            st.success("🏆 Достижение: «Проклятие снято» (все концовки ЛИКСЫ)")
    
    total = 0
    for tale in tales.keys():
        total += len(st.session_state.achieved_endings.get(tale, set()))
    progress["total_endings_found"] = total
    
    if total >= 50 and not ach["total_50"]:
        ach["total_50"] = True
        st.balloons()
        st.success("🏆 Достижение: «Коллекционер» (50 концовок)")
    if total >= 80 and not ach["total_80"]:
        ach["total_80"] = True
        st.balloons()
        st.success("🏆 Достижение: «Профессионал» (80 концовок)")
    
    total_possible = 16 + 14 + 20 + 12 + 12 + 25 + 20 + 9
    if total >= total_possible and not ach["total_all"]:
        ach["total_all"] = True
        st.balloons()
        st.balloons()
        st.success("👑 ДОСТИЖЕНИЕ: «Библиотекарь» (ВСЕ концовки!)")
    
    # Сохраняем прогресс после каждого достижения
    save_user_progress()

# --- Стили (ИСПРАВЛЕННЫЕ для лучшей читаемости) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
    
    /* Общий фон */
    .stApp {
        background: linear-gradient(135deg, #fcf3e0 0%, #fef9e7 100%);
    }
    
    /* Заголовки - ТЕМНЫЕ И ЧЕТКИЕ */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif;
        color: #2c1e0e !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    h1 {
        font-size: 3rem;
        border-bottom: 3px solid #b5926a;
        padding-bottom: 15px;
        margin-bottom: 30px;
    }
    
    /* Обычный текст - ТЕМНО-КОРИЧНЕВЫЙ */
    p, li, .stMarkdown, .stText, .stChatMessage p, .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        font-family: 'Open Sans', sans-serif;
        color: #2c1e0e !important;
        font-size: clamp(1rem, 2vw, 1.2rem);
        line-height: 1.6;
        font-weight: 500 !important;
    }
    
    /* Специально для сообщений об ошибках и информации */
    .stAlert {
        background-color: #f8f0e0 !important;
        border-left: 5px solid #b5926a !important;
        color: #2c1e0e !important;
    }
    
    .stInfo {
        background-color: #e6f0fa !important;
        color: #1a4c7a !important;
    }
    
    .stSuccess {
        background-color: #e0f0e0 !important;
        color: #1a5a1a !important;
    }
    
    .stWarning {
        background-color: #fff0d0 !important;
        color: #8a6a2a !important;
    }
    
    .stError {
        background-color: #ffe0e0 !important;
        color: #a03232 !important;
    }
    
    /* Боковая панель */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5e9d8 0%, #ecdcc5 100%);
        border-right: 2px solid #b5926a;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #2c1e0e !important;
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
    
    /* Все кнопки */
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
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Текст на кнопках */
    .stButton > button p {
        color: #2a1c0e !important;
        font-weight: 700 !important;
    }
    
    /* Поля ввода */
    .stTextInput > label {
        color: #2c1e0e !important;
        font-weight: 600;
    }
    
    .stTextInput > div > input {
        background-color: white !important;
        border: 2px solid #b5926a !important;
        border-radius: 30px !important;
        padding: 12px 20px !important;
        color: #2c1e0e !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    /* Чат сообщения */
    .stChatMessage {
        animation: fadeIn 0.3s ease-out;
        background: white !important;
        border: 2px solid #b5926a !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stChatMessage[data-testid="chatMessageUser"] {
        background: linear-gradient(135deg, #e6d5b8, #d4b68a) !important;
    }
    
    .stChatMessage p {
        color: #2c1e0e !important;
        font-weight: 500 !important;
    }
    
    /* Карточки сказок */
    div[data-testid="column"] > div {
        background: white;
        border-radius: 24px;
        padding: 25px;
        border: 2px solid #b5926a;
        box-shadow: 0 10px 25px rgba(93,58,26,0.15);
        height: auto !important;
        min-height: 500px;
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"] > div p {
        color: #2c1e0e !important;
    }
    
    /* Прогресс-бар */
    .stProgress > div > div {
        background: linear-gradient(90deg, #b5926a, #8b6b4f) !important;
        border-radius: 10px;
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
    if st.session_state.get('user'):
        user = st.session_state.user
        st.markdown(f"👋 Привет, **{user.get('name', user['email'])}**!")
        st.markdown(f"📧 {user['email']}")
        
        if st.button("🚪 Выйти", width='stretch'):
            logout_user()
    else:
        st.markdown("👋 Добро пожаловать!")
    
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
