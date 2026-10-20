import streamlit as st
from google import genai
from pypdf import PdfReader
from io import BytesIO
from datetime import date
import json

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("AI-Powered Conversational Assistant")
st.caption("An AI assistant for business questions and document analysis.")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = f"""
You are a reliable AI business and technology assistant.

TODAY'S DATE: {date.today().strftime("%d %B %Y")}

ACCURACY RULES:
1. Treat the user's explicit statements and corrections
   as the primary source of truth about their own experience,
   education, employment, and timeline.
2. Never invent dates, qualifications, contradictions,
   or explanations unsupported by evidence.
3. A student can complete an internship before graduating.
   Do not assume an internship is upcoming just because
   the graduation year is later.
4. Use the current date above to determine whether an event
   is past, present, or future.
5. Accept user corrections and do not repeat old assumptions
   after the user has corrected them.
6. Clearly distinguish facts, inferences, and unknowns.
7. If something is unclear, explain what is unknown
   instead of guessing.
8. Never claim you cannot determine today's date when
   it is provided above.
9. Never invent statistics, sources, citations, or facts.

RESUME AND CAREER QUESTIONS:
- Evaluate timelines using the dates actually provided.
- Do not recommend changing dates or verb tenses without
  evidence that they are incorrect.
- Respect the user's confirmed corrections.

BUSINESS AND DOCUMENT ANALYSIS:
- Base conclusions on available evidence.
- Separate facts from assumptions.
- Explain limitations when information is missing.
- Provide practical, evidence-based recommendations.

Be concise, professional, accurate, and transparent.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Document Analysis")
    uploaded_file = st.file_uploader("Upload a business PDF", type=["pdf"])
    analyze_button = st.button(
        "Analyze PDF",
        disabled=uploaded_file is None
    )

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

if analyze_button and uploaded_file is not None:
    try:
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))

        if reader.is_encrypted:
            st.error("This PDF is encrypted.")
        else:
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

            if not text.strip():
                st.warning("No readable text found in this PDF.")
            else:
                prompt = f"""
                {SYSTEM_PROMPT}
                Analyze this business report.
                Provide:
                1. Executive summary
                2. Key findings
                3. Risks and limitations
                4. Recommendations
                5. Suggested performance metrics

                REPORT TEXT:
                {text[:12000]}
                """

                with st.spinner("Analyzing document..."):
                    result = client.interactions.create(
                        model=MODEL,
                        input=prompt
                    )

                st.subheader("Document Analysis")
                st.markdown(result.output_text)

    except Exception as e:
        st.error(f"Document analysis failed: {e}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a business or technology question...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    recent_messages = st.session_state.messages[-8:]

    history_text = json.dumps(
        recent_messages,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
    {SYSTEM_PROMPT}

    CONVERSATION HISTORY:
    {history_text}

    Answer the latest user question using the conversation history.
    Prioritize explicit user corrections over earlier assistant
    assumptions. Do not treat earlier assistant claims as verified
    facts unless supported by the user or source material.
    """

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = client.interactions.create(
                    model=MODEL,
                    input=prompt
                )

            answer = result.output_text
            st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(
                "Request failed. Check your API key, model availability, "
                f"network, or API quota. Details: {e}"
            )
