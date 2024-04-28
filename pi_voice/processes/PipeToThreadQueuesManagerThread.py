from pi_voice import logger
from queue import Queue as q
from multiprocessing.queues import Queue as mq
from multiprocessing.synchronize import Event


class PipeToThreadQueuesManagerThread:
    def __init__(
        self,
        pipe,
        action_prediction_finished_event: Event,
        # p2q_sent_event: Event,
        thread_queues: list[q],
    ):
        self.pipe = pipe
        self.action_prediction_finished_event: Event = action_prediction_finished_event
        # self.p2q_sent_event: Event = p2q_sent_event
        self.thread_queues: list[q] = thread_queues

    def _pipe_data_to_threads(self):
        while True:
            if self.action_prediction_finished_event.wait(timeout=3):
                try:
                    data = self.pipe.recv()
                    logger.info(f"Received data: {data}")
                    
                    logger.info("Queueing data to threads...")
                    for queue in self.thread_queues:
                        print(f"Queue: {queue}")
                        queue.put(data)

                    # self.p2q_sent_event.set()
                except Exception as e:
                    logger.error(f"Error piping data to threads: {e}")
                finally:
                    self.action_prediction_finished_event.clear()

    def run(self):
        self._pipe_data_to_threads()

    def stop(self):
        self.pipe.close()
        for queue in self.thread_queues:
            queue.put(None)
