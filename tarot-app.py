import streamlit as st
import random
import time
import google.generativeai as genai
import importlib.metadata

# ==========================================
# 👇 [필수] API 키 입력
MY_SECRET_KEY = "AIzaSyACXNn2KKH1093AToL1lflB80Pt7oGT7AM"
# ==========================================

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Zoe의 상냥한 타로 상담소", page_icon="🔮", layout="wide")

# --- 2. 라이브러리 버전 확인 (화면 상단 표시) ---
try:
    version = importlib.metadata.version("google-generativeai")
except:
    version = "확인 불가"

# --- 3. UI 설정 ---
st.title("🔮 Zoe의 상냥한 타로 상담소")
# 버전이 0.8.3 이상인지 눈으로 확인하기 위해 표시합니다.
st.caption(f"🚀 System Info: google-generativeai v{version} (0.8.3 이상이어야 함)")
st.markdown("### Zoe가 당신의 운명을 읽어드립니다.")

# --- 4. 사이드바 설정 ---
with st.sidebar:
    st.header("🔧 설정")
    if len(MY_SECRET_KEY) < 20:
        api_key = st.text_input("Google AI API Key 입력", type="password")
        st.warning("⚠️ 코드 10번째 줄에 API Key를 입력해주세요.")
    else:
        api_key = MY_SECRET_KEY
        st.success("✅ Zoe가 준비되었습니다.")

# --- 5. 타로 데이터 (78장) ---
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
    {"name": "Wands", "emoji": "🪄", "mean": "열정/행동"}, {"name": "Cups", "emoji": "🏆", "mean": "감정/사랑"},
    {"name": "Swords", "emoji": "⚔️", "mean": "이성/고뇌"}, {"name": "Pentacles", "emoji": "🪙", "mean": "현실/물질"}
]
ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
full_deck = major_arcana + [{"name": f"{r} of {s['name']}", "emoji": s['emoji'], "suit_meaning": s['mean']} for s in suits for r in ranks]

# --- 6. 사용자 질문 ---
question = st.text_input("고민을 적어주세요:", placeholder="예: 지금 하는 일이 잘 풀릴까요?")

# --- 7. 상담 로직 ---
if st.button("Zoe에게 물어보기 🎴"):
    if not api_key or len(api_key) < 20:
        st.error("⚠️ API Key 오류: 설정에서 키를 확인해주세요.")
    elif not question:
        st.warning("질문을 입력해주세요!")
    else:
        with st.spinner('Zoe가 78장의 카드를 읽고 있습니다...'):
            try:
                # 카드 뽑기
                cards = random.sample(full_deck, 3)
                positions = ["과거", "현재", "미래"]
                
                # 프롬프트 구성
                card_text = "\n".join([f"{i+1}. {positions[i]}: {c['name']} {c.get('suit_meaning','')}" for i, c in enumerate(cards)])
                
                prompt = f"""
                당신은 타로 마스터 Zoe입니다.
                질문: "{question}"
                카드:
                {card_text}
                
                친절하고 신비로운 말투(해요체)로, 카드의 상징과 질문을 연결해 해석해주세요.
                Markdown으로 보기 좋게 출력하세요.
                """

                # 모델 호출 (오직 1.5 Flash만 사용)
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                # 결과 출력
                st.divider()
                st.write(f"### **Q. {question}**")
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        st.markdown(f"<div style='text-align:center; color:gray;'>{positions[i]}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:60px; text-align:center;'>{cards[i]['emoji']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; font-weight:bold;'>{cards[i]['name']}</div>", unsafe_allow_html=True)
                
                st.divider()
                st.subheader("🔮 Zoe의 해석")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.info("System Info 버전을 확인해주세요. 0.8.3 미만이면 requirements.txt 수정이 반영되지 않은 것입니다.")
