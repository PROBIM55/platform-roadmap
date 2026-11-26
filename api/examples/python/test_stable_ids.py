"""Регрессии выбора объектов. Запуск: python -m unittest test_stable_ids.py"""

import copy
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, patch

from common import SelectionError, find_discipline, find_section
import download_archive
import plan as plan_example
import upload_drawing


def document():
    return {"document": {"disciplines": [{"id": "d1", "name": "Вода"}], "sections": [
        {"id": "s1", "disciplineId": "d1", "name": "План", "cadVersions": []},
    ]}}


class StableIdsTests(unittest.TestCase):
    def test_empty_selectors_are_rejected_before_client_or_fallback(self):
        for module, base, flag in [
            (upload_drawing, ["--project", "p1", "--file", "sample.dwg", "--discipline-id", "d1"], "--section-id"),
            (upload_drawing, ["--project", "p1", "--file", "sample.dwg", "--section-id", "s1"], "--discipline-id"),
            (download_archive, ["--project", "p1", "--out", "out.zip"], "--discipline-id"),
            (download_archive, ["--project", "p1", "--out", "out.zip"], "--discipline"),
            (upload_drawing, ["--project", "p1", "--file", "sample.dwg", "--section-id", "s1"], "--discipline"),
            (upload_drawing, ["--project", "p1", "--file", "sample.dwg", "--discipline-id", "d1"], "--section"),
            (plan_example, [], "--project"),
        ]:
            for value in ("", "   "):
                with self.subTest(module=module.__name__, flag=flag, value=value), \
                        patch("sys.argv", [module.__name__] + base + [flag, value]), \
                        patch.object(module, "Client") as client, redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 2)
                client.assert_not_called()

    def test_ids_survive_all_display_name_changes(self):
        plan = document()
        plan["document"]["disciplines"][0]["name"] = "Другое название"
        plan["document"]["sections"][0]["name"] = "Переименованный файл"
        self.assertEqual(find_discipline(plan, discipline_id="d1")["name"], "Другое название")
        self.assertEqual(find_section(plan, section_id="s1")["name"], "Переименованный файл")
        self.assertIsNone(find_section(plan, "other-discipline", section_id="s1"))

    def test_missing_id_does_not_fall_back_to_same_name(self):
        plan = document()
        self.assertIsNone(find_discipline(plan, "Вода", discipline_id="deleted"))
        self.assertIsNone(find_section(plan, "d1", "План", section_id="deleted"))

    def test_ambiguous_discipline_name_fails_but_id_works(self):
        plan = document()
        plan["document"]["disciplines"].append({"id": "d2", "name": " ВОДА "})
        with self.assertRaises(SelectionError):
            find_discipline(plan, "Вода")
        self.assertEqual(find_discipline(plan, discipline_id="d2")["id"], "d2")

    def test_ambiguous_file_name_fails_but_other_discipline_is_separate(self):
        plan = document()
        plan["document"]["sections"].append({"id": "s2", "disciplineId": "d2", "name": "План"})
        self.assertEqual(find_section(plan, "d1", "план")["id"], "s1")
        plan["document"]["sections"][1]["disciplineId"] = "d1"
        with self.assertRaises(SelectionError):
            find_section(plan, "d1", "план")

    def upload(self, args, initial=None, final=None):
        client = MagicMock()
        client.plan_path.return_value = "/projects/p1/plan"
        initial = initial or document()
        answers = {"/projects/p1/plan": initial, "/projects/p1/plan/uploads/limits": {"maxSourceBytes": 100}}
        reads = 0

        def get(path):
            nonlocal reads
            if path == "/projects/p1/plan":
                reads += 1
                return final if final and reads > 1 else initial
            return answers[path]

        client.get.side_effect = get
        client.post.return_value = {"section": {"id": "created", "name": "Новый", "disciplineId": "d1"}}
        client.request.return_value = {"cadVersion": {"id": "v1", "number": 1, "status": "submitted"}}
        argv = ["upload_drawing.py", "--project", "p1", "--file", "sample.dwg", "--import-id", "imp1", "--unit", "mm"] + args
        with patch("sys.argv", argv), patch.object(upload_drawing, "Client", return_value=client), \
                patch.object(upload_drawing.os.path, "isfile", return_value=True), \
                patch.object(upload_drawing.os.path, "getsize", return_value=1), \
                patch.object(upload_drawing, "wait_import", return_value={}), \
                patch.object(upload_drawing, "wait_ready", return_value="ready"), redirect_stdout(io.StringIO()) as out:
            try:
                upload_drawing.main()
            except (SystemExit, SelectionError) as error:
                return client, error, out.getvalue()
        return client, None, out.getvalue()

    def test_upload_rereads_by_id_if_names_change_during_processing(self):
        final = copy.deepcopy(document())
        final["document"]["disciplines"][0]["name"] = "Другое название"
        final["document"]["sections"][0].update(name="Другое имя", cadVersions=[{"id": "v1", "status": "accepted"}])
        client, error, output = self.upload(["--section-id", "s1", "--wait-ready"], final=final)
        self.assertIsNone(error)
        self.assertIn("Итоговый статус версии: accepted", output)
        self.assertEqual(client.request.call_args.args[:2], ("POST", "/projects/p1/plan/sections/s1/cad-versions"))
        client.post.assert_not_called()

    def test_upload_missing_id_cannot_create_or_register_another_file(self):
        client, error, _ = self.upload(["--section-id", "deleted"])
        self.assertIsInstance(error, SystemExit)
        client.post.assert_not_called()
        client.request.assert_not_called()

    def test_upload_file_from_different_discipline_is_rejected(self):
        initial = document()
        initial["document"]["disciplines"].append({"id": "d2", "name": "Газ"})
        client, error, _ = self.upload(["--discipline-id", "d2", "--section-id", "s1"], initial)
        self.assertIsInstance(error, SystemExit)
        client.post.assert_not_called()
        client.request.assert_not_called()

    def test_missing_name_requires_explicit_creation(self):
        client, error, _ = self.upload(["--discipline-id", "d1", "--section", "Старое имя"])
        self.assertIsInstance(error, SystemExit)
        client.post.assert_not_called()
        client.request.assert_not_called()

    def test_explicit_creation_uses_selected_discipline(self):
        client, error, _ = self.upload(["--discipline-id", "d1", "--section", "Новый", "--create-section"])
        self.assertIsNone(error)
        client.post.assert_called_once_with("/projects/p1/plan/sections", {"disciplineId": "d1", "name": "Новый"})
        self.assertEqual(client.request.call_args.args[1], "/projects/p1/plan/sections/created/cad-versions")

    def test_duplicate_file_names_do_not_write(self):
        initial = document()
        initial["document"]["sections"].append({"id": "s2", "disciplineId": "d1", "name": "ПЛАН"})
        client, error, _ = self.upload(["--discipline-id", "d1", "--section", "План", "--create-section"], initial)
        self.assertIsInstance(error, SelectionError)
        client.post.assert_not_called()
        client.request.assert_not_called()

    def test_archive_missing_id_does_not_download_entire_plan(self):
        client = MagicMock()
        client.get.return_value = document()
        with patch("sys.argv", ["download_archive.py", "--project", "p1", "--discipline-id", "deleted", "--out", "out.zip"]), \
                patch.object(download_archive, "Client", return_value=client), \
                patch.object(download_archive.os.path, "exists", return_value=False), self.assertRaises(SystemExit):
            download_archive.main()
        client.download.assert_not_called()

    def test_project_discovery_shows_id_and_current_name(self):
        client = MagicMock()
        client.get.return_value = {"projects": [{"projectId": "p1", "name": "Новое название"}]}
        with patch("sys.argv", ["plan.py", "--projects"]), patch.object(plan_example, "Client", return_value=client), \
                redirect_stdout(io.StringIO()) as out:
            plan_example.main()
        client.get.assert_called_once_with("/api/platform/network-federation/me")
        self.assertIn("p1: Новое название", out.getvalue())


if __name__ == "__main__":
    unittest.main()
