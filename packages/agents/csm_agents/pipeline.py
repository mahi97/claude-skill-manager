"""Pipeline agent - orchestrates the full scout -> evaluate -> propose flow."""

from __future__ import annotations

import logging

from csm_core.evaluator import evaluate_item
from csm_core.models import EvaluationReport, Proposal
from csm_core.proposer import generate_proposals_batch
from csm_core.registry import Registry

from .scout import ScoutAgent

logger = logging.getLogger(__name__)


class PipelineAgent:
    """Orchestrates the full discovery pipeline: scout -> evaluate -> propose."""

    def __init__(self, registry: Registry):
        self.registry = registry
        self.scout = ScoutAgent(registry)

    async def run_full_pipeline(self) -> dict:
        """Run the complete pipeline and return a summary."""
        # Step 1: Scout
        logger.info("=== Phase 1: Scouting ===")
        scout_results = await self.scout.scout_all()
        total_new = sum(len(items) for items in scout_results.values())
        logger.info(f"Scouting complete: {total_new} new candidates")

        # Step 2: Evaluate all unevaluated candidates
        logger.info("=== Phase 2: Evaluating ===")
        candidates = self.registry.load_candidates()
        installed = self.registry.load_installed()
        existing_evals = {e.item_id: e for e in self.registry.load_evaluations()}

        reports: dict[str, EvaluationReport] = {}
        for candidate in candidates:
            if candidate.id not in existing_evals:
                report = evaluate_item(candidate, installed)
                self.registry.save_evaluation(report)
                reports[candidate.id] = report
                logger.info(f"  Evaluated {candidate.name}: {report.overall_score:.2f} ({report.recommendation})")
            else:
                reports[candidate.id] = existing_evals[candidate.id]

        # Step 3: Generate proposals
        logger.info("=== Phase 3: Proposing ===")
        proposals = generate_proposals_batch(candidates, reports, installed)
        for proposal in proposals:
            self.registry.save_proposal(proposal)
            logger.info(f"  Proposal: {proposal.title} [{proposal.recommendation}]")

        return {
            "scouted_sources": len(scout_results),
            "new_candidates": total_new,
            "evaluated": len(reports),
            "proposals_generated": len(proposals),
            "proposals": proposals,
        }

    def evaluate_candidates(self) -> list[EvaluationReport]:
        """Evaluate all unevaluated candidates without scouting."""
        candidates = self.registry.load_candidates()
        installed = self.registry.load_installed()
        existing_evals = {e.item_id for e in self.registry.load_evaluations()}

        reports = []
        for candidate in candidates:
            if candidate.id not in existing_evals:
                report = evaluate_item(candidate, installed)
                self.registry.save_evaluation(report)
                reports.append(report)

        return reports

    def generate_proposals(self) -> list[Proposal]:
        """Generate proposals for evaluated candidates."""
        candidates = self.registry.load_candidates()
        installed = self.registry.load_installed()
        evals = {e.item_id: e for e in self.registry.load_evaluations()}

        proposals = generate_proposals_batch(candidates, evals, installed)
        for p in proposals:
            self.registry.save_proposal(p)
        return proposals
