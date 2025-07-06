import os
import tempfile
from pathlib import Path
from bitpaper.secure_core import SecureBitPaperEncoder, SecureBitPaperDecoder

def test_error_correction():
    print("Testing Error Correction...")
    
    # Create test data
    test_data = b"This is a test file for error correction testing. " * 3
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        
        # Test with 10% error correction
        encoder = SecureBitPaperEncoder(error_correction_level=0.1)
        decoder = SecureBitPaperDecoder(error_correction_level=0.1)
        
        # Encode
        print("\nEncoding with 10% error correction...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("\nDecoding with error correction...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        
        # Verify
        if test_data == decoded_data:
            print("✓ Data matches perfectly with error correction!")
        else:
            print("✗ Data mismatch with error correction")
            return False
        
        # Test corruption resistance
        print("\nTesting corruption resistance...")
        corrupted_bitstream = list(decoded_bitstream)
        corruption_count = 0
        
        # Corrupt every 50th bit (2% corruption)
        for i in range(0, len(corrupted_bitstream), 50):
            if i < len(corrupted_bitstream):
                corrupted_bitstream[i] = '1' if corrupted_bitstream[i] == '0' else '0'
                corruption_count += 1
        
        corrupted_bitstream = ''.join(corrupted_bitstream)
        print(f"Corrupted {corruption_count} bits out of {len(corrupted_bitstream)} ({corruption_count/len(corrupted_bitstream)*100:.1f}%)")
        
        try:
            recovered_data = decoder.bitstream_to_data(corrupted_bitstream)
            if test_data == recovered_data:
                print("✓ Error correction successful!")
                return True
            else:
                print("✗ Error correction failed")
                return False
        except ValueError as e:
            print(f"✗ Error correction failed: {e}")
            return False
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
    finally:
        os.unlink(test_file)

def test_data_capacity():
    print("\n=== Data Capacity Test ===")
    
    encoder = SecureBitPaperEncoder()
    
    # Calculate maximum capacity
    a4_width, a4_height = 2480, 3508
    max_cols = encoder.bits_per_row
    max_rows = (a4_height - 8) // encoder.cell_size
    max_bits = max_cols * max_rows
    
    print(f"Maximum bits per A4 page: {max_bits:,}")
    print(f"Maximum bytes per A4 page: {max_bits // 8:,}")
    
    # Test with different error correction levels
    for ecc_level in [0.0, 0.1, 0.2, 0.25]:
        test_data = b"Test data for capacity measurement. " * 10
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            f.write(test_data)
            test_file = f.name
        
        try:
            encoder = SecureBitPaperEncoder(error_correction_level=ecc_level)
            bitstream = encoder.file_to_bitstream(test_file)
            print(f"ECC {ecc_level*100:.0f}%: {len(bitstream)} bits ({len(bitstream)//8} bytes)")
        except Exception as e:
            print(f"ECC {ecc_level*100:.0f}%: Failed - {e}")
        finally:
            os.unlink(test_file)
    
    return True

if __name__ == "__main__":
    print("=== Error Correction Test Suite ===\n")
    
    success = True
    success &= test_error_correction()
    success &= test_data_capacity()
    
    if success:
        print("\n🎉 Error correction tests passed!")
    else:
        print("\n❌ Some error correction tests failed.") 