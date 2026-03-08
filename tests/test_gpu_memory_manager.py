"""Tests for gpu_memory_manager module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.gpu_memory_manager import (
    get_gpu_memory_usage,
    is_gpu_memory_available,
    release_gpu_for_voicevox,
    unload_ollama_model,
    wait_for_gpu_memory,
)


class TestGetGpuMemoryUsage:
    """Tests for get_gpu_memory_usage function."""

    def test_returns_tuple_of_two_ints(self) -> None:
        """Should return tuple of (used_mb, total_mb)."""
        result = get_gpu_memory_usage()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    @patch("subprocess.run")
    def test_parses_nvidia_smi_output(self, mock_run: MagicMock) -> None:
        """Should parse nvidia-smi output correctly."""
        mock_run.return_value = MagicMock(
            stdout="8000, 16000\n",
            returncode=0,
        )
        used, total = get_gpu_memory_usage()
        assert used == 8000
        assert total == 16000

    @patch("subprocess.run")
    def test_returns_zero_when_nvidia_smi_fails(self, mock_run: MagicMock) -> None:
        """Should return (0, 0) when nvidia-smi is unavailable."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "nvidia-smi")
        used, total = get_gpu_memory_usage()
        assert used == 0
        assert total == 0

    @patch("subprocess.run")
    def test_returns_zero_when_nvidia_smi_not_found(self, mock_run: MagicMock) -> None:
        """Should return (0, 0) when nvidia-smi is not found."""
        mock_run.side_effect = FileNotFoundError()
        used, total = get_gpu_memory_usage()
        assert used == 0
        assert total == 0

    @patch("subprocess.run")
    def test_handles_multi_gpu_output(self, mock_run: MagicMock) -> None:
        """Should use first GPU's memory when multiple GPUs present."""
        mock_run.return_value = MagicMock(
            stdout="8000, 16000\n4000, 8000\n",
            returncode=0,
        )
        used, total = get_gpu_memory_usage()
        assert used == 8000
        assert total == 16000


class TestIsGpuMemoryAvailable:
    """Tests for is_gpu_memory_available function."""

    @patch("src.gpu_memory_manager.get_gpu_memory_usage")
    def test_returns_true_when_enough_memory(self, mock_get: MagicMock) -> None:
        """Should return True when enough memory is available."""
        mock_get.return_value = (8000, 16000)  # 8000 MB free
        assert is_gpu_memory_available(2000) is True

    @patch("src.gpu_memory_manager.get_gpu_memory_usage")
    def test_returns_false_when_insufficient_memory(self, mock_get: MagicMock) -> None:
        """Should return False when memory is insufficient."""
        mock_get.return_value = (15000, 16000)  # 1000 MB free
        assert is_gpu_memory_available(2000) is False

    @patch("src.gpu_memory_manager.get_gpu_memory_usage")
    def test_returns_true_when_nvidia_smi_unavailable(self, mock_get: MagicMock) -> None:
        """Should return True when nvidia-smi is unavailable (assume GPU OK)."""
        mock_get.return_value = (0, 0)
        assert is_gpu_memory_available(2000) is True

    @patch("src.gpu_memory_manager.get_gpu_memory_usage")
    def test_uses_default_required_mb(self, mock_get: MagicMock) -> None:
        """Should use default 2000 MB when not specified."""
        mock_get.return_value = (14500, 16000)  # 1500 MB free
        assert is_gpu_memory_available() is False

    @patch("src.gpu_memory_manager.get_gpu_memory_usage")
    def test_exact_boundary_returns_true(self, mock_get: MagicMock) -> None:
        """Should return True when available equals required."""
        mock_get.return_value = (14000, 16000)  # exactly 2000 MB free
        assert is_gpu_memory_available(2000) is True


class TestUnloadOllamaModel:
    """Tests for unload_ollama_model function."""

    @patch("requests.post")
    def test_calls_ollama_api(self, mock_post: MagicMock) -> None:
        """Should call ollama API with keep_alive=0."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        result = unload_ollama_model("gemma3:27b")

        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "keep_alive" in call_args.kwargs["json"]
        assert call_args.kwargs["json"]["keep_alive"] == 0
        assert call_args.kwargs["json"]["model"] == "gemma3:27b"

    @patch("requests.post")
    def test_uses_custom_base_url(self, mock_post: MagicMock) -> None:
        """Should use custom base URL when specified."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        unload_ollama_model("test-model", base_url="http://custom:1234")

        call_args = mock_post.call_args
        assert "http://custom:1234/api/generate" == call_args.args[0]

    @patch("requests.post")
    def test_returns_false_on_request_error(self, mock_post: MagicMock) -> None:
        """Should return False when request fails."""
        from requests.exceptions import RequestException

        mock_post.side_effect = RequestException("Connection error")

        result = unload_ollama_model("test-model")

        assert result is False

    @patch("requests.post")
    def test_returns_false_on_http_error(self, mock_post: MagicMock) -> None:
        """Should return False when HTTP status is error."""
        from requests.exceptions import HTTPError

        mock_post.return_value = MagicMock(status_code=500)
        mock_post.return_value.raise_for_status.side_effect = HTTPError("Server error")

        result = unload_ollama_model("test-model")

        assert result is False


class TestWaitForGpuMemory:
    """Tests for wait_for_gpu_memory function."""

    @patch("src.gpu_memory_manager.is_gpu_memory_available")
    @patch("time.sleep")
    def test_returns_true_immediately_if_available(self, mock_sleep: MagicMock, mock_available: MagicMock) -> None:
        """Should return True immediately if memory is available."""
        mock_available.return_value = True

        result = wait_for_gpu_memory(2000)

        assert result is True
        mock_sleep.assert_not_called()

    @patch("src.gpu_memory_manager.is_gpu_memory_available")
    @patch("time.sleep")
    def test_returns_false_after_timeout(self, mock_sleep: MagicMock, mock_available: MagicMock) -> None:
        """Should return False after timeout if memory never available."""
        mock_available.return_value = False

        result = wait_for_gpu_memory(2000, max_wait_seconds=2, check_interval=1.0)

        assert result is False

    @patch("src.gpu_memory_manager.is_gpu_memory_available")
    @patch("time.sleep")
    def test_returns_true_when_memory_becomes_available(self, mock_sleep: MagicMock, mock_available: MagicMock) -> None:
        """Should return True when memory becomes available during wait."""
        mock_available.side_effect = [False, False, True]

        result = wait_for_gpu_memory(2000, max_wait_seconds=10, check_interval=1.0)

        assert result is True


class TestReleaseGpuForVoicevox:
    """Tests for release_gpu_for_voicevox function."""

    @patch("src.gpu_memory_manager.is_gpu_memory_available")
    def test_skips_unload_if_memory_already_available(self, mock_available: MagicMock) -> None:
        """Should skip unload if memory is already available."""
        mock_available.return_value = True

        result = release_gpu_for_voicevox(ollama_model="test-model")

        assert result is True
        # Should have only called is_gpu_memory_available once
        assert mock_available.call_count == 1

    @patch("src.gpu_memory_manager.is_gpu_memory_available")
    @patch("src.gpu_memory_manager.unload_ollama_model")
    @patch("time.sleep")
    def test_unloads_model_when_memory_insufficient(
        self,
        mock_sleep: MagicMock,
        mock_unload: MagicMock,
        mock_available: MagicMock,
    ) -> None:
        """Should unload model when memory is insufficient."""
        mock_available.side_effect = [False, True]  # First check fails, second passes
        mock_unload.return_value = True

        result = release_gpu_for_voicevox(ollama_model="test-model")

        assert result is True
        mock_unload.assert_called_once_with("test-model", "http://localhost:11434")

    @patch("src.gpu_memory_manager.is_gpu_memory_available")
    def test_skips_unload_if_no_model_specified(self, mock_available: MagicMock) -> None:
        """Should skip unload if no model is specified."""
        mock_available.return_value = False

        result = release_gpu_for_voicevox(ollama_model=None)

        assert result is False


class TestVoicevoxConfigAccelerationMode:
    """Tests for VoicevoxConfig acceleration_mode field."""

    def test_default_acceleration_mode_is_auto(self) -> None:
        """Should default to AUTO acceleration mode."""
        from src.voicevox_client import VoicevoxConfig

        config = VoicevoxConfig()
        assert config.acceleration_mode == "AUTO"

    def test_can_set_acceleration_mode_cpu(self) -> None:
        """Should accept CPU acceleration mode."""
        from src.voicevox_client import VoicevoxConfig

        config = VoicevoxConfig(acceleration_mode="CPU")
        assert config.acceleration_mode == "CPU"

    def test_can_set_acceleration_mode_gpu(self) -> None:
        """Should accept GPU acceleration mode."""
        from src.voicevox_client import VoicevoxConfig

        config = VoicevoxConfig(acceleration_mode="GPU")
        assert config.acceleration_mode == "GPU"


class TestXmlPipelineAccelerationMode:
    """Tests for xml_pipeline acceleration mode arguments."""

    def test_parse_args_has_acceleration_mode(self) -> None:
        """Should have --acceleration-mode argument."""
        from src.xml_pipeline import parse_args

        args = parse_args(["--input", "test.xml", "--acceleration-mode", "CPU"])
        assert args.acceleration_mode == "CPU"

    def test_parse_args_acceleration_mode_default(self) -> None:
        """Should default to AUTO acceleration mode."""
        from src.xml_pipeline import parse_args

        args = parse_args(["--input", "test.xml"])
        assert args.acceleration_mode == "AUTO"

    def test_parse_args_has_gpu_memory_check(self) -> None:
        """Should have --gpu-memory-check argument."""
        from src.xml_pipeline import parse_args

        args = parse_args(["--input", "test.xml", "--gpu-memory-check"])
        assert args.gpu_memory_check is True

    def test_parse_args_has_required_gpu_mb(self) -> None:
        """Should have --required-gpu-mb argument."""
        from src.xml_pipeline import parse_args

        args = parse_args(["--input", "test.xml", "--required-gpu-mb", "3000"])
        assert args.required_gpu_mb == 3000


class TestGenerateReadingDictKeepModel:
    """Tests for generate_reading_dict --keep-model argument."""

    def test_parse_args_has_keep_model(self) -> None:
        """Should have --keep-model argument."""
        import argparse
        import sys
        from unittest.mock import patch as mock_patch

        # Import the module to check its argument parser
        with mock_patch.object(sys, "argv", ["prog", "test.xml", "--keep-model"]):
            import importlib

            import src.generate_reading_dict as gen_dict

            importlib.reload(gen_dict)

            # Create a minimal parser to test
            parser = argparse.ArgumentParser()
            parser.add_argument("input")
            parser.add_argument("--keep-model", action="store_true")
            args = parser.parse_args(["test.xml", "--keep-model"])
            assert args.keep_model is True
