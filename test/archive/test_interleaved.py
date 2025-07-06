import os
import tempfile
import time
from pathlib import Path
from bitpaper.interleaved_core import InterleavedBitPaperEncoder, InterleavedBitPaperDecoder

def test_interleaved_encoding():
    print("Testing Interleaved BitPaper...")
    
    # Create test data
    test_data = b"This is an interleaved, signed, and encrypted message!"
    password = "my_secret_password_123"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        print(f"Original data: {test_data}")
        
        # Encode with interleaving
        encoder = InterleavedBitPaperEncoder(password, "private_key.pem", error_correction_level=0.1)
        decoder = InterleavedBitPaperDecoder(password, "public_key.pem", error_correction_level=0.1)
        
        # Encode
        print("\nEncoding with interleaving...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("\nDecoding with deinterleaving...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        print(f"Decoded data: {decoded_data}")
        
        # Verify
        if test_data == decoded_data:
            print("\n✓ Interleaved data matches perfectly!")
            return True
        else:
            print("\n✗ Interleaved data mismatch")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(test_file)

def test_corruption_resistance():
    print("\n=== Testing Corruption Resistance ===")
    
    test_data = b"Test message for corruption resistance"
    password = "test_password"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        encoder = InterleavedBitPaperEncoder(password, error_correction_level=0.2)
        decoder = InterleavedBitPaperDecoder(password, error_correction_level=0.2)
        
        # Encode
        bitstream = encoder.file_to_bitstream(test_file)
        img = encoder.bitstream_to_image(bitstream)
        
        # Decode normally
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        
        if test_data != decoded_data:
            print("✗ Normal decoding failed")
            return False
        
        # Test with corruption
        corrupted_bitstream = list(decoded_bitstream)
        corruption_count = 0
        
        # Corrupt every 100th bit (1% corruption)
        for i in range(0, len(corrupted_bitstream), 100):
            if i < len(corrupted_bitstream):
                corrupted_bitstream[i] = '1' if corrupted_bitstream[i] == '0' else '0'
                corruption_count += 1
        
        corrupted_bitstream = ''.join(corrupted_bitstream)
        print(f"Corrupted {corruption_count} bits out of {len(corrupted_bitstream)} ({corruption_count/len(corrupted_bitstream)*100:.1f}%)")
        
        try:
            recovered_data = decoder.bitstream_to_data(corrupted_bitstream)
            if test_data == recovered_data:
                print("✓ Corruption resistance successful!")
                return True
            else:
                print("✗ Corruption resistance failed")
                return False
        except ValueError as e:
            print(f"✗ Corruption resistance failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    print("=== Interleaved BitPaper Test Suite ===\n")
    
    success = True
    success &= test_interleaved_encoding()
    success &= test_corruption_resistance()
    
    if success:
        print("\n🎉 Interleaved tests passed!")
    else:
        print("\n❌ Some interleaved tests failed.") 