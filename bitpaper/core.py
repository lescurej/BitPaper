import zlib
import lzma
import bz2
import base64
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import cv2
from bitpaper.utils import Config

class BitPaperEncoder:
    def __init__(self, cell_size=None, bits_per_row=None, max_rows=None, pretty_mode=False):
        self.cell_size = cell_size if cell_size is not None else Config.cell_size
        self.bits_per_row = bits_per_row if bits_per_row is not None else Config.bits_per_row
        self.max_rows = max_rows if max_rows is not None else Config.max_rows
        self.border_width = Config.border_width
        self.pretty_mode = pretty_mode
        self.margin = 100 if pretty_mode else 0
        self.bits_per_page = self.bits_per_row * self.max_rows

    def file_to_bitstream_pages(self, filepath):
        """Optimized encoding with minimal overhead"""
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        # Create compact metadata (no JSON overhead)
        filename = Path(filepath).name.encode('utf-8')
        metadata_header = len(filename).to_bytes(1, 'big') + filename
        
        # Combine data efficiently
        combined_data = metadata_header + file_data
        
        # Try multiple compression algorithms
        compressed_data = self._best_compression(combined_data)
        
        # Convert to bitstream efficiently
        bitstream = self._bytes_to_bitstream(compressed_data)
        
        # Split into pages
        if self.pretty_mode:
            available_width = 2480 - (2 * self.margin)
            available_height = 3508 - (2 * self.margin)
            max_cols = available_width // self.cell_size
            max_rows = available_height // self.cell_size
            bits_per_page = max_cols * max_rows
        else:
            bits_per_page = self.bits_per_page
        
        pages = []
        for i in range(0, len(bitstream), bits_per_page):
            page_bits = bitstream[i:i + bits_per_page]
            pages.append(page_bits)
        
        return pages, {'filename': Path(filepath).name, 'size': len(file_data)}

    def _best_compression(self, data):
        """Try multiple compression algorithms and pick the best"""
        algorithms = [
            ('zlib', lambda d: zlib.compress(d, level=9)),
            ('lzma', lambda d: lzma.compress(d, preset=9)),
            ('bz2', lambda d: bz2.compress(d, compresslevel=9))
        ]
        
        best_result = None
        best_size = float('inf')
        
        for name, compressor in algorithms:
            try:
                compressed = compressor(data)
                if len(compressed) < best_size:
                    best_size = len(compressed)
                    best_result = (name, compressed)
            except:
                continue
        
        if best_result is None:
            # Fallback to zlib
            return zlib.compress(data, level=9)
        
        # Add algorithm identifier
        algo_id = {'zlib': 0, 'lzma': 1, 'bz2': 2}[best_result[0]]
        return bytes([algo_id]) + best_result[1]

    def _bytes_to_bitstream(self, data):
        """Efficient bitstream conversion"""
        # Pre-allocate the exact size needed
        total_bits = len(data) * 8
        bitstream = ['0'] * total_bits
        
        for i, byte in enumerate(data):
            for j in range(8):
                bit_idx = i * 8 + j
                bitstream[bit_idx] = '1' if (byte >> (7-j)) & 1 else '0'
        
        return ''.join(bitstream)

    def file_to_bitstream(self, filepath):
        """Single-page version for backward compatibility"""
        pages, metadata = self.file_to_bitstream_pages(filepath)
        if len(pages) > 1:
            raise ValueError(f"Data too large for single page: {len(pages)} pages needed")
        return pages[0], metadata

    def bitstream_to_image(self, bitstream, metadata=None, page_num=1, total_pages=1):
        """Convert bitstream to image"""
        if self.pretty_mode:
            return self._bitstream_to_pretty_image(bitstream)
        else:
            return self._bitstream_to_simple_image(bitstream)

    def _bitstream_to_simple_image(self, bitstream):
        """Simple image without margins"""
        rows = (len(bitstream) + self.bits_per_row - 1) // self.bits_per_row
        
        width, height = 2480, 3508
        img = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, width - 1, height - 1], outline=0, width=self.border_width)
        
        # Fill data area efficiently
        for idx, bit in enumerate(bitstream):
            row = idx // self.bits_per_row
            col = idx % self.bits_per_row
            x = self.border_width + col * self.cell_size
            y = self.border_width + row * self.cell_size
            color = 0 if bit == '1' else 255
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], fill=color)
        
        return img

    def _bitstream_to_pretty_image(self, bitstream):
        """Pretty image with margins"""
        available_width = 2480 - (2 * self.margin)
        available_height = 3508 - (2 * self.margin)
        max_cols = available_width // self.cell_size
        max_rows = available_height // self.cell_size
        
        width, height = 2480, 3508
        img = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([self.margin, self.margin, width - self.margin, height - self.margin], 
                      outline=0, width=self.border_width)
        
        # Fill data area
        for idx, bit in enumerate(bitstream):
            row = idx // max_cols
            col = idx % max_cols
            x = self.margin + self.border_width + col * self.cell_size
            y = self.margin + self.border_width + row * self.cell_size
            color = 0 if bit == '1' else 255
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], fill=color)
        
        return img

class BitPaperDecoder:
    def __init__(self, cell_size=None, bits_per_row=None, max_rows=None, pretty_mode=False):
        self.cell_size = cell_size if cell_size is not None else Config.cell_size
        self.bits_per_row = bits_per_row if bits_per_row is not None else Config.bits_per_row
        self.max_rows = max_rows if max_rows is not None else Config.max_rows
        self.border_width = Config.border_width
        self.pretty_mode = pretty_mode
        self.margin = 100 if pretty_mode else 0

    def images_to_bitstream(self, images):
        """Decode multiple images"""
        combined_bitstream = ""
        for i, image in enumerate(images):
            page_bitstream = self.image_to_bitstream(image)
            combined_bitstream += page_bitstream
            print(f"Page {i+1} decoded: {len(page_bitstream)} bits")
        return combined_bitstream

    def image_to_bitstream(self, image, expected_length=None):
        """Convert image to bitstream"""
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        if self.pretty_mode:
            return self._pretty_image_to_bitstream(img_array, expected_length)
        else:
            return self._simple_image_to_bitstream(img_array, expected_length)

    def _simple_image_to_bitstream(self, img_array, expected_length=None):
        """Simple decoding"""
        data_width = self.bits_per_row * self.cell_size
        data_height = self.max_rows * self.cell_size
        
        x0, y0 = self.border_width, self.border_width
        x1, y1 = x0 + data_width, y0 + data_height
        
        data_region = img_array[y0:y1, x0:x1]
        
        if expected_length:
            rows = (expected_length + self.bits_per_row - 1) // self.bits_per_row
        else:
            rows = self.max_rows
        
        bitstream = ""
        for row in range(rows):
            for col in range(self.bits_per_row):
                x = col * self.cell_size
                y = row * self.cell_size
                cell = data_region[y:y+self.cell_size, x:x+self.cell_size]
                bitstream += "1" if cell.mean() < 128 else "0"
                if expected_length and len(bitstream) >= expected_length:
                    return bitstream[:expected_length]
        
        return bitstream

    def _pretty_image_to_bitstream(self, img_array, expected_length=None):
        """Pretty decoding"""
        available_width = 2480 - (2 * self.margin)
        available_height = 3508 - (2 * self.margin)
        max_cols = available_width // self.cell_size
        max_rows = available_height // self.cell_size
        
        x0 = self.margin + self.border_width
        y0 = self.margin + self.border_width
        x1 = x0 + (max_cols * self.cell_size)
        y1 = y0 + (max_rows * self.cell_size)
        
        data_region = img_array[y0:y1, x0:x1]
        
        if expected_length:
            rows = (expected_length + max_cols - 1) // max_cols
        else:
            rows = max_rows
        
        bitstream = ""
        for row in range(rows):
            for col in range(max_cols):
                x = col * self.cell_size
                y = row * self.cell_size
                cell = data_region[y:y+self.cell_size, x:x+self.cell_size]
                bitstream += "1" if cell.mean() < 128 else "0"
                if expected_length and len(bitstream) >= expected_length:
                    return bitstream[:expected_length]
        
        return bitstream

    def bitstream_to_data(self, bitstream):
        """Optimized decoding"""
        # Convert bitstream to bytes efficiently
        bytes_data = bytearray()
        for i in range(0, len(bitstream), 8):
            byte_str = bitstream[i:i+8]
            if len(byte_str) == 8:
                byte_val = int(byte_str, 2)
                bytes_data.append(byte_val)
        
        # Decompress with algorithm detection
        try:
            algo_id = bytes_data[0]
            compressed_data = bytes_data[1:]
            
            if algo_id == 0:
                decompressed = zlib.decompress(compressed_data)
            elif algo_id == 1:
                decompressed = lzma.decompress(compressed_data)
            elif algo_id == 2:
                decompressed = bz2.decompress(compressed_data)
            else:
                raise ValueError("Unknown compression algorithm")
            
            # Extract metadata and data
            filename_length = decompressed[0]
            filename = decompressed[1:1+filename_length].decode('utf-8')
            original_data = decompressed[1+filename_length:]
            
            return original_data, {'filename': filename, 'size': len(original_data)}
            
        except Exception as e:
            raise ValueError(f"Failed to decode data: {e}") 