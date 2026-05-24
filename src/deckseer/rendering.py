from __future__ import annotations

import json

from deckseer.audit.card_priors import CardPriorAuditResult
from deckseer.models import RecommendationResult


def render_recommendation(result: RecommendationResult, output_format: str, *, diagnosis: dict | None = None) -> str:
    if output_format == "json":
        if diagnosis is None:
            return json.dumps(result.to_dict(), indent=2)
        return json.dumps({"diagnosis": diagnosis, "recommendation": result.to_dict()}, indent=2)
    if output_format == "markdown":
        return _render_markdown_result(result, diagnosis=diagnosis)
    return _render_text_result(result, diagnosis=diagnosis)


def render_card_catalog(catalog: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(catalog, indent=2)

    lines = [f"Cards ({catalog['count']})"]
    for card in catalog["cards"]:
        roles = ", ".join(card["roles"]) if card["roles"] else "no roles"
        lines.append(f"{card['id']} - {card['name']} [{card['character']}, {card['type']}, {card['rarity']}, cost {card['cost']}]")
        lines.append(f"   Roles: {roles}")
    return "\n".join(lines)


def render_card_prior_audit(result: CardPriorAuditResult, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2)

    summary = result.to_dict()["summary"]
    flagged_rows = [row for row in result.rows if row.flags]
    lines = [
        "Card Prior Audit",
        f"Source: {result.empirical_source}",
        f"Rows: {summary['rows']} | Flagged: {summary['flagged_rows']} | Flags: {summary['flags']}",
    ]
    if summary["flags_by_code"]:
        lines.append("Flags by code:")
        for code, count in summary["flags_by_code"].items():
            lines.append(f"   {code}: {count}")
    if summary["flags_by_severity"]:
        lines.append("Flags by severity:")
        for severity, count in summary["flags_by_severity"].items():
            lines.append(f"   {severity}: {count}")
    if summary["flagged_rows_by_character"]:
        lines.append("Flagged rows by character:")
        for character, count in summary["flagged_rows_by_character"].items():
            lines.append(f"   {character}: {count}")
    if not result.rows:
        return "\n".join(lines)

    lines.append("Flagged rows:")
    if not flagged_rows:
        lines.append("   none")
    for row in flagged_rows:
        prior = "unknown" if row.quality_prior is None else f"{row.quality_prior:.1f}"
        impact = "unknown" if row.empirical_impact is None else f"{row.empirical_impact:.2f}"
        sample_size = "unknown" if row.sample_size is None else str(row.sample_size)
        lines.append(f"   {row.card_id} - {row.name} [{row.character}, prior {prior}, impact {impact}, n={sample_size}, patch {row.patch or 'unknown'}]")
        for flag in row.flags:
            lines.append(f"      {flag.severity}: {flag.code} - {flag.message}")

    clean_rows = [row for row in result.rows if not row.flags]
    if clean_rows:
        clean_ids = ", ".join(row.card_id for row in clean_rows)
        lines.append(f"Clean rows: {clean_ids}")
    return "\n".join(lines)


def render_empirical_coverage(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    coverage = report["coverage"]
    lines = [
        f"Empirical Coverage: {report['status'].upper()}",
        f"Files: {summary['loaded_files']}/{summary['files']} loaded | Rows: {summary['rows']} | Flags: {summary['flags']}",
        f"Character target: {coverage['min_rows_per_character']} row(s) each",
    ]
    if coverage["rows_by_character"]:
        lines.append(f"Rows by character: {_format_counts(coverage['rows_by_character'])}")
    if coverage["rows_by_patch"]:
        lines.append(f"Rows by patch: {_format_counts(coverage['rows_by_patch'])}")
    if coverage["rows_by_review_status"]:
        lines.append(f"Rows by review status: {_format_counts(coverage['rows_by_review_status'])}")
    if coverage["traceable_rows_by_character"]:
        lines.append(f"Traceable rows by character: {_format_counts(coverage['traceable_rows_by_character'])}")
    if coverage["provenance_gaps"]:
        lines.append(f"Provenance gaps: {_format_counts(coverage['provenance_gaps'])}")
    if coverage["characters_below_minimum"]:
        lines.append(f"Characters below target: {_format_counts(coverage['characters_below_minimum'])}")
    else:
        lines.append("Characters below target: none")
    if coverage["missing_traceable_catalog_characters"]:
        lines.append(f"Characters without traceable rows: {', '.join(coverage['missing_traceable_catalog_characters'])}")
    if summary["flags_by_severity"]:
        lines.append(f"Flag severity: {_format_counts(summary['flags_by_severity'])}")
    if summary["flags_by_code"]:
        lines.append(f"Flag codes: {_format_counts(summary['flags_by_code'])}")
    if report["errors"]:
        lines.append("Errors:")
        for error in report["errors"]:
            lines.append(f"   {error['path']}: {error['message']}")
    if coverage["covered_card_ids"]:
        lines.append(f"Covered cards: {', '.join(coverage['covered_card_ids'])}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_intake(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        f"Empirical Intake: {report['status'].upper()}",
        f"Entries: {summary['entries']} | Proposed: {summary['proposed']} | Rejected: {summary['rejected']}",
    ]
    if summary["entries_by_character"]:
        lines.append(f"Entries by character: {_format_counts(summary['entries_by_character'])}")
    if summary["entries_by_review_status"]:
        lines.append(f"Entries by status: {_format_counts(summary['entries_by_review_status'])}")
    if report["entries"]:
        lines.append("Intake entries:")
        for entry in report["entries"]:
            card_id = entry["card_id"] or "class-level"
            lines.append(f"   {entry['id']}: {entry['character']} {card_id} [{entry['review_status']}]")
            lines.append(f"      {entry['candidate_notes']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_triage(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        f"Empirical Triage: {report['status'].upper()}",
        f"Active flags: {summary['active_flags']} | Triaged: {summary['triaged_flags']} | Resolved: {summary['resolved_active_flags']} | Unresolved: {summary['unresolved_active_flags']} | Missing: {summary['missing_triage_entries']} | Stale: {summary['stale_triage_entries']} | Open: {summary['open_triage_entries']}",
    ]
    if summary["statuses_by_active_flag"]:
        lines.append(f"Active triage statuses: {_format_counts(summary['statuses_by_active_flag'])}")
    if summary["unresolved_statuses_by_active_flag"]:
        lines.append(f"Unresolved triage statuses: {_format_counts(summary['unresolved_statuses_by_active_flag'])}")
    if summary["flags_by_code"]:
        lines.append(f"Flags by code: {_format_counts(summary['flags_by_code'])}")
    if summary["flags_by_card"]:
        lines.append(f"Flags by card: {_format_counts(summary['flags_by_card'])}")
    if summary["next_actions"]:
        lines.append("Next actions:")
        for action, count in summary["next_actions"].items():
            lines.append(f"   {action} ({count})")
    if report["matched_flags"]:
        lines.append("Triaged active flags:")
        for row in report["matched_flags"]:
            triage = row["triage"]
            lines.append(f"   {row['card_id']} - {row['card_name']} [{row['flag_code']}, {triage['status']}]")
            lines.append(f"      {triage['next_action']}")
    if report["missing_triage"]:
        lines.append("Missing triage:")
        for row in report["missing_triage"]:
            lines.append(f"   {row['card_id']} [{row['flag_code']}] from {row['empirical_file']}")
    if report["stale_triage"]:
        lines.append("Stale triage:")
        for row in report["stale_triage"]:
            lines.append(f"   {row['id']}: {row['card_id']} [{row['flag_code']}]")
    for error in report.get("audit_errors", []):
        lines.append(f"Error: {error['path']}: {error['message']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_current_patch_review(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    ready = "yes" if summary["ready_for_draft_check"] else "no"
    forbidden = "blocked" if summary["forbidden_grimoire_blocked"] else "ready for promotion review"
    lines = [
        f"Empirical Current-Patch Review: {report['status'].upper()}",
        f"Worksheet: {report['path']}",
        f"Entries: {summary['entries']} | Complete: {summary['complete_entries']} | Incomplete: {summary['incomplete_entries']} | Ready for draft check: {ready}",
        f"Null fields: {summary['total_null_fields']} | Missing fields: {summary['total_missing_fields']}",
        f"Triage cards covered: {', '.join(summary['triage_cards_covered']) if summary['triage_cards_covered'] else 'none'}",
        f"Forbidden Grimoire prior-change status: {forbidden}",
    ]
    if summary["blocked_all_patches_rows"]:
        lines.append(f"All Patches rows blocked: {summary['blocked_all_patches_rows']}")
    if summary["audit_preview_ran"]:
        lines.append(f"Audit preview: ran | Flags: {summary['audit_flags']}")
    else:
        lines.append("Audit preview: not run")
    if summary["strict_validation_error"]:
        lines.append(f"Strict validation error: {summary['strict_validation_error']}")
    if summary["resolution_statuses"]:
        lines.append(f"Row statuses: {_format_counts(summary['resolution_statuses'])}")
    lines.append("Rows:")
    for row in report["rows"]:
        lines.append(f"   {row['id']}: {row['card_id']} [{row['resolution_status']}]")
        if row["patch"]:
            lines.append(f"      Patch: {row['patch']}")
        if row["null_fields"]:
            lines.append(f"      Null fields: {', '.join(row['null_fields'])}")
        if row["missing_fields"]:
            lines.append(f"      Missing fields: {', '.join(row['missing_fields'])}")
    if report["triage_matches"]:
        lines.append("Triage matches:")
        for entry in report["triage_matches"]:
            lines.append(f"   {entry['card_id']} [{entry['flag_code']}, {entry['status']}]")
            lines.append(f"      {entry['next_action']}")
    lines.append("Next commands: empirical-draft-check, then empirical-promote-draft preview")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_capture_guide(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["worksheet_summary"]
    lines = [
        f"Empirical Capture Guide: {report['character']} [{report['status'].upper()}]",
        f"Source target: {report['source_target']}",
        f"Worksheet: {report['worksheet_path']}",
        f"Entries: {summary['entries']} | Complete: {summary['complete_entries']} | Incomplete: {summary['incomplete_entries']}",
        f"Required values: {', '.join(report['required_values'])}",
        f"Safety flow: {' -> '.join(report['safety_flow'])}",
        "Rows:",
    ]
    for row in report["rows"]:
        status = "complete" if row["is_complete"] else "incomplete"
        lines.append(f"   {row['entry_id']}: {row['card_id']} [{status}]")
        if row["null_fields"]:
            lines.append(f"      Null fields: {', '.join(row['null_fields'])}")
        if row["missing_fields"]:
            lines.append(f"      Missing fields: {', '.join(row['missing_fields'])}")
        lines.append(f"      Preview: {row['preview_command']}")
        lines.append(f"      Write: {row['write_command']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_capture_packet(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    lines = [
        "Empirical Capture Packet",
        f"Source target: {report['source_target']}",
        f"Worksheet: {report['worksheet_path']}",
        f"Required fields: {', '.join(report['required_fields'])}",
        "Entries:",
    ]
    for entry in report["entries"]:
        lines.append(f"   {entry['entry_id']}: {entry['card_id']}")
        for field in report["required_fields"]:
            lines.append(f"      {field}: {entry[field] if entry[field] is not None else '<fill>'}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_capture_packet_apply(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["worksheet_report"]["summary"]
    ready = "yes" if summary["ready_for_draft_check"] else "no"
    wrote = "yes" if report["wrote_file"] else "no"
    mode = "write" if report["write_requested"] else "preview"
    lines = [
        f"Empirical Packet Apply: {report['status'].upper()}",
        f"Mode: {mode} | Wrote file: {wrote}",
        f"Packet: {report['packet_path']}",
        f"Worksheet: {report['worksheet_path']}",
        f"Rows updated: {len(report['updated_rows'])}",
        f"Entries: {summary['entries']} | Complete: {summary['complete_entries']} | Incomplete: {summary['incomplete_entries']} | Ready for draft check: {ready}",
        f"Remaining null fields: {summary['total_null_fields']} | Missing fields: {summary['total_missing_fields']}",
    ]
    for row in report["updated_rows"]:
        lines.append(f"   {row['entry_id']}: {row['card_id']} -> {', '.join(row['updated_fields'])}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_cross_class_capture_packet(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        "Empirical Cross-Class Capture Packet",
        f"Source target: {report['source_target']}",
        f"Groups: {summary['groups']} | Entries: {summary['entries']}",
        f"Required fields: {', '.join(report['required_fields'])}",
    ]
    for group in report["groups"]:
        lines.append(f"{group['character']}: {group['worksheet_path']}")
        for entry in group["entries"]:
            lines.append(f"   {entry['entry_id']}: {entry['card_id']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_cross_class_capture_packet_apply(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    wrote = "yes" if report["wrote_files"] else "no"
    mode = "write" if report["write_requested"] else "preview"
    lines = [
        f"Empirical Cross-Class Packet Apply: {report['status'].upper()}",
        f"Mode: {mode} | Wrote files: {wrote}",
        f"Packet: {report['packet_path']}",
        (
            f"Groups: {summary['groups']} | Updated rows: {summary['updated_rows']} | "
            f"Ready groups: {summary['ready_groups']} | Incomplete groups: {summary['incomplete_groups']}"
        ),
        (
            f"Remaining null fields: {summary['remaining_null_fields']} | "
            f"Missing fields: {summary['remaining_missing_fields']}"
        ),
    ]
    for group in report["groups"]:
        worksheet_summary = group["worksheet_report"]["summary"]
        ready = "yes" if worksheet_summary["ready_for_draft_check"] else "no"
        lines.append(f"{group['character']}: {group['worksheet_path']}")
        lines.append(
            (
                f"   Rows updated: {len(group['updated_rows'])} | Ready for draft check: {ready} | "
                f"Remaining null fields: {worksheet_summary['total_null_fields']}"
            )
        )
        for row in group["updated_rows"]:
            lines.append(f"   {row['entry_id']}: {row['card_id']} -> {', '.join(row['updated_fields'])}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_cross_class_readiness(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        f"Empirical Cross-Class Readiness: {report['status'].upper()}",
        (
            f"Worksheets: {summary['worksheets']} | Complete: {summary['complete_worksheets']} | "
            f"Incomplete: {summary['incomplete_worksheets']} | Audit flags: {summary['audit_flags']}"
        ),
        (
            f"Remaining null fields: {summary['remaining_null_fields']} | "
            f"Missing fields: {summary['remaining_missing_fields']}"
        ),
    ]
    for worksheet in report["worksheets"]:
        ready = "yes" if worksheet["ready_for_draft_check"] else "no"
        lines.append(
            (
                f"{worksheet['character']}: {worksheet['status'].upper()} | "
                f"null fields: {worksheet['remaining_null_fields']} | "
                f"missing fields: {worksheet['remaining_missing_fields']} | ready: {ready} | "
                f"audit flags: {worksheet['audit_flags']}"
            )
        )
        lines.append(f"   Next: {worksheet['next_command']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_cross_class_promotion_preview(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        f"Empirical Cross-Class Promotion Preview: {report['status'].upper()}",
        (
            f"Worksheets: {summary['worksheets']} | Blocked: {summary['blocked_worksheets']} | "
            f"Promotion ready: {summary['promotion_ready']} | Review needed: {summary['review_needed']} | "
            f"Audit flags: {summary['audit_flags']}"
        ),
    ]
    for preview in report["previews"]:
        line = (
            f"{preview['character']}: {preview['status'].upper()} | "
            f"null fields: {preview['remaining_null_fields']} | "
            f"output: {preview['output_path']}"
        )
        if preview["audit_flags"]:
            line = f"{line} | audit flags: {preview['audit_flags']}"
        if preview["allow_review_flags_needed"]:
            line = f"{line} | needs --allow-review-flags"
        if preview["output_exists"]:
            line = f"{line} | output exists"
        lines.append(line)
        lines.append(f"   Next: {preview['next_command']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_draft(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    ready = "yes" if summary["promotion_ready"] else "no"
    lines = [
        f"Empirical Draft: {report['status'].upper()}",
        f"Entries: {summary['entries']} | Audit flags: {summary['audit_flags']} | Promotion ready: {ready}",
    ]
    if summary["rows_by_character"]:
        lines.append(f"Rows by character: {_format_counts(summary['rows_by_character'])}")
    if summary["rows_by_review_status"]:
        lines.append(f"Rows by review status: {_format_counts(summary['rows_by_review_status'])}")

    audit_summary = report["audit_preview"]["summary"]
    if audit_summary["flags_by_severity"]:
        lines.append(f"Flag severity: {_format_counts(audit_summary['flags_by_severity'])}")
    if audit_summary["flags_by_code"]:
        lines.append(f"Flag codes: {_format_counts(audit_summary['flags_by_code'])}")
    flagged_rows = [row for row in report["audit_preview"]["rows"] if row["flags"]]
    if flagged_rows:
        lines.append("Flagged rows:")
        for row in flagged_rows:
            lines.append(f"   {row['card_id']} [{row['character']}]")
            for flag in row["flags"]:
                lines.append(f"      {flag['severity']}: {flag['code']} - {flag['message']}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_worksheet(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    ready = "yes" if summary["ready_for_draft_check"] else "no"
    lines = [
        f"Empirical Worksheet: {report['status'].upper()}",
        f"Entries: {summary['entries']} | Complete: {summary['complete_entries']} | Incomplete: {summary['incomplete_entries']} | Ready for draft check: {ready}",
        f"Null fields: {summary['total_null_fields']} | Missing fields: {summary['total_missing_fields']}",
    ]
    if summary["rows_by_character"]:
        lines.append(f"Rows by character: {_format_counts(summary['rows_by_character'])}")
    incomplete_entries = [entry for entry in report["entries"] if not entry["is_complete"]]
    if incomplete_entries:
        lines.append("Incomplete entries:")
        for entry in incomplete_entries:
            label = entry["id"] or f"entry[{entry['index']}]"
            card_id = entry["card_id"] or "unknown_card"
            lines.append(f"   {label}: {card_id}")
            if entry["null_fields"]:
                lines.append(f"      Null fields: {', '.join(entry['null_fields'])}")
            if entry["missing_fields"]:
                lines.append(f"      Missing fields: {', '.join(entry['missing_fields'])}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_worksheet_fill(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["worksheet_report"]["summary"]
    ready = "yes" if summary["ready_for_draft_check"] else "no"
    wrote = "yes" if report["wrote_file"] else "no"
    mode = "write" if report["write_requested"] else "preview"
    updated = ", ".join(report["updated_fields"]) if report["updated_fields"] else "none"
    lines = [
        f"Empirical Worksheet Fill: {report['status'].upper()}",
        f"Mode: {mode} | Wrote file: {wrote}",
        f"Entry: {report['updated_entry_id']}",
        f"Updated fields: {updated}",
        f"Entries: {summary['entries']} | Complete: {summary['complete_entries']} | Incomplete: {summary['incomplete_entries']} | Ready for draft check: {ready}",
        f"Remaining null fields: {summary['total_null_fields']} | Missing fields: {summary['total_missing_fields']}",
    ]
    incomplete_entries = [entry for entry in report["worksheet_report"]["entries"] if entry["id"] == report["updated_entry_id"] and not entry["is_complete"]]
    for entry in incomplete_entries:
        if entry["null_fields"]:
            lines.append(f"Entry null fields: {', '.join(entry['null_fields'])}")
        if entry["missing_fields"]:
            lines.append(f"Entry missing fields: {', '.join(entry['missing_fields'])}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_empirical_promotion(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    ready = "yes" if summary["promotion_ready"] else "no"
    wrote = "yes" if report["wrote_file"] else "no"
    mode = "write" if report["write_requested"] else "preview"
    review_flags = "allowed" if report.get("allow_review_flags") else "blocked"
    lines = [
        f"Empirical Promotion: {report['status'].upper()}",
        f"Mode: {mode} | Wrote file: {wrote} | Review flags: {review_flags}",
        f"Output: {report['output_path']}",
        f"Entries: {summary['entries']} | Audit flags: {summary['audit_flags']} | Promotion ready: {ready}",
    ]
    if report["payload"]:
        lines.append("Active empirical payload:")
        lines.append(json.dumps(report["payload"], indent=2))
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_accuracy_report(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        f"Accuracy Report: {report['status'].upper()}",
        f"Scenarios: {summary['scenarios']} | Passed: {summary['passed']} | Failed: {summary['failed']}",
    ]
    if summary["review_status_counts"]:
        lines.append(f"Review statuses: {_format_counts(summary['review_status_counts'])}")
    for scenario in report["scenarios"]:
        status = "PASS" if scenario["passed"] else "FAIL"
        actual = scenario["actual_top_choice"] or "none"
        score = "unknown" if scenario["actual_top_score"] is None else f"{scenario['actual_top_score']:.1f}"
        confidence = scenario["actual_confidence"] or "unknown"
        lines.append(
            f"{status} {scenario['id']}: expected {scenario['expected_top_choice']}, got {actual} ({score}, {confidence})"
        )
        if scenario["missing_reason_keywords"]:
            lines.append(f"   Missing reason keywords: {', '.join(scenario['missing_reason_keywords'])}")
        if scenario["error"]:
            lines.append(f"   Error: {scenario['error']}")
    return "\n".join(lines)


def render_project_qa(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    summary = report["summary"]
    lines = [
        f"Project QA: {report['status'].upper()}",
        f"Data health: {summary['data_health_status']} ({summary['data_health_failures']} failures)",
        f"Run files: {summary['run_files']} | Blocked: {summary['run_blocked_files']} | Deck metadata gaps: {summary['run_files_with_deck_metadata_gaps']}",
        f"Recommendation smoke: {summary['recommendation_smoke_passed']} passed | {summary['recommendation_smoke_failed']} failed",
        f"Recommendation baseline: {'checked' if summary['recommendation_baseline_checked'] else 'not checked'} | Mismatches: {summary['recommendation_baseline_mismatches']}",
        f"Empirical audits: {summary['empirical_audits']} | Flags: {summary['empirical_flags']}",
    ]
    if summary["empirical_coverage_checked"]:
        lines.append(
            f"Empirical coverage: {summary['empirical_coverage_status']} | Rows: {summary['empirical_coverage_rows']} | Missing characters: {summary['empirical_coverage_missing_characters']}"
        )
    if summary["empirical_triage_checked"]:
        lines.append(
            f"Empirical triage: {summary['empirical_triage_status']} | Active flags: {summary['empirical_triage_active_flags']} | Triaged: {summary['empirical_triage_triaged_flags']} | Missing: {summary['empirical_triage_missing_entries']} | Open: {summary['empirical_triage_open_entries']}"
        )
    if summary["accuracy_checked"]:
        lines.append(
            f"Accuracy scenarios: {summary['accuracy_passed']} passed | {summary['accuracy_failed']} failed"
        )
    if summary["empirical_flags_by_severity"]:
        lines.append(f"Empirical flag severity: {_format_counts(summary['empirical_flags_by_severity'])}")
    if summary["empirical_flags_by_code"]:
        lines.append(f"Empirical flag codes: {_format_counts(summary['empirical_flags_by_code'])}")
    failed_smokes = [check for check in report["recommendation_smoke"]["checks"] if not check["passed"]]
    if failed_smokes:
        lines.append("Recommendation smoke failures:")
        for check in failed_smokes:
            lines.append(f"   {check['path']}: {check['error']}")
    passed_smokes = [check for check in report["recommendation_smoke"]["checks"] if check["passed"]]
    if passed_smokes:
        lines.append("Recommendation smoke top choices:")
        for check in passed_smokes:
            lines.append(
                f"   {check['path']}: {check['top_choice']} ({check['top_score']:.1f}, {check['confidence']})"
            )
    baseline_mismatches = report["recommendation_baseline"]["mismatches"]
    if baseline_mismatches:
        lines.append("Recommendation baseline mismatches:")
        for mismatch in baseline_mismatches:
            lines.append(
                f"   {mismatch['path']}: expected {mismatch['expected_top_choice']}, got {mismatch['actual_top_choice'] or 'none'}"
            )
    if report["empirical_audits"]:
        lines.append("Empirical audit files:")
        for audit in report["empirical_audits"]:
            audit_summary = audit["summary"]
            lines.append(
                f"   {audit['empirical_source']}: {audit_summary['flagged_rows']} flagged rows, {audit_summary['flags']} flags"
            )
            if audit_summary["flags_by_severity"]:
                lines.append(f"      Severity: {_format_counts(audit_summary['flags_by_severity'])}")
            if audit_summary["flags_by_code"]:
                lines.append(f"      Codes: {_format_counts(audit_summary['flags_by_code'])}")
    accuracy_report = report.get("accuracy_report")
    if accuracy_report is not None:
        failed_accuracy = [scenario for scenario in accuracy_report["scenarios"] if not scenario["passed"]]
        if failed_accuracy:
            lines.append("Accuracy scenario mismatches:")
            for scenario in failed_accuracy:
                actual = scenario["actual_top_choice"] or "none"
                lines.append(f"   {scenario['id']}: expected {scenario['expected_top_choice']}, got {actual}")
    empirical_coverage = report.get("empirical_coverage")
    if empirical_coverage is not None:
        coverage = empirical_coverage["coverage"]
        if coverage["characters_below_minimum"]:
            lines.append(f"Empirical coverage below target: {_format_counts(coverage['characters_below_minimum'])}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_exporter_toolchain_preflight(report: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2)

    checks = report["checks"]
    release = checks["release_info"]
    manifest = checks["steam_manifest"]
    dotnet = checks["dotnet_sdk"]
    template = checks["sts2_template"]
    megadot = checks["megadot"]
    godot = checks["godot"]
    summary = report["summary"]
    release_label = release.get("version") or "unknown"
    build_label = manifest.get("buildid") or "unknown"
    branch_label = manifest.get("branch") or release.get("branch") or "unknown"
    sdk_label = ", ".join(dotnet.get("sdk_versions") or []) if dotnet["ok"] else "missing"
    engine_paths = [check["path"] for check in (megadot, godot) if check["ok"]]
    engine_label = ", ".join(engine_paths) if engine_paths else "missing"

    lines = [
        f"Exporter Toolchain Preflight: {report['status'].upper()}",
        f"STS2 install: {_ok_label(checks['sts2_install']['ok'])} ({checks['sts2_install']['path']})",
        f"Release: {release_label} | Build: {build_label} | Branch: {branch_label}",
        f".NET SDK: {sdk_label}",
        f"STS2 template: {_ok_label(template['ok'])}",
        f"Megadot/Godot: {engine_label}",
        f"Mods folder: {_ok_label(checks['mods_folder']['ok'])} ({checks['mods_folder']['path']})",
        f"Deckseer export folder: {_ok_label(checks['deckseer_export_folder']['ok'])} ({checks['deckseer_export_folder']['path']})",
    ]
    lines.append(f"Blockers: {', '.join(summary['blockers']) if summary['blockers'] else 'none'}")
    lines.append(f"Warnings: {', '.join(summary['warnings']) if summary['warnings'] else 'none'}")
    for caveat in report.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_data_summary(summary: dict, output_format: str, *, show_gap_ids: bool = False, max_gap_ids: int = 12) -> str:
    if output_format == "json":
        return json.dumps(summary, indent=2)

    lines = [
        "Data Summary",
        f"Cards: {summary['totals']['cards']} | Characters: {summary['totals']['characters']} | Relics: {summary['totals']['relics']} | Potions: {summary['totals']['potions']}",
    ]
    if summary.get("filters", {}).get("character") is not None:
        lines.append(f"Filter: character={summary['filters']['character']}")
    lines.append("Cards by character:")
    for character, count in summary["cards_by_character"].items():
        lines.append(f"   {character}: {count}")
    lines.append("Source patches:")
    for patch, count in summary["source_patches"].items():
        lines.append(f"   {patch}: {count}")
    lines.append("Metadata gaps:")
    for gap_name, gap in summary["metadata_gaps"].items():
        lines.extend(_render_counted_ids(gap_name, gap, show_ids=show_gap_ids, max_ids=max_gap_ids))
    lines.append("Review flags:")
    for flag_name, flag in summary["review_flags"].items():
        lines.extend(_render_counted_ids(flag_name, flag, show_ids=show_gap_ids, max_ids=max_gap_ids))
    lines.append("Top roles:")
    for role, count in list(summary["roles"].items())[:10]:
        lines.append(f"   {role}: {count}")
    for caveat in summary.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_data_health(health: dict, output_format: str, *, max_ids: int = 12) -> str:
    if output_format == "json":
        return json.dumps(health, indent=2)

    lines = [
        f"Data Health: {health['status'].upper()}",
        f"Failures: {health['failure_count']}",
    ]
    if health.get("filters", {}).get("character") is not None:
        lines.append(f"Filter: character={health['filters']['character']}")

    failures = health["failures"]
    if failures:
        lines.append("Blocking failures:")
        for section_name, section in failures.items():
            lines.append(f"   {section_name}:")
            if "count" in section:
                lines.extend(_render_counted_ids("value", section, show_ids=True, max_ids=max_ids))
                continue
            for item_name, item in section.items():
                lines.extend(_render_counted_ids(item_name, item, show_ids=True, max_ids=max_ids))
    else:
        lines.append("Blocking failures: none")

    ignored_flags = health.get("ignored_review_flags", {})
    if ignored_flags:
        lines.append("Ignored review flags:")
        for flag_name, flag in ignored_flags.items():
            lines.extend(_render_counted_ids(flag_name, flag, show_ids=False, max_ids=max_ids))
    for caveat in health.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def render_data_review(review: dict, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(review, indent=2)

    lines = [
        "Data Review",
        f"Cards: {review['totals']['cards']} | Flags: {review['totals']['flags']}",
    ]
    filters = review.get("filters", {})
    active_filters = [f"{key}={value}" for key, value in filters.items() if value is not None]
    if active_filters:
        lines.append(f"Filters: {', '.join(active_filters)}")
    for flag_name, cards in review["review_flags"].items():
        lines.append(f"{flag_name} ({len(cards)})")
        if not cards:
            lines.append("   none")
            continue
        for card in cards:
            roles = ", ".join(card["roles"]) if card["roles"] else "no roles"
            notes = "; ".join(card["source_notes"]) if card["source_notes"] else "no source notes"
            lines.append(
                f"   {card['id']} - {card['name']} [{card['character']}, {card['type']}, {card['rarity']}, cost {card['cost']}, prior {card['quality_prior']:.1f}]"
            )
            lines.append(f"      Patch: {card['source_patch'] or 'unspecified'} | Roles: {roles}")
            lines.append(f"      Notes: {notes}")
    for caveat in review.get("caveats", []):
        lines.append(f"Caveat: {caveat}")
    return "\n".join(lines)


def _render_counted_ids(name: str, item: dict, *, show_ids: bool, max_ids: int) -> list[str]:
    lines = [f"   {name}: {item['count']}"]
    if show_ids and item["ids"]:
        visible_ids = item["ids"][:max(0, max_ids)]
        suffix = "" if len(visible_ids) == len(item["ids"]) else f" ... +{len(item['ids']) - len(visible_ids)} more"
        lines.append(f"      ids: {', '.join(visible_ids)}{suffix}")
    return lines


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{name}={count}" for name, count in counts.items())


def _ok_label(ok: bool) -> str:
    return "ok" if ok else "missing"


def _render_text_result(result: RecommendationResult, *, diagnosis: dict | None = None) -> str:
    lines: list[str] = []
    if diagnosis is not None:
        lines.extend(_render_text_diagnosis(diagnosis))
        lines.append("")

    lines.append(result.recommendation_type.replace("_", " ").title())
    for choice in result.ranked_choices:
        lines.append(f"{choice.rank}. {choice.name} ({choice.choice}) - {choice.score:.1f} [{choice.confidence}]")
        lines.append(f"   Why: {' '.join(choice.reasoning)}")
        lines.append(f"   Risks: {' '.join(choice.risks)}")
    return "\n".join(lines)


def _render_markdown_result(result: RecommendationResult, *, diagnosis: dict | None = None) -> str:
    lines: list[str] = []
    if diagnosis is not None:
        profile = diagnosis["deck_profile"]
        hp = diagnosis["hp"]
        needs = diagnosis["prioritized_needs"][:3]
        need_summary = ", ".join(f"{need['name']} {need['priority']:.1f}" for need in needs) if needs else "none"
        lines.extend(
            [
                "## Run Diagnosis",
                "",
                f"- Phase: `{profile['phase']}`",
                f"- Deck size: `{profile['size']}`",
                f"- HP: `{hp['current']}/{hp['max']}`",
                f"- Top needs: {need_summary}",
            ]
        )
        for caveat in diagnosis.get("caveats", []):
            lines.append(f"- Caveat: {caveat}")
        lines.append("")

    title = f"{result.recommendation_type.replace('_', ' ').title()} Recommendation"
    lines.extend([f"## {title}", "", "| Rank | Choice | Score | Confidence |", "| ---: | --- | ---: | --- |"])
    for choice in result.ranked_choices:
        lines.append(f"| {choice.rank} | {choice.name} (`{choice.choice}`) | {choice.score:.1f} | {choice.confidence} |")
    lines.append("")
    for choice in result.ranked_choices:
        lines.extend(
            [
                f"### {choice.rank}. {choice.name}",
                "",
                f"- ID: `{choice.choice}`",
                f"- Score: `{choice.score:.1f}`",
                f"- Why: {' '.join(choice.reasoning)}",
                f"- Risks: {' '.join(choice.risks)}",
                "",
            ]
        )
    return "\n".join(lines)


def _render_text_diagnosis(diagnosis: dict) -> list[str]:
    profile = diagnosis["deck_profile"]
    hp = diagnosis["hp"]
    needs = diagnosis["prioritized_needs"][:3]
    need_summary = ", ".join(f"{need['name']} {need['priority']:.1f}" for need in needs) if needs else "none"
    lines = [
        "Run Diagnosis",
        f"   Phase: {profile['phase']} | Deck size: {profile['size']} | HP: {hp['current']}/{hp['max']}",
        f"   Top needs: {need_summary}",
    ]
    for caveat in diagnosis.get("caveats", []):
        lines.append(f"   Caveat: {caveat}")
    return lines
