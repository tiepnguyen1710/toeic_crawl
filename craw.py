import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
import re

def extract_question_number(text):
    """Extract numeric question number from text."""
    if not text:
        return None
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None

def process_question(question, context_wrapper=None, group_images=None, processed_questions={}):
    """Process individual question and return data dictionary."""
    # Get question number
    question_number_tag = question.find("div", class_="question-number")
    question_number = extract_question_number(question_number_tag.text.strip() if question_number_tag else None)
    
    if not question_number:
        logger.warning(f"Could not extract question number from {question_number_tag.text if question_number_tag else 'None'}")
        return None

    # Avoid processing the same question number again (track the most recent one)
    if question_number in processed_questions:
        logger.info(f"Overwriting previous data for question number: {question_number}")

    # Get question text
    question_text_tag = question.find("div", class_="question-text")
    question_text = question_text_tag.text.strip() if question_text_tag else None

    # Initialize Paragraph as None
    paragraph = None

    if 131 <= question_number <= 146:
        paragraph_wrapper = question.find_previous("div", class_="context-content text-highlightable")
        
        if paragraph_wrapper:
            paragraph_text = paragraph_wrapper.get_text(strip=True)
            paragraph = paragraph_text
        else:
            print("No paragraph wrapper found.")

    transcript = None

    if context_wrapper:
        transcript_div = context_wrapper.find("div", class_="collapse show")
        if transcript_div:
            transcript = transcript_div.text.strip()

    parent_wrapper = question.find_parent("div", class_="question-group-wrapper")

    # Search only within the parent wrapper for transcripts
    if parent_wrapper:
        group_transcript_div = parent_wrapper.find("div", class_="context-content context-transcript text-highlightable")
        if group_transcript_div:
            collapse_div = group_transcript_div.find("div", class_="collapse show")
            if collapse_div:
                transcript = collapse_div.text.strip()

    # Extract images
    images = group_images if group_images else []
    if context_wrapper and not images:
        img_tags = context_wrapper.find_all("img")
        images = [img["data-src"] for img in img_tags if "data-src" in img.attrs]

    # Get answers
    answers = []
    answer_tags = question.find_all("div", class_="form-check")
    for tag in answer_tags:
        label = tag.find("label")
        if label:
            answers.append(label.text.strip())

    # Get correct answer
    correct_answer = question.find("div", class_="mt-2 text-success")
    correct_answer = correct_answer.text.strip().replace("Đáp án đúng:", "").strip() if correct_answer else None

    # Get answer explanations
    explanation_wrapper = question.find_next("div", class_="question-explanation-wrapper")
    explanations = []
    if explanation_wrapper:
        collapse_div = explanation_wrapper.find("div", class_="collapse show")
        if collapse_div:
            paragraphs = collapse_div.find_all("p")
            for p in paragraphs:
                explanations.append(p.text.strip())

    # Combine explanations into a single string for CSV export
    explanation_text = " | ".join(explanations) if explanations else None

    # Create the question data dictionary
    question_data = {
        "Question Number": question_number,
        "Question Text": question_text,
        "Paragraph": paragraph,  # Add Paragraph here, only for 131-146
        "Transcript": transcript,  # This will always have a value (default: "No transcript")
        "Answers": answers,
        "Right Answer": correct_answer,
        "Answers Translation": explanation_text,  # Append explanation content here
        "Images": images if images else None
    }

    # Update the dictionary with the latest data for the same question number
    processed_questions[question_number] = question_data

    return question_data



def main():
    # Load the HTML file
    name = input("Enter name of the html file: ")
    
    with open(f"{name}.html", "r", encoding="utf-8") as file:
        content = file.read()

    logger.info(f"Starting crawl {name}...")

    soup = BeautifulSoup(content, "html.parser")
    data = []
    processed_questions = {}

    try:
        # Process standalone questions
        for question in soup.find_all("div", class_="question-wrapper"):
            context_wrapper = question.find_previous("div", class_="context-wrapper")
            process_question(question, context_wrapper, processed_questions=processed_questions)

        # Process question groups
        for group in soup.find_all("div", class_="question-group-wrapper"):
            # Extract images from the group first
            img_tags = group.find_all("img")
            group_images = [img["data-src"] for img in img_tags if "data-src" in img.attrs]

            for question in group.find_all("div", class_="question-wrapper"):
                context_wrapper = question.find_previous("div", class_="context-wrapper")
                process_question(question, context_wrapper, group_images=group_images, processed_questions=processed_questions)

        data = list(processed_questions.values())

        df = pd.DataFrame(data)
        df = df.replace({"": None, "[]": None})

        # Sort by question number
        df["Question Number"] = pd.to_numeric(df["Question Number"])
        df = df.sort_values("Question Number")

        # Log statistics and potential issues
        logger.info(f"Total questions processed: {len(processed_questions)}")
        logger.info(f"Question number range: {min(processed_questions)} to {max(processed_questions)}")

        # Save to CSV
        df.to_csv(f"{name}_df.csv", index=False, encoding="utf-8")
        logger.success(f"Saved successfully {name}_df.csv")

    except Exception as e:
        logger.error(f"The process failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
