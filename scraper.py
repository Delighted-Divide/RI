import os
import time
from playwright.sync_api import sync_playwright

def scrape_novel():
    base_url = "https://novelfull.com/reverend-insanity/chapter-1.html"
    output_dir = "chapters"
    log_file = "scraper.log"
    os.makedirs(output_dir, exist_ok=True)

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"Scraping started at {time.ctime()}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        current_url = base_url
        chapter_count = 1

        while current_url:
            msg = f"[{time.ctime()}] Scraping {current_url} (Chapter {chapter_count})..."
            print(msg)
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(msg + "\n")
            
            try:
                page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
                
                # Extract content
                data = page.evaluate("""
                    () => {
                        const contentElement = document.getElementById('chapter-content');
                        if (!contentElement) return null;

                        // Remove ad elements
                        const ads = contentElement.querySelectorAll('div[align="center"], iframe, script, ins, .adsbygoogle');
                        ads.forEach(ad => ad.remove());

                        // Get text content
                        const paragraphs = Array.from(contentElement.querySelectorAll('p')).map(p => p.innerText.trim()).filter(t => t.length > 0);
                        
                        const title = document.querySelector('.chapter-title')?.innerText || document.querySelector('h2')?.innerText || '';
                        
                        const nextBtn = document.getElementById('next_chap');
                        const nextUrl = nextBtn ? nextBtn.href : null;

                        return {
                            title: title,
                            content: paragraphs.join('\\n\\n'),
                            nextUrl: nextUrl
                        };
                    }
                """)

                if not data or not data['content']:
                    error_msg = f"Failed to find content for {current_url}"
                    print(error_msg)
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(error_msg + "\n")
                    break

                # Save to file
                filename = f"chapter_{chapter_count:04d}.txt"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"{data['title']}\n\n")
                    f.write(data['content'])

                success_msg = f"Saved {filename}: {data['title']}"
                print(success_msg)
                # No need to log every success to file if we want to keep it small, but let's log every 10
                if chapter_count % 10 == 0:
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(success_msg + "\n")

                # Update for next iteration
                next_url = data['nextUrl']
                if next_url and next_url != current_url and 'reverend-insanity' in next_url:
                    current_url = next_url
                    chapter_count += 1
                else:
                    end_msg = "No more chapters found or reached the end."
                    print(end_msg)
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(end_msg + "\n")
                    current_url = None

                # Delay
                time.sleep(1)

            except Exception as e:
                error_msg = f"Error scraping {current_url}: {e}"
                print(error_msg)
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(error_msg + "\n")
                break

        browser.close()

if __name__ == "__main__":
    scrape_novel()
