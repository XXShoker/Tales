import streamlit as st
import replicate
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
if "image_counter" not in st.session_state:
    st.session_state.image_counter = 0  # для перегенерации

# --- Проверка токена Replicate ---
REPLICATE_API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN", None)
if REPLICATE_API_TOKEN is None:
    st.error("❌ API-токен Replicate не найден. Добавьте REPLICATE_API_TOKEN в секреты приложения.")
    st.stop()

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# --- Функция генерации изображения через Replicate ---
@st.cache_data(ttl=3600)
def generate_image_replicate(prompt, counter):
    try:
        output = replicate_client.run(
            "stability-ai/stable-diffusion-3.5-large",
            input={
                "prompt": prompt,
                "width": 1024,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 25,
                "negative_prompt": "ugly, blurry, low quality, bad anatomy, child drawing, cartoon"
            }
        )
        if output and isinstance(output, list) and len(output) > 0:
            image_url = output[0]
            img_response = requests.get(image_url, timeout=15)
            if img_response.status_code == 200:
                return Image.open(BytesIO(img_response.content))
            else:
                st.warning("Не удалось скачать изображение")
                return None
        else:
            st.warning("Replicate не вернул изображение")
            return None
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

# --- Боковая панель (без изменений) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x100/ffe6f0/ff69b4?text=📚", width='stretch')
    st.markdown("## 🌟 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
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
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    current_scene = st.session_state.scenes.get(st.session_state.scene_id)

    if current_scene:
        # --- Генерация изображения с учётом счётчика ---
        if current_scene.get("prompt"):
            with st.spinner("🎨 Волшебная картинка создаётся..."):
                image = generate_image_replicate(current_scene["prompt"], st.session_state.image_counter)
            
            if image:
                st.image(image, width='stretch', caption="✨ Волшебная иллюстрация")
                if st.button("🔄 Другая картинка"):
                    st.session_state.image_counter += 1
                    st.rerun()
            else:
                st.image("https://via.placeholder.com/800x400/ffe6f0/ff69b4?text=✨+Представьте+сами", width='stretch')
                st.caption("🌟 Не удалось сгенерировать картинку, но вы можете представить эту сцену сами!")
        else:
            st.image("https://via.placeholder.com/800x400/ffe6f0/ff69b4?text=✨+Вообразите+эту+сцену", width='stretch')

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
