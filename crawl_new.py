from bs4 import BeautifulSoup

# Mở và đọc file HTML
with open('number1.txt', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Lấy tất cả các phần tử cần crawl theo class
audio_sources = soup.find_all('div', class_='context-content context-audio')
images = soup.find_all('div', class_='context-content context-image')
transcripts = soup.find_all('div', class_='context-content context-transcript text-highlightable')
numbers = soup.find_all('div', class_='question-number')
# Kiểm tra dữ liệu đã lấy được
print(f'Audio sources found: {len(audio_sources)}')
print(f'Image sources found: {len(images)}')
print(f'Transcripts found: {len(transcripts)}')

# In chi tiết từng phần tử HTML
print("\nIn chi tiết audio sources:")
for audio_div in audio_sources:
    # Tìm thẻ <audio> trong mỗi thẻ <div>
    audio_tag = audio_div.find('audio')
    if audio_tag:
        # Lấy URL từ thẻ <source>
        audio_source = audio_tag.find('source')
        if audio_source:
            audio_url = audio_source.get('src')
            print(f'Audio URL: {audio_url}')
        else:
            print('No audio source found')
    else:
        print('No audio tag found')

print("\nIn chi tiết image sources:")
for image_div in images:
    # Tìm thẻ <img> trong mỗi thẻ <div>
    image_tag = image_div.find('img')
    if image_tag:
        # Lấy URL từ thuộc tính data-src hoặc src
        image_url = image_tag.get('data-src') if 'data-src' in image_tag.attrs else image_tag.get('src')
        print(f'Image URL: {image_url}')
    else:
        print('No image tag found')

print("\nIn chi tiết transcripts:")
for transcript_div in transcripts:
    # Tìm thẻ <div> có class 'collapse' trong mỗi thẻ transcript
    collapse_div = transcript_div.find('div', class_='collapse')
    if collapse_div:
        # Lấy nội dung bên trong thẻ <div class="collapse"> mà không lấy thẻ <div> itself
        transcript_html = collapse_div.decode_contents()  # Lấy nội dung bên trong
        print(f'Transcript HTML: \n{transcript_html}')
    else:
        print('No transcript content found')
for number in numbers: 
   
    question_number = number.find('strong')
    if question_number:
        print(f'Question Number: {question_number.text}')
    else:
        print('No strong tag found inside question number div')


print("\nCrawl hoàn thành.")
