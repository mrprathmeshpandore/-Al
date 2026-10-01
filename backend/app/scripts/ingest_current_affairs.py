import argparse
import sys
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.services.current_affairs import (
    CurrentAffairsIngestionService,
    ManualCurrentAffairsSource,
    CurrentAffairCandidate,
)


def run_ingestion():
    parser = argparse.ArgumentParser(description="Prashasak AI Current Affairs Ingestion CLI")
    parser.add_argument("--source", type=str, default="manual", help="Source type: manual or feed")
    parser.add_argument("--limit", type=int, default=20, help="Max items to fetch")
    args = parser.parse_args()

    print(f"Starting Prashasak AI Current Affairs Ingestion (Source: {args.source}, Limit: {args.limit})...")

    db = SessionLocal()
    try:
        service = CurrentAffairsIngestionService(db=db)

        # Sample official government releases candidate for manual ingestion test
        sample_candidates = [
            CurrentAffairCandidate(
                title="Union Cabinet Approves National AI Governance Framework for Public Service Delivery",
                source_name="Press Information Bureau (PIB)",
                source_url="https://pib.gov.in/PressReleasePage.aspx?PRID=20260901",
                content="The Union Cabinet chaired by the Prime Minister has approved the comprehensive National Artificial Intelligence Governance Framework to streamline digital public service delivery, ensure ethical data utilization, and establish administrative accountability across government departments.",
                published_at=datetime.now(timezone.utc),
                category="GOVERNANCE",
                topic="AI in Public Administration",
                subtopic="Digital India & E-Governance",
            ),
            CurrentAffairCandidate(
                title="Supreme Court Issues Directives on Environmental Impact Assessment in Ecological Fragile Zones",
                source_name="Supreme Court of India Official Portal",
                source_url="https://main.sci.gov.in/judgments/2026/eia_order.pdf",
                content="A three-judge bench of the Supreme Court of India issued binding directives mandating rigorous cumulative environmental impact assessment prior to approving infrastructure developments in ecologically sensitive regions.",
                published_at=datetime.now(timezone.utc),
                category="ENVIRONMENT",
                topic="Environmental Governance & Judiciary",
                subtopic="Ecological Conservation",
            )
        ]

        source = ManualCurrentAffairsSource(candidates=sample_candidates, source_name="Official Ingestion CLI")
        results = service.ingest_source(source=source, limit=args.limit)

        print(f"Successfully processed {len(results)} current affair items:")
        for affair in results:
            print(f"  - [{affair.category}] {affair.title} (Status: {affair.analysis_status}, ID: {affair.id})")

    except Exception as e:
        print(f"Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_ingestion()
