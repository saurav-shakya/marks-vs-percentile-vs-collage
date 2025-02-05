import google.generativeai as genai
import os
import json
import numpy as np

def setup_gemini():
    """Setup Gemini API with the provided API key"""
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def analyze_percentile(marks, historical_data):
    """Analyze percentile using Gemini 2.0 Flash"""
    try:
        # Calculate basic statistics
        marks = float(marks)
        historical_marks = historical_data['marks'].values
        total_students = len(historical_marks)
        students_below = np.sum(historical_marks < marks)
        rank = total_students - students_below

        # Calculate percentile
        percentile = (students_below / total_students) * 100
        percentile = min(99.99, max(0, percentile))

        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Prepare statistics for analysis
        data_summary = historical_data.describe().to_string()

        prompt = f"""
        As a JEE Main expert, analyze this student's performance:

        Student's Marks: {marks}/300
        Total Students in Dataset: {total_students}
        Student's Rank: {rank}
        Calculated Percentile: {percentile:.2f}

        Statistical Summary:
        {data_summary}

        Provide a detailed analysis of the student's performance.
        Follow this format strictly for response:
        {{
            "percentile": {percentile:.2f},
            "analysis": "<detailed_analysis_of_performance>",
            "comparative_stats": {{
                "above_average": <true/false based on if marks are above mean>,
                "relative_position": "<clear_description_of_rank_position>"
            }}
        }}
        """

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.9,
                top_k=40
            )
        )

        # Parse and validate the response
        try:
            result = json.loads(response.text)
            if 'percentile' in result:
                result['percentile'] = min(99.99, max(0, float(result['percentile'])))
                result['percentile'] = round(result['percentile'], 2)
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            # Return basic analysis if JSON parsing fails
            return {
                "percentile": round(percentile, 2),
                "analysis": "Analysis based on historical data comparison",
                "comparative_stats": {
                    "above_average": marks > np.mean(historical_marks),
                    "relative_position": f"Rank {rank} out of {total_students}"
                }
            }

    except Exception as e:
        print(f"Error in analyze_percentile: {str(e)}")
        return None

def get_study_suggestions(marks, percentile):
    """Get personalized study suggestions using Gemini 2.0 Flash"""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = f"""
    As a JEE Main expert counselor, analyze the student's performance and provide detailed guidance:
    Student Details:
    - Marks: {marks}/300
    - Current Percentile: {percentile}

    Provide a structured response in the following format:
    1. Performance Analysis
    2. Key Focus Areas (list 3-4 subjects/topics)
    3. Study Strategy
    4. Time Management Tips
    5. Quick Practice Questions (2-3 questions)

    Keep each section concise and actionable.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_flash_cards(topic):
    """Generate study flash cards using Gemini 2.0"""
    # Using Gemini 2.0 model
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Create 5 expert-level flash cards for JEE Main preparation on: {topic}

    Requirements:
    1. Make cards progressively harder (from basic to advanced)
    2. Include visual descriptions where applicable
    3. Add mnemonics or memory tricks
    4. Include real JEE exam context

    Format each card as a JSON object with:
    {{
        "front": "Detailed question or concept",
        "back": "Comprehensive explanation with step-by-step solution",
        "tips": "Memory tricks, shortcuts, and common pitfalls to avoid",
        "difficulty": "basic/intermediate/advanced",
        "related_topics": ["List", "of", "related", "concepts"]
    }}

    Return as a JSON array of 5 cards.
    """

    safety_config = genai.types.SafetySettingDict(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_NONE"
    )

    try:
        response = model.generate_content(
            prompt,
            safety_settings=[safety_config],
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating flash cards: {e}")
        return []

def analyze_college_fit(percentile, college_data):
    """Analyze and suggest best-fit colleges based on percentile"""
    model = genai.GenerativeModel('gemini-pro')
    colleges_str = "\n".join([
        f"- {row['college_name']} ({row['branch']}): {row['cutoff_general']} percentile"
        for _, row in college_data.iterrows()
    ])

    prompt = f"""
    As a college counselor, analyze these colleges for a student with {percentile} percentile:

    {colleges_str}

    Provide a detailed analysis in this format:
    1. Safe Choices (2-3 colleges)
    2. Target Colleges (2-3 colleges)
    3. Reach Colleges (1-2 colleges)
    4. Branch-specific recommendations
    5. Location considerations
    6. Future prospects

    Keep the analysis data-driven and actionable.
    """
    response = model.generate_content(prompt)
    return response.text

def summarize_content(text, context=""):
    """Summarize content with specific context"""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Summarize this JEE preparation content. Context: {context}

    Content:
    {text[:5000]}  # Limit text length

    Provide a structured summary with:
    1. Key Points (3-4 bullet points)
    2. Important Formulas/Concepts
    3. Practice Tips
    4. Common Mistakes to Avoid
    """
    response = model.generate_content(prompt)
    return response.text