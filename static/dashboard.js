document.addEventListener('DOMContentLoaded', function() {
    // Session validation
    const clientSessionId = localStorage.getItem("session_id");
    if(clientSessionId === null) {
        alert("Session expired. Please log in again.");
        window.location.href = "/";
    }

    // Load user profile information from localStorage
    const loadProfileData = () => {
        const profilePicture = localStorage.getItem('user_profile_pic');
        const walletAddress = localStorage.getItem('wallet_address');
        const walletChain = localStorage.getItem('wallet_chain');
        
        // Set profile picture if available
        if (profilePicture && document.getElementById('user-profile-picture')) {
            document.getElementById('user-profile-picture').src = profilePicture;
        }
        
        // Show wallet address if available (truncated)
        if (walletAddress && document.getElementById('wallet-address')) {
            const shortAddress = walletAddress.substring(0, 6) + '...' + walletAddress.substring(walletAddress.length - 4);
            document.getElementById('wallet-address').textContent = shortAddress;
        } else if (document.getElementById('wallet-address')) {
            document.getElementById('wallet-address').textContent = 'Guest User';
        }
        
        // Show blockchain badge if applicable
        const chainBadge = document.getElementById('chain-badge');
        if (chainBadge) {
            if (walletChain) {
                chainBadge.textContent = walletChain;
                
                // Set badge color based on chain
                if (walletChain === 'Ethereum') {
                    chainBadge.classList.add('bg-blue-200', 'text-blue-800');
                } else if (walletChain === 'Polygon') {
                    chainBadge.classList.add('bg-purple-200', 'text-purple-800');
                } else if (walletChain === 'Solana') {
                    chainBadge.classList.add('bg-green-200', 'text-green-800');
                }
            } else {
                chainBadge.classList.add('hidden');
            }
        }
    };

    // Fetch session info from server
    fetch(`/api/session_info?session_id=${clientSessionId}`, {
        method: "GET",
    })
    .then(RESPONSE => RESPONSE.json())
    .then(DATA => {
        // Update greeting and highscore
        document.getElementById('greeting-label').innerText = `${DATA.greeting}`;
        document.getElementById('highscore-label').innerText = `Your highest score: ${DATA.high_score}`;
        
        // If server has profile info, update localStorage
        if (DATA.profile_picture && !localStorage.getItem('user_profile_pic')) {
            localStorage.setItem('user_profile_pic', DATA.profile_picture);
        }
        
        if (DATA.wallet_address && !localStorage.getItem('wallet_address')) {
            localStorage.setItem('wallet_address', DATA.wallet_address);
        }
        
        if (DATA.wallet_chain && !localStorage.getItem('wallet_chain')) {
            localStorage.setItem('wallet_chain', DATA.wallet_chain);
        }
        
        // Load profile data after server response
        loadProfileData();
    })
    .catch(err => {
        console.error("Error fetching session info:", err);
        // Still try to load profile data from localStorage even if server fails
        loadProfileData();
    });

    // Quiz confirmation handlers
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
});