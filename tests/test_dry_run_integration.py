"""Integration tests for --dry-run mode across all pipeline steps.

These tests verify that each pipeline entry point:
1. Accepts --dry-run flag
2. Exits with code 0
3. Outputs expected [dry-run] summary lines
4. Does NOT perform expensive operations (LLM calls, TTS, file writes)
"""

import os
import subprocess
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
INTEGRATION_BOOK = FIXTURES_DIR / "integration_book.xml"
PROJECT_ROOT = Path(__file__).parent.parent


def run_dry_run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run a pipeline command with --dry-run and return the result.

    Returns CompletedProcess with combined stdout+stderr in stdout attribute.
    """
    env_cmd = [sys.executable, *cmd]
    env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    return subprocess.run(
        env_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT),
        env=env,
    )


def _get_dialogue_fixture(tmp_path: Path) -> Path:
    """Create a minimal dialogue XML fixture for testing."""
    dialogue_dir = tmp_path / "hash123"
    dialogue_dir.mkdir(parents=True, exist_ok=True)
    dialogue_file = dialogue_dir / "dialogue_book.xml"
    dialogue_file.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<dialogue_book>\n"
        '  <dialogue-section number="1" title="Test Section">\n'
        '    <introduction speaker="narrator">テストの導入です。</introduction>\n'
        "    <dialogue>\n"
        '      <utterance speaker="SPEAKER_A">テストの発話です。</utterance>\n'
        '      <utterance speaker="SPEAKER_B">テストの応答です。</utterance>\n'
        "    </dialogue>\n"
        '    <conclusion speaker="narrator">テストの結論です。</conclusion>\n'
        "  </dialogue-section>\n"
        "</dialogue_book>\n",
        encoding="utf-8",
    )
    return dialogue_file


class TestGenDictDryRun:
    """Integration tests for generate_reading_dict.py --dry-run."""

    def test_exits_successfully(self) -> None:
        result = run_dry_run(
            [
                "src/generate_reading_dict.py",
                str(INTEGRATION_BOOK),
                "--model",
                "dummy-model",
                "--dry-run",
            ]
        )
        assert result.returncode == 0, f"output: {result.stdout}"

    def test_outputs_dry_run_summary(self) -> None:
        result = run_dry_run(
            [
                "src/generate_reading_dict.py",
                str(INTEGRATION_BOOK),
                "--model",
                "dummy-model",
                "--dry-run",
            ]
        )
        output = result.stdout
        assert "DRY-RUN" in output
        assert "Input" in output
        assert "Total terms" in output

    def test_no_llm_call_attempted(self) -> None:
        """Verify dry-run doesn't try to connect to Ollama (would fail without server)."""
        result = run_dry_run(
            [
                "src/generate_reading_dict.py",
                str(INTEGRATION_BOOK),
                "--model",
                "nonexistent-model",
                "--dry-run",
            ]
        )
        assert result.returncode == 0


class TestCleanTextDryRun:
    """Integration tests for text_cleaner_cli --dry-run."""

    def test_exits_successfully(self) -> None:
        result = run_dry_run(
            [
                "-m",
                "src.text_cleaner_cli",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                "/tmp/test_dry_run_output",
                "--dry-run",
            ]
        )
        assert result.returncode == 0, f"output: {result.stdout}"

    def test_outputs_dry_run_summary(self) -> None:
        result = run_dry_run(
            [
                "-m",
                "src.text_cleaner_cli",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                "/tmp/test_dry_run_output",
                "--dry-run",
            ]
        )
        output = result.stdout
        assert "DRY-RUN" in output
        assert "Content items" in output

    def test_no_file_written(self, tmp_path: Path) -> None:
        """Verify dry-run doesn't create output files."""
        output_dir = tmp_path / "dry_run_output"
        result = run_dry_run(
            [
                "-m",
                "src.text_cleaner_cli",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                str(output_dir),
                "--dry-run",
            ]
        )
        assert result.returncode == 0
        assert not output_dir.exists(), "Output directory should not be created in dry-run"


class TestXmlTtsDryRun:
    """Integration tests for xml_pipeline --dry-run."""

    def test_exits_successfully(self) -> None:
        result = run_dry_run(
            [
                "-m",
                "src.xml_pipeline",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                "/tmp/test_dry_run_output",
                "--dry-run",
            ]
        )
        assert result.returncode == 0, f"output: {result.stdout}"

    def test_outputs_dry_run_summary(self) -> None:
        result = run_dry_run(
            [
                "-m",
                "src.xml_pipeline",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                "/tmp/test_dry_run_output",
                "--dry-run",
            ]
        )
        output = result.stdout
        assert "DRY-RUN" in output
        assert "Content items" in output
        assert "Total characters" in output
        assert "Estimated TTS chunks" in output

    def test_no_voicevox_initialization(self) -> None:
        """Verify dry-run doesn't try to initialize VOICEVOX (would fail without runtime)."""
        result = run_dry_run(
            [
                "-m",
                "src.xml_pipeline",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                "/tmp/test_dry_run_output",
                "--voicevox-dir",
                "/nonexistent/voicevox",
                "--dry-run",
            ]
        )
        assert result.returncode == 0

    def test_no_file_written(self, tmp_path: Path) -> None:
        """Verify dry-run doesn't create output directory."""
        output_dir = tmp_path / "dry_run_output"
        result = run_dry_run(
            [
                "-m",
                "src.xml_pipeline",
                "-i",
                str(INTEGRATION_BOOK),
                "-o",
                str(output_dir),
                "--dry-run",
            ]
        )
        assert result.returncode == 0
        assert not output_dir.exists(), "Output directory should not be created in dry-run"


class TestDialoguePipelineDryRun:
    """Integration tests for dialogue_pipeline --dry-run."""

    def test_exits_successfully(self, tmp_path: Path) -> None:
        dialogue_file = _get_dialogue_fixture(tmp_path)
        result = run_dry_run(
            [
                "-m",
                "src.dialogue_pipeline",
                "-i",
                str(dialogue_file),
                "-o",
                str(tmp_path),
                "--dict-source",
                str(INTEGRATION_BOOK),
                "--dry-run",
            ]
        )
        assert result.returncode == 0, f"output: {result.stdout}"

    def test_outputs_dry_run_summary(self, tmp_path: Path) -> None:
        dialogue_file = _get_dialogue_fixture(tmp_path)
        result = run_dry_run(
            [
                "-m",
                "src.dialogue_pipeline",
                "-i",
                str(dialogue_file),
                "-o",
                str(tmp_path),
                "--dict-source",
                str(INTEGRATION_BOOK),
                "--dry-run",
            ]
        )
        output = result.stdout
        assert "DRY-RUN" in output
        assert "Sections" in output
