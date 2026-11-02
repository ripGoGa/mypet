from typing import Literal

LIGHT_TSS_MAX = 70
MEDIUM_TSS_MAX = 101


def classify_training_intensity(tss: float | None) -> Literal["light", "medium", "hard"] | None:
    if tss is None:
        return None
    elif tss <= LIGHT_TSS_MAX:
        return "light"
    elif tss < MEDIUM_TSS_MAX:
        return "medium"
    else:
        return "hard"
