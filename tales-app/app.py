import streamlit as st
import os
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
if "achieved_endings" not in st.session_state:
    st.session_state.achieved_endings = {}  # {tale_name: set(endings_ids)}

def count_total_endings(tale_name):
    """Подсчитывает количество концовок (сцен с options=[]) в сказке"""
    tale = tales.get(tale_name)
    if not tale:
        return 0
    count = 0
    for scene_id, scene in tale["scenes"].items():
        if scene.get("options") == []:
            count += 1
    return count

def get_ending_stats(tale_name):
    """Возвращает (количество открытых, всего)"""
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
    # Инициализируем множество для этой сказки, если ещё нет
    if tale_name not in st.session_state.achieved_endings:
        st.session_state.achieved_endings[tale_name] = set()

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
    # Кнопка доната с актуальной ссылкой
    try:
        st.link_button("💖 Поддержать донатом", "https://donate.stream/donate_69b56f4953f16", width='stretch')
    except AttributeError:
        st.markdown(
            '<a href="https://donate.stream/donate_69b56f4953f16" target="_blank">'
            '<button style="background-color:#FF4B4B; color:white; padding:0.5rem 1rem; '
            'border:none; border-radius:0.5rem; width:100%; font-size:1rem; '
            'cursor:pointer;">💖 Поддержать донатом</button></a>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    
    # Статистика концовок для текущей сказки
    if st.session_state.selected_tale is not None:
        opened, total = get_ending_stats(st.session_state.selected_tale)
        st.markdown(f"### 📊 Прогресс")
        st.markdown(f"**{st.session_state.selected_tale}**")
        st.progress(opened / total if total > 0 else 0)
        st.markdown(f"Найдено концовок: **{opened} / {total}**")
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
    # Экран выбора сказки с обложками
    st.markdown("### Выберите сказку для чтения")
    tale_names = list(tales.keys())
    cols = st.columns(2)
    for i, tale_name in enumerate(tale_names):
        with cols[i % 2]:
            with st.container(border=True):
                cover_path = tales[tale_name].get("cover", "")
                if cover_path and os.path.exists(cover_path):
                    st.image(cover_path, width='stretch')
                else:
                    st.image("https://via.placeholder.com/400x200/ffe6f0/ff69b4?text=✨+Сказка", width='stretch')
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
        # Если это концовка (нет options)
        if not current_scene.get("options"):
            # Проверяем, есть ли ending_type и ending_number
            if current_scene.get("ending_type") and current_scene.get("ending_number"):
                ending_type = current_scene["ending_type"]
                ending_num = current_scene["ending_number"]
                # Определяем эмодзи для типа
                type_emoji = {
                    "happy": "😊",
                    "sad": "😢",
                    "neutral": "😐",
                    "secret": "🤫"
                }.get(ending_type, "🌟")
                
                # Запоминаем, что концовка открыта
                tale = st.session_state.selected_tale
                ending_id = f"{ending_type}_{ending_num}"
                if tale not in st.session_state.achieved_endings:
                    st.session_state.achieved_endings[tale] = set()
                st.session_state.achieved_endings[tale].add(ending_id)
                
                st.markdown("---")
                st.markdown(f"## {type_emoji} **Концовка #{ending_num}**")
                st.markdown(f"**Тип:** {ending_type.capitalize()}")
                
                # --- Дополнительное сообщение в зависимости от типа ---
                if ending_type == "happy":
                    st.success("🎉 Поздравляем! Это счастливый конец!")
                else:
                    st.info("😕 Это не счастливый конец. Попробуй пройти сказку снова, возможно, ты найдёшь счастливый конец!")
                
                # Показываем общее количество концовок в этой сказке
                opened, total = get_ending_stats(tale)
                st.markdown(f"*Всего в этой сказке **{total}** концовок. Ты нашёл уже **{opened}**.*")
            else:
                # Старая сказка без типов концовок
                st.markdown("---")
                st.markdown("🎉 **Конец сказки!**")
            
            # Кнопки после концовки
            st.markdown("---")
            if len(st.session_state.scene_history) > 1:
                if st.button("↩️ Вернуться к предыдущему выбору", width='stretch'):
                    go_back()
            if st.button("🔄 Начать эту сказку заново", width='stretch'):
                start_tale(st.session_state.selected_tale)
                st.rerun()
        else:
            # Обычная сцена с вариантами
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
        st.error("⚠️ Сцена не найдена. Вернитесь к выбору сказок.")
        if st.button("⬅️ К выбору сказок", width='stretch'):
            reset_to_main()
            st.rerun()
