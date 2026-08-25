"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Parallel Scheduler Engine (FG167).
    Dependency-aware, DAG-driven concurrent task execution engine.
    Eliminates sequential bottlenecks through dynamic topological task graph
    orchestration, dependency resolution, and maximum throughput execution.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready parallel task scheduler. Zero child's place.
    Ecclesiastes 3:1 - "To every thing there is a season, and a time to every purpose under the heaven..."
    Proverbs 16:3 - "Commit thy works unto the Lord, and thy thoughts shall be established."

Collaboration & Maintenance:
    - [Architecture]: Directed Acyclic Graph (DAG) parallel worker pool dispatcher.
    - [Concurrency]: Thread-safe state machine with lock-free task enqueuing.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, List, Set, Optional

logger = logging.getLogger("WilsyOS.ParallelScheduler")


class TaskState(Enum):
    """Execution states for scheduled DAG tasks."""
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class DependencyGraphError(Exception):
    """Raised when the task graph contains cyclic dependencies or invalid nodes."""
    pass


@dataclass
class TaskNode:
    """
    Encapsulates a single task node within the execution DAG.
    """
    task_id: str
    action: Callable[..., Any]
    dependencies: Set[str] = field(default_factory=set)
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    retries: int = 0
    
    state: TaskState = TaskState.PENDING
    result: Any = None
    error: Optional[Exception] = None
    execution_time_sec: float = 0.0


class ParallelScheduler:
    """
    Dependency-aware parallel task scheduler for maximum throughput.
    Orchestrates execution of tasks based on topological dependency resolution.
    """

    def __init__(self, max_workers: int = 8) -> None:
        """
        Initializes the parallel scheduler.

        Args:
            max_workers (int): Maximum number of concurrent worker threads.
        """
        self.max_workers = max_workers
        self._tasks: Dict[str, TaskNode] = {}
        self._dependents: Dict[str, Set[str]] = {}  # task_id -> set of task_ids depending on it
        self._lock = Lock()

    # [FUNCTION EXPLANATION]: Registers a task and its prerequisites into the execution DAG.
    def add_task(
        self,
        task_id: str,
        action: Callable[..., Any],
        dependencies: Optional[List[str]] = None,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        retries: int = 0,
    ) -> None:
        """
        Registers a new task into the graph.

        Args:
            task_id (str): Unique task identifier.
            action (Callable[..., Any]): Callable function to execute.
            dependencies (Optional[List[str]]): List of prerequisite task IDs.
            args (Optional[List[Any]]): Positional arguments for action.
            kwargs (Optional[Dict[str, Any]]): Keyword arguments for action.
            retries (int): Number of automatic retry attempts on failure.
        """
        deps_set = set(dependencies) if dependencies else set()
        task = TaskNode(
            task_id=task_id,
            action=action,
            dependencies=deps_set,
            args=args or [],
            kwargs=kwargs or {},
            retries=retries,
        )

        with self._lock:
            if task_id in self._tasks:
                raise ValueError(f"Task with ID '{task_id}' already registered in scheduler.")

            self._tasks[task_id] = task

            # Register reverse dependency mapping
            for dep in deps_set:
                if dep not in self._dependents:
                    self._dependents[dep] = set()
                self._dependents[dep].add(task_id)

            if task_id not in self._dependents:
                self._dependents[task_id] = set()

    # [FUNCTION EXPLANATION]: Validates DAG topology using Kahn's algorithm to detect cycles or missing deps.
    def validate_dag(self) -> List[str]:
        """
        Validates that the task graph is acyclic and all dependencies exist.

        Returns:
            List[str]: Topologically sorted list of task IDs.

        Raises:
            DependencyGraphError: If cycles exist or missing dependencies are referenced.
        """
        with self._lock:
            # 1. Verify all referenced dependencies exist
            for task_id, node in self._tasks.items():
                for dep in node.dependencies:
                    if dep not in self._tasks:
                        raise DependencyGraphError(
                            f"Task '{task_id}' depends on non-existent task '{dep}'."
                        )

            # 2. Kahn's Algorithm for cycle detection and topological sort
            in_degree: Dict[str, int] = {
                t_id: len(node.dependencies) for t_id, node in self._tasks.items()
            }
            queue: List[str] = [t_id for t_id, deg in in_degree.items() if deg == 0]
            topological_order: List[str] = []

            while queue:
                curr = queue.pop(0)
                topological_order.append(curr)

                for dependent in self._dependents.get(curr, set()):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            if len(topological_order) != len(self._tasks):
                unresolved = [t_id for t_id, deg in in_degree.items() if deg > 0]
                raise DependencyGraphError(
                    f"Cyclic dependency detected in task graph involving tasks: {unresolved}"
                )

            return topological_order

    # [FUNCTION EXPLANATION]: Executes a single task node with retry logic and state recording.
    def _execute_task_node(self, task_id: str) -> None:
        """Helper executed by thread pool workers."""
        with self._lock:
            node = self._tasks[task_id]
            node.state = TaskState.RUNNING

        logger.info(f"Executing task [{task_id}]...")
        start_time = time.perf_counter()
        
        attempts = 0
        max_attempts = node.retries + 1
        success = False
        last_error: Optional[Exception] = None

        while attempts < max_attempts and not success:
            attempts += 1
            try:
                result = node.action(*node.args, **node.kwargs)
                duration = time.perf_counter() - start_time
                with self._lock:
                    node.result = result
                    node.execution_time_sec = duration
                    node.state = TaskState.COMPLETED
                success = True
                logger.info(f"Task [{task_id}] COMPLETED in {duration:.4f}s.")
            except Exception as e:
                last_error = e
                logger.warning(f"Task [{task_id}] attempt {attempts}/{max_attempts} failed: {e}")

        if not success:
            duration = time.perf_counter() - start_time
            with self._lock:
                node.error = last_error
                node.execution_time_sec = duration
                node.state = TaskState.FAILED
            logger.error(f"Task [{task_id}] FAILED after {max_attempts} attempts.")

    # [FUNCTION EXPLANATION]: Runs the execution loop using maximum thread concurrency as dependencies clear.
    def run(self) -> Dict[str, TaskNode]:
        """
        Executes the registered DAG with parallel thread workers.

        Returns:
            Dict[str, TaskNode]: Dictionary of executed tasks with final states and outputs.
        """
        self.validate_dag()

        # Track remaining in-degree for real-time dispatching
        in_degree: Dict[str, int] = {}
        with self._lock:
            for t_id, node in self._tasks.items():
                in_degree[t_id] = len(node.dependencies)

        active_futures: Dict[Future[None], str] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            with self._lock:
                ready_tasks = [t_id for t_id, deg in in_degree.items() if deg == 0]
                for t_id in ready_tasks:
                    self._tasks[t_id].state = TaskState.READY

            # Submit initial batch of root tasks
            for t_id in ready_tasks:
                fut = executor.submit(self._execute_task_node, t_id)
                active_futures[fut] = t_id

            while active_futures:
                # Wait for at least one task to complete
                done_future = next(iter(active_futures.keys()))
                for f in list(active_futures.keys()):
                    if f.done():
                        done_future = f
                        break

                done_future.result()  # Ensure exception in thread wrapper is raised if any
                completed_task_id = active_futures.pop(done_future)

                with self._lock:
                    completed_node = self._tasks[completed_task_id]

                    # If a task failed, mark dependent tasks as SKIPPED
                    if completed_node.state == TaskState.FAILED:
                        self._cascade_skip(completed_task_id)
                        continue

                    # Dispatch downstream tasks whose dependencies are now satisfied
                    for dependent in self._dependents.get(completed_task_id, set()):
                        if self._tasks[dependent].state == TaskState.SKIPPED:
                            continue

                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            self._tasks[dependent].state = TaskState.READY
                            fut = executor.submit(self._execute_task_node, dependent)
                            active_futures[fut] = dependent

        return self._tasks

    # [FUNCTION EXPLANATION]: Recursively skips dependent tasks if a prerequisite failed.
    def _cascade_skip(self, failed_task_id: str) -> None:
        """Cascades SKIPPED state down the dependency chain."""
        stack = list(self._dependents.get(failed_task_id, set()))
        while stack:
            curr = stack.pop()
            if self._tasks[curr].state not in (TaskState.COMPLETED, TaskState.FAILED, TaskState.SKIPPED):
                self._tasks[curr].state = TaskState.SKIPPED
                logger.warning(f"Task [{curr}] SKIPPED due to prerequisite failure.")
                stack.extend(self._dependents.get(curr, set()))
