from datetime import datetime, timezone

from src.config import load_settings
from src.database import (
    get_database_connection,
    initialize_database,
)
from src.extract import extract_youtube_data
from src.load import (
    load_daily_statistics,
    load_videos,
)
from src.logger import setup_logger
from src.transform import transform_videos
from src.youtube_api import YouTubeAPIClient


def main() -> None:
    """Run the complete TV Derana YouTube ETL pipeline."""

    logger = setup_logger()

    start_time = datetime.now(timezone.utc)

    logger.info("========================================")
    logger.info("TV Derana YouTube ETL started")
    logger.info("========================================")

    connection = None

    try:
        # ---------------------------------------------------------
        # 1. Load configuration
        # ---------------------------------------------------------

        settings = load_settings()

        logger.info("Configuration loaded successfully.")

        # ---------------------------------------------------------
        # 2. Extract
        # ---------------------------------------------------------

        logger.info("Starting YouTube data extraction...")

        youtube_client = YouTubeAPIClient(
            api_key=settings.youtube_api_key
        )

        raw_videos = extract_youtube_data(
            client=youtube_client,
            channel_id=settings.youtube_channel_id,
            max_videos=settings.max_videos_per_run,
        )

        logger.info(
            "Extraction completed. Videos retrieved: %d",
            len(raw_videos),
        )

        if not raw_videos:
            logger.warning("No videos were retrieved.")
            return

        # ---------------------------------------------------------
        # 3. Transform
        # ---------------------------------------------------------

        snapshot_date = datetime.now(
            timezone.utc
        ).date()

        logger.info(
            "Starting transformation. Snapshot date: %s",
            snapshot_date,
        )

        video_records, statistics_records = transform_videos(
            raw_videos=raw_videos,
            snapshot_date=snapshot_date,
        )

        logger.info(
            "Transformation completed. Valid videos: %d",
            len(video_records),
        )

        # ---------------------------------------------------------
        # 4. Connect to PostgreSQL
        # ---------------------------------------------------------

        logger.info("Connecting to PostgreSQL...")

        connection = get_database_connection(settings)

        logger.info("PostgreSQL connection successful.")

        # ---------------------------------------------------------
        # 5. Initialize database
        # ---------------------------------------------------------

        initialize_database(connection)

        logger.info("Database tables verified.")

        # ---------------------------------------------------------
        # 6. Load video metadata
        # ---------------------------------------------------------

        video_count = load_videos(
            connection,
            video_records,
        )

        logger.info(
            "Video metadata loaded: %d records",
            video_count,
        )

        # ---------------------------------------------------------
        # 7. Load daily statistics
        # ---------------------------------------------------------

        statistics_count = load_daily_statistics(
            connection,
            statistics_records,
        )

        logger.info(
            "Daily statistics loaded: %d records",
            statistics_count,
        )

        # ---------------------------------------------------------
        # 8. Finish
        # ---------------------------------------------------------

        end_time = datetime.now(timezone.utc)
        duration = end_time - start_time

        logger.info("========================================")
        logger.info(
            "ETL completed successfully in %s",
            duration,
        )
        logger.info("========================================")

    except Exception:
        logger.exception("ETL process failed.")
        raise

    finally:
        if connection is not None:
            connection.close()
            logger.info("PostgreSQL connection closed.")


if __name__ == "__main__":
    main()