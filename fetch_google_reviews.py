from playwright.sync_api import sync_playwright
import csv

business_name = input("Enter business name: ").strip()

MAX_REVIEWS = 100
SCROLL_TIMES = 20

reviews = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page(
        viewport={"width": 1366, "height": 900}
    )

    print("\nOpening Google Maps...")
    page.goto("https://www.google.com/maps", timeout=60000)
    page.wait_for_timeout(8000)

    print("Searching business...")

    search_box = page.locator("input[name='q']").first
    search_box.click()
    search_box.fill(business_name)
    search_box.press("Enter")

    page.wait_for_timeout(10000)

    print("Opening reviews...")

    try:
        page.get_by_text("Reviews").first.click(timeout=15000)
        page.wait_for_timeout(6000)
    except:
        print("Reviews button not found.")
        browser.close()
        exit()

    print("Loading reviews...")

    for _ in range(SCROLL_TIMES):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1500)

    print("Extracting reviews...")

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

with open("reviews.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["review"])

    for review in reviews:
        writer.writerow([review])

print(f"\nSaved {len(reviews)} reviews to reviews.csv")