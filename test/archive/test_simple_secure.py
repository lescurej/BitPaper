import os
import tempfile
from pathlib import Path
from bitpaper.secure_core import SecureBitPaperEncoder, SecureBitPaperDecoder

def test_simple_secure():
    print("Testing Simple Secure BitPaper (without error correction)...")
    
    # Create test data
    test_data = b"This is a test file for secure BitPaper encoding. " * 5
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        
        # Use minimal error correction for testing
        encoder = SecureBitPaperEncoder(error_correction_level=0.1)
        decoder = SecureBitPaperDecoder(error_correction_level=0.1)
        
        # Encode
        print("Encoding data...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("Decoding data...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        
        # Verify
        if test_data == decoded_data:
            print("✓ Data matches perfectly!")
            return True
        else:
            print("✗ Data mismatch detected")
            return False
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    test_simple_secure() 