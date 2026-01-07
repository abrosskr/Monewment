import unittest
import os
import shutil
from src.ant_client.core.vault.shredder import VaultShredder

class TestDeepVault(unittest.TestCase):
    def setUp(self):
        self.test_dir = "temp_vault_test"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create a dummy file (Small for Striped RS performance)
        self.file_path = os.path.join(self.test_dir, "secret_plans.txt")
        self.original_content = b"Monewment Top Secret Blueprint: Phase 7 is Moon Base." * 10
        with open(self.file_path, "wb") as f:
            f.write(self.original_content)
            
        self.shredder = VaultShredder()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_shred_and_recover(self):
        print("\n🚀 Testing DeepVault Shredder...")
        
        # 1. Process
        result = self.shredder.process_file(self.file_path)
        shards = result["shards"]
        key = result["key"]
        
        print(f"✅ Sharded into {len(shards)} pieces. (Encrypted Size: {result['encrypted_size']} bytes)")
        
        # 2. Verify Shard Count (N=10 + M=4 = 14)
        self.assertEqual(len(shards), 14)
        
        # 3. Simulate Data Loss (Kill 4 shards)
        # We simulate loss by replacing them with empty bytes or removing them?
        # Our simplistic EC Decode expects joined bytes, so let's try to reconstruct with subset?
        # Reedsolo `decode` takes the FULL message (with potential errors).
        # So we must provide the "corrupted" byte stream where missing parts are zeroed out?
        # Alternatively, since we used `rsc.encode`, the output contains everything.
        # IF we want to test recovery properly with `reedsolo`, we need to simulate byte errors.
        
        # NOTE: Our current implementation of `ErasureCoding.encode` splits the RESULT of RS encoding.
        # This means `shards` contains [Data...Data...Parity...Parity].
        # If we lose a shard, we lose a chunk of the RS-encoded stream.
        # To recover, we should reconstruct the stream with "holes" where lost shards were.
        
        # Let's verify happy path first (ALL shards)
        recovered_happy = self.shredder.recover_file(shards, key, result["encrypted_size"])
        self.assertEqual(recovered_happy, self.original_content)
        print("✅ Happy Path Recovery Successful")
        
        # 4. Simulate Loss (Zero out 4 random shards)
        # This simulates "Missing File" from P2P network.
        # We fill the lost shard's slot with null bytes of same length.
        
        damaged_shards = list(shards)
        # Destroy index 0, 5, 10, 13
        for idx in [0, 5, 10, 13]:
            damaged_shards[idx] = None
            
        print("💥 4 Shards Destroyed (Simulated)")
        
        recovered_sad = self.shredder.recover_file(damaged_shards, key, result["encrypted_size"])
        self.assertEqual(recovered_sad, self.original_content)
        print("✅ Recovery from Partial Loss Successful")

if __name__ == "__main__":
    unittest.main()
