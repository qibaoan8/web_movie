# encoding: utf-8

import Queue,sys,time,os
from threading import Thread
from find_file import find_file
from convert_video import get_long_time_stamp
from config import RESOURCE_PATH

class Worker(Thread):
    def __init__(self, job_queue, res_queue, worker_fun):
        """
        """
        super(Worker, self).__init__()
        self._job_queue = job_queue
        self.res_queue = res_queue
        self.worker_fun = worker_fun

    def run(self):
        """
        """
        while True:
            try:
                domain_name = self._job_queue.get(timeout=2)
                domain_info = self.worker_fun(domain_name)
                self.res_queue.put(domain_info)
                self._job_queue.task_done()
            except Queue.Empty:
                pass
            except Exception as e:
                print "thread exception, error=[%s]" % str(e)


class Super_Queue():
    """
    超级队列
    """
    def __init__(self, worker_num):
        """
        """
        self._job_queue = Queue.Queue()
        self.res_queue = Queue.Queue()
        self._worker_num = worker_num

    def start(self, worker_fun):
        """
        启动函数
        """
        # 加载现在文件到队列里面
        self._load_queuefile_to_queue()
        workers = [Worker(self._job_queue, self.res_queue, worker_fun) for i in range(self._worker_num)]
        for worker in workers:
            worker.start()

        # for worker in workers:
        #     worker.join()

    def add_task(self, filename):
        # 生成文件随机名称
        queue_file = os.path.join(RESOURCE_PATH, get_long_time_stamp() + ".queue")
        o_mp4 = {
            "filename":filename,
            "queuefile":queue_file
        }
        self._create_queuefile(o_mp4)
        self._job_queue.put(o_mp4)

    def _create_queuefile(self, body):
        f = open(body['queuefile'], "w")  # data是自己定义的格式
        f.write(str(body))
        f.close()

    def _load_queuefile_to_queue(self):
        """
        在启动的时候将所有的文件添加到队列里面
        :return:
        """
        for queue_file in find_file(RESOURCE_PATH, ".queue"):
            queue_file = os.path.join(RESOURCE_PATH, queue_file)
            with open(queue_file) as f:
                o_mp4 = eval(f.read())
                self._job_queue.put(o_mp4)

def task_fun(mp4):
    print "bagin ", mp4['filename'], mp4['queuefile']
    os.remove(mp4['queuefile'])
    return

if __name__ == '__main__':
    s = Super_Queue(10)
    s.start(task_fun)
    s.add_task("/home/admin/a.mp4")
