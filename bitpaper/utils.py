class Config:
    # Optimized for full A4 usage AND printability
    cell_size = 6  # Back to 6px for reliable printing
    bits_per_row = 413  # Full A4 width: 2480px ÷ 6px = 413
    max_rows = 584  # Full A4 height: 3508px ÷ 6px = 584
    border_width = 3  # Balanced border
    error_correction_level = 0.1
    enable_encryption = False
    enable_interleaving = False
    enable_signatures = False 