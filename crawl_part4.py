from bs4 import BeautifulSoup

# Mở và đọc file HTML
with open('part4.txt', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Lấy tất cả các phần tử cần crawl theo class
audio_sources = soup.find_all('div', class_='context-content context-audio')
#images = soup.find_all('div', class_='context-content context-image')
transcripts = soup.find_all('div', class_='context-content context-transcript text-highlightable')
question_wrappers = soup.find_all('div', class_='question-wrapper')
explain_wrappers = soup.find_all('div', class_='question-explanation-wrapper')


# Kiểm tra dữ liệu đã lấy được
print(f'Audio sources found: {len(audio_sources)}')
#print(f'Image sources found: {len(images)}')
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
for i, (audio_div, transcript_div) in enumerate(zip(audio_sources,  transcripts)):
    #print(f"i = {i}, audio_div = {audio_div}, image_div = {image_div}, transcript_div = {transcript_div}")
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
    # image_tags = image_div.find_all('img')
    # for index, image_tag in enumerate(image_tags):
    #     image_obj = {}
    #     if image_tag:
    #         image_obj['img'] = image_tag.get('data-src') if 'data-src' in image_tag.attrs else image_tag.get('src')
    #         image_obj['index'] = index
    #         obj['image'].append(image_obj)
    #     else:
    #         obj['image'].append({'img': 'No image tag found', 'index': index})

    # In chi tiết transcripts
    collapse_div = transcript_div.find('div', class_='collapse')
    if collapse_div:
        transcript_html = collapse_div.decode_contents()  # Lấy nội dung bên trong
        obj['transcript'] = transcript_html
    else:
        obj['transcript'] = 'No transcript content found'

    # Duyệt qua từng question_wrapper và lấy thông tin cho từng câu hỏi
    for j in range(3):
        question_index = i * 3 + j  # Tính chỉ số câu hỏi trong toàn bộ danh sách
        print(question_index)
        if question_index < len(question_wrappers):
            question_wrapper = question_wrappers[question_index]
            question_data = {}

            # Lấy thông tin questionNumber từ question-wrapper
            question_number_tag = question_wrapper.find('div', class_='question-number')
            if question_number_tag:
                question_data['questionNumber'] = int(question_number_tag.find('strong').text.strip())

            question_content = question_wrapper.find('div', class_='question-content text-highlightable')
            if question_content:
                question_text = question_content.find('div', class_='question-text')
                if question_text: 
                    question = question_text.text.strip()
                    question_data['question'] = question

            # Lấy phần giải thích từ question-explanation-wrapper
            explanation_wrapper = question_wrapper.find_next('div', class_='question-explanation-wrapper')
            if explanation_wrapper:
                collapse_div = explanation_wrapper.find('div', class_='collapse')
                if collapse_div:
                    explain_html = collapse_div.decode_contents()  # Lấy nội dung giải thích
                    question_data['explain'] = explain_html

        # Lấy thông tin câu hỏi (nếu có) và đáp án
        #question_data['question'] = ''  # Bạn có thể thêm nội dung câu hỏi nếu có
        question_data['answer'] = ['Statement A.', 'Statement B.', 'Statement C.', 'Statement C.']  # Mảng đáp án với 4 phần tử
        question_data['correctAnswer'] = ''  # Đáp án đúng sẽ được thêm sau

        # Lấy thông tin đáp án từ các form-check divs
        answers_div = question_wrapper.find_all('div', class_='form-check')
        max_answers = min(len(answers_div), TOEIC_PARTS['Part1']['answerCount'])  # Giới hạn số đáp án
        correct_div = question_wrapper.find('div', class_='mt-2 text-success')

        if correct_div:
            correct_answer_text = correct_div.text.strip().split(":")[-1].strip()  # Lấy phần đáp án từ 'Đáp án đúng: B'
        else:
            correct_answer_text = None  # Nếu không tìm thấy, gán giá trị None

        for k in range(max_answers):  # Chỉ lặp trong giới hạn số đáp án
            answer_div = answers_div[k]
            input_tag = answer_div.find('input')
            answer_label = answer_div.find('label')

            # Lấy giá trị đáp án (A, B, C, D)
            if input_tag and answer_label:
                answer_value = input_tag.get('value')
                answer_text = answer_label.text.strip()[3:]

                # Lưu đáp án vào mảng answer trong questionData
                question_data['answer'][k] = f"{answer_text}"

                if correct_answer_text and correct_answer_text == answer_value:
                     question_data['correctAnswer'] = answer_text 

        # Thêm câu hỏi vào mảng questionData
        obj['questionData'].append(question_data)
       

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
