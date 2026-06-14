"""CLI entry point for Sovereign Memory Bank."""

import argparse
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

    # evolve command
    subparsers.add_parser("evolve", help="Run one evolution cycle")

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

        asyncio.run(Ingester(settings).ingest_directory(args.source))
    elif args.command == "evolve":
        import asyncio
        from sovereign_memory_bank.evolution.engine import EvolutionEngine

        asyncio.run(EvolutionEngine(settings).run_cycle())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
