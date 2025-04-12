let currentEmail = null;
let questionCount = 0;
let maxQuestions = 10;
let errorsCounted = 0;

const sessionId = localStorage.getItem("session_id");
if(sessionId === null) {
  alert("Session expired. Please log in again.");
  window.location.href = "/";
}


// load email generated by AI
async function loadEmail() {
  console.log("Fetching new email...")

  const res = await fetch("/generate_email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      company_name: "ExampleCorp",
      user_email: "user@example.com",
      position: "IT Specialist"
    })
  });

  currentEmail = await res.json();
  document.getElementById("emailBox").textContent = currentEmail.content;
}

// User submission 
async function submitAnswer(isPhishingGuess) {
  if (!currentEmail) return;

  console.log(currentEmail.id, isPhishingGuess, sessionId);

  const res = await fetch("/submit_answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email_id: currentEmail.id,
      is_phishing_guess: isPhishingGuess,
      highlights: [],
      session_id: sessionId,
    })
  });


  // get and compare the result; display feedback later
  const result = await res.json();
  document.getElementById("quizFeedback").textContent = `${result.feedback} (+${result.points_earned} pts)`;

  questionCount += 1;
  if (result.points_earned < 0){
    errorsCounted += 1;
  }

  if (questionCount >= maxQuestions) {
    await fetch("/finish_quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        errors: errorsCounted,
        session_id: sessionId,
      })
    });
    setTimeout(() => window.location.href = "/dashboard", 2000);
  } else {
    setTimeout(() => {
      document.getElementById("quizFeedback").textContent = "";
      loadEmail();
    }, 1000);
  }
}

window.onload = loadEmail;
