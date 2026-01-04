## Celery 
its a distributed task queue framework for python that allowes to run tasks in the background.

- Runs tasks on the background 
- Can be used to run tasks on multiple machines
- can add multiple workers to run tasks 
- Supports multiple message brokers like RabbitMQ, Redis, SQS etc
- we can use this for async tasks and batch processing and also for scheduling tasks

## Celery Architecture

**Tasks:** A unit of work that can be executed by a worker
**Workers:** A process that executes tasks
**Brokers:** A service that stores and delivers tasks to workers
**Result Backend:** A service that stores the results of tasks


## Flow of a task:
1. Task is added to the broker
2. Worker picks up the task from the broker
3. Worker executes the task
4. Result is stored in the result backend
5. Task is marked as completed

```text
┌─────────────┐
│  Producer   │ (Your Django/Flask app)
│  (Client)   │
└──────┬──────┘
       │ enqueue task
       ↓
┌─────────────────┐
│     BROKER      │ (Redis/RabbitMQ)
│  Message Queue  │ ← Task message stored here
└──────┬──────────┘
       │ fetch task
       ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Worker 1   │     │   Worker 2   │     │   Worker N   │
│  (executes)  │     │  (executes)  │     │  (executes)  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │ store result       │ store result       │ store result
       └──────────────┬─────┴────────────────────┘
                      ↓
             ┌────────────────┐
             │ Result Backend │ (Redis/DB)
             │  (State store) │
             └────────────────┘
                      ↑
                      │ query result
                      │
                  Client polls
```

Types of Tasks:
1. Regular Tasks: Tasks that are executed immediately
**Example:**
```python
@app.task
def add(x, y):
    return x + y
```

2. Bound Tasks: Tasks that are "bound" to the Task instance itself

**How is this binding happening?**
- By passing `bind=True` to the `@app.task` decorator, Celery injects the task instance (`self`) as the first argument to the task function. This makes the function a "bound" method, similar to class methods in Python. 

**How is it different from a regular task?**
- Regular tasks only receive the arguments you define (`def add(x, y): ...`) and have no access to the task object itself or its metadata.
- Bound tasks receive `self` as the first parameter: 
    - `self` is an instance of the task class, so you get access to attributes and methods such as `self.request`, `self.retry`, `self.update_state`, and more.

**What is the advantage of using bound tasks?**
- You can access rich context and control task behavior, including:
    - Retrying tasks (`self.retry(...)`)
    - Reading task metadata, request information, and unique IDs (`self.request`)
    - Custom progress reporting
    - Updating task state for monitoring

**Example:**
```python
@app.task(bind=True)
def add(self, x, y):
    # Access to self.request.id, self.retry(), self.update_state(), etc.
    print(f"Task ID: {self.request.id}")
    return x + y
```

3. Named Tasks: Tasks that are named and can be called by their name
Meaning we can call the task by its name like `add.delay(1, 2)`
```python
@app.task(name='tasks.add')
def add(x, y):
    return x + y
```

main parameters for a task:
- name: the name of the task
- countdown: the number of seconds to wait before the task is executed
- eta: the time at which the task is executed (exec task after a given time)
- expires: the time after which the task is expired (if task is not executed before this time, it will be deleted)


4. Task Chaining: Tasks that are chained together (output of previous task is input to next task)

in a `chain`, the output of each task is passed as input to the next task in sequence and the final result is the output of the last task.

```python
from celery import chain

# Each task receives the previous task's output as its input (unless you specify otherwise).
workflow = chain(
    task1.s(10, 10),  # result1 = task1(10, 10)
    task2.s(),        # result2 = task2(result1)
    task3.s()         # result3 = task3(result2)
)
# The final result will be the output of task3
workflow_result = workflow.apply_async()
print(workflow_result.get())  

```


5. Task Group: Tasks that are grouped together
in a `group`, all tasks are executed in parallel and the result is a list of results of all tasks.

```python
from celery import group

# All tasks run simultaneously
parallel = group(
    add.s(2, 2),   # 4
    add.s(4, 4),   # 8
    add.s(8, 8)    # 16
)
result = parallel.apply_async()
print(result.get())  # [4, 8, 16]

```

6. Chord: Tasks that are chained together and grouped together
in a `chord`, all tasks are executed in parallel and the result is a list of results of all tasks and the final result is the output of the last task.

its a combination of `group` and `chain`

meaning:
- all tasks in the group are executed in parallel
- the result of the group is passed as input to the last task
- the final result is the output of the last task

```text
┌─────────────────┐
│     Group      │ (add.s(2, 2), add.s(4, 4), add.s(8, 8))
└──────┬──────────┘
       │
       ↓
┌──────────────┐
│     Chord    │ (task4.s())
└──────┬───────┘
       │
       ↓
┌──────────────┐
│     Result   │ (4, 8, 16)
└──────────────┘
```

```python
from celery import chord

# All tasks run simultaneously
chord = chord(group(task1.s(10, 10), task2.s(), task3.s()))(task4.s())
result = chord.apply_async()
print(result.get())  # [4, 8, 16]
```

7. Periodic Tasks: Tasks that are executed periodically
in a `periodic task`, the task is executed periodically at a given interval.

```python
# celery_app.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-daily-report': {
        'task': 'tasks.send_daily_report',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': 3600.0,  # Every hour (in seconds)
    },
    'weekly-backup': {
        'task': 'tasks.weekly_backup',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Every Sunday
    },
}
```

running a beat:
```bash
celery -A celery_app beat --loglevel=info
```

running a worker:
```bash
celery -A celery_app worker --loglevel=info
```

### Differenc between a regular task and a periodic task:

- Regular task: is executed immediately when the task is called
- Periodic task: is executed periodically at a given interval


## Celery Command Line: Complete Inner Workings & Master Guide

```bash
celery -A celery_app worker -Q HighPriorityQueue,LowPriorityQueue -n worker1@%h  --loglevel=info --concurrency=4 --autoscale=10,3 --autoreload --time-limit=300 --soft-time-limit=250 --max-tasks-per-child=100 --pool=threads
```

This command starts a Celery worker process that will listen for and execute tasks from the specified Celery application (`celery_app` in this case).

- `-A celery_app`: Specifies the Celery application to use.
- `worker`: Starts a Celery worker process.
- `--loglevel=info`: Sets the logging level to INFO.
- `-concurrency=4`: Sets the concurrency level to 4. (number of workers to run) if not specified, it will use the number of cores available.
- `--autoscale=10,3`: Automatically scales the number of workers up to 10 and down to 3 based on the load. (max workers, min workers)
- `--autoreload`: Automatically reloads the application when the code changes. (Old task )
- `-Q HighPriorityQueue,LowPriorityQueue`: Specifies the queues to listen to. (comma separated list of queues) will only listen to the specified queues and process only tasks from those queues rest all are ignored.
- `--time-limit=300`: Specifies the time limit for a task in seconds. (if task takes longer than this, it will be killed)
- `--soft-time-limit=250`: Specifies the soft time limit for a task in seconds. (if task takes longer than this, it will be killed but it will be retried)
- `--max-tasks-per-child=100`: Specifies the maximum number of tasks a worker can execute before it is replaced. (if a worker executes more than this number of tasks, it will be replaced)
- `-n worker1@%h`: Specifies the name of the worker. (worker1@%h means worker1@hostname)
- `--pool=threads`: Specifies the pool type to use. (threads)
`-A <app>`: THE APPLICATION PARAMETER  (Tells Celery where to find your Celery application instance)





```python
# celery.py
from celery import Celery

app = Celery('myproject')  # ← This is what -A references
app.conf.broker_url = 'redis://localhost:6379/0'
```

```bash
celery -A celery_app worker
       ↑
       └─ Looks for 'app' variable in celery_app module
```


```bash
celery -A app worker --concurrency=4

Creates:
├─ Master process (listens to queue)
├─ Child process 1 (executes task A)
├─ Child process 2 (executes task B)
├─ Child process 3 (executes task C)
└─ Child process 4 (executes task D)

All 4 execute SIMULTANEOUSLY on 4 CPU cores
```

** Memory Usage:**

```bash
Each process consumes ~25MB base + task memory

--concurrency=4:
├─ Master: 25MB
├─ Child 1: 25MB
├─ Child 2: 25MB
├─ Child 3: 25MB
└─ Child 4: 25MB
   Total: ~125MB

--concurrency=10:
Total: ~275MB

--concurrency=1:
Total: ~50MB (minimal)
```

** Performance Considerations:**
```bash
- Concurrency should match your CPU cores for optimal performance.
- Too many workers (concurrency) wastes memory.
- Too few workers (concurrency) wastes CPU.
- Use 1-2x CPU cores for concurrency.
- Adjust based on task complexity and queue depth.

CPU-bound tasks (calculations):
└─ concurrency = number of CPU cores
    └─ celery -A app worker --concurrency=4  (on 4-core machine)

I/O-bound tasks (API calls, DB queries):
└─ concurrency = cores × 2-4
    └─ celery -A app worker --concurrency=16  (on 4-core machine)

High-latency I/O (slow APIs):
└─ concurrency = cores × 4-8
    └─ celery -A app worker --concurrency=32

```

** AutoReloading:

```bash
Initial start:
00:00 Worker imports your modules
00:00 Worker ready to accept tasks

You modify code:
00:05 celery_app.py updated
      └─ Code change detected!

Worker reacts:
00:06 Kills child processes
00:07 Reloads Python modules
00:08 Spawns fresh child processes
00:09 Ready with new code

Next task:
00:10 Uses UPDATED code

Currently executing tasks:
├─ Use OLD code (no interruption)
└─ Complete before reload finishes

New tasks after reload:
└─ Use NEW code

```
** Pool Types:
```bash
- prefork: (default) Processes — best for CPU-bound tasks, strong isolation.
- threads: Threads within a process — lighter weight, sometimes more memory efficient,
           but no true parallelism due to GIL (unless your tasks are I/O-bound).
- eventlet/gevent: Lightweight green threads — for async, not recommended unless tasks are non-blocking.
``` 


