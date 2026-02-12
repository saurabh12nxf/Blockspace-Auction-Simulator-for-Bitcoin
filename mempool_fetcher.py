"""
Mempool Data Fetcher Module

This module handles fetching real-time mempool data from the mempool.space API.
It retrieves the current state of pending transactions waiting for confirmation.

Bitcoin Concept:
The mempool (memory pool) is where unconfirmed transactions wait before being
included in a block. Miners select transactions from the mempool based on fee rates.
"""

import requests
from typing import List, Dict, Optional
import time


class MempoolFetcher:
    """
    Fetches and processes mempool data from mempool.space API.
    
    The mempool.space API provides projected mempool blocks, which show how
    transactions would be organized into blocks based on current fee rates.
    """
    
    BASE_URL = "https://mempool.space/api/v1"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the mempool fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.last_fetch_time = None
        self.cached_data = None
    
    def fetch_mempool_blocks(self) -> Optional[List[Dict]]:
        """
        Fetch projected mempool blocks from the API.
        
        Returns:
            List of mempool block dictionaries, or None if fetch fails.
            Each block contains transaction data organized by fee rate.
        
        API Response Structure:
        Each mempool block contains:
        - blockSize: Total size in bytes
        - blockVSize: Total virtual size in vBytes
        - nTx: Number of transactions
        - totalFees: Total fees in satoshis
        - medianFee: Median fee rate in sat/vB
        - feeRange: Array of fee rates [min, max, 10th percentile, 25th, 50th, 75th, 90th]
        """
        endpoint = f"{self.BASE_URL}/fees/mempool-blocks"
        
        try:
            print(f"Fetching mempool data from {endpoint}...")
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            self.cached_data = data
            self.last_fetch_time = time.time()
            
            print(f"✓ Successfully fetched {len(data)} projected mempool blocks")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching mempool data: {e}")
            return None
    
    def get_fee_recommendations(self) -> Optional[Dict[str, int]]:
        """
        Fetch current fee recommendations for different priority levels.
        
        Returns:
            Dictionary with fee recommendations in sat/vB:
            - fastestFee: Next block confirmation (high priority)
            - halfHourFee: ~30 minutes confirmation
            - hourFee: ~1 hour confirmation
            - economyFee: Low priority (1+ hours)
            - minimumFee: Minimum to enter mempool
        """
        endpoint = f"{self.BASE_URL}/fees/recommended"
        
        try:
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching fee recommendations: {e}")
            return None
    
    def extract_transactions_data(self, mempool_blocks: List[Dict]) -> List[Dict]:
        """
        Extract and flatten transaction data from mempool blocks.
        
        Args:
            mempool_blocks: Raw mempool blocks from API
        
        Returns:
            List of transaction dictionaries with fee rate and size info
        
        Note: The API provides aggregated data, so we approximate individual
        transactions based on fee ranges and block statistics.
        """
        transactions = []
        
        for block_idx, block in enumerate(mempool_blocks):
            # Extract fee range data
            fee_range = block.get('feeRange', [])
            if not fee_range or len(fee_range) < 2:
                continue
            
            # Fee range format: [min, max, 10th, 25th, 50th, 75th, 90th percentile]
            min_fee = fee_range[0]
            max_fee = fee_range[1]
            median_fee = block.get('medianFee', fee_range[4] if len(fee_range) > 4 else min_fee)
            
            # Approximate transaction distribution
            # We create representative transactions at different fee levels
            num_tx = block.get('nTx', 0)
            block_vsize = block.get('blockVSize', 0)
            
            if num_tx > 0 and block_vsize > 0:
                avg_tx_size = block_vsize / num_tx
                
                # Create representative transactions at different fee percentiles
                fee_levels = [
                    (max_fee, 0.1),      # Top 10% highest fees
                    (fee_range[6] if len(fee_range) > 6 else median_fee, 0.2),  # 75-90th percentile
                    (median_fee, 0.4),   # Around median
                    (fee_range[3] if len(fee_range) > 3 else min_fee, 0.2),     # 25-50th percentile
                    (min_fee, 0.1)       # Bottom 10%
                ]
                
                for fee_rate, proportion in fee_levels:
                    transactions.append({
                        'fee_rate': fee_rate,
                        'vsize': avg_tx_size,
                        'block_position': block_idx,
                        'fee': fee_rate * avg_tx_size
                    })
        
        return transactions
    
    def get_mempool_summary(self, mempool_blocks: List[Dict]) -> Dict:
        """
        Generate a summary of current mempool state.
        
        Args:
            mempool_blocks: Mempool blocks data
        
        Returns:
            Dictionary with mempool statistics
        """
        if not mempool_blocks:
            return {}
        
        total_tx = sum(block.get('nTx', 0) for block in mempool_blocks)
        total_vsize = sum(block.get('blockVSize', 0) for block in mempool_blocks)
        
        # Get fee range from first block (highest priority transactions)
        first_block = mempool_blocks[0] if mempool_blocks else {}
        fee_range = first_block.get('feeRange', [])
        
        return {
            'total_pending_tx': total_tx,
            'total_pending_vsize': total_vsize,
            'projected_blocks': len(mempool_blocks),
            'highest_fee_rate': fee_range[1] if len(fee_range) > 1 else 0,
            'lowest_fee_rate': mempool_blocks[-1].get('feeRange', [0])[0] if mempool_blocks else 0,
            'next_block_median': first_block.get('medianFee', 0)
        }
