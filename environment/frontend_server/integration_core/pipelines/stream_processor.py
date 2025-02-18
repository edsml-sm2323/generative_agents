import os 
import time 
import subprocess 
import threading 
from django.conf  import settings 
 
class HLSStreamGenerator:
    _instances = {}  # 多实例支持 
 
    def __init__(self, session_id, width=1280, height=720, fps=30):
        self.session_id  = session_id 
        self.output_dir  = os.path.join(settings.MEDIA_ROOT,  'hls', session_id)
        os.makedirs(self.output_dir,  exist_ok=True)
        
        # FFmpeg管道配置 
        self.ffmpeg_cmd  = [
            'ffmpeg', '-y',
            '-f', 'image2pipe',
            '-vcodec', 'png',
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-g', '30',
            '-f', 'hls',
            '-hls_time', '4',
            '-hls_list_size', '5',
            '-hls_flags', 'delete_segments',
            '-hls_segment_filename', f'{self.output_dir}/segment_%03d.ts', 
            f'{self.output_dir}/playlist.m3u8' 
        ]
        
        self.process  = None 
        self.lock  = threading.Lock()
        self.is_running  = False 
 
    def start(self):
        with self.lock: 
            if not self.is_running: 
                self.process  = subprocess.Popen(
                    self.ffmpeg_cmd, 
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE 
                )
                self.is_running  = True 
                threading.Thread(target=self._monitor_errors).start()
 
    def feed_frame(self, frame_data):
        with self.lock: 
            if self.process  and self.is_running: 
                try:
                    self.process.stdin.write(frame_data) 
                    self.process.stdin.flush() 
                except BrokenPipeError:
                    self._restart_pipeline()
 
    def _restart_pipeline(self):
        self.stop() 
        self.start() 
 
    def _monitor_errors(self):
        while self.process.poll()  is None:
            err = self.process.stderr.readline() 
            if err:
                print(f"[FFmpeg Error] {err.decode().strip()}") 
 
    def stop(self):
        with self.lock: 
            if self.process: 
                self.process.stdin.close() 
                self.process.terminate() 
                self.process.wait() 
                self.is_running  = False 
 
    @classmethod 
    def get_instance(cls, session_id):
        if session_id not in cls._instances:
            cls._instances[session_id] = HLSStreamGenerator(session_id)
        return cls._instances[session_id]