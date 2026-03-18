import time
import sys
# Pridanie app cesty do modulu
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.domains.portfolio import get_portfolio

def test_cache():
    print("--- 1. Volanie funkcie ---")
    start1 = time.time()
    res1 = get_portfolio()
    dur1 = time.time() - start1
    print(f"Čas prvej odpovede: {dur1:.4f}s")
    
    print("\n--- 2. Volanie z LRU Cache ---")
    start2 = time.time()
    res2 = get_portfolio()
    dur2 = time.time() - start2
    print(f"Čas druhej odpovede (z cache): {dur2:.4f}s")

if __name__ == "__main__":
    test_cache()
