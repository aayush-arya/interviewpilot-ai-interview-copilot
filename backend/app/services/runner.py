"""Sandboxed code execution (see docs/SECURITY.md for the threat model and
the container-per-run upgrade path for multi-tenant deployments).

Contract: programs read from stdin, write to stdout. A test passes when
trimmed stdout equals the trimmed expected output.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

from app.core.config import get_settings

OUTPUT_CAP = 64 * 1024

LANGUAGE_CONFIG = {
    "python": {"file": "main.py", "cmd": lambda d: [sys.executable, "-I", os.path.join(d, "main.py")]},
    "javascript": {"file": "main.js", "cmd": lambda d: ["node", os.path.join(d, "main.js")]},
    "java": {"file": "Main.java", "compile": lambda d: ["javac", os.path.join(d, "Main.java")],
             "cmd": lambda d: ["java", "-cp", d, "Main"]},
    "cpp": {"file": "main.cpp",
            "compile": lambda d: ["g++", "-O2", "-o", os.path.join(d, "main_exe"), os.path.join(d, "main.cpp")],
            "cmd": lambda d: [os.path.join(d, "main_exe")]},
}


@dataclass
class RunResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    runtime_ms: int


def _minimal_env() -> dict:
    """Strip secrets; keep only what interpreters need to start."""
    keep = {"SYSTEMROOT", "PATH", "TEMP", "TMP", "PATHEXT", "COMSPEC", "HOME", "LANG"}
    return {k: v for k, v in os.environ.items() if k.upper() in keep}


class CodeRunner:
    def __init__(self, timeout_s: float | None = None):
        self.timeout_s = timeout_s or get_settings().CODE_TIMEOUT_SECONDS

    def language_available(self, language: str) -> bool:
        probe = {"python": sys.executable, "javascript": "node", "java": "javac", "cpp": "g++"}
        return shutil.which(probe[language]) is not None

    def run(self, language: str, code: str, stdin: str = "") -> RunResult:
        config = LANGUAGE_CONFIG[language]
        if not self.language_available(language):
            return RunResult("", f"{language} runtime is not installed on this server", 127, False, 0)

        workdir = tempfile.mkdtemp(prefix="icrun_")
        try:
            with open(os.path.join(workdir, config["file"]), "w", encoding="utf-8") as f:
                f.write(code)

            if "compile" in config:
                compile_result = self._exec(config["compile"](workdir), "", workdir)
                if compile_result.exit_code != 0:
                    return RunResult("", compile_result.stderr or "Compilation failed",
                                     compile_result.exit_code, compile_result.timed_out, 0)

            return self._exec(config["cmd"](workdir), stdin, workdir)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def _exec(self, cmd: list[str], stdin: str, cwd: str) -> RunResult:
        start = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
                cwd=cwd,
                env=_minimal_env(),
            )
            runtime = int((time.monotonic() - start) * 1000)
            return RunResult(
                stdout=proc.stdout[:OUTPUT_CAP],
                stderr=proc.stderr[:OUTPUT_CAP],
                exit_code=proc.returncode,
                timed_out=False,
                runtime_ms=runtime,
            )
        except subprocess.TimeoutExpired as e:
            runtime = int((time.monotonic() - start) * 1000)
            out = e.stdout or ""
            if isinstance(out, bytes):
                out = out.decode(errors="replace")
            return RunResult(out[:OUTPUT_CAP], "Time limit exceeded", -1, True, runtime)
        except FileNotFoundError:
            return RunResult("", "Runtime executable not found", 127, False, 0)
