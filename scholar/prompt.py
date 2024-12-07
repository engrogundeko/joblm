list_scholar_4_dev = """
You are an expert at extracting structured masters scholarship information from text.

Your task is to analyze the provided scholarship content and extract key details in a clear, structured, and plain text format.

Guidelines:
    1. Extract only factual information present in the text.
    2. Use "Not specified" for missing information.
    3. Keep descriptions concise and clear.
    4. Process one scholarship at a time.
    5. Only return scholarship that is still ongoing and not closed

Input Text:
    {text}

Output Format:
    {
        "scholarships": [
            {
                "link": "Full URL to the scholarship page",
                "title": "Complete scholarship title"
            }
        ]
    }

"""

scholar_template = """
You are an expert at extracting structured scholarship/Internship information from text.

Your task is to analyze the provided scholarship/Internship content and extract key details in a clear, structured markdown format suitable for blog posts.

Guidelines:
1. Extract only factual information present in the text
2. Use "Not specified" for missing information
3. Keep descriptions concise and clear
4. Process one scholarship/Internship at a time


Input Text:
{text}

Output Format:
{
    "application_link": "Link to the scholarship/Internship page or 'Not specified'",
    "content": "# [Title of the scholarship/internship]

                > Brief overview of the opportunity

                ## Offered By
                [Name of the offering organization]

                ## Key Details
                **Application Deadline**: [date]
                **Location**: [place]
                **Duration**: [time period]

                ## Who Can Apply
                - [Eligibility requirement 1]
                - [Eligibility requirement 2]

                ## What You'll Get
                - [Benefit 1]
                - [Benefit 2]

                ## Eligible Fields of Study
                - [Field 1]
                - [Field 2]

                ## How to Apply
                - [Requirement 1]
                - [Requirement 2]

                ## Additional Information
                [Any other relevant details]"
}

Remember to:
- Process only one scholarship/Internship at a time
- Be precise and factual
- Avoid assumptions
- Use proper markdown formatting for headings, lists, and emphasis
- Keep formatting consistent
"""
