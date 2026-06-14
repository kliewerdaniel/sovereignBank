"""CLI entry point for Sovereign Memory Bank."""

import argparse
import json
import uvicorn

from sovereign_memory_bank.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Sovereign Memory Bank")
    subparsers = parser.add_subparsers(dest="command")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument("--host", default=settings.api_host)
    serve_parser.add_argument("--port", type=int, default=settings.api_port)

    # init command
    subparsers.add_parser("init", help="Initialize memory bank directory structure")

    # ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents from kbmd/")
    ingest_parser.add_argument("--source", default=str(settings.kbmd_dir))
    ingest_parser.add_argument("--skip-embeddings", action="store_true", help="Skip embedding generation")

    # evolve command
    subparsers.add_parser("evolve", help="Run one evolution cycle")

    # status command
    subparsers.add_parser("status", help="Show memory bank status")

    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run(
            "sovereign_memory_bank.api.app:app",
            host=args.host,
            port=args.port,
            reload=True,
        )
    elif args.command == "init":
        from sovereign_memory_bank.layers.layer_manager import LayerManager

        lm = LayerManager(settings.memory_bank_dir)
        lm.initialize()
        print(f"Memory bank initialized at {settings.memory_bank_dir}")
    elif args.command == "ingest":
        import asyncio
        from sovereign_memory_bank.ingestion.ingester import Ingester

        result = asyncio.run(Ingester(settings, skip_embeddings=args.skip_embeddings).ingest_directory(args.source))
        print("\n--- Ingestion Complete ---")
        print(json.dumps(result, indent=2))
    elif args.command == "evolve":
        import asyncio
        from sovereign_memory_bank.evolution.engine import EvolutionEngine

        result = asyncio.run(EvolutionEngine(settings).run_cycle())
        print("\n--- Evolution Complete ---")
        print(json.dumps(result, indent=2))
    elif args.command == "status":
        _show_status()
    else:
        parser.print_help()


def _show_status():
    """Show memory bank statistics."""
    from pathlib import Path
    import json

    mb = settings.memory_bank_dir
    if not mb.exists():
        print("Memory bank not initialized. Run: smb init")
        return

    # Count files per layer
    print("=== Sovereign Memory Bank Status ===\n")
    for layer_idx in range(7):
        layer_dir = mb / f"layer-{layer_idx}"
        if layer_dir.exists():
            count = sum(1 for _ in layer_dir.rglob("*.md"))
            json_count = sum(1 for _ in layer_dir.rglob("*.json"))
            total = count + json_count
            print(f"  Layer {layer_idx}: {total} files")

    # Graph stats
    graph_path = mb / "graph.json"
    if graph_path.exists():
        data = json.loads(graph_path.read_text())
        print(f"\n  Graph: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")

    # Vector store
    vector_dir = mb / "vectors"
    if vector_dir.exists():
        print(f"  Vectors: {vector_dir}")

    print()


if __name__ == "__main__":
    main()
