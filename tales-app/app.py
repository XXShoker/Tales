import streamlit as st
import urllib.parse
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

# --- Функции ---
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

def get_image_url(prompt):
    if not prompt:
        return None
    encoded_prompt = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=512&nologo=true"

# --- Боковая панель ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x100/ffe6f0/ff69b4?text=📚", use_container_width=True)
    st.markdown("## 🌟 О проекте")
    st.markdown(
        "Добро пожаловать в мир **интерактивных сказок**! "
        "Вы сами выбираете, как развернётся история. "
        "Все сказки абсолютно бесплатны."
    )
    st.markdown("---")
    # Кнопка доната
    try:
        st.link_button("💖 Поддержать донатом", "https://donate.stream/your-link", use_container_width=True)
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
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()
        if st.button("❌ Завершить и выйти", use_container_width=True):
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
                if st.button(f"✨ Начать", key=f"choose_{tale_name}", use_container_width=True):
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
        # --- Блок отладки картинок ---
        st.markdown("---")
        st.subheader("🔍 Отладка изображения")
        if current_scene.get("prompt"):
            st.write(f"**Промпт:** {current_scene['prompt']}")
            image_url = get_image_url(current_scene["prompt"])
            st.write(f"**Сгенерированный URL:** {image_url}")
            # Пробуем открыть ссылку в новой вкладке (инструкция)
            st.markdown(f"[Открыть URL в браузере]({image_url})")
            # Отображаем картинку
            try:
                st.image(image_url, use_container_width=True, caption="✨ Волшебная иллюстрация")
            except Exception as e:
                st.error(f"Ошибка загрузки изображения: {e}")
            if st.button("🔄 Другая картинка", key="regenerate_image"):
                st.rerun()
        else:
            st.warning("⚠️ Для этой сцены не задан промпт. Добавьте поле 'prompt' в tales_data.py.")
            # Можно показать заглушку
            st.image("https://via.placeholder.com/800x400/ffe6f0/ff69b4?text=✨+Представьте+сами", use_container_width=True)
        st.markdown("---")

        # Основные кнопки выбора
        if current_scene.get("options"):
            st.markdown("### Твой выбор:")
            for opt in current_scene["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", use_container_width=True):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
            if len(st.session_state.scene_history) > 1:
                st.markdown("---")
                if st.button("↩️ Назад к предыдущему выбору", use_container_width=True):
                    go_back()
        else:
            st.markdown("---")
            st.markdown("🎉 **Конец сказки!**")
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Вернуться к предыдущему выбору", use_container_width=True):
                    go_back()
            if st.button("🔄 Начать эту сказку заново", use_container_width=True):
                start_tale(st.session_state.selected_tale)
                st.rerun()
    else:
        st.error("⚠️ Сцена не найдена. Вернитесь к выбору сказок.")
        if st.button("⬅️ К выбору сказок"):
            reset_to_main()
            st.rerun()
