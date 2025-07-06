from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import random

A4_WIDTH = 2480
A4_HEIGHT = 3508

class CameraSimulator:
    @staticmethod
    def simulate(image, noise_level=0.1, blur_level=0.5, contrast_variation=0.2, perspective_distortion=True):
        if image.mode != 'RGB':
            image = image.convert('RGB')
        working = image.copy()
        if perspective_distortion:
            angle = random.uniform(-3, 3)
            scale_factor = random.uniform(0.95, 1.05)
            working = working.rotate(angle, expand=True, fillcolor=(255, 255, 255))
            if scale_factor != 1.0:
                new_width = int(working.width * scale_factor)
                new_height = int(working.height * scale_factor)
                working = working.resize((new_width, new_height))
            width, height = working.size
            # Ensure margin is not too large
            margin = max(0, min(int(0.08 * min(width, height)), min(width, height) // 4))
            src = [
                (0, 0),
                (width - 1, 0),
                (width - 1, height - 1),
                (0, height - 1)
            ]
            max_shift = max(1, int(0.07 * min(width, height)))
            dst = [
                (random.randint(0, max_shift), random.randint(0, max_shift)),
                (width - 1 - random.randint(0, max_shift), random.randint(0, max_shift)),
                (width - 1 - random.randint(0, max_shift), height - 1 - random.randint(0, max_shift)),
                (random.randint(0, max_shift), height - 1 - random.randint(0, max_shift))
            ]
            coeffs = CameraSimulator._find_perspective_coeffs(src, dst)
            if len(coeffs) != 8:
                raise ValueError('Perspective transform requires 8 coefficients')
            transformed = working.transform(
                (width + 2 * margin, height + 2 * margin),
                Image.Transform.PERSPECTIVE,
                coeffs,
                resample=Image.Resampling.BICUBIC,
                fillcolor=(255, 255, 255)
            )
            working = transformed
        if blur_level > 0:
            blur_radius = int(blur_level * 2)
            working = working.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        if contrast_variation > 0:
            contrast_factor = 1.0 + random.uniform(-contrast_variation, contrast_variation)
            enhancer = ImageEnhance.Contrast(working)
            working = enhancer.enhance(contrast_factor)
            brightness_factor = 1.0 + random.uniform(-contrast_variation, contrast_variation)
            enhancer = ImageEnhance.Brightness(working)
            working = enhancer.enhance(brightness_factor)
        if noise_level > 0:
            img_array = np.array(working)
            noise = np.random.normal(0, noise_level * 50, img_array.shape).astype(np.int16)
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            working = Image.fromarray(img_array)
        # Resize to fit A4 if needed
        w, h = working.size
        scale = min(A4_WIDTH / w, A4_HEIGHT / h, 1.0)
        if scale < 1.0:
            working = working.resize((int(w * scale), int(h * scale)), resample=Image.Resampling.LANCZOS)
        # Always output A4 size, centered, no cropping
        a4_canvas = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
        x = (A4_WIDTH - working.width) // 2
        y = (A4_HEIGHT - working.height) // 2
        a4_canvas.paste(working, (x, y))
        return a4_canvas.convert('L')

    @staticmethod
    def _find_perspective_coeffs(src, dst):
        matrix = []
        for p1, p2 in zip(dst, src):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
        A = np.array(matrix, dtype=np.float64)
        B = np.array(src).reshape(8)
        res = np.linalg.lstsq(A, B, rcond=None)[0]
        return res.tolist() 