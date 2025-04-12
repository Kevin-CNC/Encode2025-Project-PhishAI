# PhishQuiz Backend Updated - Session Redirects, Wallet Login, Tracking, High Score Logic

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import pipeline
import uuid
import random as r

app = FastAPI()

# ------------------ Static Mount ------------------
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------ AI Model Load ------------------
try:
    phishing_detector = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")
except:
    phishing_detector = None

# ------------------ Models ------------------
class EmailContext(BaseModel):
    company_name: str
    user_email: str
    position: str

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
def generate_email(ctx: EmailContext):
    
    email_generator = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")
    chance = r.randint(0,1)
    
    prompt = str()
    if chance == 0: # Write a non-fraudolent email
        prompt = f"""Write an email from {ctx.company_name} to a {ctx.position} about a sensible & work-related topic.
        Make it realistic and professional, following the basic guidelines for email writing in an IT setting.
        You may or may not add a link if you so choose."""
    else: # Write a fraudulent email
        prompt = f"""Write a phishing email from {ctx.company_name} to a {ctx.position} about a sensible & work-related topic.
        Make it realistic and professional, following the basic guidelines for email writing in an IT setting.
        You may or may not add a link if you so choose; And if you do, make it a phishing link.
        However, add slight hints and potential clues to the fact that this is a phishing email.
        """
        
    generated = str()
    try:
        generated = email_generator(prompt, max_length=200, do_sample=True, top_k=50)[0]['generated_text']
    except Exception:
        generated = f"Subject: Important Notice from {ctx.company_name}\n\nYour account is in trouble. Please verify now."
    
    
    is_phishing = phishing_detector(generated)[0]['label'] == 'spam' if phishing_detector else True
    email_id = str(uuid.uuid4())
    EMAILS[email_id] = {"content": generated, "is_phishing": is_phishing}
    return EmailGenerated(id=email_id, content=generated, is_phishing=is_phishing)

@app.post("/submit_answer", response_model=Score)
def submit_answer(sub: UserSubmission):
    # === Answer Processing Logic ===
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
