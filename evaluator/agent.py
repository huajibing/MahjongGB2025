import subprocess
import threading
import queue
import time
import os
import sys # For stderr printing in threads for debug

class Agent:
    def __init__(self, agent_main_path, agent_id):
        self.agent_main_path = agent_main_path
        self.agent_id = int(agent_id) # Ensure agent_id is int
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.message_queue = queue.Queue()
        self.error_queue = queue.Queue() # For stderr lines
        self._running = False
        # Using os.path.basename for a cleaner log prefix if agent_main_path is long
        self._log_prefix = f"Agent-{self.agent_id} ({os.path.basename(self.agent_main_path)}):"

    def _reader_thread(self, pipe, queue_obj, pipe_name):
        # pipe_name is "stdout" or "stderr"
        try:
            for line in iter(pipe.readline, ''):
                stripped_line = line.strip()
                if self._running: # Only queue if agent is supposed to be running
                    if stripped_line:
                        queue_obj.put(stripped_line)
                        # Useful for live debugging of agent's stderr, but can be noisy
                        # if pipe_name == "stderr":
                        #    print(f"{self._log_prefix} STDERR_PIPE: {stripped_line}", file=sys.stderr)
                else: # If not _running, just consume and break
                    break
        except Exception as e:
            # This might happen if pipe is closed abruptly e.g. process killed
            # print(f"{self._log_prefix} Exception in {pipe_name} reader: {e}", file=sys.stderr)
            pass
        finally:
            try:
                if pipe: pipe.close()
            except Exception: pass
            # print(f"{self._log_prefix} {pipe_name} reader thread finished.", file=sys.stderr)


    def start(self):
        if self.process is not None and self.process.poll() is None:
            # print(f"{self._log_prefix} Agent is already running (PID {self.process.pid}).")
            return

        while not self.message_queue.empty():
            try: self.message_queue.get_nowait()
            except queue.Empty: break
        while not self.error_queue.empty():
            try: self.error_queue.get_nowait()
            except queue.Empty: break

        try:
            command = ['python', self.agent_main_path] # Ensure python executable is appropriate if using venvs elsewhere
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            self._running = True # Set running flag *before* starting threads

            self.stdout_thread = threading.Thread(target=self._reader_thread, args=(self.process.stdout, self.message_queue, "stdout"))
            self.stdout_thread.daemon = True
            self.stdout_thread.start()

            self.stderr_thread = threading.Thread(target=self._reader_thread, args=(self.process.stderr, self.error_queue, "stderr"))
            self.stderr_thread.daemon = True
            self.stderr_thread.start()
            # print(f"{self._log_prefix} Started (PID {self.process.pid}).")

        except FileNotFoundError: # Specific error for script not found
            self._running = False
            # print(f"{self._log_prefix} ERROR - Script '{self.agent_main_path}' not found.", file=sys.stderr)
            raise
        except Exception as e: # Other potential errors during Popen (permissions, etc.)
            self._running = False
            # print(f"{self._log_prefix} ERROR starting from '{self.agent_main_path}': {e}", file=sys.stderr)
            raise

    def stop(self, timeout_stop=2.0, timeout_kill=1.0): # Reduced timeouts for faster test cycles
        if not self._running and (self.process is None or self.process.poll() is not None):
            # print(f"{self._log_prefix} Not running or already stopped.")
            return

        # print(f"{self._log_prefix} Stopping (PID {self.process.pid if self.process else 'N/A'})...")
        self._running = False # Signal reader threads to stop queuing and exit

        if self.process and self.process.stdin:
            try:
                if not self.process.stdin.closed:
                    self.process.stdin.close()
            except (OSError, ValueError): pass # Ignore errors on closing already closed/broken pipe

        if self.stdout_thread and self.stdout_thread.is_alive():
            self.stdout_thread.join(timeout=0.5)
        if self.stderr_thread and self.stderr_thread.is_alive():
            self.stderr_thread.join(timeout=0.5)

        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=timeout_stop)
            except subprocess.TimeoutExpired:
                self.process.kill()
                try:
                    self.process.wait(timeout=timeout_kill)
                except subprocess.TimeoutExpired:
                    pass
            except Exception as e:
                pass

        self.process = None

    def send_request(self, request_str):
        if not (self.process and self.process.stdin and not self.process.stdin.closed and self._running):
            raise BrokenPipeError(f"{self._log_prefix} Agent not running/ready, cannot send request.")

        try:
            self.process.stdin.write(request_str + '\n')
            self.process.stdin.flush()
        except BrokenPipeError:
            raise
        except Exception as e:
            raise

    def get_response(self, timeout_seconds=5):
        if not self._running and self.message_queue.empty():
             raise ConnectionAbortedError(f"{self._log_prefix} Agent not running and no pending messages.")

        stderr_lines = []
        while not self.error_queue.empty():
            try: stderr_lines.append(self.error_queue.get_nowait())
            except queue.Empty: break

        try:
            response = self.message_queue.get(timeout=timeout_seconds)
            return response
        except queue.Empty:
            while not self.error_queue.empty():
                try: stderr_lines.append(self.error_queue.get_nowait())
                except queue.Empty: break

            if stderr_lines:
                raise TimeoutError(f"{self._log_prefix} Timeout waiting for response. STDERR: {' | '.join(stderr_lines)}")
            else:
                raise TimeoutError(f"{self._log_prefix} Timeout waiting for response. No STDERR output.")
        except Exception as e:
            raise ConnectionError(f"{self._log_prefix} Connection error getting response: {e}") from e

    def get_all_accumulated_stderr(self):
        lines = []
        while True:
            try:
                lines.append(self.error_queue.get_nowait())
            except queue.Empty:
                break
        return lines

if __name__ == '__main__':
    print("evaluator.agent.py: Agent class defined.")
    print("To test, use evaluator/__main__.py or run evaluation.py tests.")
    # Example of direct test (requires dummy_agent_main.py in current dir or correct path):
    # dummy_path = "dummy_agent_A_eval.py"
    # if os.path.exists(dummy_path):
    #     print(f"Attempting direct test with {dummy_path}...")
    #     test_agent = Agent(dummy_path, 99)
    #     try:
    #         test_agent.start()
    #         test_agent.send_request("0 0")
    #         print(f"Test agent got INIT response: {test_agent.get_response(2)}")
    #         test_agent.send_request("W1 W2 W3 B1 B2 B3 T1 T2 T3 F1 F2 F3 J1")
    #         print(f"Test agent got HAND response: {test_agent.get_response(2)}")
    #         test_agent.send_request("2 W1")
    #         print(f"Test agent got DRAW response: {test_agent.get_response(2)}")
    #         stderr = test_agent.get_all_accumulated_stderr()
    #         if stderr: print(f"Test agent STDERR: {' | '.join(stderr)}")
    #     except Exception as e:
    #         print(f"Agent direct test error: {e}", file=sys.stderr)
    #         all_stderr = test_agent.get_all_accumulated_stderr()
    #         if all_stderr: print(f"Agent direct test STDERR dump: {' | '.join(all_stderr)}", file=sys.stderr)
    #     finally:
    #         test_agent.stop()
    # else:
    #     print(f"Skipping direct test: {dummy_path} not found.")
