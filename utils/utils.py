import json
from datetime import datetime
from uuid import uuid4

from pylon.core.tools import log

from tools import task_tools, rpc_tools


def run_test(test, config_only: bool = False, execution: bool = False) -> dict:
    event = test.configure_execution_json(
        output='cc',
        execution=execution
    )

    if config_only:
        return event

    from ..models.ui_report import UIReport
    report = UIReport(
        uid=uuid4(),
        name=test.name,
        project_id=test.project_id,
        start_time=datetime.utcnow().isoformat("T") + "Z",
        is_active=True,
        browser=test.browser.split("_")[0],
        browser_version=test.browser.split("_")[0],
        # TODO set environment
        environment="local",
        loops=test.loops,
        aggregation=test.aggregation
    )
    report.insert()
    event["cc_env_vars"]["REPORT_ID"] = str(report.id)

    resp = task_tools.run_task(test.project_id, [event])
    resp['redirect'] = f'/task/{resp["task_id"]}/results'  # todo: where this should lead to?

    test.rpc.call.increment_statistics(test.project_id, 'ui_performance_test_runs')
    return resp