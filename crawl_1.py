from bs4 import BeautifulSoup

# Mở và đọc file HTML
with open('part1.txt', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Lấy tất cả các phần tử cần crawl theo class
audio_sources = soup.find_all('div', class_='context-content context-audio')
images = soup.find_all('div', class_='context-content context-image')
transcripts = soup.find_all('div', class_='context-content context-transcript text-highlightable')
question_wrappers = soup.find_all('div', class_='question-wrapper')
explain_wrappers = soup.find_all('div', class_='question-explanation-wrapper')


# Kiểm tra dữ liệu đã lấy được
print(f'Audio sources found: {len(audio_sources)}')
print(f'Image sources found: {len(images)}')
print(f'Transcripts found: {len(transcripts)}')

TOEIC_PARTS = {
    'Part1': {
        'questionPerGroup': 1,  # Số câu hỏi trong mỗi nhóm
        'answerCount': 4  # Số lượng đáp án mỗi câu
    }
}
# Tạo danh sách để lưu dữ liệu dưới dạng đối tượng
data = []

# In chi tiết từng phần tử HTML và lưu vào object
for audio_div, image_div, transcript_div, question_wrapper in zip(audio_sources, images, transcripts, question_wrappers):
    # Khởi tạo đối tượng cho từng phần tử
    obj = {'audio': '', 'image': [], 'transcript': '' , 'questionData' : []}

    # In chi tiết audio sources
    audio_tag = audio_div.find('audio')
    if audio_tag:
        audio_source = audio_tag.find('source')
        if audio_source:
            obj['audio'] = audio_source.get('src')
        else:
            obj['audio'] = 'No audio source found'
    else:
        obj['audio'] = 'No audio tag found'

    # Lấy thông tin image
    image_tags = image_div.find_all('img')
    for index, image_tag in enumerate(image_tags):
        image_obj = {}
        if image_tag:
            image_obj['img'] = image_tag.get('data-src') if 'data-src' in image_tag.attrs else image_tag.get('src')
            image_obj['index'] = index
            obj['image'].append(image_obj)
        else:
            obj['image'].append({'img': 'No image tag found', 'index': index})

    # In chi tiết transcripts
    collapse_div = transcript_div.find('div', class_='collapse')
    if collapse_div:
        transcript_html = collapse_div.decode_contents()  # Lấy nội dung bên trong
        obj['transcript'] = transcript_html
    else:
        obj['transcript'] = 'No transcript content found'

    # Lấy thông tin questionNumber và explain cùng một lần
    question_number_tag = question_wrapper.find('div', class_='question-number')
    explanation_wrapper = question_wrapper.find('div', class_='question-explanation-wrapper')

    if question_number_tag:
        question_number = question_number_tag.find('strong').text.strip()

        # Lấy phần giải thích nếu có
        explanation_text = ''
        if explanation_wrapper:
            explanation_div = explanation_wrapper.find('div', class_='collapse')
            if explanation_div:
                explanation_text = '\n'.join(explanation_div.stripped_strings)

        # Tạo mảng questionData với cả questionNumber và explain cùng một lần
        obj['questionData'] = [
            {
                'questionNumber': question_number,
                'question': '',  # Bạn có thể thêm nội dung câu hỏi nếu có
                'explain': explanation_text,  # Gán giải thích vào đây
                'answer': ['A.', 'B.', 'C.', 'D.'],  # Mảng đáp án với 4 phần tử
                'correctAnswer': ''  # Đáp án đúng sẽ được thêm sau
            }
            for _ in range(TOEIC_PARTS['Part1']['questionPerGroup'])  # Lặp theo số câu hỏi
        ]

        # Lấy thông tin đáp án từ các form-check divs
        answers_div = question_wrapper.find_all('div', class_='form-check')
        max_answers = min(len(answers_div), TOEIC_PARTS['Part1']['answerCount'])  # Giới hạn số đáp án

        for i in range(max_answers):  # Chỉ lặp trong giới hạn số đáp án
            answer_div = answers_div[i]
            input_tag = answer_div.find('input')
            answer_label = answer_div.find('label')

            # Lấy giá trị đáp án (A, B, C, D)
            if input_tag and answer_label:
                answer_value = input_tag.get('value')
                answer_text = answer_label.text.strip()

                # Lưu đáp án vào mảng answer trong questionData
                for question in obj['questionData']:
                    question['answer'][i] = f"{answer_text}"

                # Kiểm tra nếu đáp án đúng (class="correct")
                if input_tag.has_attr('class') and 'correct' in input_tag['class']:
                    for question in obj['questionData']:
                        question['correctAnswer'] = answer_value  # Lưu đáp án đúng
    else:
        obj['questionData'] = []

    # Thêm object vào danh sách dữ liệu
    data.append(obj)

# In kết quả dữ liệu đã được lưu vào object
print("\nIn dữ liệu đã lưu vào object:")
# for item in data:
#     print(f"Audio: {item['audio']}")
#     print(f"Image: {item['image']}")
#     print(f"Transcript: {item['transcript']}")
#     print("\n---")
print(data)
print("\nCrawl hoàn thành.")
