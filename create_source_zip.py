import pathlib
import zipfile

root = pathlib.Path(r'C:\Users\Siddharth\Downloads\Autonomous_Code_Debugging_Agent')
out = root / 'Autonomous_Code_Debugging_Agent_Source.zip'
exclude = {'.git', '.venv', 'build', 'dist', '.pytest_cache', '.cache', 'generated_repos', 'reports'}

with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        rel = p.relative_to(root)
        if p.is_dir() and any(part in exclude for part in rel.parts):
            continue
        if p.is_file() and any(part in exclude for part in rel.parts):
            continue
        if p.is_file():
            z.write(p, arcname=rel.as_posix())

print('ZIP_CREATED', out.exists(), out.stat().st_size)
