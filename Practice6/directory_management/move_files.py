import shutil
from pathlib import Path

src_dir = Path("source_dir")
dst_dir = Path("destination_dir")
archive_dir = Path("archive_dir")

# Setup directories and files
src_dir.mkdir(exist_ok=True)
dst_dir.mkdir(exist_ok=True)
archive_dir.mkdir(exist_ok=True)

for i in range(1, 4):
    (src_dir / f"file{i}.txt").write_text(f"Content of file {i}")
(src_dir / "image.png").write_text("fake png data")
(src_dir / "report.pdf").write_text("fake pdf data")

print("Source directory contents:")
for f in sorted(src_dir.iterdir()):
    print(f"  {f.name}")

# Move all .txt files to destination
print("\nMoving .txt files to destination_dir...")
for txt_file in list(src_dir.glob("*.txt")):
    shutil.move(str(txt_file), str(dst_dir / txt_file.name))
    print(f"  Moved: {txt_file.name}")

# Copy remaining files to archive
print("\nCopying remaining files to archive_dir...")
for remaining in src_dir.iterdir():
    shutil.copy2(remaining, archive_dir / remaining.name)
    print(f"  Copied: {remaining.name}")

print("\nDestination dir:")
for f in sorted(dst_dir.iterdir()):
    print(f"  {f.name}")

print("\nArchive dir:")
for f in sorted(archive_dir.iterdir()):
    print(f"  {f.name}")

# Cleanup
shutil.rmtree(src_dir, ignore_errors=True)
shutil.rmtree(dst_dir, ignore_errors=True)
shutil.rmtree(archive_dir, ignore_errors=True)
print("\nCleaned up all directories.")
