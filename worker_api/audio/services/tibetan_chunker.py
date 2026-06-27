from botok import WordTokenizer

_tokenizer = None


def _get_tokenizer() -> WordTokenizer:
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = WordTokenizer()
    return _tokenizer


def chunk_tibetan_text(text: str, max_syllables: int = 15) -> list[str]:
    """
    Chunk Tibetan text by syllable count using botok.
    
    Args:
        text: Tibetan text to chunk
        max_syllables: Maximum syllables per chunk (default 15)
    
    Returns:
        List of text chunks respecting word boundaries
    """
    if not text or not text.strip():
        return []
    
    tokenizer = _get_tokenizer()
    tokens = tokenizer.tokenize(text, split_affixes=False)
    
    chunks = []
    current_chunk_tokens = []
    current_syllable_count = 0
    
    for token in tokens:
        syllable_count = len(token.syls) if token.syls else 1
        
        if current_syllable_count + syllable_count > max_syllables and current_chunk_tokens:
            chunk_text = "".join(t.text for t in current_chunk_tokens)
            chunks.append(chunk_text)
            current_chunk_tokens = [token]
            current_syllable_count = syllable_count
        else:
            current_chunk_tokens.append(token)
            current_syllable_count += syllable_count
    
    if current_chunk_tokens:
        chunk_text = "".join(t.text for t in current_chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks
