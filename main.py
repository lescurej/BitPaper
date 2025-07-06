import sys
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from bitpaper.core import BitPaperEncoder, BitPaperDecoder
from bitpaper.simple_interleaved_core import SimpleInterleavedBitPaperEncoder, SimpleInterleavedBitPaperDecoder

def ultra_fast_save_images_to_pdf(images, output_pdf_path):
    """Ultra-fast PDF generation with memory-only operations"""
    page_width, page_height = A4
    pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=A4)
    
    for i, img in enumerate(images):
        # Convert image to memory buffer (no disk I/O)
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', optimize=True)
        img_buffer.seek(0)
        
        # Calculate optimal dimensions
        img_width, img_height = img.size
        img_width_pt = img_width * 72 / 300
        img_height_pt = img_height * 72 / 300
        
        # Center image on page
        x = (page_width - img_width_pt) / 2
        y = (page_height - img_height_pt) / 2
        
        # Use memory buffer directly
        pdf_canvas.drawImage(ImageReader(img_buffer), x, y, width=img_width_pt, height=img_height_pt)
        pdf_canvas.showPage()
        
        # Clear buffer for next iteration
        img_buffer.close()
    
    pdf_canvas.save()

def optimized_save_images_to_pdf(images, output_pdf_path):
    """Optimized PDF generation with batch processing"""
    page_width, page_height = A4
    pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=A4)
    
    # Pre-calculate all image buffers
    image_buffers = []
    for img in images:
        buffer = BytesIO()
        img.save(buffer, format='PNG', optimize=True, quality=95)
        buffer.seek(0)
        image_buffers.append(buffer)
    
    # Batch process all pages
    for i, (img, buffer) in enumerate(zip(images, image_buffers)):
        img_width, img_height = img.size
        img_width_pt = img_width * 72 / 300
        img_height_pt = img_height * 72 / 300
        
        x = (page_width - img_width_pt) / 2
        y = (page_height - img_height_pt) / 2
        
        pdf_canvas.drawImage(ImageReader(buffer), x, y, width=img_width_pt, height=img_height_pt)
        pdf_canvas.showPage()
    
    # Clean up all buffers
    for buffer in image_buffers:
        buffer.close()
    
    pdf_canvas.save()

def encode_and_decode(input_file, output_pdf, decoded_file, secure_mode=False, pretty_mode=True, password=None, private_key_path=None, public_key_path=None):
    if secure_mode:
        encoder = SimpleInterleavedBitPaperEncoder(password, private_key_path, error_correction_level=0.15)
        decoder = SimpleInterleavedBitPaperDecoder(password, public_key_path, error_correction_level=0.15)
        print("🔐 Using SECURE mode with encryption and error correction")
        
        # Secure mode uses single-page encoding
        bitstream, metadata = encoder.file_to_bitstream(input_file)
        bitstream_pages = [bitstream]
        metadata = {'filename': Path(input_file).name, 'size': len(open(input_file, 'rb').read())}
    else:
        encoder = BitPaperEncoder(pretty_mode=pretty_mode)
        decoder = BitPaperDecoder(pretty_mode=pretty_mode)
        mode = "PRETTY" if pretty_mode else "SIMPLE"
        print(f"📄 Using {mode} mode (multi-page support)")
        
        # Get bitstream pages and metadata
        bitstream_pages, metadata = encoder.file_to_bitstream_pages(input_file)
    
    print(f"Encoded into {len(bitstream_pages)} pages")
    print(f"File metadata: {metadata}")
    
    # Generate images for each page
    images = []
    total_bits = 0
    for i, bitstream in enumerate(bitstream_pages):
        if secure_mode:
            img = encoder.bitstream_to_image(bitstream)  # Secure mode: only bitstream
        else:
            img = encoder.bitstream_to_image(bitstream)  # Normal mode: use defaults for optional params
        images.append(img)
        total_bits += len(bitstream)
        print(f"Page {i+1}: {len(bitstream)} bits, image size: {img.size}")
    
    print(f"Total encoded bitstream length: {total_bits} bits")
    
    # Use ultra-fast PDF generation
    ultra_fast_save_images_to_pdf(images, output_pdf)
    print(f"PDF saved: {output_pdf} ({len(images)} pages)")
    os.system(f"open {output_pdf}")
    
    # Decode ALL pages with correct lengths
    print("\n Decoding all pages...")
    decoded_bitstream = decoder.images_to_bitstream(images)
    print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
    
    # Decode the data
    decoded_data, decoded_metadata = decoder.bitstream_to_data(decoded_bitstream)
    print(f"Decoded data size: {len(decoded_data)} bytes")
    print(f"Decoded metadata: {decoded_metadata}")
    
    # Save decoded file
    with open(decoded_file, 'wb') as f:
        f.write(decoded_data)
    print(f"Decoded file saved: {decoded_file}")
    
    # Verify data integrity
    with open(input_file, 'rb') as f:
        original_data = f.read()
    
    if decoded_data == original_data:
        print("✅ Data integrity verified!")
    else:
        print("❌ Data integrity check failed!")
        return False
    
    return True

def interactive_mode_selection():
    print("🧪 BitPaper - Interactive Mode Selection")
    print("=" * 50)
    
    # Get input file
    while True:
        input_file = input("Enter file path to encode: ").strip().strip("'\"")  # Remove quotes
        if os.path.exists(input_file):
            break
        print("❌ File not found. Please try again.")
    
    # Mode selection
    print("\n🎯 Select encoding mode:")
    print("1. Simple mode (max capacity, no margins)")
    print("2. Pretty mode (with margins, multi-page)")
    print("3. Secure mode (encrypted, error correction)")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    # Configure based on choice
    if choice == '1':
        pretty_mode = False
        secure_mode = False
        password = None
        private_key_path = None
        public_key_path = None
        output_pdf = "encoded_simple.pdf"
        decoded_file = "decoded_simple_" + Path(input_file).name
        print("📄 Using SIMPLE mode (max capacity)")
        
    elif choice == '2':
        pretty_mode = True
        secure_mode = False
        password = None
        private_key_path = None
        public_key_path = None
        output_pdf = "encoded_pretty.pdf"
        decoded_file = "decoded_pretty_" + Path(input_file).name
        print("📄 Using PRETTY mode (with margins)")
        
    else:  # choice == '3'
        pretty_mode = False
        secure_mode = True
        password = input("🔐 Enter password: ").strip()
        
        # Optional key files
        private_key_path = input("Enter Private key path (optional, press Enter to skip): ").strip()
        if not private_key_path:
            private_key_path = None
            
        public_key_path = input("🔑 Public key path (optional, press Enter to skip): ").strip()
        if not public_key_path:
            public_key_path = None
            
        output_pdf = "encoded_secure.pdf"
        decoded_file = "decoded_secure_" + Path(input_file).name
        print("🔐 Using SECURE mode (encrypted)")
    
    # Process the file
    print(f"\n🔄 Processing {input_file}...")
    encode_and_decode(input_file, output_pdf, decoded_file, 
                     secure_mode=secure_mode, pretty_mode=pretty_mode,
                     password=password, private_key_path=private_key_path, 
                     public_key_path=public_key_path)

def main():
    if len(sys.argv) > 1:
        # Command line mode (existing functionality)
        pretty_mode = True
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
            input_file = sys.argv[1]
            output_pdf = "encoded.pdf"
            decoded_file = "decoded_" + Path(input_file).name
        
        encode_and_decode(input_file, output_pdf, decoded_file, 
                         secure_mode=secure_mode, pretty_mode=pretty_mode,
                         password=password, private_key_path=private_key_path, 
                         public_key_path=public_key_path)
    else:
        # Interactive mode
        interactive_mode_selection()

if __name__ == "__main__":
    main()


