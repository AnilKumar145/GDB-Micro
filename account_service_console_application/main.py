"""
Account Service Console Application

Entry point for the console-based account management system.

Built from the same architecture as the FastAPI Accounts Service.

Author: GDB Architecture Team
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings
from app.config.logging import setup_logging, get_logger
from app.database.db import initialize_db, close_db
from database.init_db import init_schema
from ui.menu import Menu

# Configure logging
logger = setup_logging()


async def init_database_async() -> None:
    """Initialize PostgreSQL database schema asynchronously."""
    try:
        logger.info(f"Initializing PostgreSQL database: {settings.database_url}")
        await init_schema(
            settings.database_url,
            settings.db_min_size,
            settings.db_max_size
        )
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise Exception(f"Failed to initialize database: {e}")


def main() -> None:
    """Main entry point."""
    try:
        logger.info("=" * 80)
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info("=" * 80)
        
        # Initialize database schema
        asyncio.run(init_database_async())
        
        # Initialize database connection pool
        logger.info("Initializing database connection pool...")
        initialize_db(
            settings.database_url,
            settings.db_min_size,
            settings.db_max_size
        )
        logger.info("Database connection pool initialized successfully")
        
        # Run menu
        logger.info("Starting interactive menu...")
        menu = Menu()
        menu.run()
        
        # Cleanup
        logger.info("Closing database connections...")
        close_db()
        logger.info(f"{settings.app_name} stopped gracefully")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        close_db()
        print("\nApplication terminated.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        close_db()
        sys.exit(1)


if __name__ == "__main__":
    main()
