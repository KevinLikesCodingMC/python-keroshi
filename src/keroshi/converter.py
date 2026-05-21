import os
from pathlib import Path
import zipfile
import tempfile
from PIL import Image
from tqdm import tqdm

Image.init()

def jm2pdf(zip_path: str, output_path: str = None):
	zip_path = Path(zip_path)

	if not zip_path.exists():
		raise FileNotFoundError("Zip file not found.")

	if output_path is None:
		output_path = zip_path.with_suffix('.pdf')
	else:
		output_path = Path(output_path)

	with tempfile.TemporaryDirectory() as temp:
		temp_path = Path(temp)

		with zipfile.ZipFile(zip_path, 'r') as f:
			f.extractall(temp_path)

		img_paths = list(temp_path.rglob('*.webp'))
		img_paths.sort(key = lambda x : x.name)

		if not img_paths:
			print("No webp images found in the zip file.")
			return

		pil_imgs = []
		print(f"Processing {zip_path.name}, found {len(img_paths)} images...")

		for p in tqdm(img_paths, desc = "Converting"):
			try:
				img = Image.open(p)
				# RGBA 2 RGB
				if img.mode in ('RGBA', 'LA'):
					bg = Image.new("RGB", img.size, (255, 255, 255))
					bg.paste(img, mask = img.split()[3] if img.mode == 'RGBA' else None)
					pil_imgs.append(bg)
				else:
					pil_imgs.append(img.convert('RGB'))
			except Exception as e:
				print(f"\nSkipping corrupt image {p.name}: {e}")

		if pil_imgs:
			fst = pil_imgs[0]
			fst.save(output_path, save_all = True, append_images = pil_imgs[1 :])
			print(f"\nSuccess! PDF saved to: {output_path}")
		else:
			print("\nNo valid images to convert.")
