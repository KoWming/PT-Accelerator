from datetime import datetime

from app.services.cfst_service import CfstService
from app.pipelines.hosts_pipeline import HostsPipeline


def test_retries_only_for_strict_non_debug_speed_filter():
    base = {"min_speed": 2, "debug": False, "empty_result_retries": 3}
    assert CfstService._empty_result_retry_count(base) == 3
    assert CfstService._empty_result_retry_count({**base, "debug": True}) == 0
    assert CfstService._empty_result_retry_count({**base, "min_speed": 0}) == 0


def test_retry_count_is_bounded_and_supports_disabling():
    base = {"min_speed": 2, "debug": False}
    assert CfstService._empty_result_retry_count({**base, "empty_result_retries": 0}) == 0
    assert CfstService._empty_result_retry_count({**base, "empty_result_retries": 100}) == 10


def test_hosts_source_warnings_do_not_mark_pipeline_failed():
    result = {"success": True, "errors": [], "warnings": ["source timeout"]}
    assert HostsPipeline._notification_success(result) is True


def test_hosts_critical_errors_still_mark_pipeline_failed():
    result = {"success": True, "errors": ["iKuai sync failed"], "warnings": []}
    assert HostsPipeline._notification_success(result) is False


def test_last_updated_uses_completion_time_instead_of_read_time():
    service = CfstService()
    completed_at = datetime(2026, 10, 31, 23, 45, 12)
    service._completed_at = completed_at

    assert service.get_last_updated() == completed_at
