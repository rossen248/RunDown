from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class FormattedRun:
    name: str
    date: str
    distance_km: str  # Changed to string to include units
    duration_str: str  # Formatted as HH:MM:SS or MM:SS
    pace_str: str  # Formatted as MM:SS /km
    start_time: str


def _format_run(run) -> FormattedRun:
    # Format duration
    hours, rem = divmod(run.moving_time, 3600)
    minutes, seconds = divmod(rem, 60)
    duration_str = (f"{hours}:{minutes:02d}:{seconds:02d}"
                    if hours > 0 else f"{minutes}:{seconds:02d}")

    # Format pace
    if run.distance > 0:
        pace_seconds = run.moving_time / (run.distance / 1000)
        pace_min, pace_sec = divmod(int(pace_seconds), 60)
        pace_str = f"{pace_min}:{pace_sec:02d} /km"  # Added /km unit
    else:
        pace_str = "0:00 /km"  # Added /km unit

    return FormattedRun(
        name=run.name,
        date=run.start_date.date().strftime("%d %b %Y"),
        distance_km=f"{round(run.distance / 1000, 2)} km",  # Added km unit
        duration_str=duration_str,
        pace_str=pace_str,
        start_time=run.start_date.time().strftime("%H:%M")
    )


class RunDataProcessor:
    def __init__(self, runs: List):
        self.runs = runs

    def process_runs(self) -> Dict:
        """Processes runs and returns formatted data for visualization"""
        return {
            "summary_stats": self._get_summary_stats(),
            "longest_run": self._get_longest_run(),
            "fastest_run": self._get_fastest_run()
        }

    def _get_summary_stats(self) -> Dict:
        total_seconds = sum(r.moving_time for r in self.runs)
        total_distance_km = sum(r.distance for r in self.runs) / 1000

        # Format total duration
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        duration_str = (f"{hours}:{minutes:02d}:{seconds:02d}"
                        if hours > 0 else f"{minutes}:{seconds:02d}")

        # Calculate average pace
        if total_distance_km > 0:
            pace_seconds_per_km = total_seconds / total_distance_km
            pace_min, pace_sec = divmod(int(pace_seconds_per_km), 60)
            avg_pace = f"{pace_min}:{pace_sec:02d} /km"  # Added /km unit
        else:
            avg_pace = "0:00 /km"  # Added /km unit

        return {
            "total_runs": len(self.runs),
            "total_distance_km": f"{round(total_distance_km, 1)} km",  # Added km unit
            "total_duration": duration_str,
            "average_pace": avg_pace
        }

    def _get_longest_run(self) -> Optional[FormattedRun]:
        return _format_run(max(self.runs, key=lambda r: r.distance, default=None))

    def _get_fastest_run(self) -> Optional[FormattedRun]:
        valid_runs = [r for r in self.runs if r.distance > 0]
        return _format_run(min(valid_runs,
                               key=lambda r: r.moving_time / (r.distance / 1000),
                               default=None))