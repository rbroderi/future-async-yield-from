from .ast_encoding import rewrite_async_yield_from


def register() -> None:
    import codecs
    import encodings
    from collections.abc import Buffer
    from typing import IO

    import tokenize_rt  # type: ignore[import-untyped]

    # Base UTF-8 codec used for decoding before rewriting tokens
    utf_8 = encodings.search_function("utf8")
    if utf_8 is None:
        raise RuntimeError("unable to find utf8 encoding function.")

    def decode(input: Buffer, errors: str = "strict") -> tuple[str, int]:
        """Decode UTF-8, rewrite async-yield-from, output transformed UTF-8 text."""
        b = bytes(input)
        u, length = utf_8.decode(b, errors)

        tokens = tokenize_rt.src_to_tokens(u)
        tokens = rewrite_async_yield_from(tokens)
        new_src = tokenize_rt.tokens_to_src(tokens)

        return new_src, length

    class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
        def _buffer_decode(
            self, input: Buffer, errors: str, final: bool
        ) -> tuple[str, int]:
            if final:
                return decode(input, errors)
            return ("", 0)

    class StreamReader(codecs.StreamReader):
        """
        UTF-8 reader that applies async-yield-from token rewrite.
        """

        def __init__(self, stream: IO[bytes], errors: str = "strict") -> None:
            super().__init__(stream, errors)

        def decode(self, input: bytes, errors: str = "strict") -> tuple[str, int]:
            return decode(input, errors)

        def read(self, size: int = -1, chars: int = -1, firstline: bool = False) -> str:
            data = super().read(size, chars, firstline)
            if not isinstance(data, bytes):
                return data
            text, _ = decode(data)
            return text

        def readline(self, size: int | None = None, keepends: bool = False) -> str:
            data = super().readline(size, keepends)
            if not isinstance(data, bytes):
                return data
            text, _ = decode(data)
            return text

    def make_streamreader(stream: IO[bytes], errors: str = "strict") -> StreamReader:
        return StreamReader(stream, errors)

    # Patch base class dynamically (required for type correctness)
    StreamReader.__bases__ = (utf_8.streamreader,)  # type: ignore[assignment]

    codec_map: dict[str, codecs.CodecInfo] = {
        name: codecs.CodecInfo(
            name=name,
            encode=utf_8.encode,
            decode=decode,
            incrementalencoder=utf_8.incrementalencoder,
            incrementaldecoder=IncrementalDecoder,
            streamreader=make_streamreader,  # type: ignore[arg-type]
            streamwriter=utf_8.streamwriter,
        )
        for name in ("future-async-yield-from", "future_async_yield_from")
    }

    codecs.register(codec_map.get)
