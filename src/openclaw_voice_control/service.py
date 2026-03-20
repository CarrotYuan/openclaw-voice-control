from __future__ import annotations

import logging
import os
import tempfile
import time
import wave
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import numpy as np
import requests
import sounddevice as sd

from .asr import FunASRSenseVoice
from .config import VoiceControlConfig
from .openclaw_client import OpenClawClient
from .state import OverlayStateManager
from .text import clean_text_for_overlay
from .tts import MacOSTTS
from .wakeword import PorcupineWakewordEngine


class VoiceControlService:
    def __init__(self, config: VoiceControlConfig):
        self.config = config
        self.config.app.log_dir.mkdir(parents=True, exist_ok=True)
        self.config.app.runtime_dir.mkdir(parents=True, exist_ok=True)

        self.logger = self._build_logger()
        self.client = OpenClawClient(config.openclaw)
        self.tts = MacOSTTS(config.tts, config.overlay)
        self.asr = FunASRSenseVoice(config.asr)
        self.wakeword = PorcupineWakewordEngine(config.wakeword)
        self.state = OverlayStateManager(config.overlay)

    def _build_logger(self) -> logging.Logger:
        logger = logging.getLogger("openclaw.voice_control")
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        logger.propagate = False
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = RotatingFileHandler(
            self.config.app.log_dir / "voice_control.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def update_overlay_state(
        self,
        status: str,
        user_text: str = "",
        reply_text: str = "",
        meta_text: str = "",
        auto_hide_ms: int = 4000,
    ) -> None:
        self.state.write(
            status=status,
            user_text=user_text,
            reply_text=reply_text,
            meta_text=meta_text,
            auto_hide_ms=auto_hide_ms,
        )

    @staticmethod
    def rms_level(audio_chunk: np.ndarray) -> float:
        chunk = audio_chunk.astype("float32")
        if chunk.ndim > 1:
            chunk = chunk[:, 0]
        chunk /= 32768.0
        return float((chunk * chunk).mean() ** 0.5)

    def record_until_silence(self) -> Optional[str]:
        audio = self.config.audio
        self.logger.info("Start listening")
        self.update_overlay_state("listening", meta_text="请开始说话", auto_hide_ms=0)

        frames: list[np.ndarray] = []
        pending_frames: list[np.ndarray] = []
        speech_started = False
        silence_time = 0.0
        total_time = 0.0
        speech_time = 0.0
        wait_for_start_time = 0.0
        start_hit_count = 0

        block_duration = 0.1
        block_size = int(audio.sample_rate * block_duration)
        stream = sd.InputStream(
            samplerate=audio.sample_rate,
            channels=audio.channels,
            device=audio.input_device_index if audio.input_device_index >= 0 else None,
            dtype="int16",
            blocksize=block_size,
        )

        try:
            stream.start()
            while total_time < audio.max_record_seconds:
                if self.tts.is_stop_requested():
                    self.update_overlay_state("idle", auto_hide_ms=120)
                    return None

                data, _ = stream.read(block_size)
                total_time += block_duration
                level = self.rms_level(data)

                if not speech_started:
                    pending_frames.append(data.copy())
                    if len(pending_frames) > audio.max_pending_blocks:
                        pending_frames = pending_frames[-audio.max_pending_blocks :]

                    if level >= audio.start_hit_threshold:
                        start_hit_count += 1
                    else:
                        start_hit_count = 0
                        wait_for_start_time += block_duration
                        if wait_for_start_time >= audio.start_timeout_seconds:
                            self.update_overlay_state("no_speech", meta_text="没有检测到有效语音", auto_hide_ms=2200)
                            if self.config.tts.no_speech_beep_enabled:
                                self.tts.play_sound_async(self.config.tts.no_speech_sound)
                            return None

                    if start_hit_count >= audio.start_hits_required:
                        speech_started = True
                        silence_time = 0.0
                        frames.extend(pending_frames)
                        speech_time += len(pending_frames) * block_duration
                        pending_frames = []
                else:
                    frames.append(data.copy())
                    if level >= audio.silence_threshold:
                        silence_time = 0.0
                        speech_time += block_duration
                    else:
                        silence_time += block_duration
                        if silence_time >= audio.silence_seconds_end:
                            break

            if not speech_started or speech_time < audio.min_speech_seconds:
                self.update_overlay_state("no_speech", meta_text="没有检测到有效语音", auto_hide_ms=2200)
                if self.config.tts.no_speech_beep_enabled:
                    self.tts.play_sound_async(self.config.tts.no_speech_sound)
                return None

            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            with wave.open(path, "wb") as wf:
                wf.setnchannels(audio.channels)
                wf.setsampwidth(2)
                wf.setframerate(audio.sample_rate)
                for frame in frames:
                    wf.writeframes(frame.tobytes())

            if self.config.tts.record_done_beep_enabled:
                self.tts.play_sound_async(self.config.tts.record_done_sound)
            return path
        finally:
            try:
                stream.stop()
                stream.close()
            except Exception:
                self.logger.exception("Failed to close input stream")

    def handle_one_turn(self, wav_path: str) -> bool:
        try:
            user_text = self.asr.transcribe(wav_path)
            if not user_text:
                self.update_overlay_state("no_speech", meta_text="没有识别出有效文本", auto_hide_ms=2200)
                self.tts.clear_stop_flag()
                return False

            self.update_overlay_state("recognized", user_text=user_text, meta_text="识别完成", auto_hide_ms=1800)
            self.update_overlay_state("thinking", user_text=user_text, meta_text="正在思考", auto_hide_ms=0)

            reply = self.client.ask(user_text)
            reply_clean = clean_text_for_overlay(reply)
            self.update_overlay_state("reply", user_text=user_text, reply_text=reply_clean, meta_text="Jarvis", auto_hide_ms=0)

            finished = self.tts.speak(reply, clean_markdown=True)
            if finished:
                time.sleep(self.config.tts.post_reply_delay)

            self.update_overlay_state("idle", auto_hide_ms=120)
            self.tts.clear_stop_flag()
            return finished
        except requests.HTTPError:
            self.logger.exception("OpenClaw request failed")
            self.update_overlay_state("no_speech", meta_text="请求失败", auto_hide_ms=2200)
            self.tts.speak("请求失败。", clean_markdown=False)
            self.tts.clear_stop_flag()
            return False
        except Exception:
            self.logger.exception("Unexpected error during turn handling")
            self.update_overlay_state("no_speech", meta_text="出了点问题", auto_hide_ms=2200)
            self.tts.speak("出了点问题。", clean_markdown=False)
            self.tts.clear_stop_flag()
            return False
        finally:
            wav_file = Path(wav_path)
            if wav_file.exists():
                try:
                    wav_file.unlink()
                except Exception:
                    self.logger.exception("Failed to remove temp wav file: %s", wav_path)

    def run(self) -> None:
        if self.config.app.platform != "macos":
            raise RuntimeError("This first public release is intentionally limited to macOS.")

        self.logger.info(
            "Starting voice control service | platform=%s asr_model=%s language=%s",
            self.config.app.platform,
            self.config.asr.model,
            self.config.asr.language,
        )
        self.logger.info("Loading ASR model...")
        self.asr.load()
        self.logger.info("ASR model ready")
        self.logger.info("Initializing wakeword engine...")
        self.wakeword.start()
        self.logger.info("Wakeword engine ready | keyword_path=%s", self.config.wakeword.keyword_path)
        self.tts.clear_stop_flag()
        self.state.ensure_idle_state(reset=True)
        self.update_overlay_state("idle", auto_hide_ms=200)
        self.logger.info("Entered idle listening loop")

        last_trigger_time = 0.0
        while True:
            _, keyword_index = self.wakeword.read()
            if keyword_index < 0:
                continue

            now = time.time()
            if now - last_trigger_time < self.config.wakeword.cooldown_seconds:
                continue
            last_trigger_time = now
            self.logger.info("Wakeword detected")

            self.update_overlay_state("wake", meta_text="已唤醒", auto_hide_ms=1800)
            wake_ok = self.tts.speak(self.config.tts.wake_ack, clean_markdown=False)
            if not wake_ok or self.tts.is_stop_requested():
                self.update_overlay_state("idle", auto_hide_ms=120)
                self.tts.clear_stop_flag()
                continue

            wav_path = self.record_until_silence()
            if not wav_path:
                self.update_overlay_state("idle", auto_hide_ms=200)
                self.tts.clear_stop_flag()
                continue

            success = self.handle_one_turn(wav_path)
            if not success:
                continue

            while True:
                if self.tts.is_stop_requested():
                    self.update_overlay_state("idle", auto_hide_ms=120)
                    self.tts.clear_stop_flag()
                    break

                if self.config.tts.followup_beep_enabled:
                    self.tts.play_sound_async(self.config.tts.followup_beep_sound)

                followup_wav = self.record_until_silence()
                if not followup_wav:
                    self.update_overlay_state("idle", auto_hide_ms=200)
                    break

                if not self.handle_one_turn(followup_wav):
                    break
