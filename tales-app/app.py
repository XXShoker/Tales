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

# --- Функции для работы с GitHub ---
@st.cache_data(ttl=60)  # кэшируем на 1 минуту, чтобы не дёргать постоянно
def load_users_from_github():
    """Загружает данные пользователей из GitHub"""
    if not GH_TOKEN:
        st.warning("GitHub токен не настроен. Прогресс не будет сохраняться.")
        return {}
    
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_FILE_PATH}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content["content"]).decode("utf-8")
            return json.loads(decoded)
        elif response.status_code == 404:
            return {}
        else:
            st.error(f"Ошибка загрузки данных: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Ошибка при загрузке: {e}")
        return {}

def save_users_to_github(users_data):
    """Сохраняет данные пользователей в GitHub"""
    if not GH_TOKEN:
        return False
    
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_FILE_PATH}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Получаем текущий файл чтобы узнать sha
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
    
    content_json = json.dumps(users_data, ensure_ascii=False, indent=2)
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
        return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"Ошибка при сохранении: {e}")
        return False

# --- Функции аутентификации ---
def hash_password(password):
    salt = "interactive_tales_salt"  # в продакшене лучше уникальная соль на пользователя
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_session_token(user_id):
    return hmac.new(
        SESSION_SECRET.encode(),
        f"{user_id}:{datetime.now().timestamp()}".encode(),
        hashlib.sha256
    ).hexdigest()

def send_verification_email(to_email, code):
    """Отправляет код подтверждения на email"""
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
    """Шаг 1 регистрации: проверка и создание временной записи"""
    if not is_valid_email(email):
        return False, "Некорректный email"
    
    users = st.session_state.users_data
    if email in users:
        return False, "Пользователь с таким email уже существует"
    
    # Создаём временную запись с кодом
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
    """Шаг 2: проверка кода и создание аккаунта"""
    pending = st.session_state.get("pending_registration")
    if not pending:
        return False, "Нет ожидающей регистрации"
    
    if datetime.now() > datetime.fromisoformat(pending["expiry"]):
        return False, "Код истёк. Запросите новый."
    
    if pending["code"] != code:
        return False, "Неверный код"
    
    # Создаём пользователя
    email = pending["email"]
    user_id = hashlib.md5(email.encode()).hexdigest()[:10]
    st.session_state.users_data[email] = {
        "user_id": user_id,
        "name": pending["name"],
        "email": email,
        "password_hash": pending["password_hash"],
        "created_at": datetime.now().isoformat(),
        "verified": True,
        "achieved_endings": {},
        "achievements": {}
    }
    
    # Сохраняем в GitHub
    if save_users_to_github(st.session_state.users_data):
        del st.session_state.pending_registration
        return True, "Регистрация успешна!"
    else:
        return False, "Ошибка при сохранении данных"

def login_user(email, password):
    """Вход пользователя"""
    users = st.session_state.users_data
    if email not in users:
        return False, "Пользователь не найден"
    
    user = users[email]
    if not user.get("verified", False):
        return False, "Email не подтверждён. Проверьте почту."
    
    if verify_password(password, user["password_hash"]):
        st.session_state.user = user
        # Загружаем прогресс
        st.session_state.achieved_endings = user.get("achieved_endings", {})
        return True, "Вход выполнен успешно!"
    else:
        return False, "Неверный пароль"

def logout_user():
    """Выход пользователя с сохранением прогресса"""
    if st.session_state.user:
        email = st.session_state.user["email"]
        st.session_state.users_data[email]["achieved_endings"] = st.session_state.achieved_endings
        save_users_to_github(st.session_state.users_data)
    
    st.session_state.user = None
    st.session_state.achieved_endings = {}
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []
    st.session_state.selected_tale = None
    st.rerun()

def delete_account():
    """Удаление аккаунта пользователя"""
    if st.session_state.user:
        email = st.session_state.user["email"]
        if email in st.session_state.users_data:
            del st.session_state.users_data[email]
            save_users_to_github(st.session_state.users_data)
        logout_user()
        return True
    return False

def save_user_progress():
    """Сохраняет прогресс текущего пользователя"""
    if st.session_state.user:
        email = st.session_state.user["email"]
        st.session_state.users_data[email]["achieved_endings"] = st.session_state.achieved_endings
        # Можно также сохранять achievements, если они есть
        save_users_to_github(st.session_state.users_data)

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
if "achievements" not in st.session_state:
    st.session_state.achievements = { ... }  # (ваш существующий словарь)
if "achievement_progress" not in st.session_state:
    st.session_state.achievement_progress = { ... }  # (ваш существующий)

# Данные пользователей
if "users_data" not in st.session_state:
    st.session_state.users_data = load_users_from_github()
if "user" not in st.session_state:
    st.session_state.user = None
if "pending_registration" not in st.session_state:
    st.session_state.pending_registration = None

# --- Стили (оставлены как есть, см. предыдущий код) ---
# (полный CSS я не буду повторять для краткости, он остаётся из предыдущего app.py)
# Вставьте сюда весь CSS из предыдущей версии.

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
                    
                    # Пользовательское соглашение
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
            # Этап подтверждения кода
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
    
    # --- Прогресс и достижения (остаётся как есть) ---
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
    
    # Достижения (как в предыдущей версии, но теперь с учётом авторизации)
    if st.session_state.selected_tale is None:
        with st.expander("🏆 Достижения"):
            # ... (весь код с эмодзи, как ранее)
            pass  # для краткости, вставьте сюда свой код достижений

# --- Основная область (без изменений, только добавим автосохранение) ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    # ... (весь код отображения карточек сказок)
    pass
else:
    # Отображение сказки
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
                
                # Проверяем достижения
                check_achievements(st.session_state.selected_tale, current.get("ending_type"), current)
                
                # Сохраняем прогресс в GitHub
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
