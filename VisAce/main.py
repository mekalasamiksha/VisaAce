from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import List

app = FastAPI()

# CORS middleware to allow requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing, change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the input model for visa type and country
class VisaDetails(BaseModel):
    visa_type: str
    country: str
    response: List[str]
    
# Example questions based on visa type and country
# questions_db = {
#     "student": {
#         "USA": ["Why do you want to study in the USA?", "What is your chosen major?"],
#         "UK": ["Why did you choose the UK for higher studies?", "Which university are you applying to?"]
#     },
#     "work": {
#         "USA": ["What is your job role?", "How does your work contribute to the company?"],
#         "UK": ["What skills do you bring to the UK?", "Describe your professional experience."]
#     }
# }
questions_db = {
    "student": {
        "USA": [
            "What specific opportunities do you believe studying in the USA will provide for your future career?",
            "How do you plan to cover the cost of tuition and living expenses in the USA, considering the high cost of education?",
            "Can you explain how the American education system aligns with your academic and career objectives?",
            "What challenges do you anticipate in adapting to the diverse cultural environment of the USA?",
            "How do you plan to engage with the local community while studying in the USA?",
            "What unique skills or perspectives do you hope to bring to your university in the USA?",
            "What are your plans for after graduation in the USA, and how do you intend to utilize your degree?"
        ],
        "UK": [
            "What specific aspects of the UK educational system attract you, and how do they align with your goals?",
            "Given the UK's reputation for academic excellence, how do you plan to contribute to your field of study?",
            "How do you intend to manage the financial implications of living and studying in the UK?",
            "What adjustments do you expect to make when integrating into British culture and society?",
            "How do you plan to leverage your UK education to enhance your career opportunities globally?",
            "What connections or networks do you hope to build during your studies in the UK?",
            "What is your long-term vision for your career after completing your studies in the UK?"
        ],
        "CANADA": [
            "Why do you believe studying in Canada will enhance your professional qualifications?",
            "How do you plan to fund your education and living expenses in Canada, and what resources will you utilize?",
            "What do you find appealing about the Canadian approach to education and cultural diversity?",
            "How will you adapt to the climate and social environment in Canada?",
            "What role do you see yourself playing in the Canadian community while studying?",
            "What are your career aspirations in Canada post-graduation, and how do you plan to achieve them?",
            "How do you envision your Canadian education impacting your home country upon your return?"
        ],
        "AUSTRALIA": [
            "What makes Australia an attractive destination for your studies compared to other countries?",
            "How will you finance your education in Australia, considering both tuition and living expenses?",
            "What are your expectations regarding the Australian educational experience and teaching styles?",
            "How do you plan to immerse yourself in the local culture and community in Australia?",
            "What specific skills do you hope to gain from your studies in Australia, and how will they benefit you?",
            "How will you navigate the unique challenges posed by studying in a different country?",
            "What are your plans for employment in Australia after you complete your studies?"
        ],
        "GERMANY": [
            "What draws you to Germany's educational system, particularly its emphasis on research and innovation?",
            "How do you plan to finance your education, given the living costs in Germany?",
            "What is your understanding of the German approach to higher education, and how does it benefit you?",
            "How do you anticipate overcoming language barriers and cultural differences while studying?",
            "What role do you expect to play in your university community in Germany?",
            "What are your long-term career goals in Germany or your home country after your studies?",
            "How do you plan to leverage Germany's strong job market in your field after graduation?"
        ],
        "FRANCE": [
            "Why is studying in France important for your academic and career ambitions?",
            "How will you finance your studies in France, and what support do you have in place?",
            "What specific cultural aspects of France do you find most intriguing and how do you plan to engage with them?",
            "How do you plan to adapt to the French education system and its expectations?",
            "What opportunities do you see in France for your field of study, and how will you take advantage of them?",
            "How do you intend to build relationships with local students and professionals in France?",
            "What are your future plans after completing your studies in France, both in France and back home?"
        ],
        "NEW ZEALAND": [
            "What unique opportunities do you see in studying in New Zealand that you can't find elsewhere?",
            "How do you plan to manage the financial aspects of studying in New Zealand, considering the costs?",
            "What do you know about New Zealand's education system, and how do you think it will benefit you?",
            "How do you plan to immerse yourself in the Kiwi culture while studying?",
            "What are your long-term career aspirations in New Zealand after your studies?",
            "How do you foresee your education in New Zealand impacting your career path?",
            "What skills do you hope to develop during your studies in New Zealand, and how will they help you contribute to society?"
        ]
    },
    "work": {
        "USA": [
            "What specific skills do you bring to the American workplace, and how will they contribute to your employer's goals?",
            "What steps have you taken to secure this job opportunity in the USA, and what challenges did you face?",
            "How do you plan to adapt to the fast-paced and diverse work culture in the USA?",
            "What are your long-term career goals while working in the USA, and how do you plan to achieve them?",
            "How will your role in the organization help you engage with the local community in the USA?",
            "What strategies will you use to network and build professional relationships in the USA?",
            "How do you intend to maintain a healthy work-life balance in the American work environment?"
        ],
        "UK": [
            "What unique contributions do you plan to bring to your workplace in the UK?",
            "What challenges did you face in securing your job in the UK, and how did you overcome them?",
            "How do you plan to navigate the professional expectations and culture in the UK?",
            "What are your long-term career aspirations while working in the UK, and what steps will you take to achieve them?",
            "How do you plan to integrate into the local community while working in the UK?",
            "What networking strategies will you employ to establish connections in the UK?",
            "How do you plan to adapt to the work-life balance in the UK?"
        ],
        "CANADA": [
            "What skills do you possess that are particularly relevant to the Canadian job market?",
            "How did you secure this job opportunity in Canada, and what challenges did you face?",
            "What are your plans for adapting to the Canadian work culture and environment?",
            "How will your work contribute to the local community and economy in Canada?",
            "What are your long-term career goals while working in Canada, and how do you plan to achieve them?",
            "How do you plan to establish a professional network in Canada?",
            "What strategies will you use to maintain a work-life balance in Canada?"
        ],
        "AUSTRALIA": [
            "What specific skills do you bring to the Australian job market, and how will they benefit your employer?",
            "What challenges did you encounter in securing this job offer in Australia, and how did you overcome them?",
            "How do you plan to adapt to the Australian workplace culture?",
            "What contributions do you see yourself making to the local economy while working in Australia?",
            "What are your long-term career aspirations while working in Australia?",
            "How do you plan to build professional relationships in Australia?",
            "What strategies will you use to maintain a balance between work and leisure in Australia?"
        ],
        "GERMANY": [
            "What makes you a suitable candidate for the role you are applying for in Germany?",
            "What steps did you take to secure your job in Germany, and what challenges did you face?",
            "How do you plan to navigate the professional landscape and cultural nuances in Germany?",
            "What specific contributions do you believe your skills will bring to your organization in Germany?",
            "What are your long-term career goals while working in Germany?",
            "How do you plan to engage with the local professional community in Germany?",
            "What strategies will you employ to ensure compliance with German labor laws?"
        ],
        "France": [
            "How does your professional experience align with the expectations of the French job market?",
            "What steps did you take to secure this job opportunity in France, and what challenges did you face?",
            "How do you plan to adapt to the work culture and expectations in France?",
            "What unique contributions do you envision making to your workplace in France?",
            "What are your long-term career aspirations while working in France?",
            "How do you plan to network and build professional relationships in France?",
            "What strategies will you use to navigate any language barriers in the workplace?"
        ],
        "NEW ZEALAND": [
            "What specific skills do you bring to the New Zealand job market, and how will they contribute to your employer's goals?",
            "How did you secure your job in New Zealand, and what challenges did you face during the process?",
            "How do you plan to adapt to the work culture and expectations in New Zealand?",
            "What contributions do you foresee making to the local community while working in New Zealand?",
            "What are your long-term career goals while working in New Zealand, and how do you plan to achieve them?",
            "How do you plan to build professional relationships in New Zealand?",
            "What strategies will you use to maintain a work-life balance in New Zealand?"
        ]
    }
}

# Route to accept visa details and return questions
@app.post("/questions/") 
def get_questions(visa_details: VisaDetails):
    visa_type = visa_details.visa_type.lower()
    country = visa_details.country.upper()

    # Fetch questions from database or use default questions if not found
    questions = questions_db.get(visa_type, {}).get(country, ["What is your purpose for visiting?", "How long do you plan to stay?"])
    return {"questions": questions}

# @app.post("/feedback/")
# def get_feedback(visa_details: VisaDetails):
#     visa_type = visa_details.visa_type.lower()
#     country = visa_details.country.upper()
#     response = visa_details.response
        
#         # Constructing the initial prompt for the Gemini API
#     prompt = (
#         "You are an AI evaluating responses in a visa mock interview. "
#         "The applicant is applying for a " + visa_type + " visa to " + country + ". "
#         "They provided the following responses during the interview:\n"
#     )

#     # Adding user responses to the prompt
#     prompt += "\n".join([f"Q{index + 1}: {resp}" for index, resp in enumerate(response)])

#     # Adding analysis criteria and instructions
#     prompt += (
#         "\n\nAnalyze the applicant's answers based on the following criteria:\n"
#         "1. Clarity: Is the response clear and easy to understand?\n"
#         "2. Relevance: Does the response directly address the question asked?\n"
#         "3. Persuasiveness: Does the response help the applicant's case for obtaining the visa?\n"
#         "4. Improvement Suggestions: Provide advice on how the applicant can improve their answers to increase their chances of visa approval.\n\n"
#         "Give feedback on each response in a structured format:\n"
#         "- Response to Question 1:\n  - Clarity:\n  - Relevance:\n  - Persuasiveness:\n  - Improvement Suggestions:\n"
#         "- Response to Question 2:\n  - Clarity:\n  - Relevance:\n  - Persuasiveness:\n  - Improvement Suggestions:\n"
#         # Continue this pattern for all questions
#         "Please provide detailed feedback for each response."
#     )

    
#     genai.configure(api_key=os.environ["API_KEY"])
    
#     # Call the Gemini API to generate feedback
#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         result = model.generate_content(prompt)
#         feedback = result.text
#         print(result)
#         return {"feedback": feedback}
#     except Exception as e:
#         return {"error": f"An error occurred: {str(e)}"}

import openai  # Make sure this library is installed
@app.post("/feedback/")
def get_feedback(visa_details: VisaDetails):
    visa_type = visa_details.visa_type.lower()
    country = visa_details.country.upper()
    response = visa_details.response

    # Constructing the initial prompt for the OpenAI API
    prompt = (
        "You are an AI evaluating responses in a visa mock interview. "
        "The applicant is applying for a " + visa_type + " visa to " + country + ". "
        "They provided the following responses during the interview:\n"
    )

    # Adding user responses to the prompt
    prompt += "\n".join([f"Q{index + 1}: {resp}" for index, resp in enumerate(response)])

    # Adding analysis criteria and instructions
    prompt += (
        "\n\nAnalyze the applicant's answers based on the following criteria:\n"
        "1. Clarity: Is the response clear and easy to understand?\n"
        "2. Relevance: Does the response directly address the question asked?\n"
        "3. Persuasiveness: Does the response help the applicant's case for obtaining the visa?\n"
        "4. Improvement Suggestions: Provide advice on how the applicant can improve their answers to increase their chances of visa approval.\n\n"
        "Give feedback on each response in a structured format:\n"
        "- Response to Question 1:\n  - Clarity:\n  - Relevance:\n  - Persuasiveness:\n  - Improvement Suggestions:\n"
        "- Response to Question 2:\n  - Clarity:\n  - Relevance:\n  - Persuasiveness:\n  - Improvement Suggestions:\n"
        "Please provide detailed feedback for each response."
    )

    # Configure the OpenAI API with the API key
    # openai.api_key = os.environ.get("OPENAI_API_KEY")
    openai.api_key="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"

    # Call the OpenAI API to generate feedback
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the appropriate engine/model
            prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )
        
        feedback = response.choices[0].text.strip()
        return {"feedback": feedback}
    # except Exception as e:
    #     return {"error": f"An error occurred: {str(e)}"}
    except openai.error.OpenAIError as e:
        # This will catch any errors related to OpenAI API
        print("OpenAI API error:", e)
        return {"error": f"An error occurred: {str(e)}"}
    
    except Exception as e:
        # This will catch any unexpected errors
        print("Unexpected error:", e)
        return {"error": f"An unexpected error occurred: {str(e)}"}