import os
import google.generativeai as genai
import json
import logging

# Configure the Gemini API with the key from your .env file
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("!!! GEMINI API KEY NOT FOUND IN .env FILE !!!")
    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"!!! FAILED TO CONFIGURE GEMINI API: {e} !!!")
    logging.error(f"Failed to configure Gemini API: {e}")

def generate_mcqs_from_topics(topics: list, questions_per_topic: int = 3) -> list:
    all_mcqs = []
    
    json_format_instructions = """
    [
        {
            "question": "The question text",
            "options": ["Option A", "Option B", "Option C", "Option D", "Option E", "Option F", "Option G", "Option H"],
            "correct_answer": "The text of the correct option"
        }
    ]
    """

    prompt = f"""
    You are an expert quiz creator. Based on the list of topics provided below, generate exactly {questions_per_topic} unique multiple-choice questions for EACH topic.
    Each question must have exactly 8 options, and one of them must be the correct answer.
    
    IMPORTANT: Your entire response must be a single, valid JSON array containing all the generated questions. Do not include any text or explanations outside of the JSON array.
    Follow this JSON structure for each question:
    {json_format_instructions}

    Here are the topics:
    {', '.join(topics)}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        json_response_text = response.text.strip().replace("```json", "").replace("```", "")
        generated_questions = json.loads(json_response_text)
        
        for i, mcq in enumerate(generated_questions):
            topic_index = i // questions_per_topic
            if topic_index < len(topics):
                mcq['topic'] = topics[topic_index]
            else:
                mcq['topic'] = "General Knowledge"
            all_mcqs.append(mcq)

    except Exception as e:
        logging.error(f"Error generating MCQs with Gemini API: {e}")
        return []
        
    return all_mcqs
