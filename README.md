Pong 2 (Pygame)

A modern, optimized Pong game built with Python and Pygame.

Features:
- 960×540 window, 80 FPS
- Smooth controls: W/S (left) and Up/Down (right)
- Angle-based ball deflection on paddle hits
- Dotted center line, clean black/white aesthetic
- Scoreboard with player names; first to 3 wins
- Possession after scoring: non-scorer holds ball; Space to launch
- Winner screen shows the winner's name, with a Restart button (no auto-reset)
 - On launch, prompts for both players' names; random initial possession
- Sound effects from `assets/`:
  - `pong_hit.wav`: paddle hit and launch
  - `pong_score.wav`: point scored (not on final winning point)
  - `pong_win.wav`: victory fanfare

Controls:
- Left paddle: W (up), S (down)
- Right paddle: Up Arrow (up), Down Arrow (down)
- After a score, the other player holds the ball: Space to launch
- On win screen: click Restart or press Space/Enter to start a new match (names are preserved)

Notes:
- Requires a display capable of 960×540 or higher. Adjust constants in `main.py` if needed.
- Audio files expected at: `assets/pong_hit.wav`, `assets/pong_score.wav`, `assets/pong_win.wav`.


