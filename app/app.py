import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from pypdf import PdfReader
from io import BytesIO
from datetime import date
import json


st.set_page_config(
    page_title="Nexus AI | AI-Powered Conversational Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# NEXUS AI — CUSTOM DESIGN (Ahhh! Guys editing it later to add some new design)
st.markdown("""
<style>
/* Main application background */
.stApp {
    background: linear-gradient(135deg, #0B1020 0%, #111A30 55%, #17152F 100%);
    color: #F1F5F9;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Headings */
h1, h2, h3 {
    color: #F1F5F9 !important;
    letter-spacing: -0.5px;
}

/* Body text */
p, label, .stMarkdown {
    color: #D3DAEA;
}

/* Input fields and chat input */
.stTextInput input,
.stTextArea textarea,
[data-testid="stChatInput"] textarea {
    background-color: #151E34 !important;
    color: #F1F5F9 !important;
    border: 1px solid #354366 !important;
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #526DFF, #8B5CF6);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1rem;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border: 1px solid #B7C2FF;
    box-shadow: 0 0 16px rgba(103, 111, 255, 0.25);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0A0F1E;
    border-right: 1px solid #29334D;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #151E34;
    border: 1px dashed #586A98;
    border-radius: 14px;
    padding: 12px;
}

/* Chat message containers */
[data-testid="stChatMessage"] {
    background: rgba(21, 30, 52, 0.78);
    border: 1px solid rgba(89, 108, 157, 0.25);
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 10px;
}

/* Divider */
hr /* Reduce unnecessary space around the chat area */
.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 1100px !important;
}

/* Keep chat input spacing compact */
[data-testid="stChatInput"] {
    margin-top: 0.5rem !important;
    padding-top: 0 !important;
}

/* Reduce space between chat messages */
[data-testid="stChatMessage"] {
    margin-bottom: 0.4rem !important;
    padding: 0.65rem 0.85rem !important;
}

/* Reduce heading spacing */
h1, h2, h3 {
    margin-bottom: 0.45rem !important;
}

/* Developer footer */
.developer-footer {
    text-align: center;
    color: #8792AC;
    font-size: 13px;
    padding: 22px 0 10px 0;
    margin-top: 35px;
    border-top: 1px solid rgba(128, 128, 128, 0.25);
}

.developer-footer strong {
    color: #B7C2FF;
}
/* Minimize the dark strip behind the chat input because it is looking really baaddd..*/
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {
    background: transparent !important;
    padding-top: 0 !important;
    padding-bottom: 0.35rem !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">
    <div style="
        background:linear-gradient(135deg,#526DFF,#8B5CF6);
        width:58px;
        height:58px;
        border-radius:16px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:30px;
        box-shadow:0 6px 24px rgba(103,111,255,0.25);
    ">✦</div>
    <div>
        <div style="
            font-size:34px;
            font-weight:750;
            letter-spacing:-1px;
            color:#F1F5F9;
        ">Nexus AI</div>
        <div style="font-size:14px;color:#A6B1CB;">
            AI-Powered Conversational Assistant
        </div>
    </div>
</div>
<div style="color:#A6B1CB; margin:12px 0 24px 0; font-size:15px;">
    Your intelligent workspace for conversations and business document analysis.
</div>
""", unsafe_allow_html=True)

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

# AI Business Insights Dashboard
st.divider()
st.header("📊 AI Business Insights Dashboard")
st.caption(
    "Upload a business report and select Analyze PDF to generate "
    "evidence-based insights, performance indicators, and recommendations."
)

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

                st.subheader("📊 Executive Business Dashboard")
                st.markdown(result.output_text)

                st.divider()
                st.subheader("💡 Business Intelligence")

                dashboard_prompt = f"""
                Analyze the business report below and extract measurable
                business KPIs.

                Return ONLY valid JSON with this structure:
                {{
                    "revenue": null,
                    "net_profit": null,
                    "gross_margin_pct": null,
                    "operating_margin_pct": null,
                    "net_profit_margin_pct": null,
                    "revenue_growth_pct": null,
                    "key_findings": [],
                    "monthly_trend": [],
                    "category_performance": [],
                    "risks": [],
                    "recommendations": []
                    
                }}

                Rules:
                - Return revenue and net_profit as USD millions (for example, 51.6 means USD 51.6 million).
                - Use numeric values only for KPIs supported by the report.
                - Use null when a KPI is not available.
                - Do not invent or estimate missing figures.
                - Use percentages as numbers without the percent sign.
                - Map "profit" to net profit, not gross or operating profit.
                - Keep gross margin, operating margin, and net profit margin separate.
                - Keep findings, risks, and recommendations concise.
                - In the executive summary, use plain text only; avoid LaTeX, equations, and mathematical formatting.
                - Return valid JSON only, without Markdown fences or extra text.
                - For monthly_trend, return a list of objects with "month" and "revenue_millions".
                - For category_performance, return a list of objects with "category" and "revenue_millions".
                - Revenue values in both chart fields must be numeric USD millions.
                - Include only months and categories supported by the uploaded report.
                - Do not invent or estimate chart values.
                - Return an empty array if the report does not contain the required data.

                REPORT:
                {text[:12000]}
                """

                with st.spinner("Building business insights..."):
                    dashboard_result = client.interactions.create(
                        model=MODEL,
                        input=dashboard_prompt
                    )

                import re

                dashboard_text = dashboard_result.output_text.strip()
                dashboard_text = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    dashboard_text
                )

                try:
                    dashboard_data = json.loads(dashboard_text)

                    metrics = [
                        ("Revenue", "revenue", "money"),
                        ("Net Profit", "net_profit", "money"),
                        ("Gross Margin", "gross_margin_pct", "percent"),
                        ("Net Profit Margin", "net_profit_margin_pct", "percent")
                    ]

                    revenue = dashboard_data.get("revenue")
                    net_profit = dashboard_data.get("net_profit")
                    net_margin = dashboard_data.get("net_profit_margin_pct")

                    if (
                        net_margin is None
                        and revenue is not None
                        and net_profit is not None
                        and float(revenue) != 0
                    ):
                        net_margin = float(net_profit) / float(revenue) * 100

                    columns = st.columns(4)

                    for column, (label, key, value_type) in zip(columns, metrics):
                        value = (
                            net_margin
                            if key == "net_profit_margin_pct"
                            else dashboard_data.get(key)
                        )

                        if value is None:
                            display_value = "N/A"
                        elif value_type == "percent":
                            display_value = f"{float(value):.2f}%"
                        elif value_type == "money":
                            display_value = f"${float(value):,.2f}M"
                        else:
                            display_value = str(value)

                        column.metric(label, display_value)
                                            # Interactive charts
                    monthly_data = dashboard_data.get("monthly_trend", [])
                    category_data = dashboard_data.get("category_performance", [])

                    if monthly_data:
                        st.subheader("Monthly Revenue Trend")

                        monthly_df = pd.DataFrame(monthly_data)

                        if {"month", "revenue_millions"}.issubset(monthly_df.columns):
                            fig = px.line(
                                monthly_df,
                                x="month",
                                y="revenue_millions",
                                markers=True,
                                title="Monthly Revenue (USD Millions)",
                                labels={
                                    "month": "Month",
                                    "revenue_millions": "Revenue (USD Millions)",
                                },
                            )
                            fig.update_layout(hovermode="x unified")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Monthly revenue data was not available in the expected format.")

                    if category_data:
                        st.subheader("Category Revenue Performance")

                        category_df = pd.DataFrame(category_data)

                        if {"category", "revenue_millions"}.issubset(category_df.columns):
                            fig = px.bar(
                                category_df,
                                x="category",
                                y="revenue_millions",
                                title="Revenue by Category (USD Millions)",
                                labels={
                                    "category": "Category",
                                    "revenue_millions": "Revenue (USD Millions)",
                                },
                                text="revenue_millions",
                            )
                            fig.update_layout(xaxis_title="Category", yaxis_title="Revenue (USD Millions)")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Category revenue data was not available in the expected format.")

                    st.subheader("Key Findings")
                    for finding in dashboard_data.get("key_findings", []):
                        st.markdown(f"- {finding}")

                    st.subheader("⚠️ Business Risks")
                    for risk in dashboard_data.get("risks", []):
                        st.markdown(f"- {risk}")

                    st.subheader("🚀 Recommendations")
                    for recommendation in dashboard_data.get("recommendations", []):
                        st.markdown(f"- {recommendation}")

                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    st.warning(
                        "The AI summary was generated, but the KPI data "
                        "could not be displayed in dashboard format."
                    )
                    st.caption(f"Details: {e}")

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

    # Prepare page-labelled PDF context for grounded Q&A
    document_context = ""

    if uploaded_file is not None:
        try:
            pdf_reader = PdfReader(
                BytesIO(uploaded_file.getvalue())
            )

            page_chunks = []
            for page_number, page in enumerate(
                pdf_reader.pages, start=1
            ):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    page_chunks.append(
                        f"[PDF PAGE {page_number}]\\n{page_text}"
                    )

            document_context = "\\n\\n".join(page_chunks)[:12000]

        except Exception as e:
            st.warning(f"Could not read PDF for chat: {e}")

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

    PDF DOCUMENT CONTEXT:
    {document_context if document_context else "No PDF is currently available."}

    PDF QUESTION-ANSWERING RULES:
    - When a PDF is available, use its extracted text as primary
      evidence for questions about that document.
    - Cite supporting evidence using the exact page labels supplied,
      such as [PDF PAGE 3].
    - Never invent page numbers, quotations, statistics, or findings.
    - Cite a page only when its supplied text supports the claim.
    - If the document does not contain enough evidence, say so.
    - The supplied text may be truncated. If information is absent
      from the available context, explain that it cannot be verified.
    - Distinguish document evidence from your interpretation.
    - For questions unrelated to the PDF, answer normally.

    Answer the latest user question using the conversation history
    and available document context. Prioritize explicit user
    corrections over earlier assistant assumptions. Do not treat
    earlier assistant claims as verified facts unless supported
    by the user or source material.
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


# Developer credit(Guysss! This area will help me in the interview that I really made this project..)
st.markdown("""
<style>
/* Developer footer */
.developer-footer {
    text-align: center;
    color: #8792AC;
    font-size: 13px;
    padding: 22px 0 10px 0;
    margin-top: 35px;
    border-top: 1px solid rgba(128, 128, 128, 0.25);
}

.developer-footer strong {
    color: #B7C2FF;
}

/* Hide the top toolbar and Deploy controls */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* Reduce top spacing */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
}

/* Compact page layout */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 1100px !important;
}
</style>

<div class="developer-footer">
    Crafted with care by <strong>Abhyudaya</strong>
    <br/>
    AI-Powered Conversational Assistant
</div>
""", unsafe_allow_html=True)
