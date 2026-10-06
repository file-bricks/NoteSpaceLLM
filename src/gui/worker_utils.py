"""
Worker-Hilfen - sichere Lebensdauer für QThread-Worker
======================================================

Ein QThread-Objekt darf erst zerstört werden, wenn der Thread wirklich beendet
ist. Wird die letzte Python-Referenz schon in einem Slot von z.B.
``all_complete`` verworfen (run() läuft dann noch), bricht Qt mit
"QThread: Destroyed while thread is still running" ab.

``retain_until_finished`` hält deshalb eine Referenz bis zum ``finished``-Signal
und gibt sie erst danach (verzögert über die Event-Loop) frei.
"""

import time
from collections.abc import Callable, Iterable

from PySide6.QtCore import QThread, QTimer


def retain_until_finished(
    registry: dict[int, QThread],
    worker: QThread,
    on_finished: Callable[[QThread], None] | None = None,
) -> QThread:
    """Hält ``worker`` in ``registry``, bis der Thread beendet ist.

    Args:
        registry: Dict, das die Worker-Referenzen hält (z.B. ``self._workers``)
        worker: Der (noch nicht gestartete) Worker
        on_finished: Optionaler Callback, erhält den Worker nach Thread-Ende

    Returns:
        Den Worker (für Verkettung)
    """
    key = id(worker)
    registry[key] = worker

    # Die Closure referenziert den Worker bewusst NICHT direkt (nur über den
    # Key), damit kein Referenzzyklus Worker -> Slot -> Worker entsteht.
    def _release():
        finished_worker = registry.pop(key, None)
        if finished_worker is None:
            return
        # finished wird kurz vor dem endgültigen Thread-Ende emittiert
        finished_worker.wait()
        try:
            if on_finished is not None:
                on_finished(finished_worker)
        finally:
            # Letzte Referenz erst nach Rückkehr in die Event-Loop freigeben
            QTimer.singleShot(0, lambda w=finished_worker: w.isFinished())

    worker.finished.connect(_release)
    return worker


def stop_workers(workers: Iterable[QThread | None], timeout_ms: int = 3000) -> bool:
    """Fordert alle laufenden Worker zum Beenden auf und wartet auf sie.

    Returns:
        True, wenn danach kein Worker mehr läuft
    """
    running = [w for w in workers if w is not None and w.isRunning()]
    for worker in running:
        worker.requestInterruption()
        stop = getattr(worker, "stop", None)
        if callable(stop):
            stop()
    deadline = time.monotonic() + timeout_ms / 1000.0
    all_stopped = True
    for worker in running:
        remaining_ms = max(0, int((deadline - time.monotonic()) * 1000))
        if not worker.wait(remaining_ms):
            all_stopped = False
    return all_stopped
