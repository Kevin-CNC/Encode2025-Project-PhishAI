let currentEmail = null;
let questionCount = 0;
let maxQuestions = 15;
let errorsCounted = 0;
let secondsTaken = 0;
let startTime = Date.now();
let timer = setInterval(() => {
    let elapsed = Date.now() - startTime;
    secondsTaken = Math.floor(elapsed / 1000);
}, 1000);

const sessionId = localStorage.getItem("session_id");
if (sessionId === null) {
    alert("Session expired. Please log in again.");
    window.location.href = "/";
}

const resultsModal = document.getElementById("resultsModal");
const closeModalButton = document.getElementById("closeModal");
const okButton = document.getElementById("okButton");

let finalScoreDisplay = document.getElementById("finalScore");
let accuracyDisplay = document.getElementById("accuracy");
let finalTimeDisplay = document.getElementById("finalTime");
let achievementsDisplay = document.getElementById("achievements")


async function loadEmail() {
    console.log("Fetching new email...");
    const res = await fetch("/generate_email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    });
    currentEmail = await res.json();
    document.getElementById("emailBox").textContent = currentEmail.content;
}

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
        }),
    });

    const result = await res.json();
    document.getElementById("quizFeedback").textContent = `${result.feedback} (+${result.points_earned} pts)`;

    questionCount += 1;
    if (result.points_earned < 0) {
        errorsCounted += 1;
    }

    if (questionCount >= maxQuestions) {
        clearInterval(timer);

        const finishRes = await fetch("/finish_quiz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                errors: errorsCounted,
                session_id: sessionId,
                seconds_taken: secondsTaken,
            }),
        });

        const finalResult = await finishRes.json();
        const score = finalResult.score;
        const accuracy = ((maxQuestions - errorsCounted) / maxQuestions) * 100;
        let achievements = finalResult.achievements_awarded;
        if (achievements == []){
          achievements = "None..."
        } else{
          achievements = achievements.join(", ");
        }

        finalScoreDisplay.textContent = score;
        accuracyDisplay.textContent = accuracy.toFixed(2) + "%";
        finalTimeDisplay.textContent = formatTime(secondsTaken);
        resultsModal.style.display = "flex";


    } else {
        setTimeout(() => {
            document.getElementById("quizFeedback").textContent = "";
            loadEmail();
        }, 1000);
    }
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes} minutes and ${remainingSeconds} seconds`;
}

closeModalButton.addEventListener("click", () => {
    resultsModal.style.display = "none";
    window.location.href = "/dashboard";
});

okButton.addEventListener("click", () => {
    resultsModal.style.display = "none";
    window.location.href = "/dashboard";
});


window.onload = loadEmail;