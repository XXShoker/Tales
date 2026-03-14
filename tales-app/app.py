import streamlit as st
import os
import streamlit.components.v1 as components
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
        "role":"assistant",
        "content":first_scene["text"]
    })


def handle_choice(text,next_scene):

    st.session_state.messages.append({
        "role":"user",
        "content":text
    })

    st.session_state.scene_id = next_scene

    st.session_state.scene_history.append(next_scene)

    scene = st.session_state.scenes[next_scene]

    st.session_state.messages.append({
        "role":"assistant",
        "content":scene["text"]
    })


def go_back():

    if len(st.session_state.scene_history) > 1:

        st.session_state.scene_history.pop()

        st.session_state.scene_id = st.session_state.scene_history[-1]

        st.session_state.messages.pop()
        st.session_state.messages.pop()

        st.rerun()


def reset():

    st.session_state.selected_tale = None
    st.session_state.messages = []
    st.session_state.scenes = {}
    st.session_state.scene_history = []


# -------------------------
# CAROUSEL
# -------------------------

def show_carousel(tales_list):

    html = """
    <style>

    .carousel{
        display:flex;
        overflow-x:auto;
        gap:20px;
        padding:20px 10px;
        scroll-snap-type:x mandatory;
        font-family:sans-serif;
    }

    .carousel::-webkit-scrollbar{
        height:8px;
    }

    .carousel::-webkit-scrollbar-thumb{
        background:#b5926a;
        border-radius:10px;
    }

    .card{
        flex:0 0 240px;
        background:#fffaf0;
        border-radius:18px;
        padding:12px;
        scroll-snap-align:start;
        box-shadow:0 4px 12px rgba(0,0,0,0.1);
        transition:0.2s;
    }

    .card:hover{
        transform:scale(1.05);
    }

    .card img{
        width:100%;
        height:140px;
        object-fit:cover;
        border-radius:10px;
    }

    .card-title{
        font-weight:700;
        margin-top:8px;
        font-size:1.1rem;
    }

    .card-desc{
        font-size:0.9rem;
        height:55px;
        overflow:hidden;
    }

    .start-btn{
        display:block;
        margin-top:10px;
        text-align:center;
        background:#d4b68a;
        padding:8px;
        border-radius:12px;
        text-decoration:none;
        color:black;
        font-weight:600;
    }

    </style>

    <div class="carousel">
    """

    for tale_name in tales_list:

        if tale_name not in tales:
            continue

        tale = tales[tale_name]

        cover = tale.get("cover","")

        if not cover:
            cover = "https://via.placeholder.com/240x150"

        desc = tale.get("description","")

        html += f"""
        <div class="card">
            <img src="{cover}">
            <div class="card-title">{tale_name}</div>
            <div class="card-desc">{desc}</div>
            <a class="start-btn" href="?tale={tale_name}">✨ Начать</a>
        </div>
        """

    html += "</div>"

    components.html(html, height=320, scrolling=False)


# -------------------------
# HANDLE URL PARAMS
# -------------------------

params = st.query_params

if "tale" in params:

    selected = params["tale"]

    if selected in tales:

        start_tale(selected)


# -------------------------
# SIDEBAR
# -------------------------

with st.sidebar:

    st.markdown("## 📖 О проекте")

    st.write(
        "Интерактивные сказки, где ребёнок сам выбирает развитие истории."
    )

    st.markdown("---")

    st.link_button(
        "💖 Поддержать проект",
        "https://donate.stream/donate_69b56f4953f16",
        use_container_width=True
    )

    st.markdown("---")

    if st.session_state.selected_tale:

        if st.button("🔄 Сменить сказку",use_container_width=True):

            reset()
            st.rerun()


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

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    scene = st.session_state.scenes[st.session_state.scene_id]

    if not scene.get("options"):

        st.success("🎉 Конец сказки!")

        if st.button("🔄 Начать заново"):
            start_tale(st.session_state.selected_tale)
            st.rerun()

    else:

        st.markdown("### Твой выбор")

        for opt in scene["options"]:

            if st.button(opt["text"]):
                handle_choice(opt["text"],opt["next"])
                st.rerun()

        if len(st.session_state.scene_history) > 1:

            if st.button("⬅️ Назад"):
                go_back()
