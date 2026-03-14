import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="centered")

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

# --- Получение API-ключа из секретов ---
DEEPAI_KEY = st.secrets.get("DEEPAI_KEY", None)
if DEEPAI_KEY is None:
    st.error("❌ API-ключ DeepAI не найден. Добавьте DEEPAI_KEY в секреты приложения.")
    st.stop()

# --- Функция генерации изображения через DeepAI ---
@st.cache_data(ttl=3600)  # Кэшируем на 1 час
def generate_image_deepai(prompt):
    """
    Отправляет запрос к DeepAI API и возвращает PIL Image или None.
    """
    url = "https://api.deepai.org/api/text2img"
    headers = {"api-key": DEEPAI_KEY}
    data = {"text": prompt, "grid_size": "1"}
    
    try:
        # Шаг 1: получаем URL сгенерированного изображения
        response = requests.post(url, headers=headers, data=data, timeout=30)
        if response.status_code != 200:
            st.warning(f"Ошибка DeepAI: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        image_url = result.get("output_url")
        if not image_url:
            st.warning("API не вернул URL изображения")
            return None
        
        # Шаг 2: скачиваем изображение по полученному URL
        img_response = requests.get(image_url, timeout=15)
        if img_response.status_code != 200:
            st.warning("Не удалось скачать изображение")
            return None
        
        image = Image.open(BytesIO(img_response.content))
        return image
    except Exception as e:
        st.warning(f"Ошибка при генерации: {e}")
        return None

# --- Основные функции приложения (без изменений) ---
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
    st.image("https://via.placeholder.com/150x100/ffe6f0/ff69b4?text=📚", width='stretch')
    st.markdown("## 🌟 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
    # Кнопка доната (замените ссылку на свою)
    try:
        st.link_button("💖 Поддержать донатом", "https://donate.stream/your-link", width='stretch')
    except AttributeError:
        st.markdown(
            '<a href="https://donate.stream/your-link" target="_blank">'
            '<button style="background-color:#FF4B4B; color:white; padding:0.5rem 1rem; '
            'border:none; border-radius:0.5rem; width:100%; font-size:1rem; '
            'cursor:pointer;">💖 Поддержать донатом</button></a>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    if st.session_state.selected_tale is not None:
        if st.button("🔄 Сменить сказку", width='stretch'):
            reset_to_main()
            st.rerun()
        if st.button("❌ Завершить и выйти", width='stretch'):
            reset_to_main()
            st.rerun()

# --- Основная область ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

if st.session_state.selected_tale is None:
    # Экран выбора сказки
    st.markdown("### Выберите сказку для чтения")
    tale_names = list(tales.keys())
    cols = st.columns(2)
    for i, tale_name in enumerate(tale_names):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"#### {tale_name}")
                if tales[tale_name].get("description"):
                    st.markdown(tales[tale_name]["description"])
                if st.button(f"✨ Начать", key=f"choose_{tale_name}", width='stretch'):
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
        # --- Генерация изображения через DeepAI ---
        if current_scene.get("prompt"):
            with st.spinner("🎨 Волшебная картинка создаётся..."):
                image = generate_image_deepai(current_scene["prompt"])
            
            if image:
                st.image(image, width='stretch', caption="✨ Волшебная иллюстрация")
                if st.button("🔄 Другая картинка", key="regenerate_image"):
                    st.rerun()
            else:
                st.image("https://via.placeholder.com/800x400/ffe6f0/ff69b4?text=✨+Представьте+сами", width='stretch')
                st.caption("🌟 Не удалось сгенерировать картинку, но вы можете представить эту сцену сами!")
        else:
            st.image("https://via.placeholder.com/800x400/ffe6f0/ff69b4?text=✨+Вообразите+эту+сцену", width='stretch')

        # Кнопки выбора или конец сказки
        if current_scene.get("options"):
            st.markdown("### Твой выбор:")
            for opt in current_scene["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", width='stretch'):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад к предыдущему выбору", width='stretch'):
                    go_back()
        else:
            st.markdown("---")
            st.markdown("🎉 **Конец сказки!**")
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Вернуться к предыдущему выбору", width='stretch'):
                    go_back()
            if st.button("🔄 Начать эту сказку заново", width='stretch'):
                start_tale(st.session_state.selected_tale)
                st.rerun()
    else:
        st.error("⚠️ Сцена не найдена. Вернитесь к выбору сказок.")
        if st.button("⬅️ К выбору сказок", width='stretch'):
            reset_to_main()
            st.rerun()
