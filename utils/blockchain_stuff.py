from web3 import Web3
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.rpc.api import Client as SolanaClient
from typing import Dict, Optional, List
import requests
import json
import os

# === Constants & Configuration ===
EVM_RPC_URL = os.getenv("EVM_RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
EVM_CONTRACT_ADDRESS = os.getenv("EVM_CONTRACT_ADDRESS", "0x123...abc")
SOLANA_PROGRAM_ID = os.getenv("SOLANA_PROGRAM_ID", "SAMPLE1111111111111111111111111111111111111")

web3 = Web3(Web3.HTTPProvider(EVM_RPC_URL))
solana = SolanaClient(SOLANA_RPC_URL)

LEADERBOARD_ONCHAIN: List[Dict] = []  # Will be populated from on-chain or cached


# === Sample ABI (EVM Contract Must Implement this) ===
EVM_LEADERBOARD_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "player", "type": "address"}, {"internalType": "uint256", "name": "score", "type": "uint256"}],
        "name": "submitScore",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getTopPlayers",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]


# === Submit Score ===
def submit_score(wallet_address: str, score: int, chain: str = "evm") -> Optional[str]:
    if chain == "evm":
        try:
            contract = web3.eth.contract(address=EVM_CONTRACT_ADDRESS, abi=EVM_LEADERBOARD_ABI)
            tx = contract.functions.submitScore(wallet_address, score).build_transaction({
                'nonce': web3.eth.get_transaction_count(wallet_address),
                'gas': 250000,
                'gasPrice': web3.to_wei('10', 'gwei')
            })
            # NOTE: You must sign and send the transaction externally via frontend wallet (MetaMask)
            return "EVM tx built. Must be signed on frontend."
        except Exception as e:
            print("EVM Error:", e)
            return None

    elif chain == "solana":
        try:
            player = PublicKey(wallet_address)
            tx = Transaction()
            # You'd construct Solana transaction using real program logic here
            # This is a placeholder
            tx.add(...)  # smart contract interaction here
            # Return serialized transaction for frontend to sign
            return tx.serialize().hex()
        except Exception as e:
            print("Solana Error:", e)
            return None


# === Award Badges ===
def award_badge(wallet_address: str, badge_name: str, chain: str = "evm") -> Optional[str]:
    # This assumes you’ve deployed a badge contract (EVM ERC-721 or Solana NFT)
    # Implementation depends on the platform, but conceptually:
    print(f"Awarding {badge_name} badge to {wallet_address} on {chain}")
    return "Badge minted or pending signature on frontend."


# === Fetch On-Chain Leaderboard ===
def get_top_leaderboard(chain: str = "evm") -> List[Dict]:
    if chain == "evm":
        try:
            contract = web3.eth.contract(address=EVM_CONTRACT_ADDRESS, abi=EVM_LEADERBOARD_ABI)
            players = contract.functions.getTopPlayers().call()
            return [{"address": p, "score": 0} for p in players]  # Fetch scores via another function if needed
        except Exception as e:
            print("EVM Error:", e)
    elif chain == "solana":
        try:
            # You’d normally pull leaderboard data from an off-chain indexer or PDA account
            return []
        except Exception as e:
            print("Solana Error:", e)
    return []
