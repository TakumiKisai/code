"""app.py - connects the page to generator.py. All the quiz logic is Python."""
import math
from pyscript import document, when
from generator import generate_quiz

SAMPLE = """Photosynthesis
Photosynthesis is the process plants use to turn sunlight into chemical energy. It takes place in the chloroplasts, which contain chlorophyll. Chlorophyll absorbs light and gives plants their green colour.

Cellular Respiration
Cellular respiration releases energy from glucose inside the mitochondria. Oxygen is used during respiration and carbon dioxide is released as a waste product. The energy is stored in a molecule called ATP.
"""

state = {"quiz": [], "i": 0, "score": 0, "checked": False, "picked": None}


def el(element_id):
    return document.getElementById(element_id)


def set_feedback(text, kind=""):
    box = el("feedback")
    box.innerText = text
    box.className = "feedback " + kind


def show_question():
    quiz, i = state["quiz"], state["i"]
    state["checked"], state["picked"] = False, None
    set_feedback("")
    el("check").innerText = "Check answer"
    el("choices").innerHTML = ""
    el("typed").value = ""

    if not quiz:
        el("qmeta").innerText = "NO QUIZ YET"
        el("qtext").innerText = "Paste some notes below and press Build quiz."
        el("typed").classList.add("hidden")
        return
    if i >= len(quiz):
        el("qmeta").innerText = "FINISHED"
        el("qtext").innerText = f"You scored {state['score']} out of {len(quiz)}."
        el("typed").classList.add("hidden")
        el("check").innerText = "Play again"
        return

    q = quiz[i]
    el("qmeta").innerText = f"Question {i + 1} of {len(quiz)} · {q['topic']}"
    el("qtext").innerText = q["question"]
    el("score").innerText = f"Score: {state['score']}"

    if q["choices"]:
        el("typed").classList.add("hidden")
        for n, choice in enumerate(q["choices"]):
            button = document.createElement("button")
            button.className = "choice"
            button.dataset.index = str(n)
            button.innerHTML = f'<span class="num">{n + 1}</span>{choice}'
            el("choices").appendChild(button)
    else:
        el("typed").classList.remove("hidden")  # too few key terms: type the answer


def build_quiz():
    notes = el("notes").value
    state["quiz"] = generate_quiz(notes, max_questions=8)
    state["i"], state["score"] = 0, 0
    el("score").innerText = ""
    show_question()
    if not state["quiz"]:
        el("qtext").innerText = "Not enough text to make questions. Try a longer paragraph."


@when("click", "#build")
def on_build(event):
    build_quiz()


@when("click", "#choices")
def on_choice(event):
    if state["checked"]:
        return
    target = event.target.closest(".choice")
    if target is None:
        return
    for button in el("choices").children:
        button.classList.remove("picked")
    target.classList.add("picked")
    state["picked"] = int(target.dataset.index)


@when("click", "#check")
def on_check(event):
    quiz, i = state["quiz"], state["i"]
    if not quiz:
        return
    if i >= len(quiz):                      # finished: restart
        build_quiz()
        return
    if state["checked"]:                    # already checked: go to next
        state["i"] += 1
        show_question()
        return

    q = quiz[i]
    if q["choices"]:
        if state["picked"] is None:
            set_feedback("Pick an answer first.")
            return
        given = q["choices"][state["picked"]]
        for n, button in enumerate(el("choices").children):
            if q["choices"][n] == q["answer"]:
                button.classList.add("right")
            elif n == state["picked"]:
                button.classList.add("wrong")
    else:
        given = el("typed").value.strip().lower()

    state["checked"] = True
    if given == q["answer"]:
        state["score"] += 1
        set_feedback("Correct!", "good")
    else:
        set_feedback(f"Not quite. The answer was: {q['answer']}", "bad")
    el("score").innerText = f"Score: {state['score']}"
    el("check").innerText = "Next"


@when("click", "#hint")
def on_hint(event):
    quiz, i = state["quiz"], state["i"]
    if quiz and i < len(quiz) and not state["checked"]:
        answer = quiz[i]["answer"]
        set_feedback(f"Hint: it starts with '{answer[0]}' and has {len(answer)} letters.")


# Start with the sample notes already built into a quiz.
el("notes").value = SAMPLE
build_quiz()


# ---------------------------------------------------------------- MUSIC PLAYER
# Put your mp3 files in the music/ folder, then list them here.
# If your mp3 files are NOT inside a folder called "music", change MUSIC_FOLDER to "".
MUSIC_FOLDER = "music/"
TRACKS = [
    {"title": "Field - Ancient Ruins", "src":"Field - Ancient Ruins.mp3"},
    {"title": "Field - Aqua Grotto", "src": MUSIC_FOLDER + "Field - Aqua Grotto.mp3"},
    {"title": "Field - Arena Plaza", "src": MUSIC_FOLDER + "Field - Arena Plaza.mp3"},
    {"title": "Field - Boulder Province", "src": MUSIC_FOLDER + "Field - Boulder Province.mp3"},
    {"title": "Field - Green Hills", "src": MUSIC_FOLDER + "Field - Green Hills.mp3"},
    {"title": "Field - Haunted Manor", "src": MUSIC_FOLDER + "Field - Haunted Manor.mp3"},
    {"title": "Field - Icy Glaciers", "src": MUSIC_FOLDER + "Field - Icy Glaciers.mp3"},
    {"title": "Field - Jurassic Jungle", "src": MUSIC_FOLDER + "Field - Jurassic Jungle.mp3"},
    {"title": "Field - Lush Forest", "src": MUSIC_FOLDER + "Field - Lush Forest.mp3"},
    {"title": "Field - Mind Asylum", "src": MUSIC_FOLDER + "Field - Mind Asylum.mp3"},
    {"title": "Field - Mt. Grassland", "src": MUSIC_FOLDER + "Field - Mt. Grassland.mp3"},
    {"title": "Field - Pixie Island", "src": MUSIC_FOLDER + "Field - Pixie Island.mp3"},
    {"title": "Field - Riverside Road", "src": MUSIC_FOLDER + "Field - Riverside Road.mp3"},
    {"title": "Field - Sunset Shore", "src": MUSIC_FOLDER + "Field - Sunset Shore.mp3"},
    {"title": "Field - Toxic Canyon", "src": MUSIC_FOLDER + "Field - Toxic Canyon.mp3"},
    {"title": "Field - Waterfall Passage", "src": MUSIC_FOLDER + "Field - Waterfall Passage.mp3"},
    {"title": "Field - Woodland River", "src": MUSIC_FOLDER + "Field - Woodland River.mp3"},

]

audio = el("audio")
audio.volume = 0.7
music = {"current": None}

PLAY_ICON = '<polygon points="5 3 19 12 5 21 5 3"/>'
PAUSE_ICON = '<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>'


def fmt(seconds):
    seconds = int(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"


def build_playlist():
    box = el("playlist")
    box.innerHTML = ""
    for n, track in enumerate(TRACKS):
        row = document.createElement("div")
        row.className = "track"
        row.dataset.index = str(n)
        row.innerHTML = f'<span class="num">{n + 1:02d}</span><span>{track["title"]}</span>'
        box.appendChild(row)


def load_track(n, autoplay=True):
    music["current"] = n
    audio.src = TRACKS[n]["src"]
    el("trackName").innerText = TRACKS[n]["title"]
    for i, row in enumerate(el("playlist").children):
        row.classList.toggle("active", i == n)
    if autoplay:
        audio.play()


def step(direction):
    if not TRACKS:
        return
    current = music["current"] if music["current"] is not None else 0
    load_track((current + direction) % len(TRACKS))


@when("click", "#playlist")
def on_track_click(event):
    row = event.target.closest(".track")
    if row is not None:
        load_track(int(row.dataset.index))


@when("click", "#play")
def on_play(event):
    if not TRACKS:
        return
    if music["current"] is None:
        load_track(0)
    elif audio.paused:
        audio.play()
    else:
        audio.pause()


@when("click", "#next")
def on_next(event):
    step(1)


@when("click", "#prev")
def on_prev(event):
    step(-1)


@when("play", "#audio")
def on_audio_play(event):
    el("playIcon").innerHTML = PAUSE_ICON
    el("disc").classList.add("spinning")
    el("eq").classList.remove("paused")


@when("pause", "#audio")
def on_audio_pause(event):
    el("playIcon").innerHTML = PLAY_ICON
    el("disc").classList.remove("spinning")
    el("eq").classList.add("paused")


@when("error", "#audio")
def on_audio_error(event):
    # Shows which file the browser could not find, so typos are easy to spot.
    el("trackName").innerText = "File not found: " + audio.src.split("/")[-1]


@when("ended", "#audio")
def on_ended(event):
    step(1)


@when("timeupdate", "#audio")
def on_time(event):
    if not math.isfinite(audio.duration) or audio.duration == 0:
        return
    el("fill").style.width = f"{audio.currentTime / audio.duration * 100}%"
    el("tcur").innerText = fmt(audio.currentTime)
    el("tdur").innerText = fmt(audio.duration)


@when("click", "#progress")
def on_seek(event):
    if not math.isfinite(audio.duration):
        return
    rect = el("progress").getBoundingClientRect()
    audio.currentTime = (event.clientX - rect.left) / rect.width * audio.duration


@when("click", "#volume")
def on_volume(event):
    rect = el("volume").getBoundingClientRect()
    level = max(0, min(1, (event.clientX - rect.left) / rect.width))
    audio.volume = level
    el("volFill").style.width = f"{level * 100}%"


build_playlist()
