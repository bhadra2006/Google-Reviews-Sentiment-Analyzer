import streamlit as st
import pandas as pd
from transformers import pipeline

st.set_page_config(
    page_title="Google Reviews Sentiment Analyzer",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f7f7f2;
    color: #222222 !important;
}

html, body, [class*="css"] {
    color: #222222 !important;
}

h1, h2, h3, h4, h5, h6,
p, div, span, label {
    color: #222222 !important;
}

.main-title {
    font-size: 44px;
    font-weight: 900;
    color: #E30016 !important;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #333333 !important;
    font-size: 18px;
    margin-bottom: 35px;
}

.stButton > button {
    background-color: #E30016;
    color: white !important;
    border-radius: 12px;
    height: 50px;
    font-size: 17px;
    font-weight: 800;
    border: none;
    width: 100%;
}

.stButton > button:hover {
    background-color: #C7CC58;
    color: #111111 !important;
}

.metric-card {
    background-color: white;
    padding: 24px;
    border-radius: 18px;
    border-top: 8px solid #C7CC58;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.10);
    text-align: center;
}

.metric-title {
    font-size: 15px;
    color: #555555 !important;
    font-weight: 600;
}

.metric-value {
    font-size: 36px;
    font-weight: 900;
    color: #E30016 !important;
}

.report-card {
    background-color: white;
    color: #222222 !important;
    padding: 28px;
    border-radius: 18px;
    border-left: 8px solid #E30016;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.10);
    margin-top: 15px;
    font-size: 17px;
    line-height: 1.7;
    white-space: pre-wrap;
}

.report-card h3 {
    color: #E30016 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Google Reviews Sentiment Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze customer reviews and generate business insights</div>', unsafe_allow_html=True)

INPUT_FILE = "reviews.csv"

try:
    df = pd.read_csv(INPUT_FILE)
except FileNotFoundError:
    st.error("reviews.csv not found. Run fetch_google_reviews.py first.")
    st.stop()

possible_columns = ["review", "Review", "reviews", "Reviews", "Review Text"]
review_column = None

for col in possible_columns:
    if col in df.columns:
        review_column = col
        break

if review_column is None:
    review_column = df.columns[0]

st.markdown("### Ready to analyze reviews")

if st.button("Analyze Reviews"):
    with st.spinner("Analyzing reviews..."):
        sentiment_model = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            truncation=True,
            max_length=512
        )

        sentiments = []

        for review in df[review_column].dropna():
            review = str(review).strip()

            if not review:
                continue

            result = sentiment_model(review)[0]
            rating = result["label"]

            if rating in ["1 star", "2 stars"]:
                sentiment = "Negative"
            elif rating == "3 stars":
                sentiment = "Neutral"
            else:
                sentiment = "Positive"

            sentiments.append(sentiment)

        total = len(sentiments)
        positive = sentiments.count("Positive")
        negative = sentiments.count("Negative")
        neutral = sentiments.count("Neutral")

        positive_percentage = (positive / total) * 100 if total else 0
        negative_percentage = (negative / total) * 100 if total else 0
        neutral_percentage = (neutral / total) * 100 if total else 0

        if positive_percentage >= 60:
            overall = "Positive"

            insight = """Most customer reviews show positive sentiment.
The business appears to have a favorable public reputation.
Customers generally appreciate the products, services, or overall experience."""

            recommendation = """• Continue maintaining the current service quality and customer experience.
• Highlight positive customer feedback in marketing campaigns and social media promotions.
• Encourage satisfied customers to leave additional reviews to strengthen online reputation.
• Monitor customer feedback regularly to ensure service standards remain consistent.
• Use recurring positive comments to identify key strengths and competitive advantages."""

        elif negative_percentage >= 60:
            overall = "Negative"

            insight = """Most customer reviews show negative sentiment.
There may be customer dissatisfaction or service-related issues.
Repeated complaints may indicate operational or customer experience problems."""

            recommendation = """• Review negative feedback carefully to identify common customer concerns.
• Prioritize resolving recurring issues mentioned in reviews.
• Improve customer support response times and issue resolution processes.
• Engage with dissatisfied customers and address their concerns professionally.
• Track sentiment trends over time to measure improvement efforts."""

        else:
            overall = "Mixed / Neutral"

            insight = """Customer opinion is mixed.
Reviews contain both positive and negative feedback.
The business demonstrates strengths in some areas while improvements may be needed in others."""

            recommendation = """• Analyze both positive and negative reviews to identify recurring themes.
• Focus on improving areas frequently mentioned in critical feedback.
• Preserve and strengthen aspects that customers consistently appreciate.
• Continue collecting customer feedback to monitor sentiment changes.
• Consider deeper review analysis to identify specific improvement opportunities."""

        report = f"""
GOOGLE REVIEWS SENTIMENT REPORT

Total Reviews Analyzed : {total}

Sentiment Summary
-----------------
Positive Reviews : {positive} ({positive_percentage:.2f}%)
Negative Reviews : {negative} ({negative_percentage:.2f}%)
Neutral Reviews  : {neutral} ({neutral_percentage:.2f}%)

Overall Customer Opinion
------------------------
{overall}

Key Insights
------------
{insight}

Recommendations
---------------
{recommendation}
"""

    st.success("Analysis completed successfully!")

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("Total Reviews", total),
        ("Positive", positive),
        ("Negative", negative),
        ("Neutral", neutral),
    ]

    for col, (title, value) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Analysis Report")

    st.markdown(f"""
    <div class="report-card">
{report}
    </div>
    """, unsafe_allow_html=True)