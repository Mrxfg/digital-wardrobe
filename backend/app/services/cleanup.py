import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.capsule_item import CapsuleItem
from app.models.clothing_item import ClothingItem
from app.models.outfit_item import OutfitItem

TRASH_RETENTION_DAYS = 14

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def cleanup_expired_trash():
    """
    Permanently delete clothing items that have been in the trash
    for more than TRASH_RETENTION_DAYS (14 days).
    Also removes associated image files from disk.
    """
    db: Session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=TRASH_RETENTION_DAYS)

        expired_items = (
            db.query(ClothingItem)
            .filter(
                ClothingItem.is_deleted.is_(True),
                ClothingItem.deleted_at.isnot(None),
                ClothingItem.deleted_at < cutoff,
            )
            .all()
        )

        if not expired_items:
            logger.info("Trash cleanup: no expired items found")
            return

        logger.info(f"Trash cleanup: found {len(expired_items)} expired item(s)")

        for item in expired_items:
            # Delete associated photo files from disk
            _delete_item_files(item)

            # Delete junction records
            db.query(CapsuleItem).filter(CapsuleItem.clothing_item_id == item.id).delete()
            db.query(OutfitItem).filter(OutfitItem.clothing_item_id == item.id).delete()

            db.delete(item)

        db.commit()
        logger.info(f"Trash cleanup: permanently deleted {len(expired_items)} item(s)")

    except Exception as e:
        logger.error(f"Trash cleanup error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def _delete_item_files(item: ClothingItem):
    """Delete the image files associated with a clothing item from disk."""
    upload_dir = Path("uploads")

    if item.image_url:
        image_path = upload_dir / item.image_url.lstrip("/")
        _safe_unlink(image_path)

    if item.original_image_url:
        original_path = upload_dir / item.original_image_url.lstrip("/")
        _safe_unlink(original_path)


def _safe_unlink(path: Path):
    try:
        path.unlink(missing_ok=True)
    except Exception as e:
        logger.warning(f"Could not delete file {path}: {e}")


def start_scheduler():
    """Start the background scheduler with the trash cleanup job."""
    scheduler.add_job(
        cleanup_expired_trash,
        trigger="cron",
        hour=3,
        minute=0,
        id="trash_cleanup_daily",
        name="Daily trash cleanup (14-day retention)",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Trash cleanup scheduler started (runs daily at 03:00 UTC)")


def stop_scheduler():
    """Shut down the background scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Trash cleanup scheduler stopped")
