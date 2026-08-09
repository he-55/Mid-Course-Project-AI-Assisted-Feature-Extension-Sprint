hiba-project % .venv/bin/python -m pytest test_main.py -v
======================================== test session starts =========================================
platform darwin -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0 -- /Users/hiba-project/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/hiba-project
plugins: anyio-4.14.2
collected 43 items                                                                                   

test_main.py::test_health_check PASSED                                                         [  2%]
test_main.py::test_create_task_defaults_to_todo PASSED                                         [  4%]
test_main.py::test_create_task_without_description PASSED                                      [  6%]
test_main.py::test_create_task_requires_title PASSED                                           [  9%]
test_main.py::test_list_tasks PASSED                                                           [ 11%]
test_main.py::test_list_tasks_filtered_by_status PASSED                                        [ 13%]
test_main.py::test_get_single_task PASSED                                                      [ 16%]
test_main.py::test_get_missing_task_returns_404 PASSED                                         [ 18%]
test_main.py::test_update_task_details PASSED                                                  [ 20%]
test_main.py::test_update_missing_task_returns_404 PASSED                                      [ 23%]
test_main.py::test_delete_task PASSED                                                          [ 25%]
test_main.py::test_delete_missing_task_returns_404 PASSED                                      [ 27%]
test_main.py::test_forward_transitions_allowed PASSED                                          [ 30%]
test_main.py::test_move_back_to_todo_from_in_progress_returns_400 PASSED                       [ 32%]
test_main.py::test_move_back_to_todo_from_done_returns_400 PASSED                              [ 34%]
test_main.py::test_move_done_back_to_in_progress_returns_400 PASSED                            [ 37%]
test_main.py::test_illegal_transition_does_not_change_task PASSED                              [ 39%]
test_main.py::test_same_status_update_is_allowed PASSED                                        [ 41%]
test_main.py::test_create_task_with_due_date PASSED                                            [ 44%]
test_main.py::test_create_task_without_due_date_defaults_to_none PASSED                        [ 46%]
test_main.py::test_create_task_with_invalid_due_date_returns_422 PASSED                        [ 48%]
test_main.py::test_update_due_date PASSED                                                      [ 51%]
test_main.py::test_update_with_invalid_due_date_returns_422 PASSED                             [ 53%]
test_main.py::test_clear_due_date_with_explicit_null PASSED                                    [ 55%]
test_main.py::test_update_without_due_date_field_preserves_it PASSED                           [ 58%]
test_main.py::test_filter_overdue_only PASSED                                                  [ 60%]
test_main.py::test_overdue_filter_excludes_done_tasks PASSED                                   [ 62%]
test_main.py::test_filter_due_soon PASSED                                                      [ 65%]
test_main.py::test_due_soon_filter_excludes_done_tasks PASSED                                  [ 67%]
test_main.py::test_filter_no_due_date PASSED                                                   [ 69%]
test_main.py::test_due_filter_combines_with_status_filter PASSED                               [ 72%]
test_main.py::test_invalid_due_filter_returns_422 PASSED                                       [ 74%]
test_main.py::test_create_task_with_tags PASSED                                                [ 76%]
test_main.py::test_create_task_without_tags_defaults_to_empty_list PASSED                      [ 79%]
test_main.py::test_tags_are_normalized_and_deduplicated PASSED                                 [ 81%]
test_main.py::test_invalid_tags_return_422 PASSED                                              [ 83%]
test_main.py::test_update_replaces_tags_wholesale PASSED                                       [ 86%]
test_main.py::test_update_with_empty_list_clears_tags PASSED                                   [ 88%]
test_main.py::test_update_without_tags_field_preserves_them PASSED                             [ 90%]
test_main.py::test_update_with_invalid_tags_returns_422 PASSED                                 [ 93%]
test_main.py::test_filter_by_tag PASSED                                                        [ 95%]
test_main.py::test_filter_by_tag_is_case_insensitive PASSED                                    [ 97%]
test_main.py::test_tag_filter_combines_with_status_and_due PASSED                              [100%]

========================================== warnings summary ==========================================
.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /Users/hiba-project/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== 43 passed, 1 warning in 0.22s ====================================