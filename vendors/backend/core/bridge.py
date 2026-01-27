import threading
import asyncio
import time
import logging
import atexit
from typing import Optional, Dict, Any

from app.core.pipeline import PipelineService

logger = logging.getLogger(__name__)

class PipelineManager:
    """
    [Background Singleton]
    Manages the PipelineService in a separate daemon thread.
    Ensures the control loop survives Streamlit re-runs.
    """
    _instance: Optional['PipelineManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PipelineManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        logger.info("🌉 Initializing Pipeline Bridge...")
        self.pipeline = PipelineService()
        self.loop_thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event = threading.Event()
        
        # Register cleanup
        atexit.register(self.stop)
        self._initialized = True

    def start(self):
        """Start the background thread if not running."""
        if self.loop_thread and self.loop_thread.is_alive():
            logger.info("🌉 Pipeline connection reused.")
            return

        logger.info("🌉 Starting Pipeline Background Thread...")
        self._stop_event.clear()
        self.loop_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.loop_thread.start()

    def _run_async_loop(self):
        """Entry point for the background thread."""
        logger.info("🌉 Background Thread Started.")
        
        # Create a new event loop for this thread
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Run the pipeline
        try:
            self.loop.run_until_complete(self.pipeline.start())
            
            # Keep loop running until stop event
            # self.pipeline.start() spawns _poll_loop as a task, so we need to keep the loop alive?
            # Actually pipeline.start() creates a task. We need to wait.
            # Let's verify pipeline.start implementation. 
            # It puts _poll_loop in asyncio.create_task. 
            # So run_until_complete will finish immediately if start() is not generic.
            # We need to run forever.
            
            self.loop.run_forever()
            
        except Exception as e:
            logger.critical(f"🌉 Background Loop Crashed: {e}", exc_info=True)
        finally:
            self.loop.close()
            logger.info("🌉 Background Loop Closed.")

    def stop(self):
        """Stop the pipeline and thread."""
        if self.loop and self.loop.is_running():
            logger.info("🌉 Stopping Pipeline...")
            # Schedule the stop coroutine
            asyncio.run_coroutine_threadsafe(self.pipeline.stop(), self.loop)
            # Stop the loop logic? 
            # Pipeline.stop sets is_running=False, so _poll_loop exits.
            # We need to stop loop.run_forever().
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.loop_thread:
            self.loop_thread.join(timeout=2.0)
            logger.info("🌉 Thread Stopped.")

    def get_latest_frame(self) -> Dict[str, Any]:
        """Thread-safe access to latest state."""
        return self.pipeline.get_current_state()

    # --- HIL Control Interface ---
    
    def set_control_mode(self, mode: str):
        self.pipeline.set_mode(mode)

    def send_manual_command(self, watts: float):
        self.pipeline.set_manual_command(watts)

    def start_recording(self, metadata: Dict) -> str:
        return self.pipeline.start_recording(metadata)

    def trigger_calibration(self):
        """Schedule calibration sequence in the background loop."""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.pipeline.run_calibration_sequence(), 
                self.loop
            )

    def stop_recording(self):
        self.pipeline.stop_recording()

# Global Accessor
def get_pipeline_manager() -> PipelineManager:
    return PipelineManager()
