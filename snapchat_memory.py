import os
import re
import time
import requests
from bs4 import BeautifulSoup

HTML_FILE = "html/memories_history.html"  # HTML file with memory links
DOWNLOAD_FOLDER = "downloads"
DELAY = 2

def create_folders():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    images_folder = os.path.join(DOWNLOAD_FOLDER, "images")
    videos_folder = os.path.join(DOWNLOAD_FOLDER, "videos")

    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    if not os.path.exists(videos_folder):
        os.makedirs(videos_folder)

    return images_folder, videos_folder

def find_download_links():
    print(f"Reading HTML file: {HTML_FILE}")

    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all table rows
    rows = soup.find_all('tr')

    memories = []
    for row in rows:
        cells = row.find_all('td')

        # Date, Type, Location, Download
        if len(cells) >= 4:
            date = cells[0].get_text(strip=True)
            media_type = cells[1].get_text(strip=True)

            # Download link is in the 4th column
            download_cell = cells[3]
            link = download_cell.find('a', {'onclick': True})

            if link and 'downloadMemories(' in link.get('onclick', ''):
                onclick_text = link.get('onclick')

                url_match = re.search(r"downloadMemories\('([^']+)'", onclick_text)

                if url_match:
                    download_url = url_match.group(1)
                    memories.append({
                        'date': date,
                        'type': media_type,
                        'url': download_url
                    })

    print(f"Found {len(memories)} memories to download")
    return memories

def make_filename(date_str, media_type, counter):
    safe_date = re.sub(r'[^\w\-_.]', '_', date_str)

    # Choose file extension
    if 'video' in media_type.lower():
        extension = '.mp4'
    else:
        extension = '.jpg'

    return f"{counter:04d}_{safe_date}_{media_type.lower()}{extension}"

def download_file(url, filepath):
    try:
        print(f"Downloading: {os.path.basename(filepath)}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(filepath, 'wb') as file:
            file.write(response.content)

        print(f"Saved: {os.path.basename(filepath)}")
        return True

    except Exception as e:
        print(f"Failed to download {os.path.basename(filepath)}: {e}")
        return False

def main():
    print("Simple Snapchat Memory Downloader")
    print("=" * 40)

    if not os.path.exists(HTML_FILE):
        print(f"Error: Can't find {HTML_FILE}")
        return

    images_folder, videos_folder = create_folders()
    memories = find_download_links()

    if not memories:
        print("No memories found! Check your HTML file.")
        return

    downloaded = 0
    failed = 0

    print(f"\nStarting downloads...")
    print(f"Will save to: {os.path.abspath(DOWNLOAD_FOLDER)}")
    print()

    for i, memory in enumerate(memories, 1):
        filename = make_filename(memory['date'], memory['type'], i)

        if 'video' in memory['type'].lower():
            filepath = os.path.join(videos_folder, filename)
        else:
            filepath = os.path.join(images_folder, filename)


        if os.path.exists(filepath):
            print(f"Skipping (already exists): {filename}")
            continue

        success = download_file(memory['url'], filepath)

        if success:
            downloaded += 1
        else:
            failed += 1

        if i < len(memories):
            time.sleep(DELAY)

        # Show progress every 10 files
        if i % 10 == 0:
            print(f"Progress: {i}/{len(memories)} processed")

    # Final summary
    print()
    print("=" * 40)
    print(f"Download Complete!")
    print(f"Successfully downloaded: {downloaded}")
    print(f"Failed: {failed}")
    print(f"Total processed: {len(memories)}")
    print(f"Files saved to: {os.path.abspath(DOWNLOAD_FOLDER)}")
    print("=" * 40)

# Run the script
if __name__ == "__main__":
    main()