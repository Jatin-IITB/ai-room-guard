"""
Continuous police car siren that loops until stopped
Stops when: intruder leaves OR trusted person enters
"""

import numpy as np
import pyaudio
import threading
import time
import math
import random


class EmergencySiren:
    """Realistic police car siren - continuous until stopped"""
    
    def __init__(
        self,
        volume: float = 0.9,
        sample_rate: int = 44100,
        loop_duration: float = 7.0  # Duration of each loop cycle
    ):
        self.sample_rate = sample_rate
        self.volume = float(np.clip(volume, 0.0, 1.0))
        self.loop_duration = loop_duration
        self.chunk_duration = 0.03
        self.ramp_seconds = 0.3
        
        # Loop pattern: Yelp → Wail → Yelp (repeats continuously)
        self.mode_sequence = [
            ('yelp', loop_duration * 0.35),
            ('wail', loop_duration * 0.40),
            ('yelp', loop_duration * 0.25)
        ]
        
        self._stop_flag = threading.Event()
        self._thread = None
        self._pa = None
        self._stream = None
        self._is_playing = False
        
        print("✅ Continuous emergency siren initialized")
    
    def _band_limited_square(self, freq, t):
        """Band-limited square wave"""
        sr = self.sample_rate
        nyquist = sr / 2.0
        max_k = int(math.floor(nyquist / freq))
        k_vals = np.arange(1, max_k + 1, 2)
        
        if len(k_vals) > 31:
            k_vals = k_vals[:31]
        
        wave = np.zeros_like(t)
        for k in k_vals:
            wave += (1.0 / k) * np.sin(2.0 * np.pi * k * freq * t)
        
        wave *= (4.0 / np.pi)
        max_abs = np.max(np.abs(wave))
        if max_abs > 0:
            wave = wave / max_abs
        
        return wave
    
    def _siren_chunk(self, base_freq, freq_mod_func, t0):
        """Generate audio chunk"""
        sr = self.sample_rate
        n_samples = int(self.chunk_duration * sr)
        t = (np.arange(n_samples) / sr) + t0
        
        inst_freq = freq_mod_func(t)
        phase = 2.0 * np.pi * np.cumsum(inst_freq) / sr
        
        min_f = max(1.0, np.min(inst_freq))
        max_k = int(math.floor((sr / 2.0) / min_f))
        k_vals = np.arange(1, max_k + 1, 2)
        
        if len(k_vals) > 15:
            k_vals = k_vals[:15]
        
        wave = np.zeros_like(t)
        for k in k_vals:
            wave += (1.0 / k) * np.sin(k * phase)
        
        wave *= (4.0 / np.pi)
        max_abs = np.max(np.abs(wave))
        if max_abs > 0:
            wave = wave / max_abs
        
        return wave
    
    def _amplitude_envelope(self, local_t, total_mode_dur):
        """Smooth ramp up/down"""
        ramp = min(self.ramp_seconds, total_mode_dur / 2.0)
        amp = 1.0
        
        if local_t < ramp:
            amp = local_t / ramp
        elif local_t > (total_mode_dur - ramp):
            amp = max(0.0, (total_mode_dur - local_t) / ramp)
        
        return amp
    
    def _play_loop(self):
        """Main continuous loop"""
        sr = self.sample_rate
        pa = pyaudio.PyAudio()
        self._pa = pa
        
        stream = pa.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sr,
            output=True,
            frames_per_buffer=int(self.chunk_duration * sr)
        )
        self._stream = stream
        
        epoch = time.time()
        
        try:
            # ✅ INFINITE LOOP - only stops when stop_flag is set
            while not self._stop_flag.is_set():
                for mode_name, mode_dur in self.mode_sequence:
                    if self._stop_flag.is_set():
                        break
                    
                    mode_start = time.time()
                    
                    # Configure pattern
                    if mode_name == 'yelp':
                        low = 700.0 + random.uniform(-20, 20)
                        high = 1200.0 + random.uniform(-30, 30)
                        alternation_hz = 6.5 + random.uniform(-0.5, 0.5)
                        
                        def freq_mod(t_array):
                            phase = 2.0 * np.pi * alternation_hz * t_array
                            smooth = 0.5 * (1 + np.sin(phase))
                            return low * (1 - smooth) + high * smooth
                    
                    elif mode_name == 'wail':
                        low = 600.0 + random.uniform(-30, 30)
                        high = 1400.0 + random.uniform(-40, 40)
                        sweep_hz = 0.35 + random.uniform(-0.05, 0.05)
                        
                        def freq_mod(t_array):
                            lfo = 0.5 * (1 + np.sin(2.0 * np.pi * sweep_hz * t_array))
                            return low * (1 - lfo) + high * lfo
                    
                    else:
                        low = 650.0
                        high = 1250.0
                        sweep_hz = 0.5
                        
                        def freq_mod(t_array):
                            lfo = 0.5 * (1 + np.sin(2.0 * np.pi * sweep_hz * t_array))
                            return low * (1 - lfo) + high * lfo
                    
                    tremolo_rate = 7.0 + random.uniform(-1.0, 1.0)
                    tremolo_depth = 0.12 + random.uniform(-0.03, 0.03)
                    
                    # Generate chunks for this mode
                    while (time.time() - mode_start) < mode_dur and not self._stop_flag.is_set():
                        t0 = time.time() - epoch
                        samples = self._siren_chunk(low, freq_mod, t0)
                        
                        n = samples.size
                        t_chunk = (np.arange(n) / sr) + t0
                        trem = 1.0 - tremolo_depth * (0.5 * (1 + np.sin(2.0 * np.pi * tremolo_rate * t_chunk)))
                        samples = samples * trem
                        
                        elapsed_mode = time.time() - mode_start
                        amp_env = self._amplitude_envelope(elapsed_mode, mode_dur)
                        
                        micro = 1.0 + random.uniform(-0.01, 0.01)
                        samples = samples * self.volume * amp_env * micro
                        
                        samples = np.clip(samples, -1.0, 1.0)
                        stream.write(samples.astype(np.float32).tobytes())
                
                # ✅ Loop continues until stop_flag is set
        
        except Exception as e:
            print(f"⚠️ Siren error: {e}")
        
        finally:
            try:
                stream.stop_stream()
                stream.close()
                pa.terminate()
            except:
                pass
            self._stream = None
            self._pa = None
            self._is_playing = False
    
    def start(self):
        """Start continuous siren (loops until stopped)"""
        if self._is_playing:
            return
        
        self._stop_flag.clear()
        self._is_playing = True
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()
        
        print("🚨 POLICE SIREN ACTIVATED (continuous)")
    
    def stop(self):
        """Stop siren"""
        if not self._is_playing:
            return
        
        self._stop_flag.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        
        self._is_playing = False
        print("🔕 Siren stopped")
    
    def is_playing(self):
        """Check if siren is currently active"""
        return self._is_playing


if __name__ == "__main__":
    print("Testing continuous siren...")
    print("Will play for 15 seconds then stop")
    
    siren = EmergencySiren(volume=0.8)
    siren.start()
    
    try:
        time.sleep(15)
    except KeyboardInterrupt:
        pass
    
    siren.stop()
    print("Test complete!")
