from __future__ import annotations

from threading import Lock


class ServiceMetrics:
    def __init__(self, namespace: str) -> None:
        self.namespace = namespace
        self._http_requests_total = 0
        self._lock = Lock()

    def record_http_request(self) -> None:
        with self._lock:
            self._http_requests_total += 1

    def render(self) -> str:
        metric_name = f"{self.namespace}_http_requests_total"
        return (
            f"# HELP {metric_name} Total number of HTTP requests handled by the service\n"
            f"# TYPE {metric_name} counter\n"
            f"{metric_name} {self._http_requests_total}\n"
        )
