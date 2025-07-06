import os
import tempfile
import time
from pathlib import Path
from bitpaper.signed_core import SignedBitPaperEncoder, SignedBitPaperDecoder

def test_signed_encoding():
    print("Testing Signed BitPaper...")
    
    # Generate keys if they don't exist
    if not os.path.exists("private_key.pem"):
        print("Generating key pair...")
        os.system("python generate_keys.py")
    
    # Create test data
    test_data = b"This is a signed and encrypted message!"
    password = "my_secret_password_123"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        print(f"Original data: {test_data}")
        
        # Encode with signature
        encoder = SignedBitPaperEncoder(password, "private_key.pem", error_correction_level=0.1)
        decoder = SignedBitPaperDecoder(password, "public_key.pem", error_correction_level=0.1)
        
        # Encode
        print("\nEncoding with signature...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("\nDecoding with signature verification...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        print(f"Decoded data: {decoded_data}")
        
        # Verify
        if test_data == decoded_data:
            print("\n✓ Signed data matches perfectly!")
            return True
        else:
            print("\n✗ Signed data mismatch")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    print("=== Signed BitPaper Test Suite ===\n")
    
    success = test_signed_encoding()
    
    if success:
        print("\n🎉 Signature tests passed!")
    else:
        print("\n❌ Signature tests failed.") 