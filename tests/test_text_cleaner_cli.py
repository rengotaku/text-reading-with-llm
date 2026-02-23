"""Tests for text_cleaner_cli.py - XML to cleaned_text.txt CLI.

Phase 2 RED Tests - US1: テキストクリーニング単独実行
Target: src/text_cleaner_cli.py (parse_args, main)

Test Fixture: tests/fixtures/sample_book2.xml

Tasks:
- T008: CLI 引数パーステスト
- T009: XML -> cleaned_text.txt 生成テスト
- T010: エラーハンドリングテスト
- T011: 出力ディレクトリ自動作成テスト
"""

from pathlib import Path
from unittest.mock import patch

import pytest

# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK2_XML = FIXTURES_DIR / "sample_book2.xml"


# =============================================================================
# T008: CLI 引数パーステスト
# =============================================================================


class TestParseArgsInputRequired:
    """parse_args の --input 引数が必須であることを検証する。"""

    def test_parse_args_function_exists(self):
        """parse_args 関数が存在する"""
        from src.text_cleaner_cli import parse_args

        assert callable(parse_args), "parse_args は呼び出し可能な関数であるべき"

    def test_parse_args_no_args_exits(self):
        """引数なしで SystemExit (code 2) が発生する"""
        from src.text_cleaner_cli import parse_args

        with pytest.raises(SystemExit) as exc_info:
            parse_args([])

        assert exc_info.value.code == 2, (
            f"引数なしの場合、終了コード 2 であるべきだが、{exc_info.value.code} が返された"
        )

    def test_parse_args_accepts_input_long(self):
        """--input 引数を受け付ける"""
        from src.text_cleaner_cli import parse_args

        args = parse_args(["--input", str(SAMPLE_BOOK2_XML)])

        assert args.input == str(SAMPLE_BOOK2_XML), f"--input が正しくパースされるべきだが、'{args.input}' が返された"

    def test_parse_args_accepts_input_short(self):
        """-i 短縮形を受け付ける"""
        from src.text_cleaner_cli import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.input == str(SAMPLE_BOOK2_XML), f"-i が正しくパースされるべきだが、'{args.input}' が返された"


class TestParseArgsOutputOption:
    """parse_args の --output オプションを検証する。"""

    def test_output_default(self):
        """--output のデフォルトは ./output"""
        from src.text_cleaner_cli import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.output == "./output", (
            f"--output のデフォルトは './output' であるべきだが、'{args.output}' が返された"
        )

    def test_output_custom(self):
        """--output にカスタム値を設定"""
        from src.text_cleaner_cli import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--output", "/tmp/custom_output"])

        assert args.output == "/tmp/custom_output", (
            f"--output は '/tmp/custom_output' であるべきだが、'{args.output}' が返された"
        )

    def test_output_short_flag(self):
        """-o 短縮形を受け付ける"""
        from src.text_cleaner_cli import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "-o", "/tmp/out"])

        assert args.output == "/tmp/out", f"-o は '/tmp/out' であるべきだが、'{args.output}' が返された"


class TestParseArgsNoTtsOptions:
    """parse_args に TTS 関連オプション（--style-id, --speed 等）が存在しないことを検証する。
    text_cleaner_cli はテキストクリーニング専用であり、TTS オプションは不要。
    """

    def test_no_style_id_option(self):
        """--style-id オプションが存在しない"""
        from src.text_cleaner_cli import parse_args

        # --style-id を渡すとエラーになるべき（未知のオプション）
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["-i", str(SAMPLE_BOOK2_XML), "--style-id", "13"])

        assert exc_info.value.code == 2, "--style-id は text_cleaner_cli では未サポートであるべきだが、受け付けられた"

    def test_no_speed_option(self):
        """--speed オプションが存在しない"""
        from src.text_cleaner_cli import parse_args

        with pytest.raises(SystemExit) as exc_info:
            parse_args(["-i", str(SAMPLE_BOOK2_XML), "--speed", "1.5"])

        assert exc_info.value.code == 2, "--speed は text_cleaner_cli では未サポートであるべきだが、受け付けられた"


# =============================================================================
# T009: XML -> cleaned_text.txt 生成テスト
# =============================================================================


class TestMainGeneratesCleanedText:
    """main() が XML から cleaned_text.txt を正しく生成することを検証する。

    受け入れシナリオ 1:
    - Given XML ファイルが存在する
    - When main() を実行
    - Then 出力ディレクトリに cleaned_text.txt が生成される
    """

    def test_main_function_exists(self):
        """main 関数が存在する"""
        from src.text_cleaner_cli import main

        assert callable(main), "main は呼び出し可能な関数であるべき"

    def test_main_creates_cleaned_text_file(self, tmp_path):
        """main() が cleaned_text.txt を生成する"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"

        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        # 出力ディレクトリ内（ハッシュベースサブディレクトリ）に cleaned_text.txt が存在するべき
        cleaned_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_files) >= 1, (
            f"cleaned_text.txt が生成されるべきだが、見つからなかった。output_dir の内容: {list(output_dir.rglob('*'))}"
        )

    def test_main_cleaned_text_not_empty(self, tmp_path):
        """生成された cleaned_text.txt が空でない"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"

        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        cleaned_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_files[0].read_text(encoding="utf-8")
        assert len(content.strip()) > 0, "cleaned_text.txt は空でないべきだが、空のファイルが生成された"

    def test_main_no_tts_processing(self, tmp_path):
        """main() は TTS 処理を実行しない（音声ファイルが生成されない）"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"

        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        # WAV ファイルが生成されないことを確認
        wav_files = list(output_dir.rglob("*.wav"))
        assert len(wav_files) == 0, f"TTS 処理は実行されないべきだが、WAV ファイルが見つかった: {wav_files}"

    def test_main_cleaned_text_contains_chapter_markers(self, tmp_path):
        """cleaned_text.txt に章区切りマーカーが含まれる"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"

        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        cleaned_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_files[0].read_text(encoding="utf-8")
        # xml2_pipeline.py と同じ === Chapter N: Title === 形式
        assert "===" in content, f"cleaned_text.txt に章区切りマーカー（=== 形式）が含まれるべき: {content!r}"


class TestMainOverwritesExistingFile:
    """受け入れシナリオ 2: 既存ファイルの上書きを検証する。

    - Given cleaned_text.txt が既に存在する
    - When main() を再実行
    - Then 既存ファイルが上書きされる
    """

    def test_main_overwrites_existing_cleaned_text(self, tmp_path):
        """既存の cleaned_text.txt が上書きされる"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"

        # 1回目の実行
        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        cleaned_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_files) >= 1, "1回目の実行で cleaned_text.txt が生成されるべき"
        first_content = cleaned_files[0].read_text(encoding="utf-8")

        # 既存ファイルにダミーコンテンツを書き込み
        cleaned_files[0].write_text("DUMMY_CONTENT_TO_BE_OVERWRITTEN", encoding="utf-8")

        # 2回目の実行
        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        # 上書きされているべき
        second_content = cleaned_files[0].read_text(encoding="utf-8")
        assert second_content != "DUMMY_CONTENT_TO_BE_OVERWRITTEN", (
            "cleaned_text.txt は上書きされるべきだが、ダミーコンテンツのまま"
        )
        assert second_content == first_content, "2回目の実行結果は1回目と同一であるべき"


# =============================================================================
# T010: エラーハンドリングテスト
# =============================================================================


class TestErrorHandling:
    """エラーケースのテストを検証する。

    受け入れシナリオ 3:
    - Given XML ファイルが存在しない
    - When main() を実行
    - Then エラーメッセージが表示され終了コード 1 が返る
    """

    def test_file_not_found_raises_error(self):
        """存在しないファイルで FileNotFoundError が発生する"""
        from src.text_cleaner_cli import main

        non_existent = "/tmp/non_existent_test_book.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        assert non_existent in str(exc_info.value), f"エラーメッセージにファイルパスが含まれるべき: {exc_info.value}"

    def test_file_not_found_with_sys_exit(self):
        """存在しないファイルで SystemExit(1) が発生する（CLI モード）"""
        from src.text_cleaner_cli import main

        non_existent = "/tmp/non_existent_test_book.xml"

        # main は FileNotFoundError を発生させるか SystemExit(1) を発生させるべき
        with pytest.raises((FileNotFoundError, SystemExit)) as exc_info:
            main(["--input", non_existent])

        if isinstance(exc_info.value, SystemExit):
            assert exc_info.value.code == 1, f"終了コードは 1 であるべきだが、{exc_info.value.code} が返された"

    def test_invalid_xml_raises_error(self, tmp_path):
        """不正な XML でエラーが発生する"""
        from src.text_cleaner_cli import main

        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("<book><paragraph>unclosed", encoding="utf-8")

        with pytest.raises(Exception) as exc_info:
            main(["--input", str(invalid_xml)])

        error_type = type(exc_info.value).__name__
        assert "ParseError" in error_type or "XML" in str(exc_info.value).upper() or "Error" in error_type, (
            f"不正な XML でパースエラーが発生するべき。実際: {error_type}: {exc_info.value}"
        )

    def test_empty_xml_no_crash(self, tmp_path):
        """コンテンツのない XML でクラッシュしない"""
        from src.text_cleaner_cli import main

        empty_xml = tmp_path / "empty.xml"
        empty_xml.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<book></book>',
            encoding="utf-8",
        )

        # クラッシュせずに正常終了するか、適切なエラーを返すべき
        try:
            with patch("src.text_cleaner_cli.init_for_content"):
                main(["--input", str(empty_xml)])
        except SystemExit as e:
            # 正常終了（code 0）も許容
            assert e.code in (0, None), f"空の XML では正常終了するべきだが、終了コード {e.code} が返された"


# =============================================================================
# T011: 出力ディレクトリ自動作成テスト
# =============================================================================


class TestOutputDirectoryCreation:
    """出力ディレクトリが自動作成されることを検証する。

    エッジケース:
    - 出力ディレクトリが存在しない場合、自動的に作成される
    """

    def test_output_directory_created_automatically(self, tmp_path):
        """存在しない出力ディレクトリが自動作成される"""
        from src.text_cleaner_cli import main

        # 存在しないネストされたディレクトリを指定
        output_dir = tmp_path / "non_existent" / "nested" / "output"
        assert not output_dir.exists(), "テスト前提: 出力ディレクトリは存在しないべき"

        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        # ディレクトリが作成されているべき
        assert output_dir.exists(), f"出力ディレクトリが自動作成されるべきだが、存在しない: {output_dir}"

    def test_output_uses_hash_based_subdirectory(self, tmp_path):
        """出力はハッシュベースのサブディレクトリに格納される"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"

        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        # output_dir 直下ではなく、ハッシュベースのサブディレクトリに格納されるべき
        subdirs = [p for p in output_dir.iterdir() if p.is_dir()]
        assert len(subdirs) >= 1, (
            f"ハッシュベースのサブディレクトリが作成されるべきだが、見つからなかった。"
            f"output_dir の内容: {list(output_dir.iterdir())}"
        )

        # サブディレクトリ内に cleaned_text.txt が存在するべき
        cleaned_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_files) >= 1, "サブディレクトリ内に cleaned_text.txt が存在するべき"

    def test_existing_output_directory_not_error(self, tmp_path):
        """既に存在する出力ディレクトリでエラーにならない"""
        from src.text_cleaner_cli import main

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True)

        # エラーなしで実行されるべき
        with patch("src.text_cleaner_cli.init_for_content"):
            main(["--input", str(SAMPLE_BOOK2_XML), "--output", str(output_dir)])

        cleaned_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_files) >= 1, "既存の出力ディレクトリでも cleaned_text.txt が生成されるべき"
