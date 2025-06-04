# Mahjong Agent Evaluator

## Overview

This directory contains a program for evaluating the performance of Mahjong agents that conform to the standard input/output protocol defined in `../../Chinese-Standard-Mahjong/bot_io.md`. The evaluator can run games between agents in various configurations, track statistics, and report results.

It is designed to work with agents that have a `__main__.py` entry point that handles the stdin/stdout communication.

## Requirements

*   Python 3.7+ (developed with 3.10)
*   **MahjongGB**: This library is crucial for calculating game scores and hand properties. It must be installed in your Python environment. You can find it at [https://github.com/ailab-pku/PyMahjongGB](https://github.com/ailab-pku/PyMahjongGB).
    The recommended way to install it (which handles C++ submodules correctly) is:
    ```bash
    pip install git+https://github.com/ailab-pku/PyMahjongGB.git
    ```
    You will need Python development headers (e.g., `python3-dev` or `python3.10-dev` on Debian/Ubuntu) and C++ build tools (e.g., `build-essential` or `g++`) for the compilation of its C++ components. If the evaluator fails with an `ImportError: MahjongGB` or build errors during its installation, these dependencies are the most likely cause.

## Directory Structure

*   `__main__.py`: The main command-line interface for running evaluations.
*   `evaluation.py`: Implements different evaluation strategies (pairwise battles, round-robin tournaments).
*   `game_controller.py`: Manages the execution of a single game of Mahjong between four agents.
*   `agent.py`: Defines an `Agent` class that handles subprocess management and communication with an individual agent script.
*   `env.py`: Contains the Mahjong game environment logic, adapted from `../agent_trainer/env.py`. It simulates the game and enforces rules.
*   `dummy_agent_*_eval.py` (in project root, created by `evaluation.py`'s test block): Example minimal agent scripts used for testing the evaluator.

## Agent Conformance

Your Mahjong agent **must** adhere to the communication protocol specified in `../../Chinese-Standard-Mahjong/bot_io.md`. The agent should:
1.  Be executable via a `python your_agent_main.py` command (or directly if it has a shebang and is executable).
2.  Read requests from `stdin`.
3.  Write responses to `stdout`. Each response must be a single line terminated by a newline character.
4.  Follow the turn-based request/response formats detailed in `bot_io.md`.

## How to Run Evaluations

You can run the evaluator using the Python module execution command from the **root directory of this project** (`/app` in the sandbox environment):

```bash
python -m evaluator <mode> [options]
```

### Common Options
*   `--output_file <path>`: Optional. Path to save the evaluation results in JSON format. If not provided, a default filename will be generated (e.g., `pairwise_agentA_vs_agentB_P0_P1_10games.json`).

### 1. Pairwise Battle Mode

Runs a specified number of games between two primary agents (Agent A and Agent B), with the other two player slots filled according to a chosen strategy. Player 0 is always Agent A, Player 1 is always Agent B.

**Command:**

```bash
python -m evaluator pairwise <path_to_agent_a_main.py> <path_to_agent_b_main.py> [options]
```

**Pairwise Options:**

*   `<path_to_agent_a_main.py>`: (Required) Path to Agent A's script.
*   `<path_to_agent_b_main.py>`: (Required) Path to Agent B's script.
*   `-n, --num_games <int>`: Number of games to play (default: 2, as per `__main__.py` current default for argparse).
*   `--filler <type>`: Strategy for filling player slots P2 and P3.
    *   `P0_P1` (default): P2=AgentA, P3=AgentB (Game: A, B, A, B)
    *   `P0_P0`: P2=AgentA, P3=AgentA (Game: A, B, A, A)
    *   `P1_P1`: P2=AgentB, P3=AgentB (Game: A, B, B, B)

**Example:**

```bash
python -m evaluator pairwise ./my_agents/agent_v1.py ./my_agents/agent_v2.py -n 20 --filler P0_P1 --output_file v1_vs_v2_abab_results.json
```

### 2. Round-Robin Tournament Mode

Runs a tournament where each unique combination of 4 agents from the provided list plays a specified number of games.

**Command:**

```bash
python -m evaluator roundrobin <path_to_agent1.py> <path_to_agent2.py> ... [options]
```

**Round-Robin Options:**

*   `<path_to_agent1.py> ...`: (Required) A list of paths to agent scripts. Requires at least 4 agents for a standard tournament.
*   `-g, --games_per_matchup <int>`: Number of games for each unique combination of 4 agents selected from the list (default: 1).

**Example:**

```bash
python -m evaluator roundrobin ./agents/foo.py ./agents/bar.py ./agents/baz.py ./agents/qux.py -g 5 --output_file tournament_results.json
```

## Output Format

The evaluation results are printed to the console (summary) and can be saved to a JSON file.

### Pairwise Battle JSON Output Structure (Example):

```json
{
    "agent_a_path": "dummy_agent_A_eval.py",
    "agent_b_path": "dummy_agent_B_eval.py",
    "num_games_requested": 1,
    "filler_type": "P0_P1",
    "agent_a_wins": 0,
    "agent_b_wins": 0,
    "draw_games": 1,
    "agent_a_total_score": -20, // Sum of scores for all A-type players in completed games
    "agent_b_total_score": 20,  // Sum of scores for all B-type players in completed games
    "games_completed": 1,
    "errors_setup": 0,
    "errors_runtime": 0,
    "game_details": [
        {
            "id": "pb_dummy_agent_A_eval_vs_dummy_agent_B_eval_P0_P1_0",
            "scores": [-30, 10, 10, 10], // P0, P1, P2, P3
            "winner": [1, 2, 3], // List of winning player indices
            "reason": "Game ended by Mahjong or Draw after 1 turns.",
            // log_head and log_tail show first/last 5 entries from detailed game log
            "log_head": ["..."],
            "log_tail": ["..."]
        }
    ],
    "avg_score_agent_a": -10.0, // Average score per instance of Agent A in completed games
    "avg_score_agent_b": 10.0   // Average score per instance of Agent B in completed games
}
```

### Round-Robin Tournament JSON Output Structure (Example):
```json
{
    "num_agents": 4,
    "games_per_matchup": 1,
    "total_matchups_generated": 1,
    "matchup_details": [ /* ... details for each matchup ... */ ],
    "final_agent_reports": [
        {
            "agent_path": "dummy_agent_B_eval.py",
            "wins": 1, // Total wins by this agent across all games it played
            "games_played_in": 1,
            "win_rate": 1.0,
            "average_score": 10.0,
            "participated_in_runtime_error_games": 0,
            "participated_in_setup_error_games": 0
        }
        // ... other agent reports
    ]
}
```

## Dummy Agents

The `evaluation.py` script, when its `__main__` block is run (e.g. via `python -m evaluator.evaluation`), creates dummy agent scripts (`dummy_agent_A_eval.py`, `dummy_agent_B_eval.py`, etc.) in the project root directory (`/app`). These are simple agents that:
*   Respond "PASS" to initial handshakes (Type 0 INIT, Type 1 HAND).
*   If they receive a Type 2 (DRAW) message, they respond by playing the tile they just drew.
*   Respond "PASS" to all other game situations.
They are primarily for testing the evaluator's plumbing and CLI.

## Error Handling and Logging

*   The evaluator aims to catch errors like agent scripts not found, agent subprocesses crashing, or agents timing out.
*   `GameController` maintains a detailed `game_log` for each game, which includes agent communications and game state changes. This log is included in the `game_details` section of the JSON output for pairwise battles and can be similarly structured for round-robin (though the example above is simplified).
*   STDERR output from agents is captured. If an agent times out, its recent STDERR output is included in the `TimeoutError` message to aid debugging. This is logged by `GameController` and will appear in its game log.
*   Critical errors like `MahjongGB` not being installed will terminate the evaluation run with an informative message.
```
