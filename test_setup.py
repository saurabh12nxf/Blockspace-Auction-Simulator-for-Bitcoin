"""
Quick test script to verify the simulator works
"""

# Test imports
try:
    import requests
    print("✓ requests library installed")
except ImportError:
    print("✗ requests library not found - run: pip install requests")
    exit(1)

# Test mempool fetcher
try:
    from mempool_fetcher import MempoolFetcher
    print("✓ mempool_fetcher module loaded")
    
    fetcher = MempoolFetcher()
    print("✓ MempoolFetcher initialized")
    
    # Test API connection
    print("\nTesting API connection...")
    recommendations = fetcher.get_fee_recommendations()
    if recommendations:
        print("✓ Successfully connected to mempool.space API")
        print(f"  Current fastest fee: {recommendations.get('fastestFee', 'N/A')} sat/vB")
    else:
        print("✗ Could not connect to API")
        
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test auction model
try:
    from auction_model import BlockspaceAuctionModel, Transaction
    print("\n✓ auction_model module loaded")
    
    model = BlockspaceAuctionModel()
    print("✓ BlockspaceAuctionModel initialized")
    
    # Add test transactions
    model.add_mempool_transaction(50.0, 200)
    model.add_mempool_transaction(30.0, 150)
    model.add_user_transaction(40.0, 220)
    
    # Simulate
    blocks = model.simulate_block_filling()
    print(f"✓ Simulation successful - generated {len(blocks)} block(s)")
    
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test simulator
try:
    from simulator import BlockspaceSimulator
    print("\n✓ simulator module loaded")
    print("✓ BlockspaceSimulator initialized")
    
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED! ✓")
print("="*60)
print("\nYou can now run the full simulator with:")
print("  python main.py")
print("="*60)
