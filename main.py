import sys
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from bitpaper.core import BitPaperEncoder, BitPaperDecoder
from bitpaper.simple_interleaved_core import SimpleInterleavedBitPaperEncoder, SimpleInterleavedBitPaperDecoder

def save_images_to_pdf(images, output_pdf_path):
    page_width, page_height = A4
    pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=A4)
    
    for i, img in enumerate(images):
        img_width, img_height = img.size
        temp_path = f"_temp_bitmap_{i}.png"
        img.save(temp_path)
        
        img_width_pt = img_width * 72 / 300
        img_height_pt = img_height * 72 / 300
        x = (page_width - img_width_pt) / 2
        y = (page_height - img_height_pt) / 2
        
        pdf_canvas.drawImage(ImageReader(temp_path), x, y, width=img_width_pt, height=img_height_pt)
        pdf_canvas.showPage()
        
        # Clean up temp file
        Path(temp_path).unlink()
    
    pdf_canvas.save()

def encode_and_decode(input_file, output_pdf, decoded_file, secure_mode=False, pretty_mode=True, password=None, private_key_path=None, public_key_path=None):
    if secure_mode:
        encoder = SimpleInterleavedBitPaperEncoder(password, private_key_path, error_correction_level=0.15)
        decoder = SimpleInterleavedBitPaperDecoder(password, public_key_path, error_correction_level=0.15)
        print("🔐 Using SECURE mode with encryption and error correction")
    else:
        encoder = BitPaperEncoder(pretty_mode=pretty_mode)
        decoder = BitPaperDecoder(pretty_mode=pretty_mode)
        mode = "PRETTY" if pretty_mode else "SIMPLE"
        print(f"📄 Using {mode} mode (multi-page support)")
    
    with open(input_file, 'rb') as f:
        original_data = f.read()
    
    print(f"Original file size: {len(original_data)} bytes")
    
    # Get bitstream pages and metadata
    bitstream_pages, metadata = encoder.file_to_bitstream_pages(input_file)
    print(f"Encoded into {len(bitstream_pages)} pages")
    print(f"File metadata: {metadata}")
    
    # Generate images for each page
    images = []
    total_bits = 0
    for i, bitstream in enumerate(bitstream_pages):
        img = encoder.bitstream_to_image(bitstream, metadata, i+1, len(bitstream_pages))
        images.append(img)
        total_bits += len(bitstream)
        print(f"Page {i+1}: {len(bitstream)} bits, image size: {img.size}")
    
    print(f"Total encoded bitstream length: {total_bits} bits")
    
    # Save to PDF
    save_images_to_pdf(images, output_pdf)
    print(f"PDF saved: {output_pdf} ({len(images)} pages)")
    os.system(f"open {output_pdf}")
    
    # Decode ALL pages with correct lengths
    print("\n Decoding all pages...")
    decoded_bitstream = ""
    for i, (image, expected_length) in enumerate(zip(images, [len(bs) for bs in bitstream_pages])):
        page_bitstream = decoder.image_to_bitstream(image, expected_length)
        decoded_bitstream += page_bitstream
        print(f"Page {i+1} decoded: {len(page_bitstream)} bits (expected: {expected_length})")
    
    print(f"Total decoded bitstream length: {len(decoded_bitstream)} bits")
    
    decoded_data, decoded_metadata = decoder.bitstream_to_data(decoded_bitstream)
    print(f"Decoded data size: {len(decoded_data)} bytes")
    print(f"Decoded metadata: {decoded_metadata}")
    
    # Use original filename from metadata
    if decoded_metadata and 'filename' in decoded_metadata:
        decoded_file = f"decoded_{decoded_metadata['filename']}"
    
    # Ensure decoded_data is bytes
    if isinstance(decoded_data, str):
        decoded_data = decoded_data.encode('utf-8')
    
    with open(decoded_file, 'wb') as f:
        f.write(decoded_data)
    print(f"Decoded file saved: {decoded_file}")
    
    if original_data == decoded_data:
        print("✓ Original and decoded data match perfectly!")
    else:
        print("⚠ Data mismatch detected")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Simple mode: python main.py input_file.txt")
        print("  Pretty mode: python main.py --pretty input_file.txt")
        print("  Secure mode: python main.py --secure input_file.txt password [private_key.pem] [public_key.pem]")
        print("")
        print("Examples:")
        print("  python main.py secret.txt")
        print("  python main.py --pretty secret.txt")
        print("  python main.py --secure secret.txt mypassword")
        sys.exit(1)
    
    # Check for modes
    pretty_mode = True  # Default to pretty mode
    secure_mode = False
    password = None
    private_key_path = None
    public_key_path = None
    
    if sys.argv[1] == "--secure":
        if len(sys.argv) < 4:
            print("Secure mode requires: input_file password [private_key.pem] [public_key.pem]")
            sys.exit(1)
        
        secure_mode = True
        input_file = sys.argv[2]
        password = sys.argv[3]
        private_key_path = sys.argv[4] if len(sys.argv) > 4 else None
        public_key_path = sys.argv[5] if len(sys.argv) > 5 else None
        
        output_pdf = "secure_encoded.pdf"
        decoded_file = "secure_decoded_" + Path(input_file).name
        
    elif sys.argv[1] == "--simple":
        pretty_mode = False
        input_file = sys.argv[2]
        output_pdf = "encoded.pdf"
        decoded_file = "decoded_" + Path(input_file).name
        
    else:
        # Pretty mode (default)
        input_file = sys.argv[1]
        output_pdf = "encoded.pdf"
        decoded_file = "decoded_" + Path(input_file).name
    
    encode_and_decode(input_file, output_pdf, decoded_file, 
                     secure_mode=secure_mode, pretty_mode=pretty_mode,
                     password=password, private_key_path=private_key_path, 
                     public_key_path=public_key_path)

if __name__ == "__main__":
    main()


