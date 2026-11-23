"""Initialize DVC and prove recovery from its remote with an empty isolated cache."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from src.data import DATA, prepare


def run(*args, cwd=None):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', '/app'], check=True)
    if not Path('.git').exists():
        run('git', 'init', '-b', 'main')
    if not Path('.dvc/.gitignore').exists():
        run('dvc', 'init', '-f')
    before = prepare()
    run('dvc', 'add', str(DATA))
    run('dvc', 'remote', 'add', '-f', '-d', 'localstore', 'runtime/dvc-remote')
    pushed = run('dvc', 'push')
    # Separate workspace and empty cache: no removal of the user's data or cache.
    with tempfile.TemporaryDirectory() as temp:
        run('dvc', 'init', '--no-scm', cwd=temp)
        Path(temp, 'data').mkdir()
        Path(temp, 'data/iris.csv.dvc').write_bytes(Path('data/iris.csv.dvc').read_bytes())
        run('dvc', 'remote', 'add', '-d', 'source', str(Path('runtime/dvc-remote').resolve()), cwd=temp)
        pulled = run('dvc', 'pull', cwd=temp)
        after = hashlib.sha256(Path(temp, 'data/iris.csv').read_bytes()).hexdigest()
    assert before == after
    evidence = dict(sha256_original=before, sha256_restored=after, identical=True,
                    fresh_workspace=True, push=pushed, pull=pulled)
    Path('evidence').mkdir(exist_ok=True)
    Path('evidence/dvc_push_pull.json').write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
