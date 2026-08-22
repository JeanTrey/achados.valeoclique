from __future__ import annotations
from .models import Script, TimelineScene


def build_timeline(script: Script, fps: int) -> tuple[TimelineScene, ...]:
    out: list[TimelineScene] = []
    frame_cursor = 0
    time_cursor = 0.0
    for index, scene in enumerate(script.scenes):
        frame_count = max(1, round(scene.duration * fps))
        start_frame = frame_cursor
        end_frame = frame_cursor + frame_count
        duration = frame_count / fps
        out.append(TimelineScene(index, time_cursor, time_cursor + duration, start_frame, end_frame, scene))
        frame_cursor = end_frame
        time_cursor += duration
    return tuple(out)


def total_duration(timeline: tuple[TimelineScene, ...], fps: int) -> float:
    return (timeline[-1].end_frame / fps) if timeline else 0.0
