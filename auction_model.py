"""
Bitcoin Blockspace Auction Model

This module implements the core logic for simulating Bitcoin's blockspace auction.
It models how transactions compete for limited block space based on fee rates.

Key Bitcoin Concepts:
1. Block Weight Limit: 4,000,000 weight units (~1MB legacy, ~4MB theoretical max)
2. Fee Rate Priority: Miners maximize revenue by selecting highest fee-rate transactions
3. Blockspace Scarcity: Limited space creates a competitive auction environment
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for transaction confirmation"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


@dataclass
class Transaction:
    """
    Represents a Bitcoin transaction in the mempool.
    
    Attributes:
        fee_rate: Fee rate in satoshis per virtual byte (sat/vB)
        vsize: Virtual size in vBytes (accounts for SegWit discount)
        fee: Total fee in satoshis
        is_user_tx: Whether this is the user's transaction being simulated
    """
    fee_rate: float
    vsize: float
    fee: float
    is_user_tx: bool = False
    
    @property
    def weight(self) -> int:
        """
        Calculate transaction weight.
        
        Weight units = vSize * 4
        This is the actual metric used for block limits.
        """
        return int(self.vsize * 4)
    
    def __lt__(self, other):
        """
        Comparison for sorting by fee rate (descending).
        Higher fee rates have priority.
        """
        return self.fee_rate > other.fee_rate


class BlockspaceAuctionModel:
    """
    Models the Bitcoin blockspace auction mechanism.
    
    This simulates how miners select transactions to maximize fee revenue
    while respecting the block weight limit.
    """
    
    # Bitcoin consensus constants
    MAX_BLOCK_WEIGHT = 4_000_000  # 4 million weight units
    AVERAGE_BLOCK_TIME = 600      # 10 minutes in seconds
    
    def __init__(self):
        """Initialize the auction model"""
        self.mempool_transactions: List[Transaction] = []
    
    def add_mempool_transaction(self, fee_rate: float, vsize: float) -> None:
        """
        Add a transaction to the mempool.
        
        Args:
            fee_rate: Fee rate in sat/vB
            vsize: Virtual size in vBytes
        """
        fee = fee_rate * vsize
        tx = Transaction(fee_rate=fee_rate, vsize=vsize, fee=fee)
        self.mempool_transactions.append(tx)
    
    def add_user_transaction(self, fee_rate: float, vsize: float) -> Transaction:
        """
        Add the user's transaction to simulate.
        
        Args:
            fee_rate: User's proposed fee rate in sat/vB
            vsize: Transaction size in vBytes
        
        Returns:
            The created user transaction
        """
        fee = fee_rate * vsize
        user_tx = Transaction(
            fee_rate=fee_rate,
            vsize=vsize,
            fee=fee,
            is_user_tx=True
        )
        self.mempool_transactions.append(user_tx)
        return user_tx
    
    def simulate_block_filling(self) -> List[List[Transaction]]:
        """
        Simulate how miners would fill blocks from the mempool.
        
        Algorithm:
        1. Sort all transactions by fee rate (descending)
        2. Greedily fill blocks up to weight limit
        3. Continue until mempool is empty or transactions too low-fee
        
        Returns:
            List of blocks, where each block is a list of transactions
        
        This implements the "greedy knapsack" algorithm that rational miners use.
        """
        # Sort transactions by fee rate (highest first)
        sorted_txs = sorted(self.mempool_transactions, key=lambda tx: tx.fee_rate, reverse=True)
        
        blocks = []
        current_block = []
        current_weight = 0
        
        for tx in sorted_txs:
            tx_weight = tx.weight
            
            # Check if transaction fits in current block
            if current_weight + tx_weight <= self.MAX_BLOCK_WEIGHT:
                current_block.append(tx)
                current_weight += tx_weight
            else:
                # Current block is full, start new block
                if current_block:
                    blocks.append(current_block)
                current_block = [tx]
                current_weight = tx_weight
        
        # Add the last block if it has transactions
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def find_user_transaction_position(self, blocks: List[List[Transaction]]) -> Tuple[int, int, int]:
        """
        Find where the user's transaction would be included.
        
        Args:
            blocks: Simulated blocks from simulate_block_filling()
        
        Returns:
            Tuple of (block_number, position_in_block, total_position)
            Block numbers are 1-indexed (1 = next block)
        """
        total_position = 0
        
        for block_idx, block in enumerate(blocks):
            for tx_idx, tx in enumerate(block):
                total_position += 1
                if tx.is_user_tx:
                    return (block_idx + 1, tx_idx + 1, total_position)
        
        # Transaction not found (shouldn't happen)
        return (-1, -1, -1)
    
    def assess_confirmation_risk(self, block_number: int, fee_rate: float, 
                                 next_block_median: float) -> RiskLevel:
        """
        Assess the risk level for transaction confirmation.
        
        Args:
            block_number: Which block the transaction would be in (1-indexed)
            fee_rate: User's fee rate
            next_block_median: Median fee rate of next block
        
        Returns:
            Risk level enum
        
        Risk Assessment Logic:
        - Block 1 + fee >= median: LOW (very likely next block)
        - Block 1 + fee < median: MEDIUM (next block but below median)
        - Block 2-3: MEDIUM (confirmation within 30 min)
        - Block 4-6: HIGH (30-60 min wait)
        - Block 7+: VERY_HIGH (1+ hour wait, may be pushed out)
        """
        if block_number == 1:
            if fee_rate >= next_block_median:
                return RiskLevel.LOW
            else:
                return RiskLevel.MEDIUM
        elif block_number <= 3:
            return RiskLevel.MEDIUM
        elif block_number <= 6:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def generate_risk_explanation(self, block_number: int, risk_level: RiskLevel,
                                  fee_rate: float, next_block_median: float,
                                  total_competing_txs: int) -> str:
        """
        Generate human-readable explanation of the risk assessment.
        
        Args:
            block_number: Projected block number
            risk_level: Assessed risk level
            fee_rate: User's fee rate
            next_block_median: Median fee of next block
            total_competing_txs: Number of transactions ahead in queue
        
        Returns:
            Detailed explanation string
        """
        explanations = {
            RiskLevel.LOW: (
                f"Your transaction is projected for the next block with a fee rate "
                f"of {fee_rate:.1f} sat/vB, which is above the current median of "
                f"{next_block_median:.1f} sat/vB. There are {total_competing_txs} "
                f"transactions ahead of yours, but your fee rate is competitive."
            ),
            RiskLevel.MEDIUM: (
                f"Your transaction is projected for block {block_number} "
                f"(~{block_number * 10} minutes). Your fee rate of {fee_rate:.1f} sat/vB "
                f"is competitive but there are {total_competing_txs} higher-paying "
                f"transactions ahead. Confirmation is likely but not guaranteed in the next block."
            ),
            RiskLevel.HIGH: (
                f"Your transaction is projected for block {block_number} "
                f"(~{block_number * 10} minutes). Your fee rate of {fee_rate:.1f} sat/vB "
                f"is below the current competitive range. There are {total_competing_txs} "
                f"higher-paying transactions ahead. If mempool congestion increases, "
                f"your transaction may be pushed further back."
            ),
            RiskLevel.VERY_HIGH: (
                f"Your transaction is projected for block {block_number} or later "
                f"(~{block_number * 10}+ minutes). Your fee rate of {fee_rate:.1f} sat/vB "
                f"is significantly below competitive rates. With {total_competing_txs} "
                f"transactions ahead, there's high risk of delayed confirmation or being "
                f"pushed out if new higher-fee transactions enter the mempool. Consider "
                f"using RBF (Replace-By-Fee) to increase your fee if time-sensitive."
            )
        }
        
        return explanations.get(risk_level, "Unable to assess risk.")
    
    def calculate_mempool_statistics(self, blocks: List[List[Transaction]]) -> Dict:
        """
        Calculate statistics about the simulated mempool state.
        
        Args:
            blocks: Simulated blocks
        
        Returns:
            Dictionary with mempool statistics
        """
        total_txs = sum(len(block) for block in blocks)
        total_fees = sum(tx.fee for block in blocks for tx in block)
        
        if not blocks or not blocks[0]:
            return {
                'total_transactions': total_txs,
                'total_blocks': len(blocks),
                'total_fees': total_fees,
                'next_block_txs': 0,
                'next_block_fee_range': (0, 0)
            }
        
        next_block = blocks[0]
        next_block_fees = [tx.fee_rate for tx in next_block]
        
        return {
            'total_transactions': total_txs,
            'total_blocks': len(blocks),
            'total_fees': total_fees,
            'next_block_txs': len(next_block),
            'next_block_fee_range': (min(next_block_fees), max(next_block_fees)) if next_block_fees else (0, 0)
        }
