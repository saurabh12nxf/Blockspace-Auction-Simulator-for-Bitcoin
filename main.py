"""
Bitcoin Blockspace Auction Simulator - Main CLI Application

A realistic simulator that models how Bitcoin transactions compete for limited
blockspace based on fee rates. Uses real mempool data from mempool.space API.

Author: Bitcoin Protocol Engineer
Purpose: Educational tool for understanding Bitcoin's fee market dynamics
"""

import sys
from simulator import BlockspaceSimulator


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        BITCOIN BLOCKSPACE AUCTION SIMULATOR                      ║
║                                                                  ║
║        Understanding Bitcoin's Fee Market Dynamics               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help information about Bitcoin concepts"""
    help_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BITCOIN CONCEPTS EXPLAINED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 BLOCKSPACE:
   Bitcoin blocks have a maximum size of 4,000,000 weight units (~1-4MB).
   This limited space creates scarcity and competition among transactions.

💰 FEE RATE (sat/vB):
   Transactions pay fees measured in satoshis per virtual byte.
   Higher fee rates = higher priority for miners.
   Miners maximize revenue by selecting highest-paying transactions.

⚖️  VIRTUAL SIZE (vBytes):
   SegWit transactions get a "discount" on their size calculation.
   vSize = (3 × base size + total size) / 4
   This encourages use of SegWit for efficiency.

⛏️  MINER SELECTION:
   Miners use a "greedy algorithm" to fill blocks:
   1. Sort all pending transactions by fee rate (highest first)
   2. Include transactions until block is full
   3. Lower fee transactions wait for next block

🎯 THE AUCTION:
   The mempool is a continuous auction for blockspace.
   You compete against all other pending transactions.
   Your fee rate determines your priority in the queue.

⏱️  CONFIRMATION TIME:
   Average block time: ~10 minutes
   Your position in queue determines estimated wait time.
   New high-fee transactions can push you back in line.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    print(help_text)


def get_float_input(prompt: str, min_val: float = 0.0) -> float:
    """
    Get validated float input from user.
    
    Args:
        prompt: Input prompt to display
        min_val: Minimum acceptable value
    
    Returns:
        Validated float value
    """
    while True:
        try:
            value = float(input(prompt))
            if value < min_val:
                print(f"❌ Value must be at least {min_val}")
                continue
            return value
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)


def show_fee_recommendations(simulator: BlockspaceSimulator) -> None:
    """
    Display current fee recommendations.
    
    Args:
        simulator: BlockspaceSimulator instance
    """
    print("\n📊 Fetching current fee recommendations...")
    recommendations = simulator.get_fee_recommendations()
    
    if not recommendations:
        print("❌ Could not fetch fee recommendations")
        return
    
    print("\n" + "─"*60)
    print("CURRENT FEE RECOMMENDATIONS (sat/vB)")
    print("─"*60)
    print(f"🚀 Fastest (Next Block):     {recommendations.get('fastestFee', 'N/A')} sat/vB")
    print(f"⚡ Half Hour (~3 blocks):    {recommendations.get('halfHourFee', 'N/A')} sat/vB")
    print(f"🕐 One Hour (~6 blocks):     {recommendations.get('hourFee', 'N/A')} sat/vB")
    print(f"💵 Economy (Low Priority):   {recommendations.get('economyFee', 'N/A')} sat/vB")
    print(f"🔻 Minimum (Enter Mempool):  {recommendations.get('minimumFee', 'N/A')} sat/vB")
    print("─"*60)


def run_simulation(simulator: BlockspaceSimulator) -> None:
    """
    Run the main simulation flow.
    
    Args:
        simulator: BlockspaceSimulator instance
    """
    print("\n" + "="*70)
    print("TRANSACTION SIMULATION")
    print("="*70)
    
    # Get user input
    print("\nEnter your transaction details:")
    print("(Typical transaction sizes: 140-250 vBytes for simple sends,")
    print(" 400-600 vBytes for complex multi-input transactions)\n")
    
    vsize = get_float_input("Transaction size (vBytes): ", min_val=1.0)
    fee_rate = get_float_input("Proposed fee rate (sat/vB): ", min_val=1.0)
    
    # Run simulation
    print("\n🔄 Running simulation...")
    results = simulator.simulate_transaction(fee_rate, vsize)
    
    if results:
        simulator.print_simulation_results(results)
    else:
        print("❌ Simulation failed. Please try again.")


def main():
    """Main application entry point"""
    print_banner()
    
    # Initialize simulator
    simulator = BlockspaceSimulator()
    
    # Load mempool data
    print("🌐 Connecting to Bitcoin mempool...")
    if not simulator.load_mempool_data():
        print("\n❌ Failed to load mempool data. Please check your internet connection.")
        print("   The simulator requires access to mempool.space API.")
        sys.exit(1)
    
    # Main menu loop
    while True:
        print("\n" + "="*70)
        print("MAIN MENU")
        print("="*70)
        print("1. Simulate Transaction")
        print("2. View Current Fee Recommendations")
        print("3. Refresh Mempool Data")
        print("4. Learn About Bitcoin Concepts")
        print("5. Exit")
        print("="*70)
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                run_simulation(simulator)
                # Reset for next simulation
                simulator.reset_simulation()
                if not simulator.load_mempool_data():
                    print("⚠️  Warning: Could not refresh mempool data. Using cached data.")
            
            elif choice == '2':
                show_fee_recommendations(simulator)
            
            elif choice == '3':
                print("\n🔄 Refreshing mempool data...")
                simulator.reset_simulation()
                if simulator.load_mempool_data():
                    print("✅ Mempool data refreshed successfully")
                else:
                    print("❌ Failed to refresh mempool data")
            
            elif choice == '4':
                print_help()
            
            elif choice == '5':
                print("\n👋 Thank you for using Bitcoin Blockspace Auction Simulator!")
                print("   Keep learning about Bitcoin's fee market dynamics.\n")
                sys.exit(0)
            
            else:
                print("❌ Invalid option. Please select 1-5.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("   Please try again or restart the application.")


if __name__ == "__main__":
    main()
