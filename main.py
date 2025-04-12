# PhishQuiz Backend Updated - Session Redirects, Wallet Login, Tracking, High Score Logic

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import uuid
import random as r
import os
from dotenv import load_dotenv
from utils import context_generator

load_dotenv() # Load environment variables

app = FastAPI()
api_key = os.getenv("HUGGING_FACE_TOKEN")
# ------------------ Static Mount ------------------
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
app.mount("/static", StaticFiles(directory="static"), name="static")
# ------------------ Models ------------------

class EmailGenerated(BaseModel):
    id: str
    content: str
    is_phishing: bool

class UserSubmission(BaseModel):
    email_id: str
    is_phishing_guess: bool
    highlights: list[str]
    session_id: str  # <-- NEW: Pass session to identify

class Score(BaseModel):
    correct: bool
    points_earned: int
    feedback: str

# ------------------ State ------------------
EMAILS = {}
LEADERBOARD = {}
USER_SESSIONS = {}
USER_SCORES = {}
USER_PROGRESS = {}  # <-- NEW: Tracks question numbers per session

# ------------------ Pages ------------------

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

# ------------------ Game Logic ------------------
@app.post("/generate_email", response_model=EmailGenerated)
def generate_email():    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"  
    headers = {"Authorization": f"Bearer {api_key}"}
    
    ctx = context_generator.generate_context()
    
    chance = r.randint(0,1)
    fraud = False

    prompt = str()
    # apart from chance choice, we are generating a random seed so the current ai model won't just generate the same thing due to identical prompts
    
    if chance == 0: # Write a non-fraudolent email
        prompt = f"""Write an email from {ctx.company_name} to a {ctx.position} about {ctx.reason_for_contact}.
        Make it realistic and professional, following the basic guidelines for email writing in an IT setting.
        You may or may not add a link if you so choose.
        The user's email should follow the company's domain: {ctx.user_email}.
        Never include the prompt in the generated text, as it breaks immersion for the end-user.
        generation seed: {str(uuid.uuid4())}"""
    else: # Write a fraudulent email
        fraud = True
        prompt = f"""Write an email from {ctx.company_name} to a {ctx.position} about {ctx.reason_for_contact}.
        Make it realistic and professional, following the basic guidelines for email writing in an IT setting.
        The user's email should follow the company's domain: {ctx.user_email}.
        You may or may not add a link if you so choose; And if you do, make it a phishing link.
        
        However, add slight hints and potential clues to the fact that this is a phishing email, which can be but are not limited to: Spelling mistakes, unfamiliar greetings, poor grammar, inconsistent domains / email addresses, unusual requests and etc. 
        Never include the prompt in the generated text, as it breaks immersion for the end-user.
        generation seed: {str(uuid.uuid4())}"""
        
    generated_response = str()
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": 0.7, "max_new_tokens": 200} # optimized parameteres for scope
    } # Make call with current payload
    
    generated_email = str()
    try:
        generated_response = requests.post(API_URL, headers=headers, json=payload).json()
        generated_email = generated_response[0]["generated_text"]
        print("c 1")
        if "---" in generated_email:
            generated_email = generated_email.split("---", 1)[1].strip()
        else:
            generated_email = generated_email.strip()
        print("c 2")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error generating email")
    
    try:
        generated_id = str(uuid.uuid4())
        EMAILS[generated_id] = {"content": generated_email, "is_phishing": fraud}
        
        return EmailGenerated(id=generated_id, content=generated_email, is_phishing=fraud) # construct response model so it can be better handled on the client
    except Exception as e:
        print(e)

@app.post("/submit_answer", response_model=Score)
def submit_answer(sub: UserSubmission):
    # === Answer Processing Logic ===
    print(sub)
    
    email = EMAILS.get(sub.email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    correct = sub.is_phishing_guess == email['is_phishing']
    highlight_score = len(sub.highlights) * 5 if email['is_phishing'] else 0
    points = (10 if correct else -5) + highlight_score

    # === Score and Progress Update ===
    session_id = sub.session_id
    if session_id not in USER_SCORES:
        USER_SCORES[session_id] = 0
        USER_PROGRESS[session_id] = 0
    USER_SCORES[session_id] += max(points, 0)
    USER_PROGRESS[session_id] += 1  # Track progress

    # === Leaderboard Update ===
    current_score = USER_SCORES[session_id]
    LEADERBOARD[session_id] = max(current_score, LEADERBOARD.get(session_id, 0))

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

@app.get("/highscore")
def get_highscore(session_id: str):
    score = LEADERBOARD.get(session_id, 0)
    return {"session_id": session_id, "high_score": score}

# ------------------ Session Management ------------------
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
        "greeting": greeting,
        "high_score": LEADERBOARD.get(session_id, 0)
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
