import pygame, time, heapq, argparse, sys, ast
from typing import List, Tuple, Optional

from map_loader import (
    load_map, _calculate_ghost_paths, get_ghost_positions,
    successors, State, is_goal
)
from Heristics import heuristic_food_mst
from pacman_sprite import PacmanSprite

# ------------------- SETTINGS -------------------
TILE_SIZE = 32
FPS = 12
AUTO_STEP_INTERVAL = 0.12
GHOST_INTERVAL = 0.05
ASTAR_TIME_LIMIT = 12.0


# ------------------- A* SOLVER -------------------
class AStarSolver:
    def __init__(self, grid, pies, ghosts, ghost_paths, foods_map, foods_list, corners, exit_pos):
        self.grid = grid
        self.pies = pies
        self.ghosts = ghosts
        self.ghost_paths = ghost_paths
        self.foods_map = foods_map
        self.foods_list = foods_list
        self.corners = corners
        self.exit_pos = exit_pos

    def solve(self, start_state: State, time_limit: float = ASTAR_TIME_LIMIT):
        t0 = time.time()
        frontier = []
        count = 0
        heapq.heappush(frontier, (0.0, count, start_state))
        came_from, act_from, gscore = {start_state: None}, {start_state: None}, {start_state: 0.0}
        nodes, max_frontier, goal = 0, 1, None

        while frontier:
            if time.time() - t0 > time_limit:
                break
            _, _, current = heapq.heappop(frontier)
            nodes += 1

            if is_goal(current, self.exit_pos):
                goal = current
                break

            for act, nxt, cost in successors(current, self.grid, self.pies, self.ghosts,
                                             self.ghost_paths, self.foods_map, self.corners):
                new_g = gscore[current] + cost
                if nxt not in gscore or new_g < gscore[nxt]:
                    gscore[nxt] = new_g
                    h = heuristic_food_mst(nxt, self.foods_list, self.grid)
                    f = new_g + h
                    count += 1
                    heapq.heappush(frontier, (f, count, nxt))
                    came_from[nxt], act_from[nxt] = current, act
            max_frontier = max(max_frontier, len(frontier))

        stats = {"found": bool(goal), "nodes": nodes, "frontier": max_frontier, "runtime": time.time() - t0}
        if not goal:
            return [], stats

        # reconstruct path
        path = []
        s = goal
        while s != start_state:
            path.append(act_from[s])
            s = came_from[s]
        path.reverse()
        stats["path_len"] = len(path)
        return path, stats
    

# ------------------- GAME CONTROLLER -------------------
class GameController:
    def __init__(self, map_path: str, mode: str = "manual"):
        assert mode in ("manual", "auto")
        pygame.init()

        # Load map + components
        (
            self.grid,
            self.pac_start,
            self.pies,
            self.ghosts,
            self.exit_pos,
            self.corners,
            self.foods_map,
            self.foods_list,
        ) = load_map(map_path)

        if not isinstance(self.pies, set):
            self.pies = set(self.pies)
        self.ghost_paths = _calculate_ghost_paths(self.ghosts, self.grid)

        # Setup window
        self.cols, self.rows = len(self.grid[0]), len(self.grid)
        self.win_w, self.win_h = self.cols * TILE_SIZE, self.rows * TILE_SIZE + 48
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption("Pacman - Task2 (fixed v5)")

        # Font & Clock
        self.font = pygame.font.SysFont(None, 18)
        self.bigfont = pygame.font.SysFont(None, 28)
        self.clock = pygame.time.Clock()

        # Sprite
        try:
            self.sprite = PacmanSprite(tile_size=TILE_SIZE)
        except Exception:
            self.sprite = None

        # State init
        foods_mask = (1 << len(self.foods_list)) - 1
        self.state = State(self.pac_start, 0, foods_mask, 0)

        # Mode, control, plan
        self.mode = mode
        self.plan, self.astar_stats = [], None
        self.last_auto = 0.0
        self.last_ghost_move = 0.0
        self.ghost_step_counter = 0

        # UI
        self.btn_rect = pygame.Rect(self.win_w - 180, self.win_h - 40, 160, 28)
        self.running, self.message, self.message_time = True, None, 0.0

    # ---------- DRAWING ----------
    def draw(self):
        s = self.screen
        s.fill((0, 0, 0))

        # walls/background
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                color = (40, 40, 120) if ch == '%' else (8, 8, 8)
                pygame.draw.rect(s, color, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # foods
        for i, (fy, fx) in enumerate(self.foods_list):
            if (self.state.foods_mask >> i) & 1:
                pygame.draw.circle(s, (255, 200, 0),
                                   (fx * TILE_SIZE + TILE_SIZE // 2, fy * TILE_SIZE + TILE_SIZE // 2), 4)

        # pies
        for (py, px) in list(self.pies):
            pygame.draw.circle(s, (180, 0, 200),
                               (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2), 6)

        # exit
        ey, ex = self.exit_pos
        pygame.draw.rect(s, (0, 200, 0),
                         (ex * TILE_SIZE + 4, ey * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8))

        # teleports (corners)
        for (cy, cx) in self.corners:
            pygame.draw.rect(s, (0, 120, 255),
                             (cx * TILE_SIZE + 2, cy * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)

        # ghosts (independent timer)
        for (gy, gx) in get_ghost_positions(self.ghost_step_counter, self.ghosts, self.ghost_paths):
            pygame.draw.circle(s, (255, 80, 80),
                               (gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2 - 3)

        # pacman
        py, px = self.state.pos
        if self.sprite:
            try:
                self.sprite.draw(s, (py, px))
            except Exception:
                pygame.draw.circle(s, (255, 255, 0),
                                   (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2 - 3)
        else:
            pygame.draw.circle(s, (255, 255, 0),
                               (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2 - 3)

        # HUD (bottom bar)
        pygame.draw.rect(s, (18, 18, 18), (0, self.win_h - 48, self.win_w, 48))
        info = f"MODE:{self.mode.upper()}  SCORE:{self.state.total_steps}  PIE:{self.state.pie_time}  FOODS:{bin(self.state.foods_mask).count('1')}"
        s.blit(self.font.render(info, True, (230, 230, 230)), (8, self.win_h - 42))

        if self.astar_stats:
            st = f"A*: nodes={self.astar_stats.get('nodes',0)} frontier={self.astar_stats.get('frontier',0)} time={self.astar_stats.get('runtime',0):.2f}s"
            s.blit(self.font.render(st, True, (180, 180, 180)), (8, self.win_h - 24))

        pygame.draw.rect(s, (60, 60, 60), self.btn_rect)
        pygame.draw.rect(s, (200, 200, 200), self.btn_rect, 2)
        s.blit(self.font.render("TOGGLE MODE", True, (255, 255, 255)),
               (self.btn_rect.x + 16, self.btn_rect.y + 6))

        if self.message and time.time() - self.message_time < 3:
            t = self.bigfont.render(self.message, True, (255, 230, 0))
            s.blit(t, t.get_rect(center=(self.win_w // 2, (self.win_h - 48) // 2)))

        pygame.display.flip()

    # ---------- HELPER ----------
    def _parse_target(self, act: str):
        if not act.startswith("TELEPORT"):
            return None
        try:
            tup = ast.literal_eval(act.split("to")[-1].strip())
            if isinstance(tup, tuple) and len(tup) == 2:
                return tup
        except Exception:
            return None
        return None


    # ---------- APPLY ACTION ----------
    def apply_action(self, act: str) -> bool:
        """
        Use successors() to validate action. successors() returns (action_str, new_state, cost).
        If matched, update self.state = new_state (which already has total_steps incremented),
        remove pie if present, update sprite direction, and return True.
        """
        succs = successors(self.state, self.grid, self.pies, self.ghosts, self.ghost_paths, self.foods_map, self.corners)
        for a_str, new_state, _ in succs:
            # direct match or teleport-match (compare parsed targets)
            if a_str == act or (a_str.startswith("TELEPORT") and act.startswith("TELEPORT") and self._parse_target(a_str) == self._parse_target(act)):
                self.state = new_state
                # remove pie if Pacman landed on it
                if self.state.pos in self.pies:
                    self.pies.discard(self.state.pos)
                # update sprite direction on normal moves
                if self.sprite and act in ("UP", "DOWN", "LEFT", "RIGHT"):
                    self.sprite.direction = {"UP": "up", "DOWN": "down", "LEFT": "left", "RIGHT": "right"}[act]
                    self.sprite.update()
                return True
        return False


    # ---------- MANUAL STEP ----------
    def step_manual(self):
        k = pygame.key.get_pressed()
        move = None
        if k[pygame.K_UP]:
            move = "UP"
        elif k[pygame.K_DOWN]:
            move = "DOWN"
        elif k[pygame.K_LEFT]:
            move = "LEFT"
        elif k[pygame.K_RIGHT]:
            move = "RIGHT"

        moved = False
        if move:
            moved = self.apply_action(move)

        # manual teleport via 'T' key when standing on a corner
        if k[pygame.K_t]:
            if self.state.pos in self.corners:
                targets = [c for c in sorted(self.corners) if c != self.state.pos]
                if targets:
                    targ = targets[0]
                    tele_act = f"TELEPORT to {targ}"
                    if self.apply_action(tele_act):
                        moved = True

        # IMPORTANT: do NOT increment total_steps or decrement pie_time here when Pacman didn't move.
        # successors() already set pie_time/total_steps for valid moves applied in apply_action.

    # ---------- AUTO STEP (A*) ----------
    def step_auto(self, now: float):
        # plan if empty
        if not self.plan:
            solver = AStarSolver(self.grid, self.pies, self.ghosts, self.ghost_paths, self.foods_map, self.foods_list, self.corners, self.exit_pos)
            self.plan, self.astar_stats = solver.solve(self.state, time_limit=ASTAR_TIME_LIMIT)
            if not self.astar_stats.get("found", False):
                self.message = "A* failed or timeout. Switching to manual."
                self.message_time = time.time()
                self.mode = "manual"
                self.plan = []
                return
            self.last_auto = now

        # execute next action at fixed interval
        if self.plan and (now - self.last_auto) >= AUTO_STEP_INTERVAL:
            next_act = self.plan.pop(0)
            applied = self.apply_action(next_act)
            if not applied:
                # plan invalidated (ghosts moved into path etc.) — drop plan and replan next loop
                self.plan = []
            self.last_auto = now


    # ---------- CHECK END / COLLISION ----------
    def check_end_and_collision(self) -> Optional[str]:
        # win?
        if is_goal(self.state, self.exit_pos):
            return "win"
        # ghosts positions depend on independent ghost counter
        ghosts_now = get_ghost_positions(self.ghost_step_counter, self.ghosts, self.ghost_paths)
        # if not powered (pie_time == 0) and Pacman on same cell as a ghost -> dead
        if self.state.pie_time == 0 and self.state.pos in ghosts_now:
            return "dead"
        return None


    # ---------- MAIN RUN LOOP ----------
    def run(self):
        while self.running:
            now = time.time()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.btn_rect.collidepoint(ev.pos):
                        # toggle mode
                        self.mode = "auto" if self.mode == "manual" else "manual"
                        self.plan = []
                        self.astar_stats = None
                        self.message = f"MODE: {self.mode.upper()}"
                        self.message_time = time.time()

            # update according to mode
            if self.mode == "manual":
                self.step_manual()
            else:
                self.step_auto(now)

            # update ghost independent timer
            if now - self.last_ghost_move >= GHOST_INTERVAL:
                self.ghost_step_counter += 1
                self.last_ghost_move = now

            # check end / collision
            res = self.check_end_and_collision()
            if res == "win":
                self.message = "YOU WIN!"
                self.message_time = time.time()
                self.draw()
                time.sleep(2.0)
                break
            elif res == "dead":
                self.message = "YOU DIED!"
                self.message_time = time.time()
                self.draw()
                time.sleep(2.0)
                break

            # draw and cap frame rate
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


# ---------- MAIN ----------
def main():
    parser = argparse.ArgumentParser(description="Pacman Task2 - fixed v5")
    parser.add_argument("--map", type=str, default="maps/task02_pacman_example_map.txt")
    parser.add_argument("--mode", type=str, default="manual", choices=["manual", "auto"])
    args = parser.parse_args()

    try:
        game = GameController(args.map, mode=args.mode)
    except FileNotFoundError as e:
        print("Map file not found:", e)
        sys.exit(1)
    except Exception as e:
        print("Error initializing game:", e)
        sys.exit(1)

    game.run()


if __name__ == "__main__":
    main()
