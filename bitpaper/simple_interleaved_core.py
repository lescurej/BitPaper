import zlib
import reedsolo
import numpy as np
from PIL import Image, ImageDraw
import cv2
import os
import time
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from bitpaper.utils import Config

class SimpleInterleavedBitPaperEncoder:
    def __init__(self, password, private_key_path=None, cell_size=None, bits_per_row=None, error_correction_level=None):
        self.cell_size = cell_size if cell_size is not None else Config.cell_size
        self.bits_per_row = bits_per_row if bits_per_row is not None else Config.bits_per_row
        self.error_correction_level = error_correction_level if error_correction_level is not None else Config.error_correction_level
        
        # Initialize encryption
        self.cipher = self._create_cipher(password)
        
        # Initialize digital signature
        self.private_key = self._load_private_key(private_key_path) if private_key_path else None
        
        # Initialize Reed-Solomon error correction
        self.ecc_symbols = max(1, int(255 * self.error_correction_level))
        try:
            self.rs_codec = reedsolo.RSCodec(self.ecc_symbols)
        except Exception:
            self.rs_codec = None

    def _create_cipher(self, password):
        salt = b'bitpaper_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _load_private_key(self, private_key_path):
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, 'rb') as f:
                return serialization.load_pem_private_key(f.read(), password=None)
        return None

    def _sign_data(self, data):
        if self.private_key:
            signature = self.private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature
        return b''

    def _simple_interleave(self, bitstream):
        """Simple interleaving using a fixed pattern"""
        if len(bitstream) <= 1:
            return bitstream
        
        # Use a simple pattern: every 3rd bit
        interleaved = []
        for i in range(0, len(bitstream), 3):
            if i < len(bitstream):
                interleaved.append(bitstream[i])
        for i in range(1, len(bitstream), 3):
            if i < len(bitstream):
                interleaved.append(bitstream[i])
        for i in range(2, len(bitstream), 3):
            if i < len(bitstream):
                interleaved.append(bitstream[i])
        
        return ''.join(interleaved)

    def _simple_deinterleave(self, bitstream):
        """Simple deinterleaving using the same pattern"""
        if len(bitstream) <= 1:
            return bitstream
        
        # Calculate how many bits in each group
        total_bits = len(bitstream)
        group_size = total_bits // 3
        remainder = total_bits % 3
        
        # Reconstruct original order
        original = [''] * len(bitstream)
        
        # First group (every 3rd bit starting from 0)
        for i in range(group_size + (1 if remainder > 0 else 0)):
            if i < len(bitstream):
                original[i * 3] = bitstream[i]
        
        # Second group (every 3rd bit starting from 1)
        start_idx = group_size + (1 if remainder > 0 else 0)
        for i in range(group_size + (1 if remainder > 1 else 0)):
            if start_idx + i < len(bitstream) and i * 3 + 1 < len(bitstream):
                original[i * 3 + 1] = bitstream[start_idx + i]
        
        # Third group (every 3rd bit starting from 2)
        start_idx = start_idx + group_size + (1 if remainder > 1 else 0)
        for i in range(group_size):
            if start_idx + i < len(bitstream) and i * 3 + 2 < len(bitstream):
                original[i * 3 + 2] = bitstream[start_idx + i]
        
        return ''.join(original)

    def file_to_bitstream(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Create metadata with signature
        metadata = {
            'original_size': len(data),
            'timestamp': str(int(time.time())),
            'version': '1.0',
            'interleaved': True
        }
        
        # Sign the data
        signature = self._sign_data(data)
        metadata['signature'] = base64.b64encode(signature).decode('utf-8')
        
        # Encrypt data
        encrypted_data = self.cipher.encrypt(data)
        
        # Create payload with metadata
        payload = {
            'metadata': metadata,
            'data': base64.b64encode(encrypted_data).decode('utf-8')
        }
        
        # Serialize payload
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Compress payload
        compressed = zlib.compress(payload_bytes)
        
        # Add error correction if available
        if self.rs_codec:
            try:
                ecc_encoded = self.rs_codec.encode(compressed)
            except Exception as e:
                print(f"Error correction encoding failed: {e}")
                ecc_encoded = compressed
        else:
            ecc_encoded = compressed
        
        # Convert to bitstream
        bitstream = ''.join(f'{byte:08b}' for byte in ecc_encoded)
        
        # Simple interleave the bitstream
        interleaved_bitstream = self._simple_interleave(bitstream)
        
        # Check A4 constraints
        a4_width, a4_height = 2480, 3508
        max_cols = self.bits_per_row
        max_rows = (a4_height - 8) // self.cell_size
        max_bits = max_cols * max_rows
        
        if len(interleaved_bitstream) > max_bits:
            raise ValueError(f"Data too large for A4: {len(interleaved_bitstream)} bits, max {max_bits} bits")
        
        return interleaved_bitstream

    def bitstream_to_image(self, bitstream):
        rows = (len(bitstream) + self.bits_per_row - 1) // self.bits_per_row
        width = self.bits_per_row * self.cell_size + 8
        height = rows * self.cell_size + 8
        
        a4_width, a4_height = 2480, 3508
        if width > a4_width or height > a4_height:
            raise ValueError(f"Data too large for A4: required {width}x{height}, max {a4_width}x{a4_height}")
        
        img = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(img)
        border_width = 4
        
        # Encode data
        for idx, bit in enumerate(bitstream):
            row = idx // self.bits_per_row
            col = idx % self.bits_per_row
            x = border_width + col * self.cell_size
            y = border_width + row * self.cell_size
            color = 0 if bit == '1' else 255
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], fill=color)
        
        # Add border
        draw.rectangle([0, 0, width - 1, height - 1], outline=0, width=border_width)
        
        return img

class SimpleInterleavedBitPaperDecoder:
    def __init__(self, password, public_key_path=None, cell_size=None, bits_per_row=None, error_correction_level=None):
        self.cell_size = cell_size if cell_size is not None else Config.cell_size
        self.bits_per_row = bits_per_row if bits_per_row is not None else Config.bits_per_row
        self.error_correction_level = error_correction_level if error_correction_level is not None else Config.error_correction_level
        
        # Initialize encryption
        self.cipher = self._create_cipher(password)
        
        # Initialize digital signature verification
        self.public_key = self._load_public_key(public_key_path) if public_key_path else None
        
        # Initialize Reed-Solomon error correction
        self.ecc_symbols = max(1, int(255 * self.error_correction_level))
        try:
            self.rs_codec = reedsolo.RSCodec(self.ecc_symbols)
        except Exception:
            self.rs_codec = None

    def _create_cipher(self, password):
        salt = b'bitpaper_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _load_public_key(self, public_key_path):
        if public_key_path and os.path.exists(public_key_path):
            with open(public_key_path, 'rb') as f:
                return serialization.load_pem_public_key(f.read())
        return None

    def _verify_signature(self, data, signature_b64):
        if self.public_key and signature_b64:
            try:
                signature = base64.b64decode(signature_b64)
                self.public_key.verify(
                    signature,
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except Exception as e:
                print(f"Signature verification failed: {e}")
                return False
        return True  # No signature to verify

    def _simple_deinterleave(self, bitstream):
        """Simple deinterleaving using the same pattern"""
        if len(bitstream) <= 1:
            return bitstream
        
        # Calculate how many bits in each group
        total_bits = len(bitstream)
        group_size = total_bits // 3
        remainder = total_bits % 3
        
        # Reconstruct original order
        original = [''] * len(bitstream)
        
        # First group (every 3rd bit starting from 0)
        for i in range(group_size + (1 if remainder > 0 else 0)):
            if i < len(bitstream):
                original[i * 3] = bitstream[i]
        
        # Second group (every 3rd bit starting from 1)
        start_idx = group_size + (1 if remainder > 0 else 0)
        for i in range(group_size + (1 if remainder > 1 else 0)):
            if start_idx + i < len(bitstream) and i * 3 + 1 < len(bitstream):
                original[i * 3 + 1] = bitstream[start_idx + i]
        
        # Third group (every 3rd bit starting from 2)
        start_idx = start_idx + group_size + (1 if remainder > 1 else 0)
        for i in range(group_size):
            if start_idx + i < len(bitstream) and i * 3 + 2 < len(bitstream):
                original[i * 3 + 2] = bitstream[start_idx + i]
        
        return ''.join(original)

    def image_to_bitstream(self, image, expected_length=None):
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        border_width = 4
        cols = (img_array.shape[1] - 2 * border_width) // self.cell_size
        rows = (img_array.shape[0] - 2 * border_width) // self.cell_size
        
        bitstream = ""
        for row in range(rows):
            for col in range(cols):
                x = border_width + col * self.cell_size
                y = border_width + row * self.cell_size
                cell = img_array[y:y+self.cell_size, x:x+self.cell_size]
                bitstream += "1" if cell.mean() < 128 else "0"
                
                if expected_length and len(bitstream) >= expected_length:
                    return bitstream[:expected_length]
        
        return bitstream

    def bitstream_to_data(self, bitstream):
        # Deinterleave the bitstream first
        deinterleaved_bitstream = self._simple_deinterleave(bitstream)
        
        bytes_data = bytearray()
        deinterleaved_bitstream = deinterleaved_bitstream[:len(deinterleaved_bitstream) - (len(deinterleaved_bitstream) % 8)]
        
        for i in range(0, len(deinterleaved_bitstream), 8):
            byte_str = deinterleaved_bitstream[i:i+8]
            if len(byte_str) == 8:
                byte_val = int(byte_str, 2)
                bytes_data.append(byte_val)
        
        try:
            # Apply error correction if available
            if self.rs_codec:
                try:
                    corrected_result = self.rs_codec.decode(bytes(bytes_data))
                    if isinstance(corrected_result, tuple):
                        corrected_data = corrected_result[0]
                    else:
                        corrected_data = corrected_result
                except (reedsolo.ReedSolomonError, zlib.error) as e:
                    print(f"Error correction failed: {e}")
                    corrected_data = bytes(bytes_data)
            else:
                corrected_data = bytes(bytes_data)
            
            # Decompress
            decompressed = zlib.decompress(corrected_data)
            
            # Parse payload
            payload = json.loads(decompressed.decode('utf-8'))
            
            # Decrypt data
            encrypted_data = base64.b64decode(payload['data'])
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Verify signature
            metadata = payload['metadata']
            signature_verified = self._verify_signature(decrypted_data, metadata.get('signature', ''))
            
            if not signature_verified:
                print("⚠ Warning: Signature verification failed!")
            
            return decrypted_data
                
        except (zlib.error, Exception) as e:
            raise ValueError(f"Failed to decode data: {e}") 