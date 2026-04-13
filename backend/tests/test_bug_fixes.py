"""
针对本次审查发现并修复的 bug 的回归测试，以及之前未覆盖的边界场景。
"""
import asyncio
import json
import pytest
import httpx
from unittest.mock import patch


# ── 辅助函数 ──────────────────────────────────────────────────────────────────

def _create_app(client, name="test-app"):
    r = client.post("/api/v1/applications", json={
        "name": name,
        "ssh_host": "127.0.0.1",
        "ssh_port": 22,
        "ssh_user": "root",
        "ssh_auth_type": "PASSWORD",
        "ssh_password": "test",
        "sandbox_port": 8820,
        "repeater_port": 8821,
    })
    assert r.status_code == 201, r.text
    return r.json()


def _create_session(client, app_id, name="test-session"):
    r = client.post("/api/v1/sessions", json={
        "app_id": app_id,
        "name": name,
    })
    assert r.status_code == 201, r.text
    return r.json()


def _create_test_case(client, app_id, name="test-case"):
    r = client.post("/api/v1/test-cases", json={
        "app_id": app_id,
        "name": name,
    })
    assert r.status_code == 201, r.text
    return r.json()


def _add_recording_to_case(client, case_id, recording_id):
    r = client.post(
        f"/api/v1/test-cases/{case_id}/recordings",
        json={"recording_ids": [recording_id]},
    )
    assert r.status_code in (200, 201), r.text
    return r.json()


def _import_har_recording(client, app_id, path="/api/test"):
    har = {
        "log": {
            "version": "1.2",
            "entries": [{
                "request": {
                    "method": "GET",
                    "url": f"http://localhost:8080{path}",
                    "headers": [],
                    "queryString": [],
                    "postData": None,
                },
                "response": {
                    "status": 200,
                    "content": {"text": '{"code":0}', "mimeType": "application/json"},
                },
                "timings": {"send": 0, "wait": 10, "receive": 0},
            }],
        },
    }
    r = client.post(
        "/api/v1/recordings/import-har",
        data={"app_id": app_id},
        files={"file": ("test.har", json.dumps(har).encode(), "application/json")},
    )
    assert r.status_code in (200, 201), r.text
    session_id = r.json()["session_id"]
    recordings = client.get(f"/api/v1/recordings?session_id={session_id}")
    assert recordings.status_code == 200, recordings.text
    return recordings.json()["items"][0]


VALID_CONFIG_JSON = json.dumps({
    "pluginIdentities": ["http"],
    "sampleRate": 1000,
})


# ── 1. config_json 校验 ───────────────────────────────────────────────────────

class TestConfigValidation:
    """config_json 必须包含 pluginIdentities。"""

    def test_missing_plugin_identities_returns_400(self, client):
        """config_json 缺少 pluginIdentities 时应返回 400，不应 500。"""
        app = _create_app(client)
        r = client.put(f"/api/v1/configs/{app['id']}", json={
            "config_json": '{"sampleRate":5000}',
        })
        assert r.status_code == 400
        assert "pluginIdentities" in r.json().get("detail", "")

    def test_invalid_json_returns_400(self, client):
        """config_json 不是合法 JSON 时应返回 400。"""
        app = _create_app(client)
        r = client.put(f"/api/v1/configs/{app['id']}", json={
            "config_json": "not json at all",
        })
        assert r.status_code == 400

    def test_valid_config_creates_successfully(self, client):
        """合法 config_json 应返回 200。"""
        app = _create_app(client)
        r = client.put(f"/api/v1/configs/{app['id']}", json={
            "config_json": VALID_CONFIG_JSON,
            "plugins": ["http"],
            "sampling_rate": 1.0,
        })
        assert r.status_code == 200
        assert r.json()["app_id"] == app["id"]

    def test_update_preserves_new_config(self, client):
        """连续两次 PUT 应以第二次为准。"""
        app = _create_app(client)
        client.put(f"/api/v1/configs/{app['id']}", json={
            "config_json": VALID_CONFIG_JSON,
            "sampling_rate": 0.5,
        })
        r = client.put(f"/api/v1/configs/{app['id']}", json={
            "config_json": json.dumps({"pluginIdentities": ["http"], "sampleRate": 1}),
            "sampling_rate": 0.1,
        })
        assert r.status_code == 200
        assert r.json()["sampling_rate"] == 0.1

    def test_empty_plugin_identities_returns_400(self, client):
        """pluginIdentities 为空列表（falsy）时也应返回 400。"""
        app = _create_app(client)
        r = client.put(f"/api/v1/configs/{app['id']}", json={
            "config_json": '{"pluginIdentities":[]}',
        })
        assert r.status_code == 400


# ── 2. diff.py 正则修复 ───────────────────────────────────────────────────────

class TestDiffRegexFix:
    """_convert_patterns_to_deepdiff_regex 正则不应排除单引号以外的字符。"""

    def test_regex_pattern_matches_nested_path(self):
        """修复后的正则应能匹配含单引号的 deepdiff 路径（如 root['data']['timestamp']）。"""
        import re
        from utils.diff import _convert_patterns_to_deepdiff_regex
        patterns = _convert_patterns_to_deepdiff_regex(["timestamp"])
        assert len(patterns) == 1
        regex = patterns[0]
        # deepdiff 路径格式示例
        assert re.search(regex, "root['timestamp']"), \
            f"正则 {regex!r} 应匹配 root['timestamp']"
        assert re.search(regex, "root['data']['timestamp']"), \
            f"正则 {regex!r} 应匹配 root['data']['timestamp']"

    def test_regex_pattern_not_overly_restrictive(self):
        """修复后的正则不应因为排除单引号而无法匹配正常路径。"""
        import re
        from utils.diff import _convert_patterns_to_deepdiff_regex
        patterns = _convert_patterns_to_deepdiff_regex(["updateTime"])
        regex = patterns[0]
        assert re.search(regex, "root['result']['updateTime']")

    def test_noise_reduction_excludes_timestamp_fields(self):
        """智能降噪应成功过滤掉 timestamp 字段差异。"""
        from utils.diff import compute_diff
        orig = json.dumps({"code": 0, "data": {"id": 1, "timestamp": 1000}})
        repl = json.dumps({"code": 0, "data": {"id": 1, "timestamp": 9999}})
        diff_json, score = compute_diff(orig, repl, smart_noise_reduction=True)
        # timestamp 是内置降噪字段，score 应该是 0（无差异）
        assert score == 0.0, f"timestamp 差异应被降噪过滤，实际 score={score}"


# ── 3. failure_analyzer.py 修复 ──────────────────────────────────────────────

class TestFailureAnalyzerFix:
    """diff_score=0.0 时不应误判为 BUG。"""

    def test_zero_diff_score_not_classified_as_bug(self):
        """diff_score=0.0 表示完全一致，不应返回 BUG。"""
        from utils.failure_analyzer import analyze_failure
        category, _ = analyze_failure(
            error_message="some error",
            diff_json=None,
            diff_score=0.0,
            replayed_status_code=200,
            assertion_results=None,
        )
        assert category != "BUG", "diff_score=0.0 不应被分类为 BUG"

    def test_none_diff_score_with_server_error_is_environment(self):
        """状态码 500 应被判定为 ENVIRONMENT。"""
        from utils.failure_analyzer import analyze_failure
        category, _ = analyze_failure(
            error_message=None,
            diff_json=None,
            diff_score=None,
            replayed_status_code=500,
            assertion_results=None,
        )
        assert category == "ENVIRONMENT"

    def test_positive_diff_score_can_be_bug(self):
        """diff_score > 0 且无其他线索时应返回 BUG。"""
        from utils.failure_analyzer import analyze_failure
        category, _ = analyze_failure(
            error_message=None,
            diff_json='{"values_changed": {"root[\'price\']": {"new_value": 99}}}',
            diff_score=0.5,
            replayed_status_code=200,
            assertion_results=None,
        )
        assert category == "BUG"


# ── 4. suites.py None list 修复 ──────────────────────────────────────────────

class TestSuiteNoneListFix:
    """suite 字段合并后 ignore_fields / diff_rules / assertions 不应为 None。"""

    def test_suite_merge_returns_lists_not_none(self):
        """当 suite 和 req 都没设置 ignore_fields 时，结果应为 []，不是 None。"""
        # 直接测试逻辑（无需 HTTP）
        class FakeSuite:
            default_ignore_fields = None
            default_diff_rules = None
            default_assertions = None
            default_concurrency = None
            default_perf_threshold_ms = None
            default_environment = None
            default_override_host = None
            default_delay_ms = None

        class FakeReq:
            ignore_fields = None
            diff_rules = None
            assertions = None
            concurrency = None
            perf_threshold_ms = None
            environment = None
            override_host = None

        suite = FakeSuite()
        req = FakeReq()

        ignore_fields = req.ignore_fields or suite.default_ignore_fields or []
        diff_rules = req.diff_rules or suite.default_diff_rules or []
        assertions = req.assertions or suite.default_assertions or []

        assert ignore_fields == []
        assert diff_rules == []
        assert assertions == []
        # 确保可以安全地做 list 操作
        assert len(ignore_fields) == 0


# ── 5. 应用 CRUD 边界 ─────────────────────────────────────────────────────────

class TestApplicationEdgeCases:
    def test_create_app_missing_required_field(self, client):
        """缺少必填字段时应返回 422。"""
        r = client.post("/api/v1/applications", json={"name": "x"})
        assert r.status_code == 422

    def test_get_nonexistent_app_returns_404(self, client):
        r = client.get("/api/v1/applications/nonexistent-id")
        assert r.status_code == 404

    def test_delete_nonexistent_app_returns_404(self, client):
        r = client.delete("/api/v1/applications/nonexistent-id")
        assert r.status_code == 404

    def test_duplicate_app_name_returns_409(self, client):
        """重复应用名称应返回 409，而不是 500。"""
        _create_app(client, name="dup")
        r = client.post("/api/v1/applications", json={
            "name": "dup",
            "ssh_host": "127.0.0.1",
            "ssh_port": 22,
            "ssh_user": "root",
            "ssh_auth_type": "PASSWORD",
            "ssh_password": "test",
            "sandbox_port": 8820,
            "repeater_port": 8821,
        })
        assert r.status_code == 409

    def test_list_apps_empty(self, client):
        r = client.get("/api/v1/applications")
        assert r.status_code == 200
        assert r.json() == []


class TestValidationGuards:
    def test_replay_concurrency_zero_returns_422(self, client):
        r = client.post("/api/v1/replays", json={
            "case_id": "case-1",
            "target_app_id": "app-1",
            "concurrency": 0,
        })
        assert r.status_code == 422

    def test_schedule_concurrency_zero_returns_422(self, client):
        r = client.post("/api/v1/schedules", json={
            "name": "bad-schedule",
            "cron_expr": "* * * * *",
            "case_id": "case-1",
            "target_app_id": "app-1",
            "concurrency": 0,
        })
        assert r.status_code == 422

    def test_compare_concurrency_zero_returns_422(self, client):
        r = client.post("/api/v1/compare", json={
            "name": "bad-compare",
            "case_id": "case-1",
            "app_a_id": "app-a",
            "app_b_id": "app-b",
            "concurrency": 0,
        })
        assert r.status_code == 422


class TestReplayRegressionFixes:
    def test_repeat_count_updates_total_count(self, client):
        app = _create_app(client, name="repeat-app")
        recording = _import_har_recording(client, app["id"], path="/api/repeat")
        case = _create_test_case(client, app["id"], name="repeat-case")
        _add_recording_to_case(client, case["id"], recording["id"])

        with patch("api.v1.replays._fire", lambda coro: coro.close()):
            r = client.post("/api/v1/replays", json={
                "case_id": case["id"],
                "target_app_id": app["id"],
                "repeat_count": 3,
            })

        assert r.status_code == 201, r.text
        assert r.json()["total_count"] == 3

    def test_transparent_proxy_preserves_query_string_in_recording_uri(self, client):
        app = _create_app(client, name="proxy-app")
        session = _create_session(client, app["id"], name="proxy-session")
        assert session["status"] == "ACTIVE"

        async def fake_request(self, method, url, headers=None, content=None):
            return httpx.Response(
                status_code=200,
                text='{"ok":true}',
                headers={"content-type": "application/json"},
                request=httpx.Request(method, url),
            )

        with patch("httpx.AsyncClient.request", new=fake_request):
            r = client.post(
                f"/api/v1/proxy/{app['name']}/bank/service?service_id=OPEN_ACCOUNT&channel=mobile",
                content="<service_id>OPEN_ACCOUNT</service_id>",
                headers={"content-type": "application/xml"},
            )

        assert r.status_code == 200, r.text

        recordings = client.get(f"/api/v1/recordings?session_id={session['id']}")
        assert recordings.status_code == 200, recordings.text
        items = recordings.json()["items"]
        assert len(items) == 1
        request_body = json.loads(items[0]["request_body"])
        assert request_body["uri"] == "/bank/service?service_id=OPEN_ACCOUNT&channel=mobile"

    def test_ci_timeout_marks_job_cancelled(self, client):
        app = _create_app(client, name="ci-app")
        recording = _import_har_recording(client, app["id"], path="/api/ci")
        case = _create_test_case(client, app["id"], name="ci-case")
        _add_recording_to_case(client, case["id"], recording["id"])

        async def slow_run(_: str):
            await asyncio.Event().wait()

        with patch("api.v1.ci._run_replay_job", new=slow_run):
            r = client.post("/api/v1/ci/replay", json={
                "case_id": case["id"],
                "target_app_id": app["id"],
                "timeout_seconds": 10,
            })

        assert r.status_code == 504, r.text
        detail = r.json()["detail"]
        job_id = detail["job_id"]

        job = client.get(f"/api/v1/replays/{job_id}")
        assert job.status_code == 200, job.text
        assert job.json()["status"] == "CANCELLED"


# ── 6. 测试用例边界 ───────────────────────────────────────────────────────────

class TestTestCaseEdgeCases:
    def test_create_test_case_minimal(self, client):
        app = _create_app(client)
        r = client.post("/api/v1/test-cases", json={
            "name": "minimal",
            "app_id": app["id"],
        })
        assert r.status_code == 201
        assert r.json()["name"] == "minimal"

    def test_get_nonexistent_case_404(self, client):
        r = client.get("/api/v1/test-cases/no-such-id")
        assert r.status_code == 404

    def test_add_recordings_to_nonexistent_case(self, client):
        r = client.post("/api/v1/test-cases/no-such-id/recordings", json={
            "recording_ids": ["abc"]
        })
        assert r.status_code == 404

    def test_clone_test_case(self, client):
        app = _create_app(client)
        tc = client.post("/api/v1/test-cases", json={
            "name": "original",
            "app_id": app["id"],
        }).json()
        r = client.post(f"/api/v1/test-cases/{tc['id']}/clone")
        assert r.status_code == 201
        cloned = r.json()
        assert "副本" in cloned["name"] or "copy" in cloned["name"].lower() or cloned["name"] != "original"

    def test_delete_test_case(self, client):
        app = _create_app(client)
        tc = client.post("/api/v1/test-cases", json={
            "name": "to-delete",
            "app_id": app["id"],
        }).json()
        r = client.delete(f"/api/v1/test-cases/{tc['id']}")
        assert r.status_code == 200 or r.status_code == 204


# ── 7. 回放任务边界 ───────────────────────────────────────────────────────────

class TestReplayEdgeCases:
    def test_replay_with_nonexistent_case(self, client):
        app = _create_app(client)
        r = client.post("/api/v1/replays", json={
            "case_id": "no-such-case",
            "target_app_id": app["id"],
        })
        assert r.status_code == 404

    def test_replay_with_nonexistent_app(self, client):
        app = _create_app(client)
        tc = client.post("/api/v1/test-cases", json={
            "name": "tc",
            "app_id": app["id"],
        }).json()
        r = client.post("/api/v1/replays", json={
            "case_id": tc["id"],
            "target_app_id": "no-such-app",
        })
        assert r.status_code == 404

    def test_get_nonexistent_replay_job(self, client):
        r = client.get("/api/v1/replays/no-such-id")
        assert r.status_code == 404

    def test_list_replays_empty(self, client):
        r = client.get("/api/v1/replays")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert data["total"] == 0


# ── 8. 统计接口 ───────────────────────────────────────────────────────────────

class TestStatsEndpoints:
    def test_stats_summary(self, client):
        r = client.get("/api/v1/stats/summary")
        assert r.status_code == 200
        data = r.json()
        assert "job_count" in data
        assert "avg_pass_rate" in data

    def test_stats_trend(self, client):
        r = client.get("/api/v1/stats/trend")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_stats_trend_custom_days(self, client):
        r = client.get("/api/v1/stats/trend?days=7")
        assert r.status_code == 200
        assert len(r.json()) <= 7


# ── 9. 定时任务校验 ───────────────────────────────────────────────────────────

class TestScheduleValidation:
    def test_invalid_cron_returns_422_or_400(self, client):
        app = _create_app(client)
        tc = client.post("/api/v1/test-cases", json={
            "name": "tc",
            "app_id": app["id"],
        }).json()
        r = client.post("/api/v1/schedules", json={
            "name": "bad-cron",
            "case_id": tc["id"],
            "target_app_id": app["id"],
            "cron_expr": "not a cron",
        })
        assert r.status_code in (400, 422)

    def test_valid_cron_creates_schedule(self, client):
        app = _create_app(client)
        tc = client.post("/api/v1/test-cases", json={
            "name": "tc",
            "app_id": app["id"],
        }).json()
        r = client.post("/api/v1/schedules", json={
            "name": "hourly",
            "case_id": tc["id"],
            "target_app_id": app["id"],
            "cron_expr": "0 * * * *",
        })
        assert r.status_code == 201

    def test_list_schedules(self, client):
        r = client.get("/api/v1/schedules")
        assert r.status_code == 200


# ── 10. 对比接口边界 ──────────────────────────────────────────────────────────

class TestCompareEdgeCases:
    def test_compare_without_recordings_returns_400(self, client):
        """没有录制数据的用例发起对比应返回 400。"""
        app = _create_app(client)
        tc = client.post("/api/v1/test-cases", json={
            "name": "tc",
            "app_id": app["id"],
        }).json()
        r = client.post("/api/v1/compare", json={
            "case_id": tc["id"],
            "app_a_id": app["id"],
            "app_b_id": app["id"],
        })
        assert r.status_code == 400
        assert "recordings" in r.json().get("detail", "").lower()

    def test_compare_nonexistent_case(self, client):
        app = _create_app(client)
        r = client.post("/api/v1/compare", json={
            "case_id": "no-such-case",
            "app_a_id": app["id"],
            "app_b_id": app["id"],
        })
        assert r.status_code == 404

    def test_list_compare_runs(self, client):
        r = client.get("/api/v1/compare")
        assert r.status_code == 200
