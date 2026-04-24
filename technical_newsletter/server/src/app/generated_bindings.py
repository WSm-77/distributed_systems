from __future__ import annotations

import sys
from pathlib import Path

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
if str(GENERATED_DIR) not in sys.path:
	sys.path.insert(0, str(GENERATED_DIR))

import event_pb2 as event_pb2
import event_pb2_grpc as event_pb2_grpc

__all__ = ["event_pb2", "event_pb2_grpc"]
