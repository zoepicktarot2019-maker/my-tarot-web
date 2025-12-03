import streamlit as st
import random
import time
import google.generativeai as genai

# ==========================================
# 👇 [필수] API 키 입력
# 보안을 위해 실제 배포 시에는 Streamlit Secrets 기능을 사용하는 것이 좋습니다.
MY_SECRET_KEY = "AIzaSyACXNn2KKH1093AToL1lflB80Pt7oGT7AM"
# ==========================================

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Zoe의 상냥한 타로 상담소", page_icon="🔮", layout="wide")

# --- 2. UI 설정 ---
st.title("🔮 Zoe의 상냥한 타로 상담소")
st.markdown("### Zoe가 당신의 운명을 읽어드립니다.")

# --- 3. 사이드바 설정 ---
with st.sidebar:
    st.header("🔧 설정")
    
    # 키 길이가 20글자보다 짧으면 (키를 안 넣은 것으로 간주) -> 입력창 표시
    if len(MY_SECRET_KEY) < 20:
        api_key = st.text_input("Google AI API Key 입력", type="password")
        st.warning("⚠️ 코드 10번째 줄에 API Key를 입력하면 이 창이 사라집니다.")
    
    # 키가 20글자 이상이면 (키를 넣은 것으로 간주) -> 입력창 숨김
    else:
        api_key = MY_SECRET_KEY
        st.success("✅ API Key가 코드에 적용되었습니다.")
        st.info("입력창은 자동으로 숨겨졌습니다.")

# --- 4. 타로 카드 데이터 (78장) ---
major_arcana = [
    {"name": "The Fool (광대)", "emoji": "🤡"}, {"name": "The Magician (마법사)", "emoji": "🧙‍♂️"},
    {"name": "The High Priestess (여사제)", "emoji": "📜"}, {"name": "The Empress (여황제)", "emoji": "👸"},
    {"name": "The Emperor (황제)", "emoji": "👑"}, {"name": "The Hierophant (교황)", "emoji": "⛪"},
    {"name": "The Lovers (연인)", "emoji": "💕"}, {"name": "The Chariot (전차)", "emoji": "🛒"},
    {"name": "Strength (힘)", "emoji": "🦁"}, {"name": "The Hermit (은둔자)", "emoji": "🕯️"},
    {"name": "Wheel of Fortune (운명의 수레바퀴)", "emoji": "🎡"}, {"name": "Justice (정의)", "emoji": "⚖️"},
    {"name": "The Hanged Man (매달린 사람)", "emoji": "🙃"}, {"name": "Death (죽음)", "emoji": "💀"},
    {"name": "Temperance (절제)", "emoji": "🥛"}, {"name": "The Devil (악마)", "emoji": "👿"},
    {"name": "The Tower (탑)", "emoji": "⚡"}, {"name": "The Star (별)", "emoji": "🌟"},
    {"name": "The Moon (달)", "emoji": "🌙"}, {"name": "The Sun (태양)", "emoji": "🌞"},
    {"name": "Judgement (심판)", "emoji": "📯"}, {"name": "The World (세계)", "emoji": "🌍"}
]

suits = [
    {"name": "Wands (지팡이)", "emoji": "🪄", "meaning": "열정, 행동, 불"},
    {"name": "Cups (컵)", "emoji": "🏆", "meaning": "감정, 사랑, 물"},
    {"name": "Swords (검)", "emoji": "⚔️", "meaning": "이성, 고뇌, 바람"},
    {"name": "Pentacles (동전)", "emoji": "🪙", "meaning": "현실, 물질, 흙"}
]
ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]

minor_arcana = []
for suit in suits:
    for rank in ranks:
        minor_arcana.append({
            "name": f"{rank} of {suit['name']}",
            "emoji": suit['emoji'],
            "suit_meaning": suit['meaning']
        })

full_deck = major_arcana + minor_arcana

# --- 5. 사용자 질문 ---
question = st.text_input("고민을 적어주세요:", placeholder="예: 지금 하는 공부가 나에게 맞을까요?")

# --- 6. 상담 로직 ---
if st.button("Zoe에게 물어보기 🎴"):
    if not api_key or len(api_key) < 20:
        st.error("⚠️ API Key가 유효하지 않습니다. 코드나 사이드바를 확인해주세요.")
    elif not question:
        st.warning("질문을 입력해주세요!")
    else:
        with st.spinner('Zoe가 78장의 타로 카드를 해석하고 있습니다...'):
            try:
                # 1. 카드 3장 뽑기
                selected_cards = random.sample(full_deck, 3)
                positions = ["과거/원인", "현재/상황", "미래/결과"]
                
                card_info = ""
                for i in range(3):
                    card = selected_cards[i]
                    info = f"{i+1}. {positions[i]}: {card['name']}"
                    if 'suit_meaning' in card:
                        info += f" (속성: {card['suit_meaning']})"
                    card_info += info + "\n"

                # 2. 프롬프트
                prompt = f"""
                당신은 'Zoe'라는 이름의 상냥하고 신비로운 타로 마스터입니다.
                사용자 질문: "{question}"
                뽑힌 카드: {card_info}
                
                해석 조건:
                1. 친절하고 공감하는 어조(해요체)를 사용하세요.
                2. 각 카드의 상징과 사용자의 질문을 연결하여 구체적으로 해석하세요.
                3. 과거, 현재, 미래의 흐름을 자연스럽게 연결해주세요.
                4. 마지막에는 긍정적인 조언이나 용기를 주는 한마디를 덧붙이세요.
                5. Markdown 서식을 사용하여 가독성을 높이세요 (볼드체, 구분선 등).
                """

                # 3. 모델 호출 (최신 모델 gemini-1.5-flash 사용)
                genai.configure(api_key=api_key)
                
                # 오류 원인이었던 구형 모델(gemini-pro)로의 fall-back 코드를 제거했습니다.
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                # 4. 결과 출력
                st.divider()
                st.write(f"### **Q. {question}**")
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        st.markdown(f"<p style='text-align:center; color:gray;'>{positions[i]}</p>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:70px; text-align:center;'>{selected_cards[i]['emoji']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h5 style='text-align:center;'>{selected_cards[i]['name']}</h5>", unsafe_allow_html=True)
                
                st.divider()
                st.subheader("🔮 Zoe의 해석")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.info("API Key가 정확한지, 혹은 Google AI Studio에서 해당 모델 사용이 가능한지 확인해주세요.")
