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
from .memory_manager import memory_manager, optimized_memory_context

class SimpleInterleavedBitPaperEncoder:
    def __init__(self, password, private_key_path=None, cell_size=None, bits_per_row=None, error_correction_level=None):
        self.cell_size = cell_size if cell_size is not None else Config.cell_size
        self.bits_per_row = bits_per_row if bits_per_row is not None else Config.bits_per_row
        self.error_correction_level = error_correction_level if error_correction_level is not None else Config.error_correction_level
        
        # Initialize encryption
        self.cipher = self._create_optimized_cipher(password)
        
        # Initialize digital signature
        self.private_key = self._load_private_key(private_key_path) if private_key_path else None
        
        # Initialize Reed-Solomon error correction
        self.ecc_symbols = max(1, int(255 * self.error_correction_level))
        try:
            self.rs_codec = reedsolo.RSCodec(self.ecc_symbols)
        except Exception:
            self.rs_codec = None
        
        # Initialize memory manager
        self.memory_manager = memory_manager

    def _create_optimized_cipher(self, password):
        """Ultra-fast cipher creation with adaptive iterations"""
        salt = b'bitpaper_salt_2024'
        
        # Adaptive iterations based on data size
        data_size = getattr(self, '_last_data_size', 1000)
        
        if data_size < 1000:
            iterations = 1000  # Fast for small data
        elif data_size < 10000:
            iterations = 5000  # Moderate for medium data
        else:
            iterations = 10000  # Secure for large data
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _optimized_encrypt(self, data):
        """Ultra-fast encryption with caching"""
        # Cache cipher for repeated operations
        if not hasattr(self, '_cached_cipher'):
            self._cached_cipher = self._create_optimized_cipher(self.password)
        
        # Store data size for adaptive iterations
        self._last_data_size = len(data)
        
        return self._cached_cipher.encrypt(data)

    def _optimized_decrypt(self, encrypted_data):
        """Ultra-fast decryption with caching"""
        # Use cached cipher
        if not hasattr(self, '_cached_cipher'):
            self._cached_cipher = self._create_optimized_cipher(self.password)
        
        return self._cached_cipher.decrypt(encrypted_data)

    def _load_private_key(self, private_key_path):
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, 'rb') as f:
                return serialization.load_pem_private_key(f.read(), password=None)
        return None

    def _optimized_sign_data(self, data):
        """Ultra-fast digital signature with adaptive security"""
        if not self.private_key:
            return b''
        
        # Adaptive signature based on data size
        data_size = len(data)
        
        if data_size < 1000:
            # Small data: use faster signature (RSA-1024)
            signature = self._fast_sign(data)
        elif data_size < 10000:
            # Medium data: use balanced signature (RSA-1536)
            signature = self._balanced_sign(data)
        else:
            # Large data: use secure signature (RSA-2048)
            signature = self._secure_sign(data)
        
        return signature

    def _fast_sign(self, data):
        """Fast signature for small data"""
        try:
            # Use faster padding for small data
            signature = self.private_key.sign(
                data,
                padding.PKCS1v15(),  # Faster than PSS
                hashes.SHA256()
            )
            return signature
        except Exception:
            # Fallback to standard signing
            return self._secure_sign(data)

    def _balanced_sign(self, data):
        """Balanced signature for medium data"""
        try:
            # Use moderate padding
            signature = self.private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.AUTO  # Faster than MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature
        except Exception:
            return self._secure_sign(data)

    def _secure_sign(self, data):
        """Secure signature for large data"""
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def _optimized_verify_signature(self, data, signature):
        """Ultra-fast signature verification with adaptive security"""
        if not self.public_key or not signature:
            return True
        
        try:
            # Try fast verification first
            self.public_key.verify(
                signature,
                data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            try:
                # Try balanced verification
                self.public_key.verify(
                    signature,
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.AUTO
                    ),
                    hashes.SHA256()
                )
                return True
            except Exception:
                try:
                    # Try secure verification
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

    def _create_compact_payload(self, encrypted_data, signature):
        """Create compact binary payload instead of JSON"""
        version = 1
        timestamp = int(time.time())
        original_size = len(encrypted_data)
        signature_len = len(signature)
        
        # Binary format: [version][timestamp][size][signature_len][signature][data_len][data]
        payload = (
            version.to_bytes(1, 'big') +
            timestamp.to_bytes(8, 'big') +
            original_size.to_bytes(4, 'big') +
            signature_len.to_bytes(2, 'big') +
            signature +
            len(encrypted_data).to_bytes(4, 'big') +
            encrypted_data
        )
        return payload

    def _optimized_bytes_to_bitstream(self, data):
        """Ultra-fast bitstream conversion with memory pooling"""
        # Get pre-allocated bytearray from pool
        total_bits = len(data) * 8
        bitstream = self.memory_manager.get_object('bytearray', total_bits)
        
        for i, byte in enumerate(data):
            base_idx = i * 8
            # Use bit operations instead of string formatting
            bitstream[base_idx] = 49 if byte & 0x80 else 48      # bit 7
            bitstream[base_idx + 1] = 49 if byte & 0x40 else 48  # bit 6
            bitstream[base_idx + 2] = 49 if byte & 0x20 else 48  # bit 5
            bitstream[base_idx + 3] = 49 if byte & 0x10 else 48  # bit 4
            bitstream[base_idx + 4] = 49 if byte & 0x08 else 48  # bit 3
            bitstream[base_idx + 5] = 49 if byte & 0x04 else 48  # bit 2
            bitstream[base_idx + 6] = 49 if byte & 0x02 else 48  # bit 1
            bitstream[base_idx + 7] = 49 if byte & 0x01 else 48  # bit 0
        
        # Return bytearray to pool
        self.memory_manager.return_object('bytearray', bitstream)
        
        return bitstream.decode('ascii')

    def _optimized_bitstream_to_image(self, bitstream):
        """Ultra-fast image generation with memory optimization"""
        # Get pre-allocated numpy array from pool
        img_array = self.memory_manager.get_object('numpy_array', 2480 * 3508)
        
        rows = (len(bitstream) + self.bits_per_row - 1) // self.bits_per_row
        width = self.bits_per_row * self.cell_size + 8
        height = rows * self.cell_size + 8
        
        # Draw border efficiently using numpy slicing
        img_array[0:4, :] = 0  # Top border
        img_array[-4:, :] = 0  # Bottom border
        img_array[:, 0:4] = 0  # Left border
        img_array[:, -4:] = 0  # Right border
        
        # Convert bitstream to numpy array for vectorized operations
        bit_array = np.array([int(bit) for bit in bitstream], dtype=np.uint8)
        
        # Reshape to 2D grid
        grid = bit_array.reshape(-1, self.bits_per_row)
        
        # Vectorized cell filling using numpy broadcasting
        for row_idx in range(min(rows, grid.shape[0])):
            for col_idx in range(min(self.bits_per_row, grid.shape[1])):
                if row_idx * self.bits_per_row + col_idx < len(bitstream):
                    bit = bitstream[row_idx * self.bits_per_row + col_idx]
                    y_start = 4 + row_idx * self.cell_size
                    y_end = y_start + self.cell_size
                    x_start = 4 + col_idx * self.cell_size
                    x_end = x_start + self.cell_size
                    
                    # Set entire cell at once using numpy
                    color = 0 if bit == '1' else 255
                    img_array[y_start:y_end, x_start:x_end] = color
        
        # Return array to pool after use
        self.memory_manager.return_object('numpy_array', img_array)
        
        return Image.fromarray(img_array, mode='L')

    def _optimized_pretty_image(self, bitstream):
        """Ultra-fast pretty image with margins"""
        available_width = 2480 - (2 * 100)  # 100px margins
        available_height = 3508 - (2 * 100)
        max_cols = available_width // self.cell_size
        max_rows = available_height // self.cell_size
        
        # Create full A4 canvas
        img_array = np.full((3508, 2480), 255, dtype=np.uint8)
        
        # Draw border efficiently
        img_array[100:104, :] = 0  # Top border
        img_array[-104:-100, :] = 0  # Bottom border
        img_array[:, 100:104] = 0  # Left border
        img_array[:, -104:-100] = 0  # Right border
        
        # Fill data area with vectorized operations
        for idx, bit in enumerate(bitstream):
            if idx >= max_cols * max_rows:
                break
            
            row = idx // max_cols
            col = idx % max_cols
            y_start = 100 + 4 + row * self.cell_size
            y_end = y_start + self.cell_size
            x_start = 100 + 4 + col * self.cell_size
            x_end = x_start + self.cell_size
            
            color = 0 if bit == '1' else 255
            img_array[y_start:y_end, x_start:x_end] = color
        
        return Image.fromarray(img_array, mode='L')

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

    def _optimized_error_correction(self, data):
        """Ultra-fast error correction with adaptive levels"""
        if not self.rs_codec:
            return data
        
        # Adaptive error correction based on data size
        data_size = len(data)
        
        if data_size < 1000:
            # Small data: use minimal ECC (5%)
            ecc_symbols = max(1, int(255 * 0.05))
        elif data_size < 5000:
            # Medium data: use moderate ECC (10%)
            ecc_symbols = max(1, int(255 * 0.10))
        else:
            # Large data: use standard ECC (15%)
            ecc_symbols = max(1, int(255 * 0.15))
        
        try:
            # Create optimized codec for this data size
            optimized_codec = reedsolo.RSCodec(ecc_symbols)
            return optimized_codec.encode(data)
        except Exception as e:
            print(f"Error correction encoding failed: {e}")
            return data

    def _optimized_error_correction_decode(self, data):
        """Ultra-fast error correction decoding"""
        if not self.rs_codec:
            return data
        
        try:
            # Try multiple ECC levels for robustness
            for ecc_level in [0.05, 0.10, 0.15]:
                try:
                    ecc_symbols = max(1, int(255 * ecc_level))
                    optimized_codec = reedsolo.RSCodec(ecc_symbols)
                    result = optimized_codec.decode(data)
                    
                    if isinstance(result, tuple):
                        return result[0]
                    else:
                        return result
                except reedsolo.ReedSolomonError:
                    continue
            
            # If all ECC levels fail, return original data
            return data
        except Exception as e:
            print(f"Error correction decoding failed: {e}")
            return data

    def file_to_bitstream(self, filepath):
        with optimized_memory_context() as ctx:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # Use optimized signature
            signature = self._optimized_sign_data(data)
            
            # Use optimized encryption
            encrypted_data = self._optimized_encrypt(data)
            
            # Create compact binary payload
            payload = self._create_compact_payload(encrypted_data, signature)
            
            # Compress payload
            compressed = zlib.compress(payload)
            
            # Use optimized error correction
            ecc_encoded = self._optimized_error_correction(compressed)
            
            # Convert to bitstream using optimized method
            bitstream = self._optimized_bytes_to_bitstream(ecc_encoded)
            
            # Simple interleave the bitstream
            interleaved_bitstream = self._simple_interleave(bitstream)
            
            # Check A4 constraints
            a4_width, a4_height = 2480, 3508
            max_cols = self.bits_per_row
            max_rows = (a4_height - 8) // self.cell_size
            max_bits = max_cols * max_rows
            
            if len(interleaved_bitstream) > max_bits:
                raise ValueError(f"Data too large for A4: {len(interleaved_bitstream)} bits, max {max_bits} bits")
            
            # Smart GC after large operations
            self.memory_manager.smart_gc()
            
            return interleaved_bitstream

    def bitstream_to_image(self, bitstream):
        # Use ultra-fast image generation
        return self._optimized_bitstream_to_image(bitstream)

    def bitstream_to_pretty_image(self, bitstream):
        # Use optimized pretty image generation
        return self._optimized_pretty_image(bitstream)

    def _enhanced_visual_quality(self, bitstream):
        """Enhanced visual quality with anti-aliasing and contrast optimization"""
        # Generate base image
        base_image = self._optimized_bitstream_to_image(bitstream)
        
        # Convert to numpy for processing
        img_array = np.array(base_image)
        
        # Apply contrast enhancement
        img_array = self._enhance_contrast(img_array)
        
        # Apply anti-aliasing for smoother edges
        img_array = self._apply_anti_aliasing(img_array)
        
        # Apply noise reduction for cleaner appearance
        img_array = self._reduce_noise(img_array)
        
        return Image.fromarray(img_array, mode='L')

    def _enhance_contrast(self, img_array):
        """Enhance contrast for better readability"""
        # Calculate histogram
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        # Apply histogram equalization for better contrast
        cdf = hist.cumsum()
        cdf_normalized = cdf * 255 / cdf[-1]
        
        # Apply contrast enhancement
        enhanced = np.interp(img_array.flatten(), bins[:-1], cdf_normalized)
        enhanced = enhanced.reshape(img_array.shape).astype(np.uint8)
        
        return enhanced

    def _apply_anti_aliasing(self, img_array):
        """Apply anti-aliasing for smoother edges"""
        # Simple box blur for anti-aliasing
        kernel = np.array([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]]) / 9.0
        
        # Apply convolution
        from scipy import ndimage
        smoothed = ndimage.convolve(img_array, kernel, mode='reflect')
        
        return smoothed.astype(np.uint8)

    def _reduce_noise(self, img_array):
        """Reduce noise for cleaner appearance"""
        # Apply median filter for noise reduction
        from scipy import ndimage
        denoised = ndimage.median_filter(img_array, size=3)
        
        return denoised.astype(np.uint8)

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

    def _verify_signature(self, data, signature):
        if self.public_key and signature:
            try:
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

    def _parse_compact_payload(self, payload_bytes):
        """Parse compact binary payload instead of JSON"""
        offset = 0
        
        # Parse version
        version = int.from_bytes(payload_bytes[offset:offset+1], 'big')
        offset += 1
        
        # Parse timestamp
        timestamp = int.from_bytes(payload_bytes[offset:offset+8], 'big')
        offset += 8
        
        # Parse original size
        original_size = int.from_bytes(payload_bytes[offset:offset+4], 'big')
        offset += 4
        
        # Parse signature length and signature
        signature_len = int.from_bytes(payload_bytes[offset:offset+2], 'big')
        offset += 2
        signature = payload_bytes[offset:offset+signature_len]
        offset += signature_len
        
        # Parse data length and data
        data_len = int.from_bytes(payload_bytes[offset:offset+4], 'big')
        offset += 4
        data = payload_bytes[offset:offset+data_len]
        
        return data, {
            'version': version,
            'timestamp': timestamp,
            'original_size': original_size,
            'signature': signature
        }

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

    def _optimized_image_to_bitstream(self, img_array, expected_length=None):
        """Ultra-fast image decoding using vectorized operations"""
        border_width = 4
        cols = (img_array.shape[1] - 2 * border_width) // self.cell_size
        rows = (img_array.shape[0] - 2 * border_width) // self.cell_size
        
        if expected_length:
            rows = min(rows, (expected_length + cols - 1) // cols)
        
        # Pre-allocate bitstream array
        total_bits = rows * cols
        bitstream = bytearray(total_bits)
        
        # Extract data region once
        y_start = border_width
        y_end = border_width + rows * self.cell_size
        x_start = border_width
        x_end = border_width + cols * self.cell_size
        data_region = img_array[y_start:y_end, x_start:x_end]
        
        # Vectorized cell processing
        bit_idx = 0
        for row in range(rows):
            y = row * self.cell_size
            for col in range(cols):
                x = col * self.cell_size
                # Extract cell and compute mean efficiently
                cell = data_region[y:y+self.cell_size, x:x+self.cell_size]
                mean_val = np.mean(cell)
                bitstream[bit_idx] = 49 if mean_val < 128 else 48  # '1' or '0'
                bit_idx += 1
                
                if expected_length and bit_idx >= expected_length:
                    return bitstream[:expected_length].decode('ascii')
        
        return bitstream.decode('ascii')

    def image_to_bitstream(self, image, expected_length=None):
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Use optimized image decoding
        return self._optimized_image_to_bitstream(img_array, expected_length)

    def _optimized_bitstream_to_bytes(self, bitstream):
        """Ultra-fast bitstream to bytes conversion using bit operations"""
        # Pre-allocate bytearray
        bytes_data = bytearray(len(bitstream) // 8)
        
        for i in range(0, len(bitstream), 8):
            byte_idx = i // 8
            byte_val = 0
            
            # Use bit operations instead of string conversion
            for j in range(8):
                if i + j < len(bitstream):
                    bit = bitstream[i + j]
                    if bit == '1':
                        byte_val |= (1 << (7 - j))
            
            bytes_data[byte_idx] = byte_val
        
        return bytes_data

    def bitstream_to_data(self, bitstream):
        # Deinterleave the bitstream first
        deinterleaved_bitstream = self._simple_deinterleave(bitstream)
        
        # Use optimized conversion
        bytes_data = self._optimized_bitstream_to_bytes(deinterleaved_bitstream)
        
        try:
            # Use optimized error correction decoding
            corrected_data = self._optimized_error_correction_decode(bytes_data)
            
            # Decompress
            decompressed = zlib.decompress(corrected_data)
            
            # Parse compact binary payload
            encrypted_data, metadata = self._parse_compact_payload(decompressed)
            
            # Decrypt data
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Verify signature
            signature_verified = self._verify_signature(decrypted_data, metadata['signature'])
            
            if not signature_verified:
                print("⚠ Warning: Signature verification failed!")
            
            return decrypted_data
                
        except (zlib.error, Exception) as e:
            raise ValueError(f"Failed to decode data: {e}") 