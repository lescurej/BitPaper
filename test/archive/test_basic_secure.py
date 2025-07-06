import os
import tempfile
from pathlib import Path
from bitpaper.secure_core import SecureBitPaperEncoder, SecureBitPaperDecoder

def test_basic_secure():
    print("Testing Basic Secure BitPaper...")
    
    # Create test data
    test_data = b"Hello World! This is a test."
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        print(f"Original data: {test_data}")
        
        # Use no error correction for simple test
        encoder = SecureBitPaperEncoder(error_correction_level=0.0)
        decoder = SecureBitPaperDecoder(error_correction_level=0.0)
        
        # Encode
        print("\nEncoding data...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("\nDecoding data...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        print(f"Decoded data: {decoded_data}")
        
        # Verify
        if test_data == decoded_data:
            print("\n✓ Data matches perfectly!")
            return True
        else:
            print("\n✗ Data mismatch detected")
            print(f"Expected: {test_data}")
            print(f"Got: {decoded_data}")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    success = test_basic_secure()
    if success:
        print("\n✓ Basic test passed! Secure BitPaper is working.")
    else:
        print("\n❌ Basic test failed.") 