# PhishQuiz Backend Updated - Session Redirects, Wallet Login, Tracking, High Score Logic

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import uuid
import re
import random as r
import os
from dotenv import load_dotenv
from utils import context_generator, blockchain_stuff
import uvicorn

load_dotenv() # Load environment variables

app = FastAPI()
api_key = os.getenv("HUGGING_FACE_TOKEN")
##################### FASTAPI MOUNTS ###################################
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
app.mount("/static", StaticFiles(directory="static"), name="static")
########################################################################

class EmailGenerated(BaseModel):
    id: str
    content: str
    is_phishing: bool

class UserSubmission(BaseModel):
    email_id: str
    is_phishing_guess: bool
    highlights: list[str]
    session_id: str

class Score(BaseModel):
    correct: bool
    points_earned: int
    feedback: str
    
class EndGame(BaseModel):
    session_id: str
    errors: int
    seconds_taken: int
    

##################### STATES FOR APPLICATION ############################
EMAILS = {}
USER_SESSIONS = {}
USER_SCORES = {}
USER_PROGRESS = {}  


###################### PAGE LOGIC ####################################
@app.get("/", response_class=FileResponse)
def serve_home():
    return FileResponse("pages/index.html")

@app.get("/dashboard")
def serve_dashboard(session_id: str = ""):
    if not session_id or session_id not in USER_SESSIONS:
        return RedirectResponse("/")
    
    return FileResponse("pages/user-dashboard.html")

@app.get("/quiz_question")
def serve_quiz(session_id: str = ""):
    if not session_id or session_id not in USER_SESSIONS:
        return RedirectResponse("/")
    
    return FileResponse("pages/quiz-page.html")

###################### GAME LOGIC ####################################
@app.post("/generate_email", response_model=EmailGenerated)
def generate_email():    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"  
    headers = {"Authorization": f"Bearer {api_key}"}
    
    ctx = context_generator.generate_context()
    
    chance = r.randint(0,1)
    fraud = False
    
    if chance == 1:
        fraud = True

    # Create a list of random names for sender and recipient
    first_names = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Jamie", "Riley", "Quinn", "Avery"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
    
    sender_first_name = r.choice(first_names)
    sender_last_name = r.choice(last_names)
    recipient_first_name = r.choice(first_names)
    recipient_last_name = r.choice(last_names)
    
    # Generate a realistic current date
    from datetime import datetime, timedelta
    
    # Generate a date within the last 3 days for realism
    random_days = r.randint(0, 3)
    email_date = (datetime.now() - timedelta(days=random_days)).strftime("%A, %B %d, %Y")
    
    # Generate realistic domains for phishing
    company_domain = ctx.user_email.split('@')[1]
    real_domain = company_domain
    company_name_simple = ctx.company_name.lower().replace(" ", "")
    
    phishing_domains = [
        f"{company_name_simple}-secure.com",
        f"{company_name_simple}.co" if not company_name_simple.endswith(".co") else f"{company_name_simple}s.net",
        f"{company_name_simple}-verify.net",
        f"secure-{company_name_simple}.com",
        f"{real_domain.replace('.', '-')}.com",
        f"{real_domain}s.net"
    ]
    phishing_domain = r.choice(phishing_domains)
    
    # Generate job titles
    job_titles = [
        "IT Specialist", "Systems Administrator", "Network Engineer", "Security Analyst",
        "IT Manager", "CTO", "Support Specialist", "Technical Lead", "Project Manager",
        "HR Manager", "Financial Analyst", "Marketing Director", "Operations Manager"
    ]
    sender_title = r.choice(job_titles)
    
    # Generate departments
    departments = [
        "IT Department", "Information Security", "Human Resources", "Finance", 
        "Operations", "Technical Support", "Customer Service", "Marketing"
    ]
    sender_department = r.choice(departments)
    
    # Example email
    example_email = """From: Sam Smith <sam.smith@microsynth.tech>
To: Casey Johnson <casey.johnson@microsynth.tech>
Date: Thursday, April 10, 2025
Subject: IT Policy Change

Dear Casey,

I hope this email finds you well. As you are aware, MicroSynth is committed to maintaining a secure and compliant IT environment. As part of our ongoing efforts, we have recently reviewed our IT policies and procedures and identified areas for improvement.

We are pleased to inform you that we have made some changes to our IT policies regarding mobile app development. These changes are designed to enhance the security and compliance of our mobile apps and to provide guidance for mobile app developers like yourself.

The new policies include guidelines on data encryption, access controls, and secure data storage. We have also updated our policies on mobile app testing and deployment to ensure that our apps are thoroughly tested and deployed in a secure manner.

We believe that these changes are important for the continued success of MicroSynth and for the protection of our customers' data. We understand that these changes may require some adjustments to your development processes, but we are confident that you will be able to adapt to them.

If you have any questions or concerns about the new policies, please do not hesitate to contact us. We are happy to provide guidance and support to help you comply with our IT policies.

Thank you for your continued dedication to MicroSynth and for your contributions to our organization.

Best regards,
Sam Smith
Network Engineer
Human Resources
MicroSynth
555-1234"""


######### PRE-MADE EMAILS IN CASE API CALL FAILS, READY TO BE USED TO THE USER! ################################################################
    legitimate_template = f"""From: {sender_first_name} {sender_last_name} <{sender_first_name.lower()}.{sender_last_name.lower()}@{real_domain}>
To: {recipient_first_name} {recipient_last_name} <{recipient_first_name.lower()}.{recipient_last_name.lower()}@{company_domain}>
Date: {email_date}
Subject: Updates on {ctx.reason_for_contact}

Dear {recipient_first_name},

I hope this email finds you well. I'm writing to provide you with important information regarding {ctx.reason_for_contact} at {ctx.company_name}.

We have recently made some changes to our policies that will affect how we handle {ctx.reason_for_contact}. These changes are designed to improve efficiency and ensure compliance with industry standards.

Please review the attached documents for more details about these changes. If you have any questions or need clarification, don't hesitate to contact me directly.

Thank you for your attention to this matter.

Best regards,
{sender_first_name} {sender_last_name}
{sender_title}
{sender_department}
{ctx.company_name}
555-{r.randint(1000, 9999)}"""


    # Phishing email template
    phishing_template = f"""From: {sender_first_name} {sender_last_name} <{sender_first_name.lower()}.{sender_last_name.lower()}@{phishing_domain}>
To: {recipient_first_name} {recipient_last_name} <{recipient_first_name.lower()}.{recipient_last_name.lower()}@{company_domain}>
Date: {email_date}
Subject: {r.choice(["","URGENT:"])} Action Required - {ctx.reason_for_contact}

Dear {recipient_first_name},

I hope this email finds you well. I'm {r.choice(["contacting", "contating"])} you regarding an urgent matter concerning {ctx.reason_for_contact} that requires your {r.choice(["immediate", "imediate"])} attention.

Due to recent security concerns, we need all {ctx.position}s to verify their account information as soon as possible. Please click on the link below to confirm your details:

https://{phishing_domain + (r.choice(["x","/accounts"]))}/verify?id={r.randint(10000, 99999)}

This is an urgent matter and failure to verify within 24 hours may result in temporary suspension of your access.

If you have any questions, please do not reply to this email but contact us through our official website.

Regards,
{sender_first_name} {sender_last_name}
{sender_title}
{sender_department}
{ctx.company_name}
555-{r.randint(1000, 9999)}"""

#####################################################################################
###################### AI PROMPTS FOR EMAILS ########################################

    if chance == 0: # Write a non-fraudulent email
        prompt = f"""<instruction>
        Write a professional email from {sender_first_name} {sender_last_name} at {ctx.company_name} to {recipient_first_name} {recipient_last_name}, a {ctx.position} about {ctx.reason_for_contact}.
        
        Follow a format similar to this example email, but create original content:
        
        {example_email}
        
        Make sure your email has:
        - A proper From, To, Date, and Subjct line
        - A professional greeting using the recipient's name
        - 2-3 paragraphs of professional email content about {ctx.reason_for_contact}
        - A professional closing with full signature block
        
        Use these details:
        - Sender: {sender_first_name} {sender_last_name} <{sender_first_name.lower()}.{sender_last_name.lower()}@{real_domain}>
        - Recipient: {recipient_first_name} {recipient_last_name} <{recipient_first_name.lower()}.{recipient_last_name.lower()}@{company_domain}>
        - Date: {email_date}
        - Sender's title: {sender_title}
        - Sender's department: {sender_department}
        - Company: {ctx.company_name}
        
        IMPORTANT: 
        1. Make the email completely professional with NO placeholder tags
        2. If you include links, make them look legitimate (like https://{real_domain}/portal)
        3. Your response should ONLY contain the formatted email with no additional commentary
        </instruction>"""
    else: # Write a fraudulent email
        fraud = True
        prompt = f"""<instruction>
        Write a convincing phishing email pretending to be from {sender_first_name} {sender_last_name} at {ctx.company_name} to {recipient_first_name} {recipient_last_name}, a {ctx.position} about {ctx.reason_for_contact}.
        
        Follow a format similar to this example email, but create original content with subtle phishing signs:
        
        {example_email}
        
        Make sure your email has:
        - A proper From, To, Date, and Subject line
        - A greeting using the recipient's name
        - 2-3 paragraphs of content about {ctx.reason_for_contact}
        - A closing with signature block
        
        Use these details:
        - Sender: {sender_first_name} {sender_last_name} <{sender_first_name.lower()}.{sender_last_name.lower()}@{phishing_domain}>
        - Recipient: {recipient_first_name} {recipient_last_name} <{recipient_first_name.lower()}.{recipient_last_name.lower()}@{company_domain}>
        - Date: {email_date}
        - Sender's title: {sender_title}
        - Sender's department: {sender_department}
        - Company: {ctx.company_name}
        
        IMPORTANT: 
        1. Make the email look professional at first glance but include subtle phishing signs like:
           - Minor spelling/grammar errors
           - Slightly off branding
           - Unusual requests or urgency
           - The domain in the sender's email should be the phishing domain, not the real one
        2. If including links, make them look almost legitimate but wrong (like https://{phishing_domain}/login)
        3. Include a realistic phishing link if appropriate - don't use "[phishing link]" placeholder
        4. Your response should ONLY contain the formatted email with NO placeholder tags
        </instruction>"""
        
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7, 
            "max_new_tokens": 500,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload).json()
        
        if isinstance(response, list) and len(response) > 0 and "generated_text" in response[0]:
            generated_email = response[0]["generated_text"]
        elif isinstance(response, dict) and "generated_text" in response:
            generated_email = response["generated_text"]
        else:
            print(f"Unexpected response format: {response}")
            generated_email = str()
            if fraud:
                generated_email = phishing_template
            else:
                generated_email = legitimate_template
            
        # Clean up the response to ensure it only contains the email
        # Remove any instruction tags or explanations that might have been included
        if "<instruction>" in generated_email:
            generated_email = generated_email.split("</instruction>")[-1].strip()
        
        # Remove any leading explanatory text
        prefixes_to_remove = [
            "Here's the email:",
            "Here is the email:",
            "The email content:",
            "Email content:",
            "Here's a"
        ]
        for prefix in prefixes_to_remove:
            if generated_email.lower().startswith(prefix.lower()):
                generated_email = generated_email[len(prefix):].strip()
        
        # Remove any trailing explanations
        if "This email contains" in generated_email:
            generated_email = generated_email.split("This email contains")[0].strip()
            
        # Final check for any remaining placeholder brackets
        if "[" in generated_email and "]" in generated_email:
            # Try to replace obvious placeholders
            import re
            # Find all [placeholder] patterns
            placeholders = re.findall(r'\[(.*?)\]', generated_email)
            for placeholder in placeholders:
                # Generate replacements for common placeholders
                if "subject" in placeholder.lower():
                    subjects = [
                        f"Regarding {ctx.reason_for_contact}",
                        f"Important: {ctx.reason_for_contact}",
                        f"Update on {ctx.reason_for_contact}",
                        f"Information about {ctx.reason_for_contact}"
                    ]
                    replacement = r.choice(subjects)
                elif "phone" in placeholder.lower():
                    replacement = f"555-{r.randint(1000, 9999)}"
                elif "link" in placeholder.lower():
                    if fraud:
                        replacement = f"https://{phishing_domain}/portal/login"
                    else:
                        replacement = f"https://{real_domain}/portal/login"
                else:
                    # Generic replacement
                    replacement = "Additional information"
                
                # Replace the placeholder
                generated_email = generated_email.replace(f"[{placeholder}]", replacement)
        
        generated_id = str(uuid.uuid4())
        EMAILS[generated_id] = {"content": generated_email, "is_phishing": fraud}
        
        print(f"Generated email: {generated_email[:100]}...")
        
        return EmailGenerated(id=generated_id, content=generated_email, is_phishing=fraud)
    except Exception as e:
        print(f"Error generating email: {e}")
        # Use fallback template in case of any exception
        fallback_email = str()
        
        if chance == 1:
            fraud = True

        
        if fraud:
            fallback_email = phishing_template
        else:
            fallback_email = legitimate_template
        
        generated_id = str(uuid.uuid4())
        EMAILS[generated_id] = {"content": fallback_email, "is_phishing": fraud}
        
        print(f"Using fallback template due to error: {e}")
        return EmailGenerated(id=generated_id, content=fallback_email, is_phishing=fraud)
        

@app.post("/submit_answer", response_model=Score)
def submit_answer(sub: UserSubmission):
    # ANSWER PROCESS LOGIC
    email = EMAILS.get(sub.email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    correct = sub.is_phishing_guess == email['is_phishing']
    highlight_score = len(sub.highlights) * 5 if email['is_phishing'] else 0
    points = (10 if correct else -5) + highlight_score

    # UPDATE SCORE
    session_id = sub.session_id
    if session_id not in USER_SCORES:
        USER_SCORES[session_id] = 0
        USER_PROGRESS[session_id] = 0
    USER_SCORES[session_id] += max(points, 0)
    USER_PROGRESS[session_id] += 1  # Track progress

    return Score(
        correct=correct,
        points_earned=points,
        feedback="Correct!" if correct else "Wrong, be careful!"
    )

@app.get("/progress")
def get_progress(session_id: str):
    return {
        "question_number": USER_PROGRESS.get(session_id, 0),
        "total_score": USER_SCORES.get(session_id, 0)
    }

@app.post("/finish_quiz")
def finish_quiz(data: EndGame):
    session_id = data.session_id
    score = USER_SCORES.get(session_id, 0)
    wallet = USER_SESSIONS.get(session_id, {}).get("wallet", None)

    awarded = []

    if wallet and wallet != "guest":
        if wallet.startswith("0x"):
            chain = "evm"
        elif wallet.endswith(".sol"):
            chain = "solana"
        elif wallet.lower().startswith("stark"):
            chain = "starknet"
        else:
            chain = "evm"  # Default to EVM if unknown
        
        if chain == "evm": # Due to time constraints, we can only reserve this feature for EVM wallets
            awarded = blockchain_stuff.process_quiz_results(wallet, data.errors, score, chain)

    return {
        "message": "Quiz complete",
        "score": score,
        "achievements_awarded": awarded,
        "seconds_taken": data.seconds_taken,
    }


##################### MANAGEMENT LOGIC #################################
@app.get("/api/session_info")
def get_session_info(session_id: str = ""):
    if not session_id or session_id not in USER_SESSIONS:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_data = USER_SESSIONS[session_id]
    greeting = "Welcome back, guest!"

    if user_data.get("type") == "wallet":
        wallet = user_data.get("wallet", "Unknown wallet")
        greeting = f"Welcome back, {wallet}!"

    return {
        "greeting": greeting
    }


@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    wallet = data.get("wallet")
    guest = data.get("guest")
    session_id = str(uuid.uuid4())

    if guest:
        USER_SESSIONS[session_id] = {"type": "guest"}
    elif wallet:
        USER_SESSIONS[session_id] = {"type": "wallet", "wallet": wallet}
    else:
        raise HTTPException(status_code=400, detail="Missing login data")

    return JSONResponse({"session_id": session_id, "login_type": USER_SESSIONS[session_id]["type"]})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)