import zlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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
        """Convert file to multiple pages of bitstreams with metadata"""
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        # Create metadata
        metadata = {
            'filename': Path(filepath).name,
            'original_size': len(file_data),
            'timestamp': '2024-01-01'
        }
        
        # Create data structure with metadata
        data_structure = {
            'data': file_data.hex(),  # Store as hex string
            'metadata': metadata
        }
        
        # Compress the data structure
        json_data = json.dumps(data_structure).encode()
        compressed = zlib.compress(json_data)
        
        # Convert to bitstream
        bitstream = ''.join(format(byte, '08b') for byte in compressed)
        
        # Split into pages
        if self.pretty_mode:
            # Calculate available space with margins
            available_width = 2480 - (2 * self.margin)
            available_height = 3508 - (2 * self.margin)
            max_cols = available_width // self.cell_size
            max_rows = available_height // self.cell_size
            bits_per_page = max_cols * max_rows
        else:
            bits_per_page = self.bits_per_page
        
        # Split into pages
        pages = []
        for i in range(0, len(bitstream), bits_per_page):
            page_bits = bitstream[i:i + bits_per_page]
            pages.append(page_bits)
        
        return pages, metadata

    def file_to_bitstream(self, filepath):
        """Single-page version for backward compatibility"""
        pages, metadata = self.file_to_bitstream_pages(filepath)
        if len(pages) > 1:
            raise ValueError(f"Data too large for single page: {len(pages)} pages needed")
        return pages[0], metadata

    def bitstream_to_image(self, bitstream, metadata=None, page_num=1, total_pages=1):
        """Convert bitstream to image with optional pretty formatting"""
        if self.pretty_mode:
            return self._bitstream_to_pretty_image(bitstream, page_num, total_pages)
        else:
            return self._bitstream_to_simple_image(bitstream)

    def _bitstream_to_simple_image(self, bitstream):
        """Simple image without margins or formatting"""
        rows = (len(bitstream) + self.bits_per_row - 1) // self.bits_per_row
        
        # Use full A4 dimensions
        a4_width, a4_height = 2480, 3508
        width = a4_width
        height = a4_height
        
        img = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, width - 1, height - 1], outline=0, width=self.border_width)
        
        # Fill data area
        for idx, bit in enumerate(bitstream):
            row = idx // self.bits_per_row
            col = idx % self.bits_per_row
            x = self.border_width + col * self.cell_size
            y = self.border_width + row * self.cell_size
            color = 0 if bit == '1' else 255
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], fill=color)
        
        return img

    def _bitstream_to_pretty_image(self, bitstream, page_num=1, total_pages=1):
        """Pretty image with margins but NO text - only encoded data"""
        # Calculate available space with margins
        available_width = 2480 - (2 * self.margin)
        available_height = 3508 - (2 * self.margin)
        max_cols = available_width // self.cell_size
        max_rows = available_height // self.cell_size
        
        rows = (len(bitstream) + max_cols - 1) // max_cols
        
        # Use full A4 dimensions
        a4_width, a4_height = 2480, 3508
        width = a4_width
        height = a4_height
        
        img = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(img)
        
        # Draw outer border with margin
        draw.rectangle([self.margin, self.margin, width - self.margin, height - self.margin], 
                      outline=0, width=self.border_width)
        
        # Fill data area (no text, only encoded data)
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
        """Decode multiple images back to a single bitstream"""
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
        """Simple decoding without margins"""
        # Calculate data area
        data_width = self.bits_per_row * self.cell_size
        data_height = self.max_rows * self.cell_size
        
        # Extract data region
        x0 = self.border_width
        y0 = self.border_width
        x1 = x0 + data_width
        y1 = y0 + data_height
        
        data_region = img_array[y0:y1, x0:x1]
        
        # Calculate actual rows needed
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
        """Pretty decoding with margins but NO title area"""
        # Calculate available space with margins
        available_width = 2480 - (2 * self.margin)
        available_height = 3508 - (2 * self.margin)
        max_cols = available_width // self.cell_size
        max_rows = available_height // self.cell_size
        
        # Extract data region (no title area to skip)
        x0 = self.margin + self.border_width
        y0 = self.margin + self.border_width
        x1 = x0 + (max_cols * self.cell_size)
        y1 = y0 + (max_rows * self.cell_size)
        
        data_region = img_array[y0:y1, x0:x1]
        
        # Calculate actual rows needed
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
        """Convert bitstream to data with metadata support"""
        bytes_data = bytearray()
        bitstream = bitstream[:len(bitstream) - (len(bitstream) % 8)]
        for i in range(0, len(bitstream), 8):
            byte_str = bitstream[i:i+8]
            if len(byte_str) == 8:
                byte_val = int(byte_str, 2)
                bytes_data.append(byte_val)
        
        try:
            decompressed = zlib.decompress(bytes(bytes_data))
            data_structure = json.loads(decompressed.decode())
            
            # Convert hex string back to bytes
            original_data = bytes.fromhex(data_structure['data'])
            metadata = data_structure['metadata']
            
            return original_data, metadata
        except zlib.error:
            raise ValueError("Failed to decompress data")
        except json.JSONDecodeError:
            raise ValueError("Failed to parse metadata")
        except ValueError:
            raise ValueError("Failed to convert hex data") 