import threading

class ThreadPool:
    def __init__(self, max_threads):
        """
        Initialize the ThreadPool with a maximum number of concurrent threads.
        :param max_threads: Maximum number of concurrent threads.
        """
        self.max_threads = max_threads
        self.threads = []
        self.lock = threading.Lock()

    def add_thread(self, target, args=()):
        """
        Add a thread to the pool and start it if the limit is not exceeded.
        :param target: The target function to run in the thread.
        :param args: Arguments for the target function.
        :return: True if the thread was started, False if limit is reached.
        """
        with self.lock:
            if len(self.threads) < self.max_threads:
                thread = threading.Thread(target=target, args=args)
                thread.start()
                self.threads.append(thread)
                return True
            else:
                return False

    def join_all(self):
        """
        Wait for all threads in the pool to finish.
        """
        for thread in self.threads:
            thread.join()

        # Clear the thread list once all are done
        self.threads.clear()