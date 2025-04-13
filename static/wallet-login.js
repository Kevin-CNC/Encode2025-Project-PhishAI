// Import necessary wallet adapters
const solanaWeb3 = document.createElement('script');
solanaWeb3.src = 'https://cdnjs.cloudflare.com/ajax/libs/solana-web3.js/1.73.0/index.min.js';
document.head.appendChild(solanaWeb3);

// Add Starknet.js library
const starknetJs = document.createElement('script');
starknetJs.src = 'https://cdnjs.cloudflare.com/ajax/libs/starknet/5.14.1/starknet.js';
document.head.appendChild(starknetJs);

// Wallet connection state
let walletState = {
    address: null,
    chain: null,
    profilePicture: null
};

// Connect to Ethereum or Polygon (EVM-compatible chains)
async function connectEVM(chainType) {
    if (!window.ethereum) {
        alert(`Please install an EVM compatible wallet like MetaMask for ${chainType}`);
        return null;
    }
    
    try {
        // Request account access
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];
        
        // Set the correct chain ID for the selected network
        let chainId;
        if (chainType === 'Ethereum') {
            chainId = '0x1'; // Ethereum Mainnet
        } else if (chainType === 'Polygon') {
            chainId = '0x89'; // Polygon Mainnet
        }
        
        // Try to switch to the correct chain
        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId }],
            });
        } catch (switchError) {
            // If chain isn't added to MetaMask, we can suggest adding it
            if (switchError.code === 4902 && chainType === 'Polygon') {
                try {
                    await window.ethereum.request({
                        method: 'wallet_addEthereumChain',
                        params: [{
                            chainId: '0x89',
                            chainName: 'Polygon Mainnet',
                            nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
                            rpcUrls: ['https://polygon-rpc.com/'],
                            blockExplorerUrls: ['https://polygonscan.com/']
                        }]
                    });
                } catch (addError) {
                    console.error('Error adding Polygon chain:', addError);
                }
            }
        }
        
        // Get profile picture from ENS if available (Ethereum)
        let profilePicture = null;
        if (chainType === 'Ethereum') {
            try {
                // Try to resolve ENS name for the address
                const provider = new ethers.providers.Web3Provider(window.ethereum);
                const ensName = await provider.lookupAddress(address);
                
                if (ensName) {
                    const resolver = await provider.getResolver(ensName);
                    if (resolver) {
                        const avatar = await resolver.getAvatar();
                        if (avatar) {
                            profilePicture = avatar.url;
                        }
                    }
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

// Connect to Solana
async function connectSolana() {
    if (!window.solana) {
        alert("Please install a Solana wallet like Phantom");
        return null;
    }
    
    try {
        // Connect to Solana wallet
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

// Connect to Starknet
async function connectStarknet() {
    // Check if Starknet wallet is available (like Argent X or Braavos)
    if (!window.starknet) {
        alert("Please install a Starknet wallet like Argent X or Braavos");
        return null;
    }
    
    try {
        // Request connection to the wallet
        await window.starknet.enable();
        
        // Get the account address
        const starknetAccount = window.starknet.account;
        const address = starknetAccount.address;
        
        // Generate a profile picture for Starknet
        const profilePicture = `https://ui-avatars.com/api/?name=STRK&background=5c25d3&color=fff&rounded=true&bold=true&length=4`;
        
        return {
            address,
            chain: 'Starknet',
            profilePicture
        };
    } catch (error) {
        console.error("Starknet connection error:", error);
        alert(`Error connecting to Starknet: ${error.message}`);
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
    } else if (chainType === 'Starknet') {
        walletData = await connectStarknet();
    }
    
    if (!walletData) return;
    
    // Store wallet state
    walletState = walletData;
    
    try {
        // Send login request to backend
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
        
        // Save session and profile picture to localStorage
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

// Guest login function (unchanged from original)
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

// Initialize UI
document.addEventListener("DOMContentLoaded", () => {
    // Get all buttons
    const ethereumButton = document.getElementById("log-in-ethereum");
    const polygonButton = document.getElementById("log-in-polygon");
    const solanaButton = document.getElementById("log-in-solana");
    const starknetButton = document.getElementById("log-in-starknet");
    const guestButton = document.getElementById("guest-log-in");
    
    // Legacy support for generic wallet button
    const genericWalletButton = document.getElementById("log-in-wallet");
    
    // Set up event listeners
    if (ethereumButton) ethereumButton.addEventListener("click", () => loginWithWallet("Ethereum"));
    if (polygonButton) polygonButton.addEventListener("click", () => loginWithWallet("Polygon"));
    if (solanaButton) solanaButton.addEventListener("click", () => loginWithWallet("Solana"));
    if (starknetButton) starknetButton.addEventListener("click", () => loginWithWallet("Starknet"));
    if (guestButton) guestButton.addEventListener("click", GuestLogIn);
    
    // Support legacy button if it exists
    if (genericWalletButton) {
        genericWalletButton.addEventListener("click", () => {
            // Display wallet selection dialog instead of defaulting to Ethereum
            const walletOptions = document.createElement('div');
            walletOptions.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            walletOptions.innerHTML = `
                <section class="bg-white p-6 rounded-lg shadow-xl max-w-sm w-full">
                    <h3 class="text-xl font-bold mb-4">Select Your Wallet</h3>
                    <section class="space-y-3">
                        <button class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition" data-chain="Ethereum">
                            <span class="mr-2">Ξ</span> Ethereum
                        </button>
                        <button class="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition" data-chain="Polygon">
                            <span class="mr-2">◆</span> Polygon
                        </button>
                        <button class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition" data-chain="Solana">
                            <span class="mr-2">◎</span> Solana
                        </button>
                        <button class="w-full bg-violet-600 text-white py-2 px-4 rounded-md hover:bg-violet-700 transition" data-chain="Starknet">
                            <span class="mr-2">⚡</span> Starknet
                        </button>
                        <button class="w-full bg-gray-300 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-400 transition mt-4" data-action="cancel">
                            Cancel
                        </button>
                    </section>
                </section>
            `;
            
            document.body.appendChild(walletOptions);
            
            // Set up event listeners for the dialog buttons
            walletOptions.querySelectorAll('button[data-chain]').forEach(button => {
                button.addEventListener('click', () => {
                    const chain = button.getAttribute('data-chain');
                    walletOptions.remove();
                    loginWithWallet(chain);
                });
            });
            
            // Cancel button
            walletOptions.querySelector('button[data-action="cancel"]').addEventListener('click', () => {
                walletOptions.remove();
            });
        });
    }
});

// Add necessary CDN for ethers.js (needed for ENS resolution)
const ethersScript = document.createElement('script');
ethersScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js';
document.head.appendChild(ethersScript);