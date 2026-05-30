import math
import random


class ClickSimulator:
    """Generates human-like click behavior with jitter, pauses, and drift."""

    def __init__(self):
        self.enabled = False
        self.intensity = 50
        self.position_jitter_px = 5
        self.micro_pause_chance = 0.02
        self.micro_pause_min_ms = 100
        self.micro_pause_max_ms = 500

    def configure(self, enabled, intensity, jitter_px, pause_chance, pause_min, pause_max):
        self.enabled = enabled
        self.intensity = max(1, min(100, intensity))
        self.position_jitter_px = jitter_px
        self.micro_pause_chance = pause_chance
        self.micro_pause_min_ms = pause_min
        self.micro_pause_max_ms = pause_max

    def jitter_point(self, x, y, radius):
        """Pick a random point inside the circle, then apply Gaussian jitter."""
        angle = random.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(random.uniform(0, 1))
        px = x + r * math.cos(angle)
        py = y + r * math.sin(angle)

        if self.enabled:
            scale = self.intensity / 50.0
            sigma = self.position_jitter_px * scale
            px += random.gauss(0, sigma)
            py += random.gauss(0, sigma)

        return int(px), int(py)

    def jitter_interval(self, base_min_ms, base_max_ms):
        """Return a randomized interval in ms."""
        interval = random.uniform(base_min_ms, base_max_ms)
        if self.enabled:
            scale = self.intensity / 50.0
            extra = random.gauss(0, interval * 0.15 * scale)
            interval += extra
        return max(1, int(interval))

    def should_micro_pause(self):
        """Decide if this click should be followed by a micro-pause."""
        if not self.enabled:
            return False, 0
        scale = self.intensity / 50.0
        chance = self.micro_pause_chance * scale
        if random.random() < chance:
            pause = random.randint(self.micro_pause_min_ms, self.micro_pause_max_ms)
            return True, pause
        return False, 0

    def move_curve(self, start_x, start_y, end_x, end_y, steps=10):
        """Generate a Bezier-like path from start to end with random control point."""
        if not self.enabled:
            return [(end_x, end_y)]

        mid_x = (start_x + end_x) / 2 + random.gauss(0, 20)
        mid_y = (start_y + end_y) / 2 + random.gauss(0, 20)

        points = []
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier
            px = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * mid_x + t ** 2 * end_x
            py = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * mid_y + t ** 2 * end_y
            # Add tiny noise
            px += random.gauss(0, 1)
            py += random.gauss(0, 1)
            points.append((int(px), int(py)))
        return points
