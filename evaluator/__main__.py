import argparse
import json
import os
import sys

# Ensure the evaluator package can be found if running as a script directly
# For example, if running `python evaluator/__main__.py` from the project root.
# This adjusts sys.path to include the project root directory.
current_script_path = os.path.abspath(__file__)
evaluator_dir = os.path.dirname(current_script_path)
project_root = os.path.dirname(evaluator_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from evaluator.evaluation import run_pairwise_battle, run_round_robin_tournament

def main():
    parser = argparse.ArgumentParser(description="Mahjong Agent Evaluation Program")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="Evaluation mode")

    # --- Pairwise Battle Subparser ---
    parser_pairwise = subparsers.add_parser("pairwise", help="Run a pairwise battle between two agents.")
    parser_pairwise.add_argument("agent_a", help="Path to Agent A's __main__.py script.")
    parser_pairwise.add_argument("agent_b", help="Path to Agent B's __main__.py script.")
    parser_pairwise.add_argument("-n", "--num_games", type=int, default=2, help="Number of games to play (default: 2).")
    parser_pairwise.add_argument(
        "--filler",
        type=str,
        default="P0_P1",
        choices=["P0_P0", "P1_P1", "P0_P1"],
        help="Filler strategy for P2, P3 slots (default: P0_P1 -> A,B,A,B)."
    )
    parser_pairwise.add_argument("--output_file", type=str, default=None, help="Optional path to save JSON results.")


    # --- Round-Robin Tournament Subparser ---
    parser_robin = subparsers.add_parser("roundrobin", help="Run a round-robin tournament among multiple agents.")
    parser_robin.add_argument(
        "agent_paths",
        nargs='+',
        help="List of paths to agent __main__.py scripts (at least 4 required for standard tournament)."
    )
    parser_robin.add_argument(
        "-g", "--games_per_matchup",
        type=int,
        default=1,
        help="Number of games for each unique combination of 4 agents (default: 1)."
    )
    parser_robin.add_argument("--output_file", type=str, default=None, help="Optional path to save JSON results.")


    args = parser.parse_args()

    results = None
    output_target = args.output_file
    # Default output file naming refined
    agent_a_name = os.path.basename(args.agent_a).split('.')[0] if hasattr(args, 'agent_a') and args.agent_a else "agentA"
    agent_b_name = os.path.basename(args.agent_b).split('.')[0] if hasattr(args, 'agent_b') and args.agent_b else "agentB"


    try:
        if args.mode == "pairwise":
            print(f"Starting Pairwise Battle: {args.agent_a} vs {args.agent_b}")
            if not os.path.exists(args.agent_a):
                raise FileNotFoundError(f"Agent A script not found: {args.agent_a}")
            if not os.path.exists(args.agent_b):
                raise FileNotFoundError(f"Agent B script not found: {args.agent_b}")

            results = run_pairwise_battle(
                agent_a_path=args.agent_a,
                agent_b_path=args.agent_b,
                num_games=args.num_games,
                filler_type=args.filler
            )
            if not output_target:
                output_target = f"pairwise_{agent_a_name}_vs_{agent_b_name}_{args.filler}_{args.num_games}games.json"


        elif args.mode == "roundrobin":
            print(f"Starting Round-Robin Tournament with agents: {args.agent_paths}")
            if len(args.agent_paths) < 4 and len(args.agent_paths) > 0 : # Check if any agents were provided
                print(f"Warning: Round-robin typically requires at least 4 agents. You provided {len(args.agent_paths)}.")
            elif not args.agent_paths: # No agents provided
                 raise ValueError("No agent paths provided for roundrobin mode.")

            for path in args.agent_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Agent script not found: {path}")

            results = run_round_robin_tournament(
                agent_paths=args.agent_paths,
                num_games_per_matchup=args.games_per_matchup
            )
            if not output_target:
                 output_target = f"roundrobin_results_{len(args.agent_paths)}agents_{args.games_per_matchup}games_each.json"

    except FileNotFoundError as fnf_error:
        print(f"ERROR: {fnf_error}", file=sys.stderr)
        sys.exit(1)
    except ImportError as ie:
         print(f"CRITICAL IMPORT ERROR: {ie}. This often means MahjongGB is not installed or not found.", file=sys.stderr)
         print("Please ensure MahjongGB is correctly installed (see https://github.com/ailab-pku/PyMahjongGB).", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


    if results:
        print("\n--- Evaluation Complete ---")
        if args.mode == "pairwise":
            print(f"Mode: Pairwise Battle ({os.path.basename(results.get('agent_a_path','N/A'))} vs {os.path.basename(results.get('agent_b_path','N/A'))})")
            print(f"  Games Completed: {results.get('games_completed')} (Requested: {results.get('num_games_requested')})")
            print(f"  Filler Strategy: {results.get('filler_type')}")
            print(f"  Agent A Wins: {results.get('agent_a_wins')}")
            print(f"  Agent B Wins: {results.get('agent_b_wins')}")
            print(f"  Draws: {results.get('draw_games')}")
            print(f"  Errors (Setup/Runtime): {results.get('errors_setup')}/{results.get('errors_runtime')}")
            print(f"  Avg Score Agent A: {results.get('avg_score_agent_a', 0):.2f}")
            print(f"  Avg Score Agent B: {results.get('avg_score_agent_b', 0):.2f}")

        elif args.mode == "roundrobin":
            print("Mode: Round-Robin Tournament")
            print(f"  Total Matchups Generated: {results.get('total_matchups_generated')}")
            print(f"  Games per Matchup: {results.get('games_per_matchup')}")
            print("  Agent Summaries:")
            for agent_summary in results.get("final_agent_reports", []):
                print(f"    - Agent: {agent_summary['agent_path']}") # Already basename
                print(f"        Wins: {agent_summary['wins']}/{agent_summary['games_played_in']} (Rate: {agent_summary['win_rate']:.2f})")
                print(f"        Avg Score: {agent_summary['average_score']:.2f}")
                if agent_summary.get('participated_in_runtime_error_games',0) > 0 or agent_summary.get('participated_in_setup_error_games',0) > 0:
                     err_runtime = agent_summary.get('participated_in_runtime_error_games',0)
                     err_setup = agent_summary.get('participated_in_setup_error_games',0)
                     print(f"        Participated in Errored Games (Runtime/Setup): {err_runtime}/{err_setup}")

        if output_target:
            try:
                # Ensure directory for output_target exists if it's a path
                output_dir = os.path.dirname(output_target)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    print(f"Created directory for output file: {output_dir}")

                with open(output_target, 'w') as f:
                    json.dump(results, f, indent=4)
                print(f"Results saved to: {output_target}")
            except Exception as e:
                print(f"Error saving results to {output_target}: {e}", file=sys.stderr)
    else:
        print("No results were generated, possibly due to an early error or configuration issue.")

if __name__ == "__main__":
    main()
