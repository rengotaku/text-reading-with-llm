"""Tests for reference normalization functionality.

Phase 3 RED Tests - US2/US3: 図表・注釈参照の読み上げ
Tests for _normalize_references function that converts figure, table,
and note references to natural reading format.
"""

from src.text_cleaner import _normalize_references


class TestNormalizeFigureReference:
    """Test figure reference normalization: 図X.Y -> ずXのY"""

    def test_normalize_figure_reference_basic(self):
        """図X.Y形式を自然な読み仮名に変換する"""
        input_text = "図2.1を参照"
        expected = "ず2の1を参照"

        result = _normalize_references(input_text)

        assert result == expected, f"図参照が読み仮名に変換されるべき: got '{result}', expected '{expected}'"

    def test_normalize_figure_reference_full_width_dot(self):
        """全角ドット（．）でも変換される"""
        input_text = "図3．2に示す"
        expected = "ず3の2に示す"

        result = _normalize_references(input_text)

        assert result == expected

    def test_normalize_figure_single_digit(self):
        """単一数字の図参照も変換される"""
        input_text = "図1を参照"
        expected = "ず1を参照"

        result = _normalize_references(input_text)

        assert result == expected, f"単一数字の図参照も変換されるべき: got '{result}', expected '{expected}'"

    def test_normalize_figure_reference_multi_digit(self):
        """複数桁の図番号も変換される"""
        input_text = "図12.34を参照"
        expected = "ず12の34を参照"

        result = _normalize_references(input_text)

        assert result == expected


class TestNormalizeTableReference:
    """Test table reference normalization: 表X.Y -> ひょうXのY"""

    def test_normalize_table_reference_basic(self):
        """表X.Y形式を自然な読み仮名に変換する"""
        input_text = "表1.2に示す"
        expected = "ひょう1の2に示す"

        result = _normalize_references(input_text)

        assert result == expected, f"表参照が読み仮名に変換されるべき: got '{result}', expected '{expected}'"

    def test_normalize_table_reference_full_width_dot(self):
        """全角ドット（．）でも変換される"""
        input_text = "表4．5を見てください"
        expected = "ひょう4の5を見てください"

        result = _normalize_references(input_text)

        assert result == expected

    def test_normalize_table_single_digit(self):
        """単一数字の表参照も変換される"""
        input_text = "表2を参照"
        expected = "ひょう2を参照"

        result = _normalize_references(input_text)

        assert result == expected


class TestNormalizeNoteReference:
    """Test note reference normalization: 注X.Y -> ちゅうXのY"""

    def test_normalize_note_reference_basic(self):
        """注X.Y形式を自然な読み仮名に変換する"""
        input_text = "注1.6を参照"
        expected = "ちゅう1の6を参照"

        result = _normalize_references(input_text)

        assert result == expected, f"注参照が読み仮名に変換されるべき: got '{result}', expected '{expected}'"

    def test_normalize_note_reference_full_width_dot(self):
        """全角ドット（．）でも変換される"""
        input_text = "注2．3を確認"
        expected = "ちゅう2の3を確認"

        result = _normalize_references(input_text)

        assert result == expected

    def test_normalize_note_single_digit(self):
        """単一数字の注参照も変換される"""
        input_text = "注5を参照"
        expected = "ちゅう5を参照"

        result = _normalize_references(input_text)

        assert result == expected


class TestNormalizeReferencesMixed:
    """Test multiple references in single text"""

    def test_normalize_references_mixed_all_types(self):
        """図表注が混在するテキストを処理"""
        input_text = "図2.1と表3.4と注5.6"
        expected = "ず2の1とひょう3の4とちゅう5の6"

        result = _normalize_references(input_text)

        assert result == expected, f"混在する参照を正しく処理すべき: got '{result}', expected '{expected}'"

    def test_normalize_references_in_sentence(self):
        """文中の複数参照を処理"""
        input_text = "詳細は図2.3、表4.5を参照してください"
        expected = "詳細はず2の3、ひょう4の5を参照してください"

        result = _normalize_references(input_text)

        assert result == expected, f"文中の複数参照を正しく処理すべき: got '{result}', expected '{expected}'"

    def test_normalize_references_multiple_same_type(self):
        """同種の参照が複数ある場合"""
        input_text = "図1.1と図1.2を比較"
        expected = "ず1の1とず1の2を比較"

        result = _normalize_references(input_text)

        assert result == expected


class TestNormalizeReferencesIdempotent:
    """Test idempotency: processing already-normalized text"""

    def test_normalize_references_idempotent_no_refs(self):
        """参照のないテキストは変化しない"""
        input_text = "これは参照を含まないテキストです"
        expected = "これは参照を含まないテキストです"

        result = _normalize_references(input_text)

        assert result == expected, f"参照のないテキストは変化すべきでない: got '{result}', expected '{expected}'"

    def test_normalize_references_idempotent_already_processed(self):
        """処理済みテキストを再処理しても変化しない"""
        original = "図2.1を参照"
        first_pass = _normalize_references(original)
        second_pass = _normalize_references(first_pass)

        assert first_pass == second_pass, (
            f"冪等性が保証されるべき: first pass: '{first_pass}', second pass: '{second_pass}'"
        )


class TestNormalizeReferencesEdgeCases:
    """Edge cases and special scenarios"""

    def test_normalize_references_empty_string(self):
        """空文字列の処理"""
        result = _normalize_references("")
        assert result == ""

    def test_normalize_references_whitespace_only(self):
        """空白のみのテキスト"""
        result = _normalize_references("   ")
        assert result == "   "

    def test_normalize_references_heading_format(self):
        """見出し形式の参照（### 注1.1）"""
        input_text = "注1.1 概要"
        expected = "ちゅう1の1 概要"

        result = _normalize_references(input_text)

        assert result == expected

    def test_normalize_references_consecutive(self):
        """連続する参照"""
        input_text = "図1.1図1.2"
        expected = "ず1の1ず1の2"

        result = _normalize_references(input_text)

        assert result == expected

    def test_normalize_references_with_parentheses(self):
        """括弧内の参照"""
        input_text = "（図2.1参照）"
        expected = "（ず2の1参照）"

        result = _normalize_references(input_text)

        assert result == expected

    def test_normalize_references_real_world_example(self):
        """実際の使用例: ローリングアップデート注1.6"""
        input_text = "ローリングアップデート注1.6、Blue-Greenデプロイメント注1.7"
        expected = "ローリングアップデートちゅう1の6、Blue-Greenデプロイメントちゅう1の7"

        result = _normalize_references(input_text)

        assert result == expected
