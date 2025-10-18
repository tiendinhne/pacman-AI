import argparse
from game import GameController

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pacman Task2 - fixed UI + A*")
    parser.add_argument("--map", type=str, default="maps/task02_pacman_example_map.txt", help="Path to layout txt")
    parser.add_argument("--mode", type=str, default="manual", choices=["manual", "auto"], help="Start mode")
    args = parser.parse_args()

    game = GameController(args.map, mode=args.mode)
    game.run()

