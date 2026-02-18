# Phase 4 RED Tests

## Summary

- Phase: Phase 4 - User Story 3 (音声パラメータの調整)
- FAIL tests: 19
- Test file: tests/test_aquestalk_client.py

## Context

Phase 4 implements voice/pitch parameters and parameter validation for AquesTalk10.

### Already implemented (from previous phases):
- T051: speed parameter tests (Phase 3)
- T055: CLI parameter options (Phase 2)

### New tests added:
- T052: voice parameter tests (5 tests)
- T053: pitch parameter tests (5 tests)
- T054: parameter validation tests (9 tests)
- Combined parameters tests (2 tests)

## FAIL Test List

| Test File | Test Method | Expected Behavior |
|-----------|-------------|-------------------|
| tests/test_aquestalk_client.py | TestVoiceParameter::test_synthesize_accepts_voice_parameter | synthesize() accepts voice parameter |
| tests/test_aquestalk_client.py | TestVoiceParameter::test_synthesize_voice_0_minimum | voice=0 (minimum) works |
| tests/test_aquestalk_client.py | TestVoiceParameter::test_synthesize_voice_200_maximum | voice=200 (maximum) works |
| tests/test_aquestalk_client.py | TestVoiceParameter::test_synthesize_uses_config_voice_when_not_specified | Uses config.voice when not specified |
| tests/test_aquestalk_client.py | TestVoiceParameter::test_synthesize_voice_overrides_config | voice parameter overrides config |
| tests/test_aquestalk_client.py | TestPitchParameter::test_synthesize_accepts_pitch_parameter | synthesize() accepts pitch parameter |
| tests/test_aquestalk_client.py | TestPitchParameter::test_synthesize_pitch_50_minimum | pitch=50 (minimum) works |
| tests/test_aquestalk_client.py | TestPitchParameter::test_synthesize_pitch_200_maximum | pitch=200 (maximum) works |
| tests/test_aquestalk_client.py | TestPitchParameter::test_synthesize_uses_config_pitch_when_not_specified | Uses config.pitch when not specified |
| tests/test_aquestalk_client.py | TestPitchParameter::test_synthesize_pitch_overrides_config | pitch parameter overrides config |
| tests/test_aquestalk_client.py | TestParameterValidation::test_speed_below_minimum_raises_error | speed < 50 raises ValueError |
| tests/test_aquestalk_client.py | TestParameterValidation::test_speed_above_maximum_raises_error | speed > 300 raises ValueError |
| tests/test_aquestalk_client.py | TestParameterValidation::test_voice_below_minimum_raises_error | voice < 0 raises ValueError |
| tests/test_aquestalk_client.py | TestParameterValidation::test_voice_above_maximum_raises_error | voice > 200 raises ValueError |
| tests/test_aquestalk_client.py | TestParameterValidation::test_pitch_below_minimum_raises_error | pitch < 50 raises ValueError |
| tests/test_aquestalk_client.py | TestParameterValidation::test_pitch_above_maximum_raises_error | pitch > 200 raises ValueError |
| tests/test_aquestalk_client.py | TestParameterValidation::test_synthesize_speed_parameter_validation | synthesize() validates speed param |
| tests/test_aquestalk_client.py | TestParameterValidation::test_synthesize_voice_parameter_validation | synthesize() validates voice param |
| tests/test_aquestalk_client.py | TestParameterValidation::test_synthesize_pitch_parameter_validation | synthesize() validates pitch param |
| tests/test_aquestalk_client.py | TestCombinedParameters::test_synthesize_with_all_parameters | synthesize() accepts all params |
| tests/test_aquestalk_client.py | TestCombinedParameters::test_synthesize_with_partial_parameters | synthesize() works with partial params |

## Implementation Hints

### 1. Add voice/pitch parameters to synthesize()

```python
# src/aquestalk_client.py
def synthesize(
    self,
    text: str,
    speed: int | None = None,
    voice: int | None = None,
    pitch: int | None = None,
) -> bytes:
    """Synthesize text to audio.

    Args:
        text: Text to synthesize
        speed: Override speed (50-300, default: config.speed)
        voice: Override voice quality (0-200, default: config.voice)
        pitch: Override pitch (50-200, default: config.pitch)
    """
    # Use provided values or fall back to config
    actual_speed = speed if speed is not None else self.config.speed
    actual_voice = voice if voice is not None else self.config.voice
    actual_pitch = pitch if pitch is not None else self.config.pitch

    # Validate parameters
    self._validate_parameters(actual_speed, actual_voice, actual_pitch)
    ...
```

### 2. Add parameter validation in initialize()

```python
def initialize(self) -> None:
    if self._initialized:
        return

    # Validate config parameters
    self._validate_parameters(
        self.config.speed,
        self.config.voice,
        self.config.pitch
    )
    ...

def _validate_parameters(
    self,
    speed: int,
    voice: int,
    pitch: int
) -> None:
    """Validate AquesTalk10 parameters.

    Raises:
        ValueError: If any parameter is out of valid range
    """
    if not (50 <= speed <= 300):
        raise ValueError(f"speed must be 50-300, got {speed}")
    if not (0 <= voice <= 200):
        raise ValueError(f"voice must be 0-200, got {voice}")
    if not (50 <= pitch <= 200):
        raise ValueError(f"pitch must be 50-200, got {pitch}")
```

## FAIL Output Example

```
FAILED tests/test_aquestalk_client.py::TestVoiceParameter::test_synthesize_accepts_voice_parameter
  TypeError: AquesTalkSynthesizer.synthesize() got an unexpected keyword argument 'voice'

FAILED tests/test_aquestalk_client.py::TestPitchParameter::test_synthesize_accepts_pitch_parameter
  TypeError: AquesTalkSynthesizer.synthesize() got an unexpected keyword argument 'pitch'

FAILED tests/test_aquestalk_client.py::TestParameterValidation::test_speed_below_minimum_raises_error
  Failed: DID NOT RAISE <class 'ValueError'>

FAILED tests/test_aquestalk_client.py::TestParameterValidation::test_voice_below_minimum_raises_error
  Failed: DID NOT RAISE <class 'ValueError'>
```

## Test Results Summary

```
======================== 19 failed, 302 passed in 0.88s ========================
```

- Existing tests: 302 PASSED (no regressions)
- New Phase 4 tests: 19 FAILED (expected RED state)

## Parameter Ranges (AquesTalk10)

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| speed | 50 | 300 | 100 |
| voice | 0 | 200 | 100 |
| pitch | 50 | 200 | 100 |

## Next Steps

phase-executor will implement:
1. Add voice/pitch parameters to synthesize() method
2. Add _validate_parameters() helper method
3. Call validation in initialize() and synthesize()
4. Verify `make test` PASS (GREEN)
