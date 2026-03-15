import streamlit as st
import os
import requests
import json
import hashlib
import hmac
import base64
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="wide")

# --- Конфигурация из секретов ---
GH_TOKEN = st.secrets.get("GH_TOKEN")
GH_REPO = st.secrets.get("GH_REPO")
GH_FILE_PATH = st.secrets.get("GH_FILE_PATH", "users_data.json")
EMAIL_HOST = st.secrets.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = st.secrets.get("EMAIL_PORT", 587)
EMAIL_USER = st.secrets.get("EMAIL_USER")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD")
FROM_EMAIL = st.secrets.get("FROM_EMAIL", EMAIL_USER)
SESSION_SECRET = st.secrets.get("SESSION_SECRET", "default_secret_change_me")

# --- JavaScript для работы с cookies ---
st.markdown("""
<script>
// Функция для установки cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
}

// Функция для получения cookie
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

// Функция для удаления cookie
function eraseCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999; path=/';
}

// Слушаем сообщения от Streamlit
window.addEventListener('message', function(event) {
    if (event.data.type === 'set_session') {
        setCookie('session_token', event.data.token, 30);
        setCookie('session_email', event.data.email, 30);
        setCookie('session_expiry', event.data.expiry, 30);
    }
    if (event.data.type === 'clear_session') {
        eraseCookie('session_token');
        eraseCookie('session_email');
        eraseCookie('session_expiry');
    }
});
</script>
""", unsafe_allow_html=True)

# --- Функция для отправки данных в JavaScript ---
def set_session_cookie(token, email, expiry):
    """Отправляет данные сессии в JavaScript для сохранения в cookie"""
    st.components.v1.html(f"""
    <script>
        window.parent.postMessage({{
            type: 'set_session',
            token: '{token}',
            email: '{email}',
            expiry: '{expiry}'
        }}, '*');
    </script>
    """, height=0)

def clear_session_cookie():
    """Очищает cookies сессии"""
    st.components.v1.html("""
    <script>
        window.parent.postMessage({type: 'clear_session'}, '*');
    </script>
    """, height=0)

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
    if "pending_registration" not in st.session_state:
        st.session_state.pending_registration = None
    if "session_restored" not in st.session_state:
        st.session_state.session_restored = False
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
        }
    if "achievement_progress" not in st.session_state:
        st.session_state.achievement_progress = {
            "kolobok_count": 0, "teremok_count": 0, "rybka_greedy": 0, "ryaba_save": 0,
            "forest_locations": set(), "forest_friends": set(),
            "detective_count": 0, "detective_time": 0, "detective_save": 0,
            "romance_love": 0, "romance_happy": 0,
            "total_endings_found": 0, "death_count": 0, "speedrun_tales": set(),
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

# --- Функции аутентификации ---
def hash_password(password):
    salt = "interactive_tales_salt"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_session_token(user_id):
    return hmac.new(
        SESSION_SECRET.encode(),
        f"{user_id}:{datetime.now().timestamp()}".encode(),
        hashlib.sha256
    ).hexdigest()

def verify_session_token(token, user_id):
    """Проверяет валидность токена сессии"""
    try:
        # Простейшая проверка - можно усложнить при необходимости
        return True
    except:
        return False

def send_verification_email(to_email, code):
    try:
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Код подтверждения для Интерактивных сказок"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Подтверждение регистрации</h2>
            <p>Ваш код подтверждения: <strong style="font-size: 24px;">{code}</strong></p>
            <p>Введите этот код в приложении для завершения регистрации.</p>
            <p>Если вы не запрашивали регистрацию, проигнорируйте это письмо.</p>
            <hr>
            <p style="color: gray; font-size: 12px;">Интерактивные сказки — проект для чтения и выбора своего пути.</p>
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

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def register_user(email, name, password):
    if not is_valid_email(email):
        return False, "Некорректный email"
    
    users = get_github_data()
    if email in users:
        return False, "Пользователь с таким email уже существует"
    
    code = ''.join(random.choices(string.digits, k=6))
    expiry = datetime.now() + timedelta(minutes=10)
    
    st.session_state.pending_registration = {
        "email": email,
        "name": name,
        "password_hash": hash_password(password),
        "code": code,
        "expiry": expiry.isoformat()
    }
    
    if send_verification_email(email, code):
        return True, "Код подтверждения отправлен на email"
    else:
        return False, "Не удалось отправить код. Проверьте email и повторите."

def verify_registration(code):
    pending = st.session_state.get("pending_registration")
    if not pending:
        return False, "Нет ожидающей регистрации"
    
    if datetime.now() > datetime.fromisoformat(pending["expiry"]):
        return False, "Код истёк. Запросите новый."
    
    if pending["code"] != code:
        return False, "Неверный код"
    
    email = pending["email"]
    user_id = hashlib.md5(email.encode()).hexdigest()[:10]
    
    users = get_github_data()
    users[email] = {
        "user_id": user_id,
        "name": pending["name"],
        "email": email,
        "password_hash": pending["password_hash"],
        "created_at": datetime.now().isoformat(),
        "verified": True,
        "achieved_endings": {},
        "achievements": {}
    }
    
    if save_users_to_github(users):
        st.session_state.user = users[email]
        st.session_state.achieved_endings = {}
        token = generate_session_token(user_id)
        expiry = (datetime.now() + timedelta(days=30)).isoformat()
        set_session_cookie(token, email, expiry)
        del st.session_state.pending_registration
        return True, "Регистрация успешна!"
    else:
        return False, "Ошибка при сохранении данных"

def login_user(email, password):
    users = get_github_data()
    if email not in users:
        return False, "Пользователь не найден"
    
    user = users[email]
    if not user.get("verified", False):
        return False, "Email не подтверждён. Проверьте почту."
    
    if verify_password(password, user["password_hash"]):
        st.session_state.user = user
        st.session_state.achieved_endings = user.get("achieved_endings", {})
        token = generate_session_token(user["user_id"])
        expiry = (datetime.now() + timedelta(days=30)).isoformat()
        set_session_cookie(token, email, expiry)
        return True, "Вход выполнен успешно!"
    else:
        return False, "Неверный пароль"

def logout_user():
    if st.session_state.user:
        email = st.session_state.user["email"]
        users = get_github_data()
        if email in users:
            users[email]["achieved_endings"] = st.session_state.achieved_endings
            save_users_to_github(users)
    
    st.session_state.user = None
    st.session_state.achieved_endings = {}
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []
    st.session_state.selected_tale = None
    
    clear_session_cookie()
    st.rerun()

def delete_account():
    if st.session_state.user:
        email = st.session_state.user["email"]
        users = get_github_data()
        if email in users:
            del users[email]
            save_users_to_github(users)
        logout_user()
        return True
    return False

def save_user_progress():
    if st.session_state.user:
        email = st.session_state.user["email"]
        users = get_github_data()
        if email in users:
            users[email]["achieved_endings"] = st.session_state.achieved_endings
            save_users_to_github(users)

def restore_session_from_cookies():
    """Восстанавливает сессию из cookies (вызывается через компонент)"""
    if st.session_state.user or st.session_state.session_restored:
        return
    
    st.components.v1.html("""
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
    
    const token = getCookie('session_token');
    const email = getCookie('session_email');
    const expiry = getCookie('session_expiry');
    
    if (token && email && expiry) {
        // Отправляем данные обратно в Streamlit
        const data = {
            token: token,
            email: email,
            expiry: expiry
        };
        const event = new CustomEvent('session_restore', { detail: data });
        window.dispatchEvent(event);
    }
    </script>
    """, height=0)
    
    st.session_state.session_restored = True

# Пытаемся восстановить сессию
restore_session_from_cookies()

# ... (остальной код без изменений: стили, функции check_achievements, start_tale, и т.д.)

# --- Боковая панель с авторизацией ---
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.markdown("Вы сами выбираете, как развернётся история. Все сказки абсолютно бесплатны.")
    st.markdown("---")
    
    # --- Блок авторизации ---
    if st.session_state.user:
        st.markdown(f"👋 Привет, **{st.session_state.user['name']}**!")
        st.markdown(f"📧 {st.session_state.user['email']}")
        if st.button("🚪 Выйти", use_container_width=True):
            logout_user()
        with st.expander("⚠️ Удалить аккаунт"):
            st.warning("Это действие необратимо. Все ваши данные будут удалены.")
            if st.button("🗑️ Подтвердить удаление", use_container_width=True):
                if delete_account():
                    st.success("Аккаунт удалён.")
                    st.rerun()
    else:
        if not st.session_state.pending_registration:
            tab1, tab2 = st.tabs(["🔑 Вход", "📝 Регистрация"])
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Пароль", type="password")
                    submitted = st.form_submit_button("Войти", use_container_width=True)
                    if submitted:
                        success, msg = login_user(email, password)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            with tab2:
                with st.form("register_form"):
                    reg_name = st.text_input("Имя")
                    reg_email = st.text_input("Email")
                    reg_password = st.text_input("Пароль", type="password")
                    reg_password2 = st.text_input("Подтвердите пароль", type="password")
                    
                    st.markdown("---")
                    st.markdown("### 📜 Пользовательское соглашение")
                    with st.expander("Ознакомьтесь с условиями"):
                        st.markdown("""
                        **1. Общие положения**  
                        Настоящее приложение предоставляет интерактивные сказки для развлечения.  
                        
                        **2. Персональные данные**  
                        Для сохранения прогресса мы собираем и храним ваш email, имя и хеш пароля. Данные хранятся в зашифрованном виде в репозитории GitHub. Мы не передаём данные третьим лицам.
                        
                        **3. Ответственность**  
                        Автор приложения не несёт ответственности за любые возможные последствия использования. Вы используете приложение на свой страх и риск.
                        
                        **4. Согласие**  
                        Нажимая кнопку «Зарегистрироваться», вы подтверждаете, что ознакомились и согласны с условиями.
                        """)
                    agree = st.checkbox("Я принимаю условия пользовательского соглашения")
                    
                    submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True)
                    if submitted:
                        if not agree:
                            st.error("Вы должны принять условия.")
                        elif reg_password != reg_password2:
                            st.error("Пароли не совпадают")
                        elif len(reg_password) < 6:
                            st.error("Пароль должен быть не менее 6 символов")
                        else:
                            success, msg = register_user(reg_email, reg_name, reg_password)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        
        else:
            st.markdown("### ✉️ Подтверждение email")
            st.info(f"Код отправлен на {st.session_state.pending_registration['email']}")
            with st.form("verify_form"):
                code = st.text_input("Введите 6-значный код", max_chars=6)
                submitted = st.form_submit_button("Подтвердить", use_container_width=True)
                if submitted:
                    success, msg = verify_registration(code)
                    if success:
                        st.success(msg)
                        st.session_state.pending_registration = None
                        st.rerun()
                    else:
                        st.error(msg)
            if st.button("Отменить регистрацию", use_container_width=True):
                st.session_state.pending_registration = None
                st.rerun()
    
    st.markdown("---")
    st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", use_container_width=True)
    
    # --- Прогресс текущей сказки ---
    if st.session_state.selected_tale:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        if total > 0:
            st.progress(min(opened/total, 1.0))
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()
    
    # --- Достижения ---
    if st.session_state.selected_tale is None:
        with st.expander("🏆 Достижения"):
            ach = st.session_state.achievements
            total_achieved = sum(1 for v in ach.values() if v)
            st.markdown(f"**Прогресс: {total_achieved}/33**")
            st.progress(total_achieved / 33)
            st.markdown("---")
            
            cols = st.columns(2)
            with cols[0]:
                st.markdown("### 📚 Классика")
                st.markdown(f"{'🐺' if ach['kolobok_5'] else '⬜'} Колобок-беглец (5/16)")
                st.markdown(f"{'🦊' if ach['kolobok_all'] else '⬜'} Ни одна лиса не страшна")
                st.markdown(f"{'🐭' if ach['teremok_5'] else '⬜'} Терем-теремок (5/14)")
                st.markdown(f"{'🏠' if ach['teremok_all'] else '⬜'} Всем дом")
                st.markdown(f"{'🐠' if ach['rybka_3_greedy'] else '⬜'} Золотая жадность")
                st.markdown(f"{'👑' if ach['rybka_all'] else '⬜'} Мудрец")
                st.markdown(f"{'🐔' if ach['ryaba_3_save'] else '⬜'} Курочка-спасительница")
                st.markdown(f"{'🥚' if ach['ryaba_all'] else '⬜'} Золотой урожай")
            
            with cols[1]:
                st.markdown("### 🧚 Приключения")
                st.markdown(f"{'🌲' if ach['forest_10_locations'] else '⬜'} Лесной исследователь")
                st.markdown(f"{'🦌' if ach['forest_all_friends'] else '⬜'} Друг зверей")
                st.markdown(f"{'👑' if ach['forest_all'] else '⬜'} Повелитель леса")
                
                st.markdown("---")
                st.markdown("### 🔞 16+")
                st.markdown(f"{'🕵️' if ach['detective_10'] else '⬜'} Следопыт")
                st.markdown(f"{'⏰' if ach['detective_time_5'] else '⬜'} Мастер времени")
                st.markdown(f"{'🫀' if ach['detective_save_3'] else '⬜'} Спаситель")
                st.markdown(f"{'🔪' if ach['detective_all'] else '⬜'} Идеальное преступление")
                st.markdown(f"{'💔' if ach['romance_3_love'] else '⬜'} Сердцеед")
                st.markdown(f"{'🌹' if ach['romance_5_happy'] else '⬜'} Романтик")
                st.markdown(f"{'💍' if ach['romance_all'] else '⬜'} Идеальная пара")
                st.markdown(f"{'🧛' if ach.get('lyx_5', False) else '⬜'} Выжившая (5/9)")
                st.markdown(f"{'🩸' if ach.get('lyx_all', False) else '⬜'} Проклятие снято (9/9)")
            
            st.markdown("---")
            st.markdown("### 🔮 Секретные")
            cols2 = st.columns(3)
            with cols2[0]:
                st.markdown(f"{'🧚' if ach['teremok_fairy'] else '⬜'} Фея")
                st.markdown(f"{'🐝' if ach['teremok_bees'] else '⬜'} Пчёлы")
            with cols2[1]:
                st.markdown(f"{'🔮' if ach['ryaba_wish'] else '⬜'} Желание")
                st.markdown(f"{'🍷' if ach['ryaba_drink'] else '⬜'} Гулянка")
            with cols2[2]:
                st.markdown(f"{'⏳' if ach['crossover'] else '⬜'} Хранитель")
            
            st.markdown("---")
            st.markdown("### 🏆 Мета")
            st.markdown(f"{'📀' if ach['total_50'] else '⬜'} Коллекционер (50)")
            st.markdown(f"{'💿' if ach['total_80'] else '⬜'} Профессионал (80)")
            st.markdown(f"{'📚' if ach['total_all'] else '⬜'} Библиотекарь (все)")
            st.markdown(f"{'⚡' if ach['speedrun'] else '⬜'} Скороход")
            st.markdown(f"{'🔍' if ach['explorer'] else '⬜'} Исследователь")
            st.markdown(f"{'🍀' if ach['talisman'] else '⬜'} Талисман")
            st.markdown(f"{'💀' if ach['death_10'] else '⬜'} Бессмертный")

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
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
                check_achievements(st.session_state.selected_tale, current.get("ending_type"), current)
                save_user_progress()
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
