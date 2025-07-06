import os
import tempfile
from pathlib import Path
from bitpaper.encrypted_core import EncryptedBitPaperEncoder, EncryptedBitPaperDecoder

def test_encrypted_encoding():
    print("Testing Encrypted BitPaper...")
    
    # Create test data
    test_data = b"This is a secret message that should be encrypted!"
    password = "my_secret_password_123"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        print(f"Original data: {test_data}")
        
        # Encode with encryption
        encoder = EncryptedBitPaperEncoder(password, error_correction_level=0.1)
        decoder = EncryptedBitPaperDecoder(password, error_correction_level=0.1)
        
        # Encode
        print("\nEncoding with encryption...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("\nDecoding with decryption...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        print(f"Decoded data: {decoded_data}")
        
        # Verify
        if test_data == decoded_data:
            print("\n✓ Encrypted data matches perfectly!")
            return True
        else:
            print("\n✗ Encrypted data mismatch")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(test_file)

def test_wrong_password():
    print("\n=== Testing Wrong Password ===")
    
    test_data = b"Secret message"
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        # Encode with correct password
        encoder = EncryptedBitPaperEncoder(correct_password)
        bitstream = encoder.file_to_bitstream(test_file)
        img = encoder.bitstream_to_image(bitstream)
        
        # Try to decode with wrong password
        decoder = EncryptedBitPaperDecoder(wrong_password)
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        
        try:
            decoded_data = decoder.bitstream_to_data(decoded_bitstream)
            print("✗ Wrong password should have failed!")
            return False
        except Exception as e:
            print("✓ Wrong password correctly rejected")
            return True
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    print("=== Encrypted BitPaper Test Suite ===\n")
    
    success = True
    success &= test_encrypted_encoding()
    success &= test_wrong_password()
    
    if success:
        print("\n🎉 Encryption tests passed!")
    else:
        print("\n❌ Some encryption tests failed.") 