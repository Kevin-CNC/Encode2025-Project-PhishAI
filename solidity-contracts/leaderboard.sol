// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SimpleLeaderboard {
    mapping(address => uint256) public scores;

    function submitScore(uint256 score) public {
        if (score > scores[msg.sender]) {
            scores[msg.sender] = score;
        }
    }

    function getScore(address player) public view returns (uint256) {
        return scores[player];
    }
}
