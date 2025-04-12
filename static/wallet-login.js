async function loginWithWallet() {
    if (window.ethereum) {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const wallet = accounts[0];

        const res = await fetch("/api/login", {
            method: "POST",
            body: JSON.stringify({ wallet }),
            headers: { "Content-Type": "application/json" },
        });
        const data = await res.json();
        localStorage.setItem("session_id", data.session_id);
        window.location.href = `/dashboard?session_id=${data.session_id}`;
    } else {
        alert("Please install a wallet like MetaMask.");
    }
}

async function GuestLogIn(){
    const isGuest = confirm("Continue as guest?");
    if (isGuest) {
        const res = await fetch("/api/login", {
            method: "POST",
            body: JSON.stringify({ guest: true }),
            headers: { "Content-Type": "application/json" },
        });
        const data = await res.json();
        localStorage.setItem("session_id", data.session_id);
        window.location.href = `/dashboard?session_id=${data.session_id}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const loginButton = document.getElementById("log-in-wallet");
    const guestButton = document.getElementById("guest-log-in");

    if (loginButton) loginButton.addEventListener("click", loginWithWallet);
    if (guestButton) guestButton.addEventListener("click", GuestLogIn);
});
