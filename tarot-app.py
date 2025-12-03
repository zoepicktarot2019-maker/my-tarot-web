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

# --- 2. 버전 확인 ---
try:
    version = importlib.metadata.version("google-generativeai")
except:
    version = "확인 불가"

# --- 3. UI 설정 ---
st.title("🔮 Zoe의 상냥한 타로 상담소")
st.caption(f"🚀 System Status: v{version} (설치 성공!)")
st.markdown("### Zoe가 당신의 운명을 읽어드립니다.")

# --- 4. 사이드바 & 모델 자동 감지 (핵심!) ---
with st.sidebar:
    st.header("🔧 설정")
    
    # 키 확인
    if len(MY_SECRET_KEY) < 20:
        api_key = st.text_input("Google AI API Key 입력", type="password")
        st.warning("⚠️ 코드 10번째 줄에 키를 넣어주세요.")
    else:
        api_key = MY_SECRET_KEY
    
    st.divider()
    st.write("🤖 **모델 선택**")
    
    # [핵심] 사용 가능한 모델을 자동으로 찾아옵니다
    valid_models = []
    if len(api_key) > 20:
        try:
            genai.configure(api_key=api_key)
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_models.append(m.name)
        except:
            pass
            
    # 모델 선택 상자 만들기
    if valid_models:
        # gemini-1.5-flash가 있으면 그걸 기본으로, 없으면 첫 번째 것 선택
        default_idx = 0
        for i, m in enumerate(valid_models):
            if "flash" in m:
                default_idx = i
                break
        selected_model = st.selectbox("사용할 모델을 선택하세요:", valid_models, index=default_idx)
        st.success(f"✅ 연결 성공: {selected_model}")
    else:
        st.error("⚠️ 사용 가능한 모델을 찾지 못했습니다.")
        st.info("API Key가 올바른지 확인하거나, 새로 발급받아 보세요.")
        selected_model = None

# --- 5. 타로 데이터 ---
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
    {"name": "Wands", "emoji": "🪄", "mean": "열정"}, {"name": "Cups", "emoji": "🏆", "mean": "감정"},
    {"name": "Swords", "emoji": "⚔️", "mean": "이성"}, {"name": "Pentacles", "emoji": "🪙", "mean": "현실"}
]
ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
full_deck = major_arcana + [{"name": f"{r} of {s['name']}", "emoji": s['emoji'], "suit_meaning": s['mean']} for s in suits for r in ranks]

# --- 6. 메인 로직 ---
question = st.text_input("고민을 적어주세요:", placeholder="예: 유튜브 채널이 잘 될까요?")

if st.button("Zoe에게 물어보기 🎴"):
    if not selected_model:
        st.error("❌ 사용할 수 있는 AI 모델이 없습니다. 사이드바 설정을 확인하세요.")
    elif not question:
        st.warning("질문을 입력해주세요!")
    else:
        with st.spinner(f'Zoe가 {selected_model} 모델로 운명을 읽고 있습니다...'):
            try:
                cards = random.sample(full_deck, 3)
                positions = ["과거", "현재", "미래"]
                card_text = "\n".join([f"{i+1}. {positions[i]}: {c['name']} {c.get('suit_meaning','')}" for i, c in enumerate(cards)])
                
                prompt = f"""
                당신은 타로 마스터 Zoe입니다.
                질문: "{question}"
                카드:
                {card_text}
                
                친절하고 신비로운 말투(해요체)로 해석해주세요.
                Markdown 서식을 사용하세요.
                """
                
                # 선택된 모델로 호출
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt)
                
                st.divider()
                st.write(f"### **Q. {question}**")
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        st.markdown(f"<div style='text-align:center; color:gray;'>{positions[i]}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:60px; text-align:center;'>{cards[i]['emoji']}</div>", unsafe_allow_html=True)
                st.divider()
                st.subheader("🔮 Zoe의 해석")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"오류: {e}")
