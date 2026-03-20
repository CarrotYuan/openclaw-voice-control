from __future__ import annotations

import argparse
import time

import numpy as np
import sounddevice as sd


def rms_level(audio_chunk) -> float:
    chunk = audio_chunk.astype("float32")
    if chunk.ndim > 1:
        chunk = chunk[:, 0]
    chunk /= 32768.0
    return float((chunk * chunk).mean() ** 0.5)


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a short microphone sample and print RMS levels.")
    parser.add_argument("--device", type=int, default=-1, help="Input device index for sounddevice. -1 means default.")
    parser.add_argument("--seconds", type=float, default=3.0, help="How long to sample.")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Sample rate.")
    parser.add_argument("--channels", type=int, default=1, help="Number of channels.")
    args = parser.parse_args()

    block_duration = 0.1
    block_size = int(args.sample_rate * block_duration)
    total_blocks = max(1, int(args.seconds / block_duration))

    print(f"Sampling microphone for {args.seconds:.1f}s | device={args.device}")
    stream = sd.InputStream(
        samplerate=args.sample_rate,
        channels=args.channels,
        device=args.device if args.device >= 0 else None,
        dtype="int16",
        blocksize=block_size,
    )

    peaks: list[float] = []
    started_at = time.time()
    try:
        stream.start()
        for _ in range(total_blocks):
            data, _ = stream.read(block_size)
            level = rms_level(data)
            peaks.append(level)
            print(f"rms={level:.6f}")
    finally:
        stream.stop()
        stream.close()

    elapsed = time.time() - started_at
    print()
    print(f"elapsed={elapsed:.2f}s")
    print(f"max_rms={max(peaks) if peaks else 0:.6f}")
    print(f"mean_rms={float(np.mean(peaks)) if peaks else 0:.6f}")


if __name__ == "__main__":
    main()
