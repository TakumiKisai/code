"""generator.py - turns study notes into quiz questions. No AI, no internet, no libraries."""
import re
import random
from collections import Counter

# Common words that make bad answers.
STOPWORDS = set("""
about above after again against all also although always among and any are because been before being
between both but can could did does doing down during each either else even every few for from further
had has have having her here hers him his how however into its itself just like many may might more most
much must nor not now off once only other our out over own same she should since some such than that the
their them then there these they this those through thus too under until upon very was were what when
where whether which while who whom why will with within without would you your often usually called
""".split())

# Malay common words.
STOPWORDS |= set("""
yang untuk dengan adalah dalam pada atau dari kepada oleh akan telah sudah juga tidak boleh lebih
sangat antara semua setiap kerana supaya serta apabila jika maka ialah merupakan dapat seperti
sebagai bagi hanya masih lagi pula agar sebuah mereka kami kita saya anda beliau bagaimana
hingga sehingga sambil selepas sebelum semasa terhadap tentang daripada melalui manakala namun tetapi
""".split())


def split_sections(notes):
    """Split notes into (title, text) sections. Blank lines separate sections.
    A short first line with no full stop counts as a title, e.g. 'Photosynthesis'."""
    sections = []
    for block in re.split(r"\n\s*\n", notes.strip()):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        title = None
        if len(lines[0].split()) <= 6 and not lines[0].endswith((".", "!")):
            title = lines[0].rstrip(":")
            lines = lines[1:]
        text = " ".join(lines)
        if text:
            sections.append((title, text))
    return sections


def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def get_words(sentence):
    return re.findall(r"[A-Za-z][A-Za-z'-]+", sentence)


def keyword_scores(notes):
    """Score each word: frequent words and longer words are more likely to be key terms."""
    counts = Counter(
        w.lower() for w in get_words(notes)
        if len(w) >= 4 and w.lower() not in STOPWORDS
    )
    return {w: c + len(w) * 0.05 for w, c in counts.items()}


def best_keyword(sentence, scores):
    """Pick the highest-scoring word in the sentence (skipping the first word)."""
    words = get_words(sentence)[1:]
    candidates = [w for w in words if w.lower() in scores]
    if not candidates:
        return None
    return max(candidates, key=lambda w: scores[w.lower()])


def make_choices(answer, scores, sentence, marked_pool=(), n=3):
    """Wrong answers: other **marked** terms first, then similar-length key words."""
    answer = answer.lower()
    in_question = {w.lower() for w in get_words(sentence)}
    wrong = [t for t in marked_pool if t != answer and t not in sentence.lower()]
    random.shuffle(wrong)
    wrong = wrong[:n]
    if len(wrong) < n:
        others = [w for w in scores
                  if w != answer and w not in in_question and w not in wrong]
        others.sort(key=lambda w: abs(len(w) - len(answer)))
        wrong += random.sample(others[:8], min(n - len(wrong), len(others[:8])))
    choices = wrong + [answer]
    random.shuffle(choices)
    return choices if len(choices) >= 3 else None  # too few terms -> type the answer


def generate_quiz(notes, max_questions=10):
    """Return a list of question dicts: topic, question, answer, choices.
    Words wrapped in **double asterisks** are used as the answers."""
    # Remove references to images e.g figure 1
    notes = re.sub(r"\((?:gambar|rajah|jadual|figure|fig|table)[^)]*\)", "", notes, flags=re.I)
    notes = re.sub(r"\s+([.,!?])", r"\1", notes)  # tidy the space left behind
    scores = keyword_scores(notes)
    marked_pool = {m.strip().lower() for m in re.findall(r"\*\*(.+?)\*\*", notes)}
    quiz = []
    for title, text in split_sections(notes):
        section_scores = keyword_scores(text)
        topic = title or (max(section_scores, key=section_scores.get).capitalize()
                          if section_scores else "General")
        for sentence in split_sentences(text):
            plain = sentence.replace("**", "")
            if not 6 <= len(plain.split()) <= 30:
                continue
            marked = re.findall(r"\*\*(.+?)\*\*", sentence)
            if marked:                                   # you chose the answer
                answer = marked[0].strip()
                blanked = sentence.replace("**", "")
                blanked = re.sub(re.escape(answer), "_____", blanked, flags=re.I)  # hide every copy
            else:                                        # the program chooses
                answer = best_keyword(plain, scores)
                if not answer:
                    continue
                blanked = re.sub(rf"\b{re.escape(answer)}\b", "_____", plain, flags=re.I)  # hide every copy
            quiz.append({
                "topic": topic,
                "question": blanked,
                "answer": answer.lower(),
                "choices": make_choices(answer, scores, plain, marked_pool),
            })
    random.shuffle(quiz)
    return quiz[:max_questions]


if __name__ == "__main__":
    sample = """
Photosynthesis
Photosynthesis is the process plants use to turn sunlight into chemical energy. It takes place in the chloroplasts, which contain chlorophyll. Chlorophyll absorbs light and gives plants their green colour.

Cellular Respiration
Cellular respiration releases energy from glucose inside the mitochondria. Oxygen is used during respiration and carbon dioxide is released as a waste product. The energy is stored in a molecule called ATP.
"""
    questions = generate_quiz(sample, max_questions=5)
    score = 0
    for n, q in enumerate(questions, 1):
        print(f"\nQ{n} [{q['topic']}]: {q['question']}")
        if q["choices"]:
            for i, c in enumerate(q["choices"], 1):
                print(f"  {i}. {c}")
            reply = input("Your answer (number): ").strip()
            given = q["choices"][int(reply) - 1] if reply.isdigit() and 0 < int(reply) <= len(q["choices"]) else ""
        else:
            given = input("Your answer: ").strip().lower()
        if given == q["answer"]:
            print("Correct!")
            score += 1
        else:
            print(f"Not quite. The answer was: {q['answer']}")
    print(f"\nScore: {score}/{len(questions)}")
