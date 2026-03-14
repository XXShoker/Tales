import streamlit as st
from tales_data import tales

# Настройка страницы
st.set_page_config(
    page_title="Интерактивные сказки",
    page_icon="📖",
    layout="centered"
)

# --- Инициализация состояния сессии ---
if "selected_tale" not in st.session_state:
    st.session_state.selected_tale = None  # имя текущей сказки

if "scene_id" not in st.session_state:
    st.session_state.scene_id = "start"    # id текущей сцены

if "messages" not in st.session_state:
    st.session_state.messages = []          # история сообщений (роль, контент)

if "scenes" not in st.session_state:
    st.session_state.scenes = {}             # сцены загруженной сказки

# --- Функции ---
def start_tale(tale_name: str):
    """Загружает выбранную сказку и начинает с первой сцены"""
    st.session_state.selected_tale = tale_name
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    tale_data = tales.get(tale_name)
    if tale_data:
        st.session_state.scenes = tale_data["scenes"]
        first_scene = st.session_state.scenes["start"]
        st.session_state.messages.append({
            "role": "assistant",
            "content": first_scene["text"]
        })

def handle_choice(choice_text: str, next_scene_id: str):
    """Обрабатывает выбор пользователя"""
    # Добавляем выбор пользователя в историю
    st.session_state.messages.append({"role": "user", "content": choice_text})
    # Обновляем текущую сцену
    st.session_state.scene_id = next_scene_id
    # Добавляем ответ сказки (текст следующей сцены)
    next_scene = st.session_state.scenes.get(next_scene_id)
    if next_scene:
        st.session_state.messages.append({
            "role": "assistant",
            "content": next_scene["text"]
        })
    else:
        st.error(f"Сцена {next_scene_id} не найдена")

def reset_to_main():
    """Возврат к выбору сказки"""
    st.session_state.selected_tale = None
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    st.session_state.scenes = {}

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
    
    # Кнопка доната (используем st.link_button, если версия Streamlit >= 1.27)
    try:
        st.link_button(
            label="💖 Поддержать донатом",
            url="https://donate.stream/your-link",  # замените на свою ссылку
            use_container_width=True
        )
    except AttributeError:
        # Для старых версий Streamlit используем HTML
        st.markdown(
            '<a href="https://donate.stream/your-link" target="_blank">'
            '<button style="background-color:#FF4B4B; color:white; padding:0.5rem 1rem; '
            'border:none; border-radius:0.5rem; width:100%; font-size:1rem; '
            'cursor:pointer;">💖 Поддержать донатом</button></a>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Кнопки управления (видны только во время чтения)
    if st.session_state.selected_tale is not None:
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset_to_main()
            st.rerun()
        if st.button("❌ Завершить и выйти", use_container_width=True):
            reset_to_main()
            st.rerun()

# --- Основной контент ---
st.title("📖 Интерактивные сказки")
st.caption("Выбирайте свой путь в каждой истории!")

# Если сказка не выбрана — показываем галерею
if st.session_state.selected_tale is None:
    st.markdown("### Выберите сказку для чтения")
    # Показываем сказки в виде карточек (по 2 в ряд)
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
    
    # Дополнительное напоминание о донате (ненавязчивое)
    st.markdown("---")
    st.markdown(
        "🌟 *Все сказки бесплатны. Если хотите поддержать проект, "
        "воспользуйтесь кнопкой в боковой панели.*"
    )

else:
    # Отображаем историю сообщений
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Получаем текущую сцену
    current_scene = st.session_state.scenes.get(st.session_state.scene_id)

    if current_scene:
        if current_scene.get("options"):
            st.markdown("### Твой выбор:")
            for opt in current_scene["options"]:
                if st.button(opt["text"], key=f"choice_{opt['next']}", use_container_width=True):
                    handle_choice(opt["text"], opt["next"])
                    st.rerun()
        else:
            # Конец сказки
            st.markdown("---")
            st.markdown("🎉 **Конец сказки!**")
            if st.button("🔄 Начать эту сказку заново", use_container_width=True):
                start_tale(st.session_state.selected_tale)
                st.rerun()
    else:
        st.error("⚠️ Сцена не найдена. Вернитесь к выбору сказки.")
        if st.button("⬅️ К выбору сказок"):
            reset_to_main()
            st.rerun()
