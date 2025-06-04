import itertools
import time
import os # Added for os.path.basename and os.path.exists
from collections import defaultdict
from evaluator.game_controller import GameController

def run_pairwise_battle(agent_a_path, agent_b_path, num_games, filler_type="P0_P1"):
    """
    Runs a pairwise battle between Agent A and Agent B.
    P0 is Agent A, P1 is Agent B.
    filler_type determines P2, P3:
      "P0_P0": P2=A, P3=A (Agents: A, B, A, A)
      "P1_P1": P2=B, P3=B (Agents: A, B, B, B)
      "P0_P1": P2=A, P3=B (Agents: A, B, A, B) - Default
    """
    print(f"Starting pairwise battle: {os.path.basename(agent_a_path)} vs {os.path.basename(agent_b_path)} for {num_games} games. Filler: {filler_type}")

    if filler_type == "P0_P0": # A, B, A, A
        agent_paths_template = [agent_a_path, agent_b_path, agent_a_path, agent_a_path]
        agent_map = {0: 'A', 1: 'B', 2: 'A', 3: 'A'} # Who is type A or B at each position
    elif filler_type == "P1_P1": # A, B, B, B
        agent_paths_template = [agent_a_path, agent_b_path, agent_b_path, agent_b_path]
        agent_map = {0: 'A', 1: 'B', 2: 'B', 3: 'B'}
    elif filler_type == "P0_P1": # A, B, A, B
        agent_paths_template = [agent_a_path, agent_b_path, agent_a_path, agent_b_path]
        agent_map = {0: 'A', 1: 'B', 2: 'A', 3: 'B'}
    else:
        raise ValueError(f"Invalid filler_type: {filler_type}. Use 'P0_P0', 'P1_P1', or 'P0_P1'.")

    results_summary = {
        "agent_a_path": agent_a_path,
        "agent_b_path": agent_b_path,
        "num_games_requested": num_games,
        "filler_type": filler_type,
        "agent_a_wins": 0,
        "agent_b_wins": 0,
        "draw_games": 0,
        "agent_a_total_score": 0,
        "agent_b_total_score": 0,
        "games_completed": 0, # Successfully completed games (no error during game)
        "errors_setup": 0, # Errors before game loop starts (e.g. agent start)
        "errors_runtime": 0, # Errors during game loop
        "game_details": []
    }

    for i in range(num_games):
        game_id = f"pb_{os.path.basename(agent_a_path).split('.')[0]}_vs_{os.path.basename(agent_b_path).split('.')[0]}_{filler_type}_{i}"
        print(f"  Running game {i+1}/{num_games} (ID: {game_id})...")

        current_game_agent_paths = list(agent_paths_template)
        controller = GameController(agent_main_paths=current_game_agent_paths, game_id=game_id)
        game_result = {}

        try:
            game_result = controller.play_game()

            if game_result.get("error"):
                results_summary["errors_runtime"] += 1
                results_summary["game_details"].append({
                    "id": game_id, "error": game_result["error"],
                    "reason": game_result.get("reason"), "log": game_result.get("log", [])[-5:] # last 5 log entries
                })
                print(f"  Game {game_id} resulted in runtime error: {game_result['error']}")
                continue

            results_summary["games_completed"] += 1
            scores = game_result.get("scores", [0,0,0,0])
            winner_idx = game_result.get("winner") # player_id (0-3) or list of winners or None

            current_game_agent_a_score = 0
            current_game_agent_b_score = 0
            for p_idx, score_val in enumerate(scores):
                if agent_map[p_idx] == 'A':
                    current_game_agent_a_score += score_val
                elif agent_map[p_idx] == 'B':
                    current_game_agent_b_score += score_val

            results_summary["agent_a_total_score"] += current_game_agent_a_score
            results_summary["agent_b_total_score"] += current_game_agent_b_score

            if winner_idx is not None:
                winners_resolved = []
                if isinstance(winner_idx, list):
                    winners_resolved = winner_idx
                else:
                    winners_resolved = [winner_idx]

                won_by_A = any(agent_map[w_idx] == 'A' for w_idx in winners_resolved)
                won_by_B = any(agent_map[w_idx] == 'B' for w_idx in winners_resolved)

                if won_by_A and not won_by_B : results_summary["agent_a_wins"] +=1
                elif won_by_B and not won_by_A : results_summary["agent_b_wins"] +=1
                elif won_by_A and won_by_B :
                    results_summary["draw_games"] += 1

            else:
                results_summary["draw_games"] += 1

            results_summary["game_details"].append({
                "id": game_id, "scores": scores, "winner": winner_idx,
                "reason": game_result.get("reason", ""),
                "log_head": game_result.get("log", [])[:5],
                "log_tail": game_result.get("log", [])[-5:]
            })

        except ImportError as e:
            print(f"CRITICAL IMPORT ERROR for game {game_id}: {e}. This evaluation run will stop.")
            results_summary["errors_setup"] += (num_games - i)
            results_summary["game_details"].append({"id": game_id, "error": f"ImportError: {e}", "reason": "Setup failure"})
            raise
        except Exception as e:
            print(f"CRITICAL EXCEPTION for game {game_id}: {type(e).__name__} - {e}")
            import traceback
            traceback.print_exc()
            results_summary["errors_setup"] += 1
            results_summary["game_details"].append({"id": game_id, "error": str(e), "reason": "Critical runtime exception in battle setup/teardown."})

    total_valid_games = results_summary["games_completed"]
    if total_valid_games > 0:
        num_a_instances_per_game = sum(1 for role in agent_map.values() if role == 'A')
        num_b_instances_per_game = sum(1 for role in agent_map.values() if role == 'B')

        if num_a_instances_per_game > 0:
            results_summary["avg_score_agent_a"] = results_summary["agent_a_total_score"] / (total_valid_games * num_a_instances_per_game)
        else: results_summary["avg_score_agent_a"] = 0

        if num_b_instances_per_game > 0:
            results_summary["avg_score_agent_b"] = results_summary["agent_b_total_score"] / (total_valid_games * num_b_instances_per_game)
        else: results_summary["avg_score_agent_b"] = 0
    else:
        results_summary["avg_score_agent_a"] = 0
        results_summary["avg_score_agent_b"] = 0

    print(f"Pairwise battle finished. A wins: {results_summary['agent_a_wins']}, B wins: {results_summary['agent_b_wins']}, Draws: {results_summary['draw_games']}.")
    print(f"Completed games: {total_valid_games}. Setup errors: {results_summary['errors_setup']}, Runtime errors: {results_summary['errors_runtime']}.")
    return results_summary


def run_round_robin_tournament(agent_paths, num_games_per_matchup):
    num_agents = len(agent_paths)
    if num_agents < 4:
        raise ValueError("Round-robin tournament requires at least 4 agents.")

    print(f"Starting round-robin tournament with {num_agents} agents ({num_games_per_matchup} games per unique 4-player matchup).")

    agent_indices = list(range(num_agents))
    matchups_player_indices = list(itertools.combinations(agent_indices, 4))

    agent_stats = defaultdict(lambda: {"wins": 0, "total_score": 0, "games_played_in": 0, "errors_runtime": 0, "errors_setup":0})

    overall_summary = {
        "num_agents": num_agents,
        "games_per_matchup": num_games_per_matchup,
        "total_matchups_generated": len(matchups_player_indices),
        "matchup_details": []
    }

    for original_indices_tuple in matchups_player_indices:
        current_matchup_agent_paths = [agent_paths[i] for i in original_indices_tuple]
        matchup_id_str = "_".join(map(str, original_indices_tuple))

        matchup_log = {
            "matchup_original_indices": original_indices_tuple,
            "matchup_agent_paths": [os.path.basename(p) for p in current_matchup_agent_paths],
            "games_in_matchup_completed":0, "errors_runtime":0, "errors_setup":0,
            "scores_by_original_idx": defaultdict(int),
            "wins_by_original_idx": defaultdict(int)
        }
        print(f"\n--- Matchup: {matchup_id_str} ({[os.path.basename(p) for p in current_matchup_agent_paths]}) ---")

        for i in range(num_games_per_matchup):
            game_id = f"rr_{matchup_id_str}_{i}"
            print(f"  Running game {i+1}/{num_games_per_matchup} (ID: {game_id})...")

            controller = GameController(agent_main_paths=current_matchup_agent_paths, game_id=game_id)
            game_result = {}
            try:
                game_result = controller.play_game()

                if game_result.get("error"):
                    matchup_log["errors_runtime"] += 1
                    for original_idx in original_indices_tuple:
                         agent_stats[agent_paths[original_idx]]["errors_runtime"] +=1
                    print(f"  Game {game_id} resulted in runtime error: {game_result['error']}")
                    continue

                matchup_log["games_in_matchup_completed"] +=1
                scores = game_result.get("scores", [0,0,0,0])
                winner_idx_in_game = game_result.get("winner")

                for player_idx_in_game, original_agent_idx in enumerate(original_indices_tuple):
                    original_agent_path = agent_paths[original_agent_idx]
                    agent_stats[original_agent_path]["games_played_in"] += 1
                    agent_stats[original_agent_path]["total_score"] += scores[player_idx_in_game]
                    matchup_log["scores_by_original_idx"][original_agent_idx] += scores[player_idx_in_game]

                if winner_idx_in_game is not None:
                    winners_resolved = [winner_idx_in_game] if not isinstance(winner_idx_in_game, list) else winner_idx_in_game
                    for w_idx_in_game in winners_resolved:
                        winning_original_agent_idx = original_indices_tuple[w_idx_in_game]
                        winning_agent_path = agent_paths[winning_original_agent_idx]
                        agent_stats[winning_agent_path]["wins"] += 1
                        matchup_log["wins_by_original_idx"][winning_original_agent_idx] +=1

            except ImportError as e:
                print(f"CRITICAL IMPORT ERROR for game {game_id}: {e}. Tournament will stop.")
                matchup_log["errors_setup"] += (num_games_per_matchup - i)
                for original_idx in original_indices_tuple:
                     agent_stats[agent_paths[original_idx]]["errors_setup"] += (num_games_per_matchup - i)
                raise
            except Exception as e:
                print(f"CRITICAL EXCEPTION for game {game_id}: {type(e).__name__} - {e}")
                import traceback; traceback.print_exc()
                matchup_log["errors_setup"] += 1
                for original_idx in original_indices_tuple:
                     agent_stats[agent_paths[original_idx]]["errors_setup"] +=1

        overall_summary["matchup_details"].append(matchup_log)
        print(f"--- Matchup {matchup_id_str} finished. ---")

    final_agent_reports = []
    for agent_p, stats in agent_stats.items():
        final_agent_reports.append({
            "agent_path": os.path.basename(agent_p),
            "wins": stats["wins"],
            "games_played_in": stats["games_played_in"],
            "win_rate": (stats["wins"] / stats["games_played_in"]) if stats["games_played_in"] > 0 else 0,
            "average_score": (stats["total_score"] / stats["games_played_in"]) if stats["games_played_in"] > 0 else 0,
            "participated_in_runtime_error_games": stats["errors_runtime"],
            "participated_in_setup_error_games": stats["errors_setup"]
        })
    overall_summary["final_agent_reports"] = sorted(final_agent_reports, key=lambda x: x["wins"], reverse=True)

    print("\n--- Round-Robin Tournament Overall Summary ---")
    for report in overall_summary["final_agent_reports"]:
        print(f"  Agent: {report['agent_path']}")
        print(f"    Wins: {report['wins']}/{report['games_played_in']} (Rate: {report['win_rate']:.2f}), Avg Score: {report['average_score']:.2f}")
        if report['participated_in_runtime_error_games'] > 0 or report['participated_in_setup_error_games'] > 0:
            print(f"    Participated in Errored Games (Runtime/Setup): {report['participated_in_runtime_error_games']}/{report['participated_in_setup_error_games']}")
    return overall_summary


if __name__ == '__main__':
    print("Testing Evaluation Strategies...")
    dummy_agent_scripts = {
        "A": "dummy_agent_A_eval.py", "B": "dummy_agent_B_eval.py",
        "C": "dummy_agent_C_eval.py", "D": "dummy_agent_D_eval.py"
    }

    for name, script_path in dummy_agent_scripts.items():
        # Always overwrite to ensure correct version for the test
        print(f"Creating/Overwriting dummy agent {name} at {script_path}")
        dummy_agent_code = f"""
import sys
import time

agent_name = '{name}'
stderr_writer = sys.stderr

def eprint(*args, **kwargs):
    print(f"Dummy_{{agent_name}}:", *args, file=stderr_writer, **kwargs)

eprint("starting")

# Type 0: INIT
line0 = sys.stdin.readline().strip()
# eprint(f"Received for Type 0: {{line0}}")
print('PASS')
sys.stdout.flush()

# Type 1: HAND
line1 = sys.stdin.readline().strip()
# eprint(f"Received for Type 1: {{line1}}")
print('PASS')
sys.stdout.flush()

interactions = 0
max_interactions = 20

while interactions < max_interactions:
    request = sys.stdin.readline().strip()
    if not request:
        eprint("EOF received, stopping.")
        break

    eprint(f"R: {{request}}")
    parts = request.split()
    action = "PASS"

    if parts and parts[0] == '2' and len(parts) > 1:
        action = f'PLAY {{parts[1]}}'

    print(action)
    sys.stdout.flush()
    eprint(f"S: {{action}}")
    interactions += 1
    time.sleep(0.005)

eprint("stopping after max_interactions or EOF")
sys.exit(0)
"""
        with open(script_path, 'w') as f:
            f.write(dummy_agent_code)

    test_pairwise = True
    test_round_robin = True

    if test_pairwise:
        print("\n--- Testing Pairwise Battle ---")
        try:
            pairwise_results = run_pairwise_battle(
                dummy_agent_scripts["A"],
                dummy_agent_scripts["B"],
                num_games=2,
                filler_type="P0_P1"
            )
            print("Pairwise Battle Final Summary:")
            print(f"  A Wins: {pairwise_results.get('agent_a_wins')}, B Wins: {pairwise_results.get('agent_b_wins')}, Draws: {pairwise_results.get('draw_games')}")
            print(f"  Avg Score A: {pairwise_results.get('avg_score_agent_a'):.2f}, Avg Score B: {pairwise_results.get('avg_score_agent_b'):.2f}")
            print(f"  Completed Games: {pairwise_results.get('games_completed')}, Errors (Setup/Runtime): {pairwise_results.get('errors_setup')}/{pairwise_results.get('errors_runtime')}")
            if pairwise_results.get("games_completed",0) != 2 :
                 print(f"  WARNING: Pairwise did not complete all games. Details: {pairwise_results.get('game_details')[-1:]}")
        except ImportError as e: print(f"SKIPPING Pairwise Test due to ImportError (likely MahjongGB): {e}")
        except Exception as e: print(f"EXCEPTION in Pairwise Battle test: {type(e).__name__} - {e}"); import traceback; traceback.print_exc()

    if test_round_robin:
        print("\n--- Testing Round-Robin Tournament ---")
        tournament_agent_paths = [
            dummy_agent_scripts["A"], dummy_agent_scripts["B"],
            dummy_agent_scripts["C"], dummy_agent_scripts["D"]
        ]
        try:
            robin_results = run_round_robin_tournament(tournament_agent_paths, num_games_per_matchup=1)
            print("Round-Robin Final Summary (raw):")
            if robin_results and robin_results.get("final_agent_reports"):
                for rep in robin_results["final_agent_reports"]: print(f"  {rep['agent_path']}: Wins {rep['wins']}/{rep['games_played_in']}, AvgScore {rep['average_score']:.1f}")
            if robin_results.get("total_matchups_generated",0) * 1 != robin_results.get("final_agent_reports",[{}])[0].get("games_played_in", -1):
                 print(f"  WARNING: Round Robin games played does not match expected for all agents.")
        except ImportError as e: print(f"SKIPPING Round Robin Test due to ImportError (likely MahjongGB): {e}")
        except ValueError as ve: print(f"ValueError in Round Robin setup: {ve}")
        except Exception as e: print(f"EXCEPTION in Round-Robin test: {type(e).__name__} - {e}"); import traceback; traceback.print_exc()

    print("\nEvaluation strategies test finished.")
