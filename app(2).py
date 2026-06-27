# app.py
import re
import streamlit as st

METHODS = ["정의", "예시", "인과", "분석", "비교와 대조", "분류와 구분"]

METHOD_PATTERNS = {
    "정의": ["란", "은", "는", "말한다", "의미", "개념", "뜻"],
    "예시": ["예를 들어", "예", "대표적으로", "같은", "커피숍", "도서관", "공부 모임", "에드몽 드 벨라미"],
    "인과": ["때문", "므로", "따라서", "그래서", "결과", "원인", "위험하지"],
    "분석": ["구성", "요소", "부분", "이루어져", "나뉘어 구성"],
    "비교와 대조": ["반면", "하지만", "달리", "공통점", "차이점", "같지만", "와 다르게", "보다"],
    "분류와 구분": ["나뉜다", "나누다", "분류", "구분", "종류", "기준", "묶다"],
}

SETS = {
    "1세트_사회적 촉진과 억제": {
        "q1": {
            "㉠": [["쉬운"], ["과제", "취미", "노력", "친숙", "익숙"]],
            "㉡": [["혼자"], ["집중", "연습", "차분", "공부"]],
            "㉢": [["사회적 억제"]],
        },
        "wrong_concepts": {
            "easy": ["어려운", "도전", "복잡"],
            "hard": ["친구", "함께", "모임", "커피숍", "도서관"],
        },
        "q2_allowed": ["쉬운 과제", "어려운 과제", "사회적 촉진", "사회적 억제", "커피숍", "도서관", "공부 모임", "혼자", "집중", "연습", "익숙"],
        "q3_core": ["어려운", "도전", "혼자", "차분", "집중", "연습", "익숙"],
        "model_by_method": {
            "정의": "사회적 억제는 어려운 과제를 할 때 다른 사람의 존재가 수행을 방해할 수 있는 현상이다.",
            "예시": "예를 들어 쉬운 과제는 커피숍이나 도서관에서 하거나 공부 모임을 만들어 할 수 있다.",
            "인과": "어려운 과제는 충분히 연습하며 익숙해질 때까지 혼자 집중해야 하므로 차분한 환경이 필요하다.",
            "비교와 대조": "쉬운 과제는 다른 사람들과 함께하는 것이 효율적이지만, 어려운 과제는 혼자 집중하는 것이 효율적이다.",
            "분류와 구분": "학습 전략은 쉬운 과제에 적합한 방법과 어려운 과제에 적합한 방법으로 나눌 수 있다.",
            "분석": "과제에 따른 학습 전략은 과제의 난이도, 학습 환경, 함께하는 사람의 유무를 고려하여 설명할 수 있다.",
        },
    },
    "2세트_정전기": {
        "q1": {
            "㉠": [["고여", "고인", "머물"], ["물"]],
            "㉡": [["전하"], ["이동하지", "머물", "정지", "흐르지"]],
            "㉢": [["위험하지", "위험 없다", "피해 없다", "안전"]],
        },
        "wrong_concepts": {
            "static": ["흐르는 물", "폭포", "흘러내리는", "전하가 이동", "위험하다"],
            "current": ["고여 있는 물", "머물러", "정지"],
        },
        "q2_allowed": ["정전기", "전하", "정지", "머물", "이동하지", "높은 곳", "고여 있는 물", "흐르는 물", "실생활 전기", "위험하지", "전압"],
        "q3_core": ["고여", "고인", "흐르지", "머물", "정지", "전하", "이동하지", "위험하지"],
        "model_by_method": {
            "정의": "정전기란 전하가 정지 상태로 있어 그 분포가 시간적으로 변화하지 않는 전기 현상이다.",
            "예시": "예를 들어 정전기는 높은 곳에 고여 있는 물과 같다고 설명할 수 있다.",
            "인과": "정전기는 전하가 이동하지 않고 머물러 있으므로 위험하지 않다.",
            "비교와 대조": "실생활 전기가 흐르는 물과 같다면 정전기는 높은 곳에 고여 있는 물과 같다.",
            "분류와 구분": "전기는 전하가 이동하는 실생활 전기와 전하가 머물러 있는 정전기로 구분할 수 있다.",
            "분석": "정전기의 특징은 높은 전압, 전하의 정지 상태, 낮은 위험성으로 나누어 설명할 수 있다.",
        },
    },
    "3세트_AI 예술": {
        "q1": {
            "㉠": [["로봇"], ["피겨", "경기", "스케이팅", "완벽"]],
            "㉡": [["감정", "철학", "이야기", "경험", "관점"], ["예술로 보기 어렵", "예술이 아니다"]],
            "㉢": [["미술계", "변화", "범주", "확장", "상징적 가치", "가치"]],
        },
        "wrong_concepts": {
            "ai": ["감정이 담긴", "철학이 있는", "삶의 경험이 담긴", "감동을 준다"],
            "human": ["감정이 없다", "철학이 없다", "이야기가 없다"],
            "value": ["가치가 없다", "의미가 없다", "쓸모없다"],
        },
        "q2_allowed": ["인공 지능", "그림", "에드몽 드 벨라미", "알고리즘", "데이터", "인간", "감정", "철학", "이야기", "경험", "관점", "환경", "미술계", "변화", "범주", "확장", "상징적 가치"],
        "q3_core": ["인간", "감정", "철학", "경험", "관점", "환경", "감동", "울림"],
        "model_by_method": {
            "정의": "인공 지능이 그린 그림은 알고리즘과 데이터를 사용해 만들어진 작품이다.",
            "예시": "예를 들어 「에드몽 드 벨라미」는 인공 지능이 알고리즘과 데이터를 사용해 그린 작품이다.",
            "인과": "인간의 작품에는 작가의 감정과 철학, 삶의 경험이 담겨 있으므로 예술로 볼 수 있다.",
            "비교와 대조": "인간의 작품에는 감정과 철학이 담겨 있지만 인공 지능의 그림에는 감정과 독자적인 철학이 없다.",
            "분류와 구분": "그림은 인간이 만든 작품과 인공 지능이 만든 작품으로 나누어 볼 수 있다.",
            "분석": "인간 예술의 가치는 작가의 감정, 철학, 삶의 경험, 관점, 환경 등으로 설명할 수 있다.",
        },
    },
}

def norm(text):
    return re.sub(r"\s+", "", text.strip())

def contains_group(text, groups):
    t = norm(text)
    for group in groups:
        if not any(norm(k) in t for k in group):
            return False
    return True

def has_any(text, keywords):
    t = norm(text)
    return any(norm(k) in t for k in keywords)

def infer_methods(text):
    found = []
    for method, keys in METHOD_PATTERNS.items():
        if has_any(text, keys):
            found.append(method)
    return found

def extract_method(text):
    m = re.search(r"\((.*?)\)", text)
    if not m:
        return None
    raw = m.group(1).strip()
    for method in METHODS:
        if method in raw:
            return method
    return None

def remove_parentheses(text):
    return re.sub(r"\(.*?\)", "", text)

def check_q1(setdata, answers):
    results = {}
    for blank, groups in setdata["q1"].items():
        ans = answers.get(blank, "")
        ok = contains_group(ans, groups)
        results[blank] = ok
    return results

def check_method_answer(text):
    selected = extract_method(text)
    body = remove_parentheses(text)
    inferred = infer_methods(body)

    if selected:
        ok = selected in inferred
        return ok, selected, inferred
    else:
        # 용어가 없어도 실제 설명 방법의 의미가 드러나면 인정
        if inferred:
            return True, inferred[0], inferred
        return False, None, []

def check_q2(setdata, ans1, ans2):
    ok1, method1, inferred1 = check_method_answer(ans1)
    ok2, method2, inferred2 = check_method_answer(ans2)

    duplicate = method1 and method2 and method1 == method2
    content_ok1 = has_any(ans1, setdata["q2_allowed"])
    content_ok2 = has_any(ans2, setdata["q2_allowed"])

    conclusion_ok = content_ok1 and content_ok2

    final = ok1 and ok2 and not duplicate and content_ok1 and content_ok2 and conclusion_ok

    return {
        "1번 문장 방법 일치": ok1,
        "2번 문장 방법 일치": ok2,
        "서로 다른 방법 사용": not duplicate,
        "1번 지문 내용 활용": content_ok1,
        "2번 지문 내용 활용": content_ok2,
        "최종 통과": final,
        "판정 방법": (method1, method2),
        "추정 방법": (inferred1, inferred2),
    }

def check_wrong_concept(setname, setdata, text):
    wrong = []
    wc = setdata["wrong_concepts"]

    if "1세트" in setname:
        # 어려운 과제 장면에 '함께, 모임, 커피숍' 등 사회적 촉진 특성을 쓰면 오류
        if has_any(text, wc["hard"]):
            wrong.append("어려운 과제에 사회적 촉진 환경을 적용함")
    elif "2세트" in setname:
        if has_any(text, wc["static"]):
            wrong.append("정전기를 흐르는 물/전하 이동/위험성과 연결함")
    elif "3세트" in setname:
        if has_any(text, wc["ai"]):
            wrong.append("AI 그림에 인간 예술의 감정·철학 특성을 잘못 부여함")
        if has_any(text, wc["value"]):
            wrong.append("AI 그림의 상징적 가치를 전면 부정함")

    return wrong

def check_q3(setname, setdata, visual, visual_effect, audio, audio_effect):
    visual_ok = has_any(visual, setdata["q3_core"])
    audio_ok = has_any(audio, setdata["q3_core"] + ["조용", "잔잔", "적막", "연필", "메트로놈", "기계음", "음악", "소리"])
    visual_effect_ok = has_any(visual_effect, setdata["q3_core"])
    audio_effect_ok = has_any(audio_effect, setdata["q3_core"])

    visual_link = has_any(visual + visual_effect, setdata["q3_core"])
    audio_link = has_any(audio + audio_effect, setdata["q3_core"])

    wrongs = check_wrong_concept(setname, setdata, visual + visual_effect + audio + audio_effect)

    final = visual_ok and audio_ok and visual_effect_ok and audio_effect_ok and visual_link and audio_link and not wrongs

    return {
        "시각 요소 본문 개념 반영": visual_ok,
        "청각 요소 본문 개념 반영": audio_ok,
        "시각 효과 본문 근거 포함": visual_effect_ok,
        "청각 효과 본문 근거 포함": audio_effect_ok,
        "시각 요소-효과 연결": visual_link,
        "청각 요소-효과 연결": audio_link,
        "오개념 없음": not wrongs,
        "오개념": wrongs,
        "최종 통과": final,
    }

st.title("2회고사 대비 서·논술형 자동 채점기")

setname = st.selectbox("채점할 세트 선택", list(SETS.keys()))
setdata = SETS[setname]

st.header("선택지별 모범 답안")
for method, model in setdata["model_by_method"].items():
    st.markdown(f"- **{method}**: {model}")

st.divider()

st.header("[서·논술형 1] 표 빈칸 채우기")
q1_answers = {}
for blank in ["㉠", "㉡", "㉢"]:
    q1_answers[blank] = st.text_input(f"{blank} 답안", key=f"{setname}_{blank}")

if st.button("서·논술형 1 채점"):
    result = check_q1(setdata, q1_answers)
    st.write(result)

st.divider()

st.header("[서·논술형 2] 설명 방법 2가지 활용")
ans1 = st.text_area("(1) 답안", key=f"{setname}_q2_1")
ans2 = st.text_area("(2) 답안", key=f"{setname}_q2_2")

if st.button("서·논술형 2 채점"):
    result = check_q2(setdata, ans1, ans2)
    st.write(result)

st.divider()

st.header("[서·논술형 3] 영상 기획안")
visual = st.text_area("Ⓐ 시각 요소", key=f"{setname}_visual")
visual_effect = st.text_area("Ⓐ 시각 요소의 효과", key=f"{setname}_visual_effect")
audio = st.text_area("Ⓑ 청각 요소", key=f"{setname}_audio")
audio_effect = st.text_area("Ⓑ 청각 요소의 효과", key=f"{setname}_audio_effect")

if st.button("서·논술형 3 채점"):
    result = check_q3(setname, setdata, visual, visual_effect, audio, audio_effect)
    st.write(result)
