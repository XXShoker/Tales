import streamlit as st
import os
import base64
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
    st.session_state.messages.append({"role": "assistant", "content": first_scene["text"]})

def handle_choice(text, next_scene):
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.scene_id = next_scene
    st.session_state.scene_history.append(next_scene)
    scene = st.session_state.scenes[next_scene]
    st.session_state.messages.append({"role": "assistant", "content": scene["text"]})

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
# CAROUSEL HTML
# -------------------------
def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def show_carousel(tales_list):
    html = """
    <style>
    .carousel{
        display:flex;
        overflow-x:auto;
        gap:20px;
        padding:20px;
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
        flex:0 0 260px;
        background:#fffaf0;
        border-radius:18px;
        padding:12px;
        scroll-snap-align:start;
        box-shadow:0 4px 12px rgba(0,0,0,0.1);
        transition:0.2s;
        display:flex;
        flex-direction:column;
        height:340px;
    }
    .card:hover{
        transform:scale(1.05);
    }
    .card img{
        width:100%;
        height:160px;
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
        margin-top:4px;
        flex-grow:1;
        overflow:hidden;
    }
    </style>
    <div class="carousel">
    """
    for i, tale_name in enumerate(tales_list):
        if tale_name not in tales:
            continue
        tale = tales[tale_name]
        cover_path = tale.get("cover", "")
        img_html = ""
        if cover_path and os.path.exists(cover_path):
            img_base64 = image_to_base64(cover_path)
            ext = os.path.splitext(cover_path)[1].lower()
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
            img_html = f'<img src="data:{mime};base64,{img_base64}">'
        else:
            img_html = '<img src="https://via.placeholder.com/240x160">'
        desc = tale.get("description", "")
        html += f"""
        <div class="card">
            {img_html}
            <div class="card-title">{tale_name}</div>
            <div class="card-desc">{desc}</div>
        </div>
        """
    html += "</div>"
    components.html(html, height=420, scrolling=False)

    # возвращаем выбранную сказку через Streamlit кнопки
    selected = None
    for tale_name in tales_list:
        if st.button(f"✨ Начать {tale_name}", key=f"start-{tale_name}"):
            selected = tale_name
    return selected

# -------------------------
# HANDLE URL PARAMS
# -------------------------
params = st.query_params
if "tale" in params:
    selected = params["tale"][0]
    if selected in tales and st.session_state.selected_tale is None:
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
    selected = show_carousel(["Колобок", "Теремок", "Золотая рыбка", "Курочка Ряба"])
    if selected:
        start_tale(selected)
        st.experimental_rerun()

    st.markdown("## 🆕 Новые сказки")
    selected_new = show_carousel(["Путешествие в Волшебный лес"])
    if selected_new:
        start_tale(selected_new)
        st.experimental_rerun()

else:
    # история чата
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
