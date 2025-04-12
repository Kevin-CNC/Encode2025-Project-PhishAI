// Import necessary wallet adapters
const solanaWeb3 = document.createElement('script');
solanaWeb3.src = 'https://cdnjs.cloudflare.com/ajax/libs/solana-web3.js/1.73.0/index.min.js';
document.head.appendChild(solanaWeb3);

// Wallet connection state
let walletState = {
    address: null,
    chain: null,
    profilePicture: null
};

// ETHERIUM OR POLYGON
async function connectEVM(chainType) {
    if (!window.ethereum) {
        alert(`PLEASE USE AN EVM COMPATIBLE WALLET FOR ${chainType}`);
        return null;
    }
    
    try {
        // Request account access
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];

        let profilePicture = null;
        if (chainType === 'Ethereum') {
            try {
                const ensName = await window.ethereum.request({
                    method: 'eth_call',
                    params: [{
                        to: '0x4976fb03C32e5B8cfe2b6cCB31c09Ba78EBaBa41', // ENS Resolver
                        data: `0x691f3431${address.slice(2).padStart(64, '0')}` // function: getAvatar(address)
                    }, 'latest']
                });
                
                if (ensName && ensName !== '0x') {
                    profilePicture = `https://metadata.ens.domains/mainnet/avatar/${ensName}`;
                }
            } catch (error) {
                console.log("Could not fetch ENS profile picture", error);
            }
        }
        
        // Default avatar if no ENS
        if (!profilePicture) {
            profilePicture = `https://effigy.im/a/${address}.svg`;
        }
        
        return {
            address,
            chain: chainType,
            profilePicture
        };
    } catch (error) {
        console.error(`${chainType} connection error:`, error);
        alert(`Error connecting to ${chainType}: ${error.message}`);
        return null;
    }
}

// SOLANA CONNECTION
async function connectSolana() {
    if (!window.solana) {
        alert("PLEASE USE A SOLANA-BASED WALLET!");
        return null;
    }
    
    try {
        const response = await window.solana.connect();
        const address = response.publicKey.toString();
        
        // Generate a profile picture for Solana (using a placeholder service)
        const profilePicture = `https://ui-avatars.com/api/?name=SOL&background=09f&color=fff&rounded=true&bold=true&length=3`;
        
        return {
            address,
            chain: 'Solana',
            profilePicture
        };
    } catch (error) {
        console.error("Solana connection error:", error);
        alert(`Error connecting to Solana: ${error.message}`);
        return null;
    }
}

// Main login function for all wallet types
async function loginWithWallet(chainType) {
    let walletData = null;
    
    // Connect to appropriate wallet based on chain
    if (chainType === 'Ethereum' || chainType === 'Polygon') {
        walletData = await connectEVM(chainType);
    } else if (chainType === 'Solana') {
        walletData = await connectSolana();
    }
    
    if (!walletData) return;
    
    walletState = walletData;
    
    try {

        const res = await fetch("/api/login", {
            method: "POST",
            body: JSON.stringify({
                wallet: walletData.address,
                chain: walletData.chain,
                profilePicture: walletData.profilePicture
            }),
            headers: { "Content-Type": "application/json" },
        });
        
        const data = await res.json();

        localStorage.setItem("session_id", data.session_id);
        localStorage.setItem("user_profile_pic", walletData.profilePicture);
        localStorage.setItem("wallet_address", walletData.address);
        localStorage.setItem("wallet_chain", walletData.chain);
        
        // Navigate to dashboard with session
        window.location.href = `/dashboard?session_id=${data.session_id}`;
    } catch (error) {
        console.error("Login error:", error);
        alert(`Error during login: ${error.message}`);
    }
}

// Guest login function
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
        localStorage.setItem("user_profile_pic", "/static/img/guest-avatar.png");
        window.location.href = `/dashboard?session_id=${data.session_id}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const ethereumButton = document.getElementById("log-in-ethereum");
    const polygonButton = document.getElementById("log-in-polygon");
    const solanaButton = document.getElementById("log-in-solana");
    const guestButton = document.getElementById("guest-log-in");
    const genericWalletButton = document.getElementById("log-in-wallet");

    if (ethereumButton) ethereumButton.addEventListener("click", () => loginWithWallet("Ethereum"));
    if (polygonButton) polygonButton.addEventListener("click", () => loginWithWallet("Polygon"));
    if (solanaButton) solanaButton.addEventListener("click", () => loginWithWallet("Solana"));
    if (guestButton) guestButton.addEventListener("click", GuestLogIn);
    
    // Support legacy button if it exists
    if (genericWalletButton) {
        genericWalletButton.addEventListener("click", () => {
            // Default to Ethereum if generic button is clicked
            loginWithWallet("Ethereum");
        });
    }
});