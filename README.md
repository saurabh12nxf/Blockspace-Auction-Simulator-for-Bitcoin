# Bitcoin Blockspace Auction Simulator

A realistic, intermediate-level Python project that simulates how Bitcoin transactions compete for limited blockspace based on fee rates. This simulator uses real mempool data to provide accurate estimates of transaction confirmation times.

## 🎯 Project Overview

This simulator models Bitcoin's fee market dynamics by:
- Fetching real-time mempool data from mempool.space API
- Simulating how miners select transactions using fee-rate prioritization
- Estimating confirmation time and risk level for user transactions
- Providing educational insights into Bitcoin's blockspace auction mechanism

**This is NOT a toy calculator** — it implements the actual greedy algorithm that Bitcoin miners use to maximize fee revenue while respecting the 4,000,000 weight unit block limit.

## 🧠 Bitcoin Concepts Explained

### Blockspace Scarcity
Bitcoin blocks have a hard limit of **4,000,000 weight units** (approximately 1-4 MB depending on transaction types). This creates artificial scarcity where transactions must compete for inclusion.

### Fee Rate Prioritization
Transactions pay fees measured in **satoshis per virtual byte (sat/vB)**. Miners are economically incentivized to select the highest-paying transactions first, creating a continuous auction for blockspace.

### The Mempool
The mempool (memory pool) is where unconfirmed transactions wait. It's essentially a queue sorted by fee rate, where your position determines how quickly you get confirmed.

### Virtual Size (vSize)
SegWit transactions receive a "discount" in size calculation:
```
vSize = (3 × base_size + total_size) / 4
Weight = vSize × 4
```
This encourages adoption of SegWit for better network efficiency.

### Miner Block Construction
Miners use a **greedy knapsack algorithm**:
1. Sort all mempool transactions by fee rate (descending)
2. Fill block with highest-paying transactions until weight limit reached
3. Remaining transactions wait for next block

This simulator implements this exact algorithm.

## 🏗️ Project Structure

```
Blockspace Auction Simulator for Bitcoin/
│
├── main.py                 # CLI application entry point
├── simulator.py            # Orchestrates simulation logic
├── auction_model.py        # Core blockspace auction algorithm
├── mempool_fetcher.py      # API integration for mempool data
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Module Breakdown

**`mempool_fetcher.py`**
- Fetches real-time mempool data from mempool.space API
- Extracts transaction fee distributions
- Provides fee recommendations for different priority levels

**`auction_model.py`**
- Implements the core blockspace auction mechanism
- Simulates block filling using greedy algorithm
- Assesses confirmation risk based on queue position
- Models Bitcoin's 4M weight unit consensus rule

**`simulator.py`**
- Coordinates mempool fetching and auction simulation
- Generates detailed analysis and risk assessment
- Formats results for user-friendly output

**`main.py`**
- Interactive CLI interface
- Input validation and error handling
- Educational content about Bitcoin concepts

## 🚀 How to Run

### Prerequisites
- Python 3.7 or higher
- Internet connection (for mempool.space API)

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd "Blockspace Auction Simulator for Bitcoin"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the simulator:**
```bash
python main.py
```

## 📊 Example Usage

### Example Session Output

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        BITCOIN BLOCKSPACE AUCTION SIMULATOR                      ║
║                                                                  ║
║        Understanding Bitcoin's Fee Market Dynamics               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

🌐 Connecting to Bitcoin mempool...
Fetching mempool data from https://mempool.space/api/v1/fees/mempool-blocks...
✓ Successfully fetched 8 projected mempool blocks
Loading 40 representative transactions into model...
✓ Loaded 40 transactions from 8 projected blocks

======================================================================
MAIN MENU
======================================================================
1. Simulate Transaction
2. View Current Fee Recommendations
3. Refresh Mempool Data
4. Learn About Bitcoin Concepts
5. Exit
======================================================================

Select option (1-5): 2

📊 Fetching current fee recommendations...

────────────────────────────────────────────────────────────────
CURRENT FEE RECOMMENDATIONS (sat/vB)
────────────────────────────────────────────────────────────────
🚀 Fastest (Next Block):     45 sat/vB
⚡ Half Hour (~3 blocks):    38 sat/vB
🕐 One Hour (~6 blocks):     32 sat/vB
💵 Economy (Low Priority):   28 sat/vB
🔻 Minimum (Enter Mempool):  12 sat/vB
────────────────────────────────────────────────────────────────

Select option (1-5): 1

======================================================================
TRANSACTION SIMULATION
======================================================================

Enter your transaction details:
(Typical transaction sizes: 140-250 vBytes for simple sends,
 400-600 vBytes for complex multi-input transactions)

Transaction size (vBytes): 220
Proposed fee rate (sat/vB): 40

🔄 Running simulation...
Fetching mempool data from https://mempool.space/api/v1/fees/mempool-blocks...
✓ Successfully fetched 8 projected mempool blocks
Loading 40 representative transactions into model...
✓ Loaded 40 transactions from 8 projected blocks

Simulating block construction...

======================================================================
BITCOIN BLOCKSPACE AUCTION SIMULATION RESULTS
======================================================================

📝 YOUR TRANSACTION:
   Size: 220 vBytes (880 weight units)
   Fee Rate: 40.0 sat/vB
   Total Fee: 8800 sats (0.00008800 BTC)

📍 PROJECTED POSITION:
   Block Number: #1 (next block = #1)
   Position in Block: #12
   Overall Queue Position: #12
   Estimated Wait Time: ~10 minutes

⚠️  CONFIRMATION RISK: 🟢 Low
   Your transaction is projected for the next block with a fee rate of 40.0 
   sat/vB, which is above the current median of 35.2 sat/vB. There are 11 
   transactions ahead of yours, but your fee rate is competitive.

💰 FEE ANALYSIS:
   Your Fee Rate: 40.0 sat/vB
   Next Block Median: 35.2 sat/vB
   Difference: +4.8 sat/vB (+13.6%)

🌐 MEMPOOL CONTEXT:
   Total Pending Transactions: 40
   Projected Blocks: 8
   Next Block Size: 20 transactions
   Transactions Ahead of Yours: 11

======================================================================
Note: Estimates based on current mempool state. Actual confirmation
time may vary based on new transactions entering the mempool.
======================================================================
```

## 🎓 Educational Value

This project demonstrates understanding of:

1. **Bitcoin Protocol Mechanics**
   - Block weight limits and consensus rules
   - Transaction fee economics
   - Mempool dynamics

2. **Algorithm Design**
   - Greedy knapsack algorithm for block filling
   - Priority queue simulation
   - Risk assessment heuristics

3. **Software Engineering**
   - Modular architecture with separation of concerns
   - API integration and error handling
   - Clean code with comprehensive documentation

4. **Real-World Application**
   - Using live data from production Bitcoin network
   - Practical tool for fee estimation
   - Educational resource for learning Bitcoin

## 🔬 Technical Details

### Block Filling Algorithm

The simulator implements the standard miner algorithm:

```python
def simulate_block_filling(transactions):
    # Sort by fee rate (highest first)
    sorted_txs = sorted(transactions, key=lambda tx: tx.fee_rate, reverse=True)
    
    blocks = []
    current_block = []
    current_weight = 0
    
    for tx in sorted_txs:
        if current_weight + tx.weight <= MAX_BLOCK_WEIGHT:
            current_block.append(tx)
            current_weight += tx.weight
        else:
            blocks.append(current_block)
            current_block = [tx]
            current_weight = tx.weight
    
    return blocks
```

### Risk Assessment Logic

- **Low Risk**: Next block + fee ≥ median
- **Medium Risk**: Next block but fee < median, OR blocks 2-3
- **High Risk**: Blocks 4-6 (~40-60 minutes)
- **Very High Risk**: Block 7+ (~70+ minutes)

## 🛠️ Potential Extensions

Ideas for further development:
- RBF (Replace-By-Fee) simulation
- CPFP (Child-Pays-For-Parent) analysis
- Historical fee rate trends
- Mempool congestion alerts
- Multi-transaction batch optimization
- Lightning Network comparison

## 📚 Resources

- [Bitcoin Developer Guide](https://developer.bitcoin.org/devguide/)
- [mempool.space API Documentation](https://mempool.space/docs/api)
- [BIP 141 - SegWit](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki)
- [Bitcoin Transaction Fee Economics](https://bitcoinops.org/en/topics/fee-estimation/)

## 🎯 Interview Talking Points

When discussing this project:

1. **Technical Depth**: "I implemented the actual greedy algorithm miners use, respecting Bitcoin's 4M weight unit consensus rule."

2. **Real Data**: "The simulator uses live mempool data from mempool.space, not simulated data, making estimates realistic."

3. **Bitcoin Knowledge**: "I modeled key concepts like vSize calculation, fee rate prioritization, and blockspace scarcity."

4. **Software Design**: "Clean modular architecture with separation between data fetching, business logic, and presentation."

5. **Practical Application**: "This is a real tool someone could use to optimize their transaction fees on Bitcoin mainnet."

## 📄 License

Educational project for learning Bitcoin protocol development.

## 👨‍💻 Author

Built as an intermediate-level project demonstrating Bitcoin protocol knowledge and Python development skills.

---

**Note**: This simulator provides estimates based on current mempool state. Actual confirmation times may vary as new transactions enter the mempool and network conditions change.
