"""Inspect manual namespace device identities without opening devices."""
from common import kit, run
import ast
import sys

# Inspect device identities through the exact launcher namespace without opening
# devices or starting/focusing a compositor. Normal seat access remains manual.
tree = ast.parse((kit / "guided-session.py").read_text())
commands = [
    node
    for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "command" for t in node.targets)
]
command = next(node.value for node in commands if isinstance(node.value, ast.BinOp))
mask = ast.literal_eval(command.left)
assert "--dev-bind" in mask and "--unshare-net" in mask
assert "--dev" not in mask
probe = "import os, pathlib, json, socket; print(json.dumps({'devices': {str(p): [p.stat().st_dev, p.stat().st_rdev] for base in ['/dev/dri', '/dev/input'] for p in pathlib.Path(base).glob('*')}, 'net': socket.if_nameindex()}))"
run(
    "real-seat-device-bindings",
    [
        sys.executable,
        "-c",
        "\n".join(
            [
                "import json, subprocess",
                "probe = " + repr(probe),
                "host = json.loads(subprocess.check_output(['python3', '-c', probe], text=True))",
                "isolated = json.loads(subprocess.check_output("
                + repr(mask + ["--", "python3", "-c", probe])
                + ", text=True))",
                "assert host['devices'] and host['devices'] == isolated['devices']",
                "assert [name for _, name in isolated['net']] == ['lo']",
                "print(json.dumps(isolated, indent=2))",
            ]
        ),
    ],
)
