# Google-Reviews-Sentiment-Analyzer
An AI-powered business review analysis system that automatically collects Google Maps reviews using Playwright, performs sentiment analysis with Hugging Face Transformers, and generates actionable business insights through an interactive Streamlit dashboard.

## Project Overview

This project is designed to help businesses understand customer opinion from Google Maps reviews. It fetches reviews from Google Maps, performs sentiment analysis using a Hugging Face Transformer model, and generates a professional dashboard with insights and recommendations.

## Features

* Fetches Google Maps reviews using Playwright
* Saves collected reviews into a CSV file
* Performs sentiment analysis on customer reviews
* Classifies reviews as Positive, Negative, or Neutral
* Displays total reviews and sentiment counts
* Shows sentiment percentages using a dashboard
* Generates business insights and recommendations

## Project Files

### app.py

This is the main combined application file.
It includes both review collection and sentiment analysis dashboard in one Streamlit app.

### fetch_google_reviews.py

This file was created first to separately collect reviews from Google Maps using Playwright.
It searches for a business name, opens the reviews section, extracts reviews, and saves them into `reviews.csv`.

### dashboard.py

This file was created separately for analyzing the collected reviews.
It reads the `reviews.csv` file, performs sentiment analysis, and displays the dashboard with insights.

### reviews.csv

This file is generated automatically after fetching reviews.
It stores the collected Google reviews.

## Technologies Used

* Python
* Streamlit
* Playwright
* Pandas
* Hugging Face Transformers
* CSV

## How It Works

1. The user enters a business name, for example: `Tonico Cafe Kottayam`.
2. Playwright opens Google Maps and searches for the business.
3. The application opens the reviews section and collects customer reviews.
4. The reviews are saved into `reviews.csv`.
5. The sentiment analysis model analyzes each review.
6. Reviews are classified as Positive, Negative, or Neutral.
7. The Streamlit dashboard displays the final sentiment report, metrics, insights, and recommendations.

## Purpose

This project was developed as part of an internship task to demonstrate web automation, sentiment analysis, and dashboard-based business insight generation.

## Future Improvements

* Add aspect-based sentiment analysis
* Add charts for sentiment distribution
* Export final report as PDF
* Improve review extraction accuracy
* Add support for multiple businesses
