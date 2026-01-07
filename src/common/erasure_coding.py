from reedsolo import RSCodec, ReedSolomonError

class ErasureCoding:
    def __init__(self, n: int = 10, m: int = 4):
        """
        N: Original Data Shards
        M: Parity Shards
        Total Shards = N + M
        Can recover from M losses.
        """
        self.n = n
        self.m = m
        self.rsc = RSCodec(m)

    def encode(self, data: bytes) -> List[bytes]:
        """
        Striped Encoding (RAID-style).
        Splits data into N-byte chunks (Stripes).
        Computes M parity bytes for each stripe.
        Distributed to N+M shards.
        """
        # 1. Pad data to be multiple of N
        remainder = len(data) % self.n
        if remainder != 0:
            padding = self.n - remainder
            data += b'\x00' * padding
            
        # 2. Initialize Shards
        # We use bytearrays for speed
        shards = [bytearray() for _ in range(self.n + self.m)]
        
        # 3. Iterate over stripes (N bytes at a time)
        # Performance: This loop is slow in Python for large files.
        # DeepVault v2.0 Production must use C-extension (zfec).
        chunk_size = self.n
        for i in range(0, len(data), chunk_size):
            stripe = data[i : i + chunk_size]
            
            # RS Encode: Input N bytes -> Output N+M bytes
            # rsc.encode returns bytearray of (stripe + parity)
            encoded_stripe = self.rsc.encode(stripe)
            
            # Distribute to shards
            for k in range(self.n + self.m):
                shards[k].append(encoded_stripe[k])
                
        # Return as immutable bytes
        return [bytes(s) for s in shards]

    def decode(self, shards: List[bytes]) -> bytes:
        """
        Striped Decoding.
        shards: List where missing shards are None.
        """
        # 1. Identify missing indices
        missing_indices = [i for i, s in enumerate(shards) if s is None]
        valid_indices = [i for i, s in enumerate(shards) if s is not None]
        
        if not valid_indices:
            raise ValueError("All shards missing.")
            
        # Determine shard size from first valid shard
        shard_size = len(shards[valid_indices[0]])
        num_shards = self.n + self.m
        
        # Global erase positions (Since we lose whole shards, the relative index in stripe is constant)
        # If Shard k is lost, then Byte k in EVERY stripe is lost.
        erase_pos = missing_indices
        
        output_buffer = bytearray()
        
        # 2. Iterate row by row (byte by byte from each shard)
        for i in range(shard_size):
            # Construct stripe buffer (N+M bytes)
            stripe_buffer = bytearray(num_shards)
            
            for k in range(num_shards):
                if shards[k] is None:
                    # Missing (Value doesn't matter as long as erase_pos is set)
                    stripe_buffer[k] = 0
                else:
                    stripe_buffer[k] = shards[k][i]
            
            # RS Decode
            try:
                # Returns N bytes of original data
                decoded_stripe = self.rsc.decode(stripe_buffer, erase_pos=erase_pos)[0]
                # The result from rsc.decode is (message, parity_check, ...)
                # Wait, rsc.decode returns the MESSAGE part (Data) only?
                # Check reedsolo docs/code.
                # It usually returns the full corrected message+ecc. 
                # NO. rsc.decode returns (decoded_msg, decoded_ecc, errat).
                # decoded_msg is the original message (first N bytes).
                output_buffer.extend(decoded_stripe)
            except (ReedSolomonError, ValueError, IndexError):
                 raise ValueError("Unrecoverable error in stripe.")
                 
        return bytes(output_buffer)
