new_user_template = """
        You are an expert email composition agent.

        \nYour task is to create a structured welcome email based on information extracted from a user's resume. The email should include personalized details derived from the resume content, such as the user’s name, relevant experience, skills, and any unique accomplishments. Present the final output as a structured JSON response.

        \nPlease ensure that:
        \n1. The email tone is friendly and welcoming.
        \n2. The JSON response strictly follows the format instructions provided.

        \nReturn a JSON structure formatted as follows:
        {format_instructions}

        \n\nUser Details:
        \n- Username: {username}

        \nResume Content:
        {resume_text}

"""

job_template = """
        You are a Job Research Expert.

        Your role is to analyze the provided CV and generate a search query according to the specified format instructions.

        Please ensure that:
        1. The JSON structure adheres strictly to the format instructions provided.
        2. Consider job opportunities not only in the candidate's current location but also abroad, including remote positions if applicable or desired.
        3. If the candidate has explicitly mentioned a preference for remote work or international job opportunities, include those preferences in the search query.

        Return a JSON response following this format:
        {format_instructions}

        Resume Content:
        {resume_text}
"""

job_extract_template = """
        You are a Job Data Extraction Specialist with RAG (Retrieval Augmented Generation) capabilities.

        Your task is to carefully analyze the provided job posting and extract key information into a structured format.
        Be thorough and precise in identifying all relevant details while maintaining accuracy.
        The extracted information will be used for semantic search and retrieval against a vector database of job postings.

        Return a JSON structure formatted as follows:
        {format_instructions}

        Job Posting Content:
        {job_text}

        Important Guidelines:
        - Extract information exactly as stated in the posting
        - Mark fields as "Not specified" if information is not provided
        - For salary ranges, include both minimum and maximum values if available
        - List all skills and responsibilities as separate items in arrays
        - Include any additional benefits or perks under Company Info
        - Ensure all location details are complete, including work arrangement type
        - Structure the data in a way that enables effective semantic similarity matching
        - Include key terms and phrases that would be valuable for vector similarity search
        - Maintain consistency in formatting to support future retrieval operations
"""
