import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="centered")

# -------------------------
# STATE
# -------------------------
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

# -------------------------
# TALE LOGIC
# -------------------------
def start_tale(tale_name):
    st.session_state.selected_tale = tale_name
    st.session_state.scene_id = "start"
    st.session_state.messages = []
    st.session_state.scene_history = ["start"]

    tale = tales[tale_name]
    st.session_state.scenes = tale["scenes"]

    first_scene = tale["scenes"]["start"]
    st.session_state.messages.append({
        "role": "assistant",
        "content": first_scene["text"]
    })

def handle_choice(text, next_scene):
    st.session_state.messages.append({
        "role": "user",
        "content": text
    })
    st.session_state.scene_id = next_scene
    st.session_state.scene_history.append(next_scene)

    scene = st.session_state.scenes[next_scene]
    st.session_state.messages.append({
        "role": "assistant",
        "content": scene["text"]
    })

def go_back():
    if len(st.session_state.scene_history) > 1:
        st.session_state.scene_history.pop()
        st.session_state.scene_id = st.session_state.scene_history[-1]
        st.session_state.messages.pop()
        st.session_state.messages.pop()
        st.experimental_rerun()

def reset():
    st.session_state.selected_tale = None
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []

# -------------------------
# CAROUSEL через Streamlit
# -------------------------
def show_carousel(tales_list):
    cols = st.columns(len(tales_list))
    for i, tale_name in enumerate(tales_list):
        with cols[i]:
            tale = tales[tale_name]
            cover_path = tale.get("cover", "")
            if cover_path and os.path.exists(cover_path):
                st.image(cover_path, width=240)
            else:
                st.image("https://via.placeholder.com/240x160", width=240)
            st.subheader(tale_name)
            st.write(tale.get("description", ""))
            if st.button(f"✨ Начать {tale_name}", key=tale_name):
                start_tale(tale_name)
                st.experimental_rerun()

# -------------------------
# HANDLE URL PARAMS
# -------------------------
params = st.query_params
if "tale" in params:
    selected = params["tale"][0]  # берем первый элемент списка
    if selected in tales:
        start_tale(selected)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.markdown("## 📖 О проекте")
    st.write("Интерактивные сказки, где ребёнок сам выбирает развитие истории.")
    st.markdown("---")
    st.markdown("[💖 Поддержать проект](https://donate.stream/donate_69b56f4953f16)")
    st.markdown("---")
    if st.session_state.selected_tale:
        if st.button("🔄 Сменить сказку", use_container_width=True):
            reset()
            st.experimental_rerun()

# -------------------------
# MAIN
# -------------------------
st.title("📖 Интерактивные сказки")

if st.session_state.selected_tale is None:
    st.markdown("## 📚 Советские сказки")
    show_carousel([
        "Колобок",
        "Теремок",
        "Золотая рыбка",
        "Курочка Ряба"
    ])

    st.markdown("## 🆕 Новые сказки")
    show_carousel([
        "Путешествие в Волшебный лес"
    ])

else:
    # Показываем историю чата
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    scene = st.session_state.scenes[st.session_state.scene_id]

    if not scene.get("options"):
        st.success("🎉 Конец сказки!")
        if st.button("🔄 Начать заново"):
            start_tale(st.session_state.selected_tale)
            st.experimental_rerun()
    else:
        st.markdown("### Твой выбор")
        for opt in scene["options"]:
            if st.button(opt["text"], key=opt["text"]):
                handle_choice(opt["text"], opt["next"])
                st.experimental_rerun()
        if len(st.session_state.scene_history) > 1:
            if st.button("⬅️ Назад"):
                go_back()
