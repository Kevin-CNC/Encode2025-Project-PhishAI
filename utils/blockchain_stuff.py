from typing import Dict, List, Optional

class AchievementManager:
    def __init__(self):
        self._achievements = {
            "phishing_intern": {
                "name": "Phishing Intern",
                "description": "Successfully identify 10 phishing emails",
                "requirement": 5
            },
            "perfect_run": {
                "name": "Perfect Run",
                "description": "Have 0 overall mistakes. Good job!",
                "requirement": 0
            },
            "on_the_right_path": {
                "name": "On the right path",
                "description": "Achieve an overall of 100 points. Good job!",
                "requirement": 100
            },
            "speedrunner": {
                "name": "Speedrunner",
                "description": "Finish the quiz in under 5 minutes, with an 80%+ accuracy!",
                "requirement": 0.8
            }
        }
        self._user_achievements = {}
    
    def has_achievement(self, wallet_address: str, achievement_id: str) -> bool:
        user_achievements = self._user_achievements.get(wallet_address, [])
        return achievement_id in user_achievements
    
    def award_achievement(self, wallet_address: str, achievement_id: str) -> bool:
        if achievement_id not in self._achievements:
            return False
        
        if wallet_address not in self._user_achievements:
            self._user_achievements[wallet_address] = []
        
        if achievement_id not in self._user_achievements[wallet_address]:
            self._user_achievements[wallet_address].append(achievement_id)
            return True
        
        return False


# Global instance to maintain state across calls
achievement_manager = AchievementManager()





def send_onchain_badge(wallet_address: str, achievement_id: str, chain: str) -> bool:
    """
    Stub function to simulate sending achievement badge on-chain.

    Args:
        wallet_address (str): User wallet address.
        achievement_id (str): The achievement being awarded.
        chain (str): One of 'evm', 'solana', 'starknet'.

    Returns:
        bool: True if simulated success.
    """

    print(f"[Blockchain] Awarding '{achievement_id}' to {wallet_address} on {chain} chain.")
    # Here you'd integrate with:
    # - Web3 (EVM): Mint NFT / call smart contract
    # - Solana: Send transaction or custom token
    # - Starknet: Use starknet.py to invoke smart contract
    return True


def process_quiz_results(wallet_address: str, errors: int, points: int, chain: str) -> List[str]:
    awarded = []

    if errors <= achievement_manager._achievements["phishing_intern"]["requirement"]:
        if achievement_manager.award_achievement(wallet_address, "phishing_intern"):
            if send_onchain_badge(wallet_address, "phishing_intern", chain):
                awarded.append("Phishing Intern")

    if errors == achievement_manager._achievements["perfect_run"]["requirement"]:
        if achievement_manager.award_achievement(wallet_address, "perfect_run"):
            if send_onchain_badge(wallet_address, "perfect_run", chain):
                awarded.append("Perfect Run")
                
    if points == achievement_manager._achievements["on_the_right_path"]["requirement"]:
        if achievement_manager.award_achievement(wallet_address, "on_the_right_path"):
            if send_onchain_badge(wallet_address, "on_the_right_path", chain):
                awarded.append("On the right path")

    if (15 - errors) / 15 >= achievement_manager._achievements["speedrunner"]["requirement"]:
        if achievement_manager.award_achievement(wallet_address, "speedrunner"):
            if send_onchain_badge(wallet_address, "speedrunner", chain):
                awarded.append("Speedrunner")

    return awarded


