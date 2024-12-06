from typing import Dict
import urllib.parse

def get_share_buttons(title: str, url: str) -> str:
    """Generate HTML for social sharing buttons."""
    # URL encode the title and URL for sharing
    encoded_title = urllib.parse.quote(title)
    encoded_url = urllib.parse.quote(url)
    
    return f"""
    <div class="share-buttons">
        <span class="share-text">Share this scholarship:</span>
        <a href="https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}" 
           class="share-button twitter" target="_blank" rel="noopener">
            <img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" alt="Twitter" />
        </a>
        <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}" 
           class="share-button facebook" target="_blank" rel="noopener">
            <img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" alt="Facebook" />
        </a>
        <a href="https://www.linkedin.com/shareArticle?mini=true&url={encoded_url}&title={encoded_title}" 
           class="share-button linkedin" target="_blank" rel="noopener">
            <img src="https://cdn-icons-png.flaticon.com/512/733/733561.png" alt="LinkedIn" />
        </a>
        <a href="https://api.whatsapp.com/send?text={encoded_title}%20{encoded_url}" 
           class="share-button whatsapp" target="_blank" rel="noopener">
            <img src="https://cdn-icons-png.flaticon.com/512/733/733585.png" alt="WhatsApp" />
        </a>
    </div>
    """

def get_scholarship_template(scholarship: Dict[str, str]) -> str:
    """Generate HTML email template for a scholarship."""
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{scholarship['title']}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .scholarship-card {{
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .scholarship-title {{
                color: #1a73e8;
                font-size: 24px;
                margin-bottom: 15px;
                font-weight: bold;
            }}
            .content {{
                margin: 20px 0;
                white-space: pre-line;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                margin: 10px 10px 10px 0;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
                text-align: center;
            }}
            .apply-button {{
                background-color: #1a73e8;
                color: white;
            }}
            .read-more-button {{
                background-color: #f8f9fa;
                color: #1a73e8;
                border: 1px solid #1a73e8;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .share-buttons {{
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
                text-align: center;
            }}
            .share-text {{
                display: block;
                margin-bottom: 10px;
                color: #666;
                font-size: 14px;
            }}
            .share-button {{
                display: inline-block;
                margin: 0 5px;
                padding: 5px;
            }}
            .share-button img {{
                width: 24px;
                height: 24px;
                vertical-align: middle;
            }}
            .footer {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="scholarship-card">
            <h1 class="scholarship-title">{scholarship['title']}</h1>
            
            <div class="content">
                {scholarship['content']}
            </div>
            
            <div class="buttons">
                <a href="{scholarship['application_link']}" class="button apply-button" target="_blank">
                    Apply Now
                </a>
                <a href="{scholarship['link']}" class="button read-more-button" target="_blank">
                    Read More
                </a>
            </div>
            
            {get_share_buttons(scholarship['title'], scholarship['link'])}
            
            <div class="footer">
                <p>This scholarship information was sent to you by SolveByte. If you no longer wish to receive these emails, please unsubscribe.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return template

def get_multiple_scholarships_template(scholarships: list[Dict[str, str]]) -> str:
    """Generate HTML email template for multiple scholarships."""
    
    scholarships_html = ""
    for scholarship in scholarships:
        scholarships_html += f"""
        <div class="scholarship-card">
            <h2 class="scholarship-title">{scholarship['title']}</h2>
            
            <div class="content">
                {scholarship['content']}
            </div>
            
            <div class="buttons">
                <a href="{scholarship['application_link']}" class="button apply-button" target="_blank">
                    Apply Now
                </a>
                <a href="{scholarship['link']}" class="button read-more-button" target="_blank">
                    Read More
                </a>
            </div>
            
            {get_share_buttons(scholarship['title'], scholarship['link'])}
        </div>
        """
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Latest Scholarships</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .scholarship-card {{
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .scholarship-title {{
                color: #1a73e8;
                font-size: 20px;
                margin-bottom: 15px;
                font-weight: bold;
            }}
            .content {{
                margin: 20px 0;
                white-space: pre-line;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 10px 10px 0;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
                text-align: center;
            }}
            .apply-button {{
                background-color: #1a73e8;
                color: white;
            }}
            .read-more-button {{
                background-color: #f8f9fa;
                color: #1a73e8;
                border: 1px solid #1a73e8;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .share-buttons {{
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
                text-align: center;
            }}
            .share-text {{
                display: block;
                margin-bottom: 10px;
                color: #666;
                font-size: 14px;
            }}
            .share-button {{
                display: inline-block;
                margin: 0 5px;
                padding: 5px;
            }}
            .share-button img {{
                width: 24px;
                height: 24px;
                vertical-align: middle;
            }}
            .footer {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1 style="text-align: center; color: #1a73e8; margin-bottom: 30px;">Latest Scholarship Opportunities</h1>
        
        {scholarships_html}
        
        <div class="footer">
            <p>These scholarship opportunities were sent to you by SolveByte. If you no longer wish to receive these emails, please unsubscribe.</p>
        </div>
    </body>
    </html>
    """
    
    return template