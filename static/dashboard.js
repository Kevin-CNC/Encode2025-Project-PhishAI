document.addEventListener('DOMContentLoaded', function() {

    const clientSessionId = localStorage.getItem("session_id");
    if(clientSessionId === null) {
        alert("Session expired. Please log in again.");
        window.location.href = "/";
    }

    fetch(`/api/session_info?session_id=${clientSessionId}`, {
        method: "GET",
    })
    .then(RESPONSE => RESPONSE.json())
    .then(DATA => {
        document.getElementById('greeting-label').innerText = `${DATA.greeting}`;
        document.getElementById('highscore-label').innerText = `Your highest score: ${DATA.high_score}`;
    })
    .catch(err => {
        console.error("Error fetching session info:", err);
    });

    function confirmStart() {
        document.getElementById('confirmBox').classList.remove('hidden');
    }
    document.getElementById('startButton').addEventListener('click', confirmStart);


    function hideConfirm() {
        document.getElementById('confirmBox').classList.add('hidden');
    }
    document.getElementById('regretButton').addEventListener('click', hideConfirm);

    function startQuiz() {
        window.location.href = "/quiz_question?session_id=" + clientSessionId;
    }
    document.getElementById('startQuizButton').addEventListener('click', startQuiz);
    //startQuizButton
});