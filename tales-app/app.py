import streamlit as st
import os
from tales_data import tales

st.set_page_config(page_title="Интерактивные сказки", page_icon="📖", layout="centered")

# --- СТИЛИ ---
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');

.stApp {
    background-color: #fef9e7;
}

/* заголовки */

h1,h2,h3,h4{
font-family:'Cormorant Garamond',serif;
color:#5d3a1a;
}

p{
font-family:'Open Sans',sans-serif;
}

/* карточки */

.carousel-wrapper{
position:relative;
}

.carousel-container{
display:flex;
overflow-x:auto;
gap:20px;
padding:10px 40px;
scroll-behavior:smooth;
scroll-snap-type:x mandatory;
}

.carousel-container::-webkit-scrollbar{
display:none;
}

.carousel-item{
flex:0 0 260px;
scroll-snap-align:start;
}

.carousel-card{

background:#fffaf0;
border-radius:20px;
padding:15px;

height:340px;

display:flex;
flex-direction:column;

border:1px solid #e9d9c4;

transition:0.2s;
}

.carousel-card:hover{

transform:scale(1.05);

box-shadow:0 10px 25px rgba(0,0,0,0.15);

}

.carousel-card img{

width:100%;

height:150px;

object-fit:cover;

border-radius:12px;

margin-bottom:10px;

}

.carousel-card p{

height:60px;

overflow:hidden;

display:-webkit-box;

-webkit-line-clamp:3;

-webkit-box-orient:vertical;

}

.carousel-card .stButton{

margin-top:auto;

}

.carousel-card button{

width:100%;

}

/* стрелки */

.carousel-arrow{

position:absolute;

top:40%;

transform:translateY(-50%);

z-index:10;

background:rgba(0,0,0,0.5);

color:white;

border-radius:50%;

border:none;

width:36px;

height:36px;

cursor:pointer;

}

.carousel-arrow:hover{

background:rgba(0,0,0,0.8);

}

.carousel-left{
left:0;
}

.carousel-right{
right:0;
}

</style>
""", unsafe_allow_html=True)

# JS для стрелок
st.markdown("""
<script>
function scrollCarousel(id, offset) {
    const el = document.getElementById(id);
    if (el) {
        el.scrollBy({
            left: offset,
            behavior: 'smooth'
        });
    }
}
</script>
""", unsafe_allow_html=True)


# --- STATE ---
if "selected_tale" not in st.session_state:
    st.session_state.selected_tale=None

if "scene_id" not in st.session_state:
    st.session_state.scene_id="start"

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "scenes" not in st.session_state:
    st.session_state.scenes={}

if "scene_history" not in st.session_state:
    st.session_state.scene_history=[]


# --- ФУНКЦИИ ---

def start_tale(tale_name):

    st.session_state.selected_tale=tale_name
    st.session_state.scene_id="start"
    st.session_state.messages=[]
    st.session_state.scene_history=["start"]

    tale=tales[tale_name]

    st.session_state.scenes=tale["scenes"]

    first_scene=tale["scenes"]["start"]

    st.session_state.messages.append(
        {"role":"assistant","content":first_scene["text"]}
    )


def handle_choice(text,next_scene):

    st.session_state.messages.append(
        {"role":"user","content":text}
    )

    st.session_state.scene_id=next_scene

    st.session_state.scene_history.append(next_scene)

    scene=st.session_state.scenes[next_scene]

    st.session_state.messages.append(
        {"role":"assistant","content":scene["text"]}
    )


def go_back():

    if len(st.session_state.scene_history)>1:

        st.session_state.scene_history.pop()

        st.session_state.scene_id=st.session_state.scene_history[-1]

        st.session_state.messages.pop()
        st.session_state.messages.pop()

        st.rerun()


def reset():

    st.session_state.selected_tale=None
    st.session_state.messages=[]
    st.session_state.scenes={}
    st.session_state.scene_history=[]


# --- КАРУСЕЛЬ ---

def show_carousel(tales_list,key):

    st.markdown(f"""
<div class="carousel-wrapper">
<button class="carousel-arrow carousel-left" onclick="scrollCarousel('{key}',-300)">‹</button>
<div id="{key}" class="carousel-container">
""",unsafe_allow_html=True)

    for tale_name in tales_list:

        if tale_name in tales:

            st.markdown('<div class="carousel-item">',unsafe_allow_html=True)
            st.markdown('<div class="carousel-card">',unsafe_allow_html=True)

            cover=tales[tale_name].get("cover","")

            if cover and os.path.exists(cover):
                st.image(cover,use_container_width=True)
            else:
                st.image("https://via.placeholder.com/240x150",use_container_width=True)

            st.markdown(f"#### {tale_name}")

            if tales[tale_name].get("description"):
                st.markdown(tales[tale_name]["description"])

            if st.button("✨ Начать",key=f"{key}_{tale_name}"):

                start_tale(tale_name)

                st.rerun()

            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

    st.markdown(f"""
</div>
<button class="carousel-arrow carousel-right" onclick="scrollCarousel('{key}',300)">›</button>
</div>
""",unsafe_allow_html=True)



# --- SIDEBAR ---

with st.sidebar:

    st.markdown("## 📖 О проекте")

    st.markdown(
    "Интерактивные сказки где ребёнок сам выбирает путь истории."
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


# --- MAIN ---

st.title("📖 Интерактивные сказки")
st.caption("Выбирай свой путь в каждой истории")

if st.session_state.selected_tale is None:

    st.markdown("## 📚 Советские сказки")

    show_carousel(
        ["Колобок","Теремок","Золотая рыбка","Курочка Ряба"],
        "soviet"
    )

    st.markdown("## 🆕 Новые сказки")

    show_carousel(
        ["Путешествие в Волшебный лес"],
        "new"
    )

else:

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):

            st.write(msg["content"])

    scene=st.session_state.scenes[st.session_state.scene_id]

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

        if len(st.session_state.scene_history)>1:

            if st.button("⬅️ Назад"):

                go_back()
