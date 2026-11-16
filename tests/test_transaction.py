import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import json

spec = importlib.util.spec_from_file_location('manage', Path(__file__).parents[1]/'scripts/manage.py')
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)

class TransactionTests(unittest.TestCase):
    def test_restore_existing_file_mode_and_remove_new_blob_and_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root/'ucm.conf'
            original.write_bytes(b'original configuration\n')
            original.chmod(0o640)
            blob = root/'firmware/blob.bin'
            link = root/'firmware/legacy.bin'
            run = manage.transaction([(blob,b'new binary'), (original,b'corrected configuration')],
                                     [(link,'blob.bin')],root/'state')
            self.assertEqual(link.read_bytes(), b'new binary')
            manage.restore(run)
            self.assertEqual(original.read_bytes(), b'original configuration\n')
            self.assertEqual(original.stat().st_mode & 0o777, 0o640)
            self.assertFalse(blob.exists())
            self.assertFalse(link.is_symlink())

    def test_later_upgrade_blocks_entire_rollback_without_partial_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root/'first', root/'second'
            first.write_bytes(b'old first')
            second.write_bytes(b'old second')
            run = manage.transaction([(first,b'new first'),(second,b'new second')],[],root/'state')
            second.write_bytes(b'newer distro upgrade')
            with self.assertRaises(RuntimeError):
                manage.restore(run)
            self.assertEqual(first.read_bytes(), b'new first')
            self.assertEqual(second.read_bytes(), b'newer distro upgrade')

    def test_interrupted_transaction_can_restore_unchanged_original(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root/'existing'
            existing.write_bytes(b'before')
            run = manage.transaction([(existing,b'after')],[],root/'state')
            existing.write_bytes(b'before')
            manage.restore(run)
            self.assertEqual(existing.read_bytes(), b'before')

    def test_missing_backup_blocks_rollback_before_any_file_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root/'first', root/'second'
            first.write_bytes(b'old first')
            second.write_bytes(b'old second')
            run = manage.transaction([(first,b'new first'),(second,b'new second')],[],root/'state')
            manifest = json.loads((run/'manifest.json').read_text())
            (run/manifest[0]['backup']).unlink()
            with self.assertRaises(RuntimeError):
                manage.restore(run)
            self.assertEqual(first.read_bytes(), b'new first')
            self.assertEqual(second.read_bytes(), b'new second')

    def test_corrupted_backup_blocks_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/'target'
            target.write_bytes(b'original')
            run = manage.transaction([(target,b'new')],[],root/'state')
            manifest = json.loads((run/'manifest.json').read_text())
            (run/manifest[0]['backup']).write_bytes(b'corrupt')
            with self.assertRaises(RuntimeError):
                manage.restore(run)
            self.assertEqual(target.read_bytes(), b'new')

    def test_session_directory_cannot_escape_state(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(manage, 'STATE', Path(directory)):
                for name in ['..', '.', '../20261116T223654Z', '/tmp', 'arbitrary']:
                    with self.assertRaises(RuntimeError):
                        manage.session_path(name)
                session = Path(directory)/'20261116T223654Z'
                session.mkdir()
                self.assertEqual(manage.session_path(session.name), session)

    def exercise_install_lifecycle(self, preserve_existing_firmware):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, firmware, ucm = root/'project', root/'firmware', root/'init.conf'
            cache = project/'.cache/firmware'
            cache.mkdir(parents=True)
            controls = ['Left Spk', 'Right Spk', 'Left Spk2', 'Right Spk2']
            old = '\n'.join("cset name='"+name+"' on" for name in controls).encode()
            new = old.replace(b"' on", b" Switch' on")
            ucm.write_bytes(old)
            hashes = {}
            for uid in ['9', 'C']:
                data = ('synthetic test firmware '+uid).encode()
                filename = '8EA8-0-2-0x'+uid+'.bin'
                (cache/filename).write_bytes(data)
                hashes[uid] = manage.digest(data)
                if preserve_existing_firmware:
                    canonical = firmware/'ti/audio/tas2783'/filename
                    canonical.parent.mkdir(parents=True, exist_ok=True)
                    canonical.write_bytes(data)
            with mock.patch.multiple(manage, PROJECT=project, FW=firmware, UCM=ucm,
                                     HASHES=hashes, OLD_UCM=manage.digest(old), NEW_UCM=manage.digest(new)):
                with mock.patch.object(manage, 'hardware_check'):
                    files, links = manage.plan()
                    run = manage.transaction(files, links, root/'state')
                    self.assertEqual(ucm.read_bytes(), new)
                    self.assertEqual(manage.plan(), ([], []))
                    manage.restore(run)
            self.assertEqual(ucm.read_bytes(), old)
            for uid in ['9', 'C']:
                canonical = firmware/'ti/audio/tas2783'/('8EA8-0-2-0x'+uid+'.bin')
                self.assertEqual(canonical.exists(), preserve_existing_firmware)
                self.assertFalse((firmware/('8EA8-2-'+uid+'.bin')).is_symlink())
            self.assertTrue((cache/'8EA8-0-2-0x9.bin').exists())

    def test_clean_sandbox_install_idempotency_and_uninstall(self):
        self.exercise_install_lifecycle(False)

    def test_reused_firmware_survives_uninstall(self):
        self.exercise_install_lifecycle(True)

if __name__ == '__main__':
    unittest.main()
