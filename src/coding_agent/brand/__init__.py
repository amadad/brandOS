"""Brand reporting domain models and pipelines."""

from .models import BrandReport, BrandSignal
from .pipeline import BrandReportPipeline, BrandReportResult, BrandReportToolkit, BrandTask
from .sources import (
    FileSignalsProvider,
    SignalsProvider,
    StaticSignalsProvider,
    WebPageSignalsProvider,
    GoogleNewsProvider,
)
from .summarizer import HeuristicSummarizer
from .emailer import EmailSender, InMemoryEmailSender, ResendEmailSender, build_resend_from_env
from .config import BrandProfile, get_brand_profile
from .relevance import apply_relevance_filter, RejectedSignal

__all__ = [
    "BrandReport",
    "BrandReportPipeline",
    "BrandReportResult",
    "BrandReportToolkit",
    "BrandSignal",
    "BrandTask",
    "FileSignalsProvider",
    "SignalsProvider",
    "StaticSignalsProvider",
    "WebPageSignalsProvider",
    "GoogleNewsProvider",
    "HeuristicSummarizer",
    "EmailSender",
    "InMemoryEmailSender",
    "ResendEmailSender",
    "build_resend_from_env",
    "BrandProfile",
    "get_brand_profile",
    "apply_relevance_filter",
    "RejectedSignal",
]
