# 2. 라이브러리 불러오기
import gradio as gr
import pandas as pd

from itertools import combinations

# 3. 공통 데이터

# 국가별 외교 유형
countries = {
    "대한민국": "CGMF",
    "일본": "RDMP",
    "중국": "RGMP",
    "미국": "RDUF",
    "브라질": "CGMP",
    "프랑스": "CGMP",
    "호주": "CGMF"
}

# 16가지 외교 유형의 이름
type_names = {
    "CGMP": "신중한 평화 설계자형",
    "CGMF": "유연한 외교 조율가형",
    "CGUP": "소신 있는 독립 협상가형",
    "CGUF": "현실적인 관계 관리자형",
    "CDMP": "적극적인 국제 협력가형",
    "CDMF": "민첩한 글로벌 중재자형",
    "CDUP": "당당한 평화 개척자형",
    "CDUF": "능동적인 실리 외교관형",
    "RGMP": "신중한 질서 수호자형",
    "RGMF": "전략적인 국제 협상가형",
    "RGUP": "굳건한 주권 수호자형",
    "RGUF": "치밀한 국익 전략가형",
    "RDMP": "단호한 국제질서 주도자형",
    "RDMF": "기민한 외교 전략가형",
    "RDUP": "강경한 독자 노선가형",
    "RDUF": "과감한 실리 추구자형"
}

# 네 가지 외교 성향 기준
axes = [
    "협력·경쟁",
    "점진·신속",
    "다자·일방",
    "원칙·실용"
]

# 유형 판정에 사용하는 글자
letters = [
    ["C", "R"],
    ["G", "D"],
    ["M", "U"],
    ["P", "F"]
]

# 성향 조합별 기본 궁합 점수
interaction = [
    {"CC": 100, "CR": 45, "RR": 35},
    {"GG": 100, "DG": 55, "DD": 70},
    {"MM": 100, "MU": 30, "UU": 60},
    {"PP": 90, "FP": 65, "FF": 90}
]

# 외교 상황별 가중치
weights = {
    "경제·무역": [20, 15, 20, 45],
    "군사·안보": [35, 20, 30, 15],
    "기후·국제협력": [25, 15, 45, 15]
}

# 12가지 외교 상황 질문
# 각 항목: (질문, 첫 번째 선택지, 두 번째 선택지)

questions = [
    # 1~3. 협력 지향(C) / 경쟁 지향(R)
    (
        "취임 첫날, 이웃 국가가 우리나라 수출품에 40% 관세를 부과했다. 기업들이 즉각적인 대응을 요구한다. 당신의 선택은?",
        "상대국도 얻을 이익이 있는 새로운 무역 조건을 제시하며 비공개 협상을 시작한다.",
        "상대국의 주요 수출품에 맞대응 관세를 준비해 협상에서 먼저 양보하도록 압박한다."
    ),
    (
        "오랫동안 경쟁하던 국가에서 갑자기 대규모 공동 개발 사업을 제안했다. 성공하면 이익이 크지만 기술 유출도 걱정된다.",
        "핵심 기술을 보호하는 조건을 설정하고 공동 개발을 추진한다.",
        "협력보다 독자적인 기술 개발에 집중해 경쟁 우위를 확보한다."
    ),
    (
        "국제 박람회 개최권을 두고 우리나라와 경쟁국이 최종 후보에 올랐다. 경쟁국이 다른 국제사업에서는 협력하자고 제안한다.",
        "박람회 경쟁과 별개로 상호 이익이 있는 국제사업의 협력을 추진한다.",
        "박람회 유치에 유리한 조건을 얻을 때까지 다른 협력 제안도 협상 카드로 활용한다."
    ),

    # 4~6. 점진적 결정(G) / 신속한 결정(D)
    (
        "새벽 3시, 우리 영해 근처에서 정체불명의 군함이 발견됐다. 참모들의 의견이 엇갈린다. 당신의 첫 지시는?",
        "군과 외교 당국의 정보를 교차 확인하며 대응 수위를 단계적으로 결정한다.",
        "위험이 커지기 전에 즉시 경계 태세를 격상하고 대응 명령을 내린다."
    ),
    (
        "해외에서 우리 국민 수천 명이 발이 묶였다. 구조 작전에는 위험이 있지만 시간을 지체하면 피해가 커질 수 있다.",
        "현지 정부와 전문가들의 정보를 종합해 안전한 철수 계획을 확정한다.",
        "확보된 정보를 바탕으로 우선 구조팀을 출발시키고 현장에서 계획을 보완한다."
    ),
    (
        "국제회의에서 예상하지 못한 평화협정 초안이 제시됐다. 다른 정상들은 곧바로 서명할지 묻고 있다.",
        "협정이 가져올 장기적 영향을 검토하고 국내 관계 기관의 의견을 확인한다.",
        "합의의 기회가 사라지기 전에 주요 조건을 확인한 뒤 서명을 결정한다."
    ),

    # 7~9. 다자주의(M) / 일방주의(U)
    (
        "세계적인 식량 위기가 발생했다. 여러 국가가 공동 대응을 제안하지만 합의에는 시간이 걸릴 전망이다.",
        "일부 양보를 감수하더라도 국제회의에 참여해 공동 공급 체계를 마련한다.",
        "국제회의 결과를 기다리지 않고 우리나라의 식량 확보 계획부터 가동한다."
    ),
    (
        "우리나라의 핵심 산업을 위협하는 새로운 기술 규제가 등장했다. 국제기구는 공통 규칙을 논의 중이다.",
        "다른 국가와 연합해 국제 규칙을 수정하는 방향으로 영향력을 행사한다.",
        "국제적 합의와 별개로 우리 산업을 보호할 독자적인 규제를 마련한다."
    ),
    (
        "해적 활동으로 주요 해상 무역로가 위협받고 있다. 여러 국가가 연합 작전을 준비하고 있다.",
        "연합 작전에 참여해 작전 범위와 책임을 다른 국가들과 함께 결정한다.",
        "우리 상선 보호에 집중하는 독자적 작전을 먼저 추진한다."
    ),

    # 10~12. 원칙 중심(P) / 실용 중심(F)
    (
        "강력한 경제협력 제안이 도착했다. 다만 받아들이려면 그동안 공개적으로 지켜 온 외교 원칙을 일부 수정해야 한다.",
        "당장의 이익을 포기하더라도 기존 원칙과의 일관성을 유지한다.",
        "새로운 상황에 맞게 입장을 조정하고 실질적인 협상 성과를 얻는다."
    ),
    (
        "오랜 우방국이 국제협약을 위반했다는 의혹을 받고 있다. 공개적으로 비판하면 중요한 협력이 중단될 수도 있다.",
        "우방국이라도 같은 기준을 적용하고 국제협약 준수를 공개적으로 요구한다.",
        "공개 비판보다 비공개 협상을 통해 문제를 해결하고 기존 협력을 유지한다."
    ),
    (
        "대규모 에너지 계약을 눈앞에 두고 있다. 상대국은 우리나라의 기존 외교 방침과 충돌하는 조건을 요구한다.",
        "계약이 무산되더라도 기존 외교 방침에서 벗어나는 조건은 받아들이지 않는다.",
        "핵심 이익을 확보할 수 있다면 일부 조건을 조정해 계약을 성사시킨다."
    )
]

assert len(questions) == 12

assert all(
    len(question) == 3
    for question in questions
)

print("✅ 12개 질문이 정상적으로 저장되었습니다!")

# 4. 공통 궁합 계산 함수

def calculate_codes(code1, code2, situation):
    details = []
    total = 0

    for i in range(4):
        pair = "".join(sorted([code1[i], code2[i]]))

        base = interaction[i][pair]
        weight = weights[situation][i]

        contribution = base * weight / 100
        total += contribution

        details.append({
            "분석 기준": axes[i],
            "성향 조합": pair,
            "기본값": base,
            "가중치(%)": weight,
            "계산 점수": round(contribution, 2)
        })

    return round(total, 2), pd.DataFrame(details)


# 국가 A와 국가 B의 궁합을 분석하는 함수
def analyze_countries(a, b, situation):

    if a == b:
        return (
            "⚠️ 서로 다른 두 국가를 선택해 주세요.",
            pd.DataFrame()
        )

    code1 = countries[a]
    code2 = countries[b]

    score, details = calculate_codes(
        code1, code2, situation
    )

    result = (
        f"## 🌐 {a} × {b}\n\n"
        f"**외교 상황:** {situation}\n\n"
        f"**{a}:** {code1} - {type_names[code1]}\n\n"
        f"**{b}:** {code2} - {type_names[code2]}\n\n"
        f"### 외교 궁합 지수: {score}점 / 100점\n\n"
        "※ 이 점수는 탐구에서 설정한 모형에 따른 "
        "시뮬레이션 결과이며, 실제 외교 관계를 "
        "확정적으로 예측하는 값은 아닙니다."
    )

    return result, details


# 전체 국가 조합을 비교하는 함수
def compare_all(situation):
    rows = []

    for a, b in combinations(countries.keys(), 2):
        score, _ = calculate_codes(
            countries[a],
            countries[b],
            situation
        )

        rows.append({
            "국가 A": a,
            "국가 B": b,
            "유형 A": countries[a],
            "유형 B": countries[b],
            "궁합 지수": score
        })

    df = pd.DataFrame(rows)

    return df.sort_values(
        "궁합 지수",
        ascending=False
    ).reset_index(drop=True)


# 5. 첫 번째 탭에서 사용하는 유형 판정 함수

def take_test(situation, *answers):

    # 모든 질문에 응답했는지 확인
    if len(answers) != len(questions) or any(
        answer is None for answer in answers
    ):
        return (
            "⚠️ 12개 질문에 모두 답해 주세요.",
            pd.DataFrame()
        )

    code = ""
    choice_counts = []

    # 네 가지 외교 성향을 하나씩 판정
    for axis in range(4):
        first_count = 0

        # 각 성향당 세 문항 확인
        for j in range(3):
            i = axis * 3 + j

            if answers[i] == questions[i][1]:
                first_count += 1

        choice_counts.append(first_count)

        # 세 문항 중 다수결로 유형 결정
        if first_count >= 2:
            code += letters[axis][0]
        else:
            code += letters[axis][1]

    # 판정된 외교 유형의 이름 가져오기
    type_name = type_names[code]

    # 사용자 유형과 7개 국가 비교
    rows = []

    for country, country_code in countries.items():
        score, _ = calculate_codes(
            code,
            country_code,
            situation
        )

        rows.append({
            "국가": country,
            "국가 유형": country_code,
            "국가 유형명": type_names[country_code],
            "궁합 지수": score
        })

    df = pd.DataFrame(rows)

    df = df.sort_values(
        "궁합 지수",
        ascending=False
    ).reset_index(drop=True)

    # 사용자의 선택 결과 설명
    axis_summary = "\n".join(
        f"- {axes[i]}: 첫 번째 선택지 "
        f"{choice_counts[i]}회 / 3회"
        for i in range(4)
    )

    result = (
        "## 🎉 나의 외교 MBTI 결과\n\n"
        f"### {code} - {type_name}\n\n"
        "**성향별 선택 결과**\n\n"
        f"{axis_summary}\n\n"
        f"**국가 비교 상황:** {situation}\n\n"
        "아래 표에서 나의 외교 유형과 "
        "7개 국가의 궁합 지수를 확인할 수 있습니다.\n\n"
        "※ 궁합 지수는 탐구 모형에 따른 계산 결과입니다."
    )

    return result, df


import html
import os

# External photo URLs (illustrative, not documentary evidence of the scenarios).
PHOTO_IDS = [
    "1494412574643-35d324698cf8", "1497366811353-6870744d04b2",
    "1540575467063-178a50c2df87", "1500530855697-b586d89ba3ee",
    "1436491865332-7a61a109cc05", "1505373877841-8d25f7d46678",
    "1500937386664-56d1dfef3854", "1518770660439-4636190af475",
    "1500534623283-312aade485b7", "1486406146926-c627a92ad1ab",
    "1529107386315-e1a2ed48a620", "1473341304170-971dccb5ac1e"
]
MISSION_NAMES = ["무역 위기", "뜻밖의 공동 개발 제안", "국제 박람회 유치", "영해의 긴급 상황", "해외 국민 구조", "평화협정의 기회", "세계 식량 위기", "새로운 기술 규제", "해상 무역로 보호", "경제협력과 원칙", "우방국의 국제협약", "에너지 계약"]
FLAGS = dict(zip(countries, ["🇰🇷", "🇯🇵", "🇨🇳", "🇺🇸", "🇧🇷", "🇫🇷", "🇦🇺"]))
CSS = """
@font-face {font-family: Smile; src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-5@1.0/HakgyoansimDunggeunmisoTTF-R.woff2') format('woff2'); font-weight:400; font-display:swap;}
@font-face {font-family: Smile; src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-5@1.0/HakgyoansimDunggeunmisoTTF-B.woff2') format('woff2'); font-weight:700; font-display:swap;}
body, .gradio-container {background:linear-gradient(145deg,#e5f4ff,#f6fbff) !important; color:#244e76 !important;}
.gradio-container {max-width:900px !important; margin:auto !important; padding:18px !important; --body-text-color:#244e76; --body-background-fill:#eff8ff; --block-background-fill:white; --block-label-text-color:#315f86; --input-background-fill:#f4faff; --input-border-color:#c6e1f7; --color-accent:#3989cf;}
.gradio-container, .gradio-container button, .gradio-container input, .gradio-container label, .gradio-container p, .gradio-container h1, .gradio-container h2, .gradio-container h3, .gradio-container span {font-family:Smile, sans-serif !important;}
.hero {text-align:center; padding:36px 16px; border-radius:30px; background:linear-gradient(150deg,#b9e2ff,#f4fbff); border:2px solid white; box-shadow:0 8px 30px #7cadd52a; color:#285e91;}
.hero .globe {font-size:65px; line-height:1.3;} .hero h1 {font-size:clamp(27px,5vw,44px); margin:12px 0;} .hero p {font-size:18px; line-height:1.6;}
.chips {display:flex; justify-content:center; flex-wrap:wrap; gap:8px;} .chips span {background:white; border-radius:30px; padding:9px 16px;}
.mission {background:white; border:1px solid #d6e9fa; border-radius:25px; padding:14px; box-shadow:0 7px 25px #8ab9df22;}
.photo {height:clamp(180px,32vw,310px); border-radius:20px; background:linear-gradient(135deg,#a6d6f9,#eaf7ff); overflow:hidden; position:relative;}
.photo img {width:100%;height:100%;object-fit:cover;} .photo span {position:absolute; bottom:12px;left:12px; background:#ffffffed; color:#285e91; padding:8px 14px; border-radius:20px;}
.mission h2 {font-size:26px; color:#285e91; margin:18px 0 8px;} .mission p {font-size:18px; line-height:1.7; color:#284d70;}
.progress {height:10px;background:#d9ebfa;border-radius:20px; margin:12px 0 18px;position:relative;} .progress i {display:block;height:100%;background:#68b3ed;border-radius:20px;position:relative;} .progress b {position:absolute;right:-8px;top:-13px;font-size:23px;}
.answer-card label {background:#f6fbff !important;border:1px solid #cce3f8 !important;border-radius:17px !important;padding:15px !important; color:#244e76 !important;line-height:1.6 !important;}
.answer-card label:has(input:checked) {background:#dcefff !important;border:2px solid #519cdb !important;}
button.primary {background:linear-gradient(110deg,#398bd1,#65b4eb) !important;color:white !important;border:0 !important;border-radius:28px !important;min-height:48px;font-size:17px !important;}
button.secondary {border-radius:24px !important;} .tab-nav button {border-radius:20px !important;white-space:normal !important;}
.passport {background:white;border:2px dashed #a4c9ec;border-radius:24px;padding:25px;color:#285e91;text-align:center;} .passport strong {font-size:42px;letter-spacing:5px;} .match {display:grid;grid-template-columns:100px 1fr 65px;gap:8px;align-items:center;margin:13px 0;text-align:left;} .track {background:#e4f1fc;border-radius:20px;height:13px;overflow:hidden;} .track i {display:block;background:#65abe5;height:100%;border-radius:20px;}
@media(max-width:550px){.gradio-container{padding:9px !important;}.hero{padding:24px 10px;}.mission p{font-size:16px;}.match{grid-template-columns:85px 1fr 55px;}}
"""

def mission_html(i):
    url = f"https://images.unsplash.com/photo-{PHOTO_IDS[i]}?auto=format&fit=crop&w=1200&q=80"
    return f"""<div class='mission'><div>✈️ MISSION {i+1:02d} / 12</div><div class='progress'><i style='width:{(i+1)/12*100:.2f}%'><b>✈️</b></i></div><div class='photo'><img src='{url}' alt='{html.escape(MISSION_NAMES[i])}'><span>🌐 {MISSION_NAMES[i]}</span></div><h2>{MISSION_NAMES[i]}</h2><p>Q{i+1}. {html.escape(questions[i][0])}</p><p>대통령님, 어떤 결정을 내리시겠습니까?</p></div>"""

def passport_html(result, df):
    if df.empty: return ""
    code, name = result.split("### ",1)[1].split("\n",1)[0].split(" - ",1)
    bars = "".join(f"<div class='match'><span>{FLAGS[r['국가']]} {r['국가']}</span><div class='track'><i style='width:{r['궁합 지수']}%'></i></div><span>{r['궁합 지수']}점</span></div>" for _,r in df.iterrows())
    return f"<div class='passport'>🛂 MY DIPLOMATIC PASSPORT<br><strong>{code}</strong><h2>{html.escape(name)}</h2><h3>나와 세계 7개국의 외교 궁합</h3>{bars}</div>"

def create_test_tab():
    with gr.Tab("✈️ 나의 외교 MBTI"):
        index = gr.State(0)
        saved = gr.State([None]*12)
        with gr.Column(visible=True) as intro:
            gr.Markdown("### 💌 대통령님, 환영합니다!\n12가지 외교 미션을 수행하고 나만의 외교 여권을 받아 보세요.")
            start = gr.Button("대통령 취임하기! ✨", variant="primary")
        with gr.Column(visible=False) as quiz:
            visual = gr.HTML(mission_html(0))
            choice = gr.Radio(choices=list(questions[0][1:]), value=None, label="나의 선택", elem_classes="answer-card")
            warning = gr.Markdown("")
            with gr.Row():
                back = gr.Button("← 이전", interactive=False)
                forward = gr.Button("다음 미션 →", variant="primary")
        with gr.Column(visible=False) as finish:
            gr.Markdown("## 🎉 모든 외교 미션 완료!\n국가와 비교할 외교 상황을 선택해 주세요.")
            situation = gr.Dropdown(choices=list(weights), value="경제·무역", label="외교 상황")
            with gr.Row():
                edit = gr.Button("← 마지막 미션 다시 보기")
                calculate = gr.Button("나의 외교 여권 발급하기 🛂", variant="primary")
            passport = gr.HTML()
            result = gr.Markdown()
            table = gr.Dataframe(label="나와 7개국의 외교 궁합", interactive=False)
            restart = gr.Button("처음부터 다시 하기")
        start.click(lambda: (gr.update(visible=False),gr.update(visible=True)), outputs=[intro,quiz])
        def move(i, answers, selected, direction):
            answers = list(answers)
            if direction == 1 and selected is None:
                return i, answers, gr.update(),gr.update(),gr.update(),gr.update(),gr.update(),gr.update(),"⚠️ 선택지를 골라 주세요."
            answers[i] = selected
            target = max(0, i+direction)
            if target == 12:
                return i,answers,gr.update(),gr.update(),gr.update(),gr.update(),gr.update(visible=False),gr.update(visible=True),""
            return target,answers,mission_html(target),gr.update(choices=list(questions[target][1:]),value=answers[target]),gr.update(interactive=target>0),gr.update(value="미션 완료 →" if target==11 else "다음 미션 →"),gr.update(visible=True),gr.update(visible=False),""
        outputs=[index,saved,visual,choice,back,forward,quiz,finish,warning]
        forward.click(lambda i,a,c:move(i,a,c,1),[index,saved,choice],outputs)
        back.click(lambda i,a,c:move(i,a,c,-1),[index,saved,choice],outputs)
        edit.click(lambda a:(11,mission_html(11),gr.update(choices=list(questions[11][1:]),value=a[11]),gr.update(interactive=True),gr.update(value="미션 완료 →"),gr.update(visible=True),gr.update(visible=False),""),[saved],[index,visual,choice,back,forward,quiz,finish,warning])
        def show_result(s,a):
            r,d=take_test(s,*a)
            return passport_html(r,d),r,d
        calculate.click(show_result,[situation,saved],[passport,result,table])
        restart.click(lambda:(0,[None]*12,mission_html(0),gr.update(choices=list(questions[0][1:]),value=None),gr.update(interactive=False),gr.update(value="다음 미션 →"),gr.update(visible=False),gr.update(visible=False),gr.update(visible=True),"","","",pd.DataFrame()),outputs=[index,saved,visual,choice,back,forward,quiz,finish,intro,warning,passport,result,table])
# 7. 두 번째 탭: 국가 간 외교 궁합 분석

def create_country_tab():

    with gr.Tab("국가 간 외교 궁합 분석"):

        gr.Markdown("## 🌐 국가 간 외교 궁합 분석")
        gr.Markdown(
            "두 국가와 외교 상황을 선택하면 "
            "궁합 지수와 기준별 계산 결과를 확인할 수 있습니다."
        )

        # 국가 A, 국가 B를 가로로 배치
        with gr.Row():

            a = gr.Dropdown(
                choices=list(countries),
                value="대한민국",
                label="국가 A"
            )

            b = gr.Dropdown(
                choices=list(countries),
                value="일본",
                label="국가 B"
            )

        # 상황 선택
        situation = gr.Radio(
            choices=list(weights),
            value="경제·무역",
            label="외교 상황"
        )

        # 분석 버튼
        analyze_button = gr.Button(
            "국가 궁합 분석하기",
            variant="primary"
        )

        # 결과 표시
        country_result = gr.Markdown()

        detail_table = gr.Dataframe(
            label="기준별 분석 결과",
            interactive=False
        )

        # 버튼과 함수 연결
        analyze_button.click(
            fn=analyze_countries,
            inputs=[a, b, situation],
            outputs=[country_result, detail_table]
        )

# 8. 세 번째 탭: 전체 21개 국가 조합 비교

def create_all_tab():

    with gr.Tab("전체 21개 국가 조합 비교"):

        gr.Markdown("## 📊 전체 국가 궁합 순위")
        gr.Markdown(
            "외교 상황을 선택하면 "
            "7개국에서 가능한 21개 국가 조합의 "
            "궁합 점수를 높은 순서대로 확인할 수 있습니다."
        )

        # 외교 상황 선택
        all_situation = gr.Radio(
            choices=list(weights),
            value="경제·무역",
            label="외교 상황"
        )

        # 전체 계산 버튼
        all_button = gr.Button(
            "전체 궁합 계산하기",
            variant="primary"
        )

        # 결과표
        all_table = gr.Dataframe(
            label="전체 국가 궁합 순위",
            interactive=False
        )

        # 버튼과 함수 연결
        all_button.click(
            fn=compare_all,
            inputs=[all_situation],
            outputs=[all_table]
        )


# Gradio 5 and 6 use different locations for CSS and theme options.
major = int(gr.__version__.split('.')[0])
style = dict(css=CSS, theme=gr.themes.Soft(primary_hue="blue", secondary_hue="sky"))
with gr.Blocks(title="DIPLOMATCH 💌 | 오늘부터 내가 대통령?!", **(style if major < 6 else {})) as demo:
    gr.HTML("""<div class='hero'><div class='globe'>☁️ 🌍 ✈️</div><div>DIPLOMATCH 💌</div><h1>오늘부터 내가 대통령?!</h1><p>나의 선택으로 달라지는 세상,<br>나는 어떤 지도자가 될까?</p><div class='chips'><span>🌍 7개 국가</span><span>💌 12개 미션</span><span>🧩 16개 유형</span></div></div>""")
    create_test_tab()
    create_country_tab()
    create_all_tab()
    gr.Markdown("---\n이 프로그램은 고등학생의 국제관계 탐구를 위해 설계된 시뮬레이션입니다. 외교 유형과 궁합 점수는 탐구 모형의 가정에 따른 것이며 실제 국가 관계를 확정적으로 판단하는 기준이 아닙니다. 사진은 상황 이해를 위한 참고 이미지입니다.")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT",10000)), **(style if major >= 6 else {}))
