"""
Analysis queue service for VerificAI Backend
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class QueueJob:
    """Job in the analysis queue"""
    id: str
    user_id: int
    name: str
    status: str
    progress: float = 0.0
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class AnalysisQueue:
    """Simple in-memory queue for analysis jobs"""

    def __init__(self):
        self.jobs: Dict[str, QueueJob] = {}
        self.queue_order: List[str] = []
        self.active_job_id: Optional[str] = None

    async def enqueue(self, analysis) -> None:
        """Add job to queue"""
        job_id = str(analysis.id)

        job = QueueJob(
            id=job_id,
            user_id=analysis.user_id,
            name=analysis.name,
            status='queued',
            progress=0.0,
            created_at=analysis.created_at
        )

        self.jobs[job_id] = job
        self.queue_order.append(job_id)

        logger.info(f"Job {job_id} added to queue")

    async def dequeue(self) -> Optional[QueueJob]:
        """Get next job from queue"""
        # Find the first queued job
        for job_id in self.queue_order:
            job = self.jobs.get(job_id)
            if job and job.status == 'queued':
                # Mark as processing
                job.status = 'processing'
                job.started_at = datetime.utcnow()
                self.active_job_id = job_id

                logger.info(f"Job {job_id} dequeued for processing")
                return job

        return None

    async def get_active_job(self) -> Optional[QueueJob]:
        """Get currently running job (single analysis at a time)"""
        if self.active_job_id and self.active_job_id in self.jobs:
            job = self.jobs[self.active_job_id]
            if job.status == 'processing':
                return job
            else:
                # Reset active job if not processing
                self.active_job_id = None

        return None

    async def get_job(self, job_id: str) -> Optional[QueueJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)

    async def update_progress(self, job_id: str, progress: float) -> None:
        """Update job progress"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.progress = max(0.0, min(100.0, progress))

    async def complete_job(self, job_id: str, result: Dict[str, Any]) -> None:
        """Mark job as completed"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = 'completed'
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            job.result = result

            # Remove from active job
            if self.active_job_id == job_id:
                self.active_job_id = None

            logger.info(f"Job {job_id} completed successfully")

    async def fail_job(self, job_id: str, error: str) -> None:
        """Mark job as failed"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = 'failed'
            job.error_message = error
            job.completed_at = datetime.utcnow()

            # Remove from active job
            if self.active_job_id == job_id:
                self.active_job_id = None

            logger.error(f"Job {job_id} failed: {error}")

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]

            # Can only cancel queued or processing jobs
            if job.status in ['queued', 'processing']:
                job.status = 'cancelled'
                job.completed_at = datetime.utcnow()

                # Remove from active job
                if self.active_job_id == job_id:
                    self.active_job_id = None

                logger.info(f"Job {job_id} cancelled")
                return True

        return False

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        total_jobs = len(self.jobs)
        queued_jobs = sum(1 for job in self.jobs.values() if job.status == 'queued')
        processing_jobs = sum(1 for job in self.jobs.values() if job.status == 'processing')
        completed_jobs = sum(1 for job in self.jobs.values() if job.status == 'completed')
        failed_jobs = sum(1 for job in self.jobs.values() if job.status == 'failed')
        cancelled_jobs = sum(1 for job in self.jobs.values() if job.status == 'cancelled')

        active_job = await self.get_active_job()

        return {
            'total_jobs': total_jobs,
            'queued_jobs': queued_jobs,
            'processing_jobs': processing_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'cancelled_jobs': cancelled_jobs,
            'active_job': asdict(active_job) if active_job else None
        }

    async def get_job_history(self, user_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get job history"""
        jobs = list(self.jobs.values())

        # Filter by user if specified
        if user_id:
            jobs = [job for job in jobs if job.user_id == user_id]

        # Sort by created_at (most recent first)
        jobs.sort(key=lambda x: x.created_at, reverse=True)

        # Limit results
        jobs = jobs[:limit]

        return [asdict(job) for job in jobs]

    async def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up old completed/failed jobs"""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        cleaned_count = 0

        jobs_to_remove = []
        for job_id, job in self.jobs.items():
            if job.status in ['completed', 'failed', 'cancelled']:
                if job.completed_at and job.completed_at.timestamp() < cutoff_time:
                    jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            if job_id in self.queue_order:
                self.queue_order.remove(job_id)
            if self.active_job_id == job_id:
                self.active_job_id = None
            cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} old jobs")
        return cleaned_count

    async def get_job_stats(self) -> Dict[str, Any]:
        """Get job statistics"""
        stats = {
            'total_jobs': len(self.jobs),
            'by_status': {},
            'by_user': {},
            'average_processing_time': 0.0,
            'success_rate': 0.0
        }

        # Count by status
        for job in self.jobs.values():
            status = job.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

        # Count by user
        for job in self.jobs.values():
            user_id = job.user_id
            stats['by_user'][user_id] = stats['by_user'].get(user_id, 0) + 1

        # Calculate average processing time and success rate
        completed_jobs = [job for job in self.jobs.values() if job.status == 'completed' and job.started_at and job.completed_at]
        if completed_jobs:
            total_time = sum((job.completed_at - job.started_at).total_seconds() for job in completed_jobs)
            stats['average_processing_time'] = total_time / len(completed_jobs)

        total_finished = len([job for job in self.jobs.values() if job.status in ['completed', 'failed']])
        if total_finished > 0:
            stats['success_rate'] = len(completed_jobs) / total_finished

        return stats

    def reset(self) -> None:
        """Reset the queue (for testing)"""
        self.jobs.clear()
        self.queue_order.clear()
        self.active_job_id = None
        logger.info("Queue reset")