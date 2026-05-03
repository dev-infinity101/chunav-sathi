import numpy as np

# Full implementation: Prompt 3


async def get_embeddings(texts: list[str]) -> np.ndarray:
    """
    Stub — returns zero vectors of dim 768.
    Real google-genai text-embedding-004 call implemented in Prompt 3.
    """
    dim = 768
    arr = np.zeros((len(texts), dim), dtype=np.float32)
    return arr
