"""
Bitcoin Blockspace Auction Simulator

This module orchestrates the simulation by combining mempool data fetching
with the auction model to provide realistic transaction confirmation estimates.
"""

from typing import Dict, Optional
from mempool_fetcher import MempoolFetcher
from auction_model import BlockspaceAuctionModel, Transaction, RiskLevel


class BlockspaceSimulator:
    """
    Main simulator class that coordinates mempool fetching and auction simulation.
    """
    
    def __init__(self):
        """Initialize the simulator with fetcher and model components"""
        self.fetcher = MempoolFetcher()
        self.model = BlockspaceAuctionModel()
    
    def load_mempool_data(self) -> bool:
        """
        Fetch current mempool data and load it into the auction model.
        
        Returns:
            True if data loaded successfully, False otherwise
        """
        # Fetch mempool blocks from API
        mempool_blocks = self.fetcher.fetch_mempool_blocks()
        
        if not mempool_blocks:
            print("✗ Failed to fetch mempool data")
            return False
        
        # Extract transaction data
        transactions = self.fetcher.extract_transactions_data(mempool_blocks)
        
        if not transactions:
            print("✗ No transaction data available")
            return False
        
        # Load transactions into the model
        print(f"Loading {len(transactions)} representative transactions into model...")
        for tx_data in transactions:
            self.model.add_mempool_transaction(
                fee_rate=tx_data['fee_rate'],
                vsize=tx_data['vsize']
            )
        
        print(f"✓ Loaded {len(transactions)} transactions from {len(mempool_blocks)} projected blocks")
        return True
    
    def simulate_transaction(self, fee_rate: float, vsize: float) -> Optional[Dict]:
        """
        Simulate a user transaction and determine its confirmation outlook.
        
        Args:
            fee_rate: User's proposed fee rate in sat/vB
            vsize: Transaction size in vBytes
        
        Returns:
            Dictionary with simulation results, or None if simulation fails
        """
        # Add user transaction to model
        user_tx = self.model.add_user_transaction(fee_rate, vsize)
        
        # Simulate block filling
        print("\nSimulating block construction...")
        blocks = self.model.simulate_block_filling()
        
        if not blocks:
            print("✗ Simulation failed: no blocks generated")
            return None
        
        # Find user transaction position
        block_num, pos_in_block, total_pos = self.model.find_user_transaction_position(blocks)
        
        if block_num == -1:
            print("✗ User transaction not found in simulation")
            return None
        
        # Get mempool summary for context
        mempool_blocks = self.fetcher.cached_data
        mempool_summary = self.fetcher.get_mempool_summary(mempool_blocks) if mempool_blocks else {}
        next_block_median = mempool_summary.get('next_block_median', 0)
        
        # Assess risk
        risk_level = self.model.assess_confirmation_risk(block_num, fee_rate, next_block_median)
        risk_explanation = self.model.generate_risk_explanation(
            block_num, risk_level, fee_rate, next_block_median, total_pos - 1
        )
        
        # Calculate statistics
        stats = self.model.calculate_mempool_statistics(blocks)
        
        # Compile results
        results = {
            'user_transaction': {
                'fee_rate': fee_rate,
                'vsize': vsize,
                'total_fee': user_tx.fee,
                'weight': user_tx.weight
            },
            'position': {
                'block_number': block_num,
                'position_in_block': pos_in_block,
                'total_position': total_pos,
                'estimated_time_minutes': block_num * 10
            },
            'risk': {
                'level': risk_level.value,
                'explanation': risk_explanation
            },
            'mempool_context': {
                'total_pending_blocks': stats['total_blocks'],
                'total_pending_txs': stats['total_transactions'],
                'next_block_txs': stats['next_block_txs'],
                'next_block_median_fee': next_block_median,
                'competing_transactions': total_pos - 1
            },
            'fee_comparison': {
                'your_fee_rate': fee_rate,
                'next_block_median': next_block_median,
                'difference': fee_rate - next_block_median,
                'percentage_vs_median': ((fee_rate / next_block_median - 1) * 100) if next_block_median > 0 else 0
            }
        }
        
        return results
    
    def get_fee_recommendations(self) -> Optional[Dict]:
        """
        Get current fee recommendations from mempool.space.
        
        Returns:
            Dictionary with fee recommendations for different priority levels
        """
        return self.fetcher.get_fee_recommendations()
    
    def reset_simulation(self) -> None:
        """
        Reset the simulator state for a new simulation.
        """
        self.model = BlockspaceAuctionModel()
    
    def print_simulation_results(self, results: Dict) -> None:
        """
        Pretty-print simulation results to console.
        
        Args:
            results: Simulation results dictionary
        """
        print("\n" + "="*70)
        print("BITCOIN BLOCKSPACE AUCTION SIMULATION RESULTS")
        print("="*70)
        
        # Transaction details
        tx = results['user_transaction']
        print(f"\n📝 YOUR TRANSACTION:")
        print(f"   Size: {tx['vsize']:.0f} vBytes ({tx['weight']:,} weight units)")
        print(f"   Fee Rate: {tx['fee_rate']:.1f} sat/vB")
        print(f"   Total Fee: {tx['total_fee']:.0f} sats ({tx['total_fee']/100_000_000:.8f} BTC)")
        
        # Position
        pos = results['position']
        print(f"\n📍 PROJECTED POSITION:")
        print(f"   Block Number: #{pos['block_number']} (next block = #1)")
        print(f"   Position in Block: #{pos['position_in_block']}")
        print(f"   Overall Queue Position: #{pos['total_position']}")
        print(f"   Estimated Wait Time: ~{pos['estimated_time_minutes']} minutes")
        
        # Risk assessment
        risk = results['risk']
        risk_emoji = {
            'Low': '🟢',
            'Medium': '🟡',
            'High': '🟠',
            'Very High': '🔴'
        }
        print(f"\n⚠️  CONFIRMATION RISK: {risk_emoji.get(risk['level'], '⚪')} {risk['level']}")
        print(f"   {risk['explanation']}")
        
        # Fee comparison
        fee_cmp = results['fee_comparison']
        print(f"\n💰 FEE ANALYSIS:")
        print(f"   Your Fee Rate: {fee_cmp['your_fee_rate']:.1f} sat/vB")
        print(f"   Next Block Median: {fee_cmp['next_block_median']:.1f} sat/vB")
        diff_sign = "+" if fee_cmp['difference'] >= 0 else ""
        print(f"   Difference: {diff_sign}{fee_cmp['difference']:.1f} sat/vB ({diff_sign}{fee_cmp['percentage_vs_median']:.1f}%)")
        
        # Mempool context
        ctx = results['mempool_context']
        print(f"\n🌐 MEMPOOL CONTEXT:")
        print(f"   Total Pending Transactions: {ctx['total_pending_txs']:,}")
        print(f"   Projected Blocks: {ctx['total_pending_blocks']}")
        print(f"   Next Block Size: {ctx['next_block_txs']} transactions")
        print(f"   Transactions Ahead of Yours: {ctx['competing_transactions']:,}")
        
        print("\n" + "="*70)
        print("Note: Estimates based on current mempool state. Actual confirmation")
        print("time may vary based on new transactions entering the mempool.")
        print("="*70 + "\n")
