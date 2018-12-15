#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: super_queue.py
Date: 2018-12-02 10:49
Author: wang.gaofei@alibaba-inc.com 
"""

import Queue,sys
from threading import Thread

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
                return
            except Exception as e:
                print "thread exception, error=[%s]" % str(e)



class Super_Queue():

    def __init__(self, worker_num):
        """
        """
        self._job_queue = Queue.Queue()
        self.res_queue = Queue.Queue()
        self._worker_num = worker_num

        self._ret_data = []

    def start(self, worker_fun, args):
        """
        启动函数
        """
        for arg in args:
            self._job_queue.put(arg)
        workers = [Worker(self._job_queue, self.res_queue, worker_fun) for i in range(self._worker_num)]
        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        while self.res_queue.qsize() > 0:
            self._ret_data.append(self.res_queue.get())
        return self._ret_data



