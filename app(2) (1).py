# app.py
# Streamlit 자동 채점기 (축약 버전)
import re
import streamlit as st

METHODS=["정의","예시","인과","분석","비교와 대조","분류와 구분"]
METHOD_PATTERNS={
"정의":["란","의미","개념","말한다"],
"예시":["예를 들어","대표적으로","예"],
"인과":["때문","므로","따라서","그래서"],
"분석":["구성","요소","부분","이루어"],
"비교와 대조":["반면","하지만","차이","공통","다르"],
"분류와 구분":["나누","분류","구분","종류","기준","묶"]
}

def norm(t): return re.sub(r"\s+","",t)

def has_any(text, arr):
    t=norm(text)
    return any(norm(x) in t for x in arr)

def infer(text):
    out=[]
    for m,ks in METHOD_PATTERNS.items():
        if has_any(text,ks):
            out.append(m)
    return out

def declared(text):
    m=re.search(r"\((.*?)\)",text)
    if not m: return None
    for k in METHODS:
        if k in m.group(1):
            return k
    return None

def judge(text):
    d=declared(text)
    body=re.sub(r"\(.*?\)","",text)
    inf=infer(body)
    if d:
        return d in inf,d,inf
    return (len(inf)>0, inf[0] if inf else None, inf)

st.title("2회고사 대비 서논술형 자동채점기")

st.header("서논술형2 설명방법 검사")
a1=st.text_area("(1)")
a2=st.text_area("(2)")

if st.button("채점"):
    r1=judge(a1)
    r2=judge(a2)
    dup=(r1[1] and r2[1] and r1[1]==r2[1])
    st.write({
        "1번 방법 일치":r1[0],
        "2번 방법 일치":r2[0],
        "서로 다른 방법":not dup,
        "추정방법":(r1[2],r2[2])
    })

st.info("※ 전체 버전에서는 1~3세트 키워드, 오개념 검사, 결론 방향 검사, 시각·청각 요소 연결 검사 등을 추가하세요.")
