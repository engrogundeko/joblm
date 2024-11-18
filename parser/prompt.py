personal_info_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract PERSONAL INFORMATION from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
"""

work_info_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract WORK EXPERIENCE from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
"""

education_info_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract EDUCATION information from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
    """
    
skill_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract SKILLS information from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
        
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
        """
        
project_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract PROJECTS information from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
        
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instructions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
"""

award_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract AWARD INFORMATION from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instructions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
"""

volunteering_template = """
        You are a resume document information extraction expert. 
        Your duty is to extract VOLUNTEERING AND EXTRACURRICULAR ACTIVITIES information
        from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
    """
    
publication_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract PUBLICATION AND RESEARCH from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
"""

interest_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract INTEREST AND PROFESSIONAL SUBMIT information from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
    """
    
professional_template = """
        You are a resume document information extraction expert.  
        Your duty is to extract PROFESSIONAL AFFLILATIONS information from the resume document and present it in a structured JSON format.  
        Identify each relevant section, and provide extracted information according to the specified fields below.  
         
        \nIf any information is missing or labeled differently in the document, return "N/A" for that field.  
        \nIf the session is not found in the resume, return a JSON structure with N/A as values

        \nPlease follow these format instrctions carefully:
        
        \n{format_instructions}\n
        
        Resume Text:
        \n{resume_text}
"""