import streamlit as st
import pandas as pd
import csv
from playwright.sync_api import sync_playwright
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

.metric-card:hover {
    transform: translateY(-4px);
    transition: 0.3s ease;
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

.stProgress > div > div > div > div {
    background-color: #E30016;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Google Reviews Sentiment Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Fetch Google Maps reviews and analyze customer sentiment</div>', unsafe_allow_html=True)

business_name = st.text_input(
    "Enter Business Name",
    placeholder="Example: Tonico Cafe Kottayam"
)

st.caption("Enter the exact business name as it appears on Google Maps.")

MAX_REVIEWS = 100
SCROLL_TIMES = 20
INPUT_FILE = "reviews.csv"


def fetch_google_reviews(business_name):
    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        page = browser.new_page(
            viewport={"width": 1366, "height": 900}
        )

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(8000)

        search_box = page.locator("input[name='q']").first
        search_box.click()
        search_box.fill(business_name)
        search_box.press("Enter")

        page.wait_for_timeout(10000)

        try:
            page.get_by_text("Reviews").first.click(timeout=15000)
            page.wait_for_timeout(6000)
        except:
            browser.close()
            return []

        for _ in range(SCROLL_TIMES):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)

        review_elements = page.locator("span.wiI7pd").all()

        for element in review_elements:
            try:
                review = element.inner_text().strip()

                if review and review not in reviews:
                    reviews.append(review)

                if len(reviews) >= MAX_REVIEWS:
                    break

            except:
                pass

        browser.close()

    with open(INPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["review"])

        for review in reviews:
            writer.writerow([review])

    return reviews


def analyze_reviews():
    df = pd.read_csv(INPUT_FILE)

    possible_columns = ["review", "Review", "reviews", "Reviews", "Review Text"]
    review_column = None

    for col in possible_columns:
        if col in df.columns:
            review_column = col
            break

    if review_column is None:
        review_column = df.columns[0]

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
• Encourage satisfied customers to leave more reviews to strengthen online reputation.
• Monitor customer feedback regularly to ensure service standards remain consistent.
• Use repeated positive comments to identify the strongest parts of the business.
• Maintain fast response time and good customer support to keep satisfaction high.
• Compare future reviews with current results to check whether customer opinion improves or declines."""

    elif negative_percentage >= 60:
        overall = "Negative"

        insight = """Most customer reviews show negative sentiment.
There may be customer dissatisfaction or service-related issues.
Repeated complaints may indicate operational or customer experience problems."""

        recommendation = """• Review negative feedback carefully to identify common customer concerns.
• Prioritize solving repeated issues mentioned by customers.
• Improve customer support response time and issue resolution.
• Reply to dissatisfied customers politely and professionally.
• Track sentiment regularly to measure whether improvements are working.
• Identify whether complaints are related to service, product quality, delivery, pricing, or staff behavior.
• Create an action plan based on the most common problems found in reviews."""

    else:
        overall = "Mixed / Neutral"

        insight = """Customer opinion is mixed.
Reviews contain both positive and negative feedback.
The business has strengths in some areas, but improvements may be needed in others."""

        recommendation = """• Analyze both positive and negative reviews to identify recurring themes.
• Focus on improving areas frequently mentioned in critical feedback.
• Preserve and strengthen aspects that customers consistently appreciate.
• Continue collecting customer feedback to monitor sentiment changes.
• Perform deeper review analysis to find specific improvement opportunities.
• Separate reviews by topic such as service, price, quality, and customer support.
• Use this sentiment report as a starting point for business improvement decisions."""

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

    return total, positive, negative, neutral, report


if st.button("Fetch Reviews and Analyze"):
    if not business_name:
        st.error("Please enter a business name.")
    else:
        with st.spinner("Fetching Google reviews..."):
            reviews = fetch_google_reviews(business_name)

        if not reviews:
            st.error("No reviews found or reviews button not found.")
            st.stop()

        st.success(f"Saved {len(reviews)} reviews to reviews.csv")

        with st.spinner("Analyzing reviews..."):
            total, positive, negative, neutral, report = analyze_reviews()

        st.success("Analysis completed successfully!")

        positive_percentage = (positive / total) * 100 if total else 0
        negative_percentage = (negative / total) * 100 if total else 0
        neutral_percentage = (neutral / total) * 100 if total else 0

        st.markdown("## Customer Sentiment Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        cards = [
            ("Total Reviews", total, "All collected reviews"),
            ("Positive", positive, f"{positive_percentage:.1f}% favorable"),
            ("Negative", negative, f"{negative_percentage:.1f}% critical"),
            ("Neutral", neutral, f"{neutral_percentage:.1f}% neutral"),
        ]

        for col, (title, value, desc) in zip([col1, col2, col3, col4], cards):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{value}</div>
                    <div style="font-size:14px; color:#666666 !important; margin-top:6px;">
                        {desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("### Sentiment Overview")

            st.progress(positive_percentage / 100)
            st.write(f"Positive Sentiment: {positive_percentage:.2f}%")

            st.progress(negative_percentage / 100)
            st.write(f"Negative Sentiment: {negative_percentage:.2f}%")

            st.progress(neutral_percentage / 100)
            st.write(f"Neutral Sentiment: {neutral_percentage:.2f}%")

        with right:
            st.markdown("### Business Interpretation")

            if positive_percentage >= 60:
                status = "Strong Customer Satisfaction"
                summary = "Most customers are happy with the business experience."
            elif negative_percentage >= 60:
                status = "Needs Immediate Attention"
                summary = "Many customers are expressing dissatisfaction."
            else:
                status = "Mixed Customer Response"
                summary = "Customer feedback is balanced with both strengths and concerns."

            st.markdown(f"""
            <div class="report-card">
                <h3>{status}</h3>
                <p>{summary}</p>
                <p>This dashboard helps the business understand customer opinion from Google reviews and take improvement decisions based on review sentiment.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Full Text Report")

        st.markdown(f"""
        <div class="report-card">
{report}
        </div>
        """, unsafe_allow_html=True)