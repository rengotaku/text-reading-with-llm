"""Reading dictionary for TTS pronunciation fixes.

Maps technical terms and abbreviations to their correct Japanese readings.
Entries are processed in order, so more specific patterns should come first.

Note: We use (?<![A-Za-z]) and (?![A-Za-z]) instead of \b for word boundaries,
because \b doesn't work well with Japanese text (no spaces between words).
"""

import re


def _term(word: str) -> str:
    """Create a pattern that matches the word not surrounded by other letters."""
    # Negative lookbehind: not preceded by a letter
    # Negative lookahead: not followed by a letter
    return rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])"


# Format: (pattern, replacement)
# Pattern is a regex, replacement is the reading in hiragana/katakana
READING_RULES: list[tuple[str, str]] = [
    # === SRE/DevOps Terms ===
    (_term("SRE"), "エスアールイー"),
    (_term("SLO"), "エスエルオー"),
    (_term("SLI"), "エスエルアイ"),
    (_term("SLA"), "エスエルエー"),
    (_term("DevOps"), "デブオプス"),
    (_term("CI/CD"), "シーアイシーディー"),
    (_term("CI"), "シーアイ"),
    (_term("CD"), "シーディー"),
    (_term("IaC"), "アイエーシー"),
    (_term("K8s"), "クーバネティス"),
    (_term("Kubernetes"), "クーバネティス"),
    (_term("Docker"), "ドッカー"),
    (_term("Terraform"), "テラフォーム"),
    (_term("Ansible"), "アンシブル"),
    (_term("Prometheus"), "プロメテウス"),
    (_term("Grafana"), "グラファナ"),
    (_term("Datadog"), "データドッグ"),
    (_term("PagerDuty"), "ページャーデューティー"),
    (_term("toil"), "トイル"),

    # === Cloud Providers ===
    (_term("AWS"), "エーダブリューエス"),
    (_term("GCP"), "ジーシーピー"),
    (_term("Azure"), "アジュール"),
    (_term("EC2"), "イーシーツー"),
    (_term("S3"), "エススリー"),
    (_term("RDS"), "アールディーエス"),
    (_term("Lambda"), "ラムダ"),
    (_term("ECS"), "イーシーエス"),
    (_term("EKS"), "イーケーエス"),
    (_term("GKE"), "ジーケーイー"),

    # === General IT Terms ===
    (_term("API"), "エーピーアイ"),
    (_term("REST"), "レスト"),
    (_term("gRPC"), "ジーアールピーシー"),
    (_term("HTTPS"), "エイチティーティーピーエス"),
    (_term("HTTP"), "エイチティーティーピー"),
    (_term("TCP"), "ティーシーピー"),
    (_term("UDP"), "ユーディーピー"),
    (_term("DNS"), "ディーエヌエス"),
    (_term("CDN"), "シーディーエヌ"),
    (_term("SSL"), "エスエスエル"),
    (_term("TLS"), "ティーエルエス"),
    (_term("SSH"), "エスエスエイチ"),
    (_term("VPN"), "ブイピーエヌ"),
    (_term("NoSQL"), "ノーエスキューエル"),
    (_term("SQL"), "エスキューエル"),
    (_term("RDB"), "アールディービー"),
    (_term("CPU"), "シーピーユー"),
    (_term("GPU"), "ジーピーユー"),
    (_term("RAM"), "ラム"),
    (_term("SSD"), "エスエスディー"),
    (_term("HDD"), "エイチディーディー"),
    (_term("VPS"), "ブイピーエス"),
    (_term("IoT"), "アイオーティー"),
    (_term("LLM"), "エルエルエム"),
    (_term("NLP"), "エヌエルピー"),
    (_term("AI"), "エーアイ"),
    (_term("ML"), "エムエル"),
    (_term("IP"), "アイピー"),
    (_term("OS"), "オーエス"),
    (_term("VM"), "ブイエム"),
    (_term("DB"), "ディービー"),

    # === Development Terms ===
    (_term("GitHub"), "ギットハブ"),
    (_term("GitLab"), "ギットラボ"),
    (_term("Git"), "ギット"),
    (_term("VSCode"), "ブイエスコード"),
    (_term("IDE"), "アイディーイー"),
    (_term("Vim"), "ビム"),
    (_term("Emacs"), "イーマックス"),
    (_term("JSON"), "ジェイソン"),
    (_term("YAML"), "ヤムル"),
    (_term("XML"), "エックスエムエル"),
    (_term("CSV"), "シーエスブイ"),
    (_term("README"), "リードミー"),
    (_term("PR"), "プルリクエスト"),
    (_term("MR"), "マージリクエスト"),

    # === Agile/Management ===
    (_term("Agile"), "アジャイル"),
    (_term("Scrum"), "スクラム"),
    (_term("Kanban"), "カンバン"),
    (_term("KPI"), "ケーピーアイ"),
    (_term("OKR"), "オーケーアール"),
    (_term("ROI"), "アールオーアイ"),
    (_term("PO"), "プロダクトオーナー"),
    (_term("PM"), "プロジェクトマネージャー"),

    # === Companies/Organizations ===
    (_term("Google"), "グーグル"),
    (_term("Amazon"), "アマゾン"),
    (_term("Microsoft"), "マイクロソフト"),
    (_term("Meta"), "メタ"),
    (_term("Netflix"), "ネットフリックス"),
    (_term("Uber"), "ウーバー"),
    (_term("Slack"), "スラック"),

    # === Symbols & Special Cases ===
    (r"&", "アンド"),
    (_term("vs"), "バーサス"),
    (_term("VS"), "バーサス"),
    (r"\betc\.", "など"),
    (_term("etc"), "など"),

    # === Context-dependent Kanji Readings ===
    # 方: ホウ vs カタ - use カタ after の
    (r"の方", "のカタ"),
    # 何: ナン vs ナニ - use ナニ before か
    (r"何か", "ナニか"),
    (r"何を", "ナニを"),
    (r"何が", "ナニが"),
    (r"何も", "ナニも"),
]

# Compile patterns for efficiency
_COMPILED_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(pattern), replacement) for pattern, replacement in READING_RULES
]


def apply_reading_rules(text: str) -> str:
    """Apply all reading rules to convert technical terms to readings."""
    for pattern, replacement in _COMPILED_RULES:
        text = pattern.sub(replacement, text)
    return text
