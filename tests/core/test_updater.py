# -*- coding: utf-8 -*-
import hashlib
import io
import json
import os
import shutil
import tempfile
import zipfile

from support import RuntimeTest, module


BASE = 'https://github.com/dkruben/Driftkings_SettingsLab/releases/download/'


def manifest(version='1.1.0', data=b'package'):
    return dict(schema=1, version=version, channel='beta' if '-' in version else 'stable',
                gameVersion='2.4.1.0', file='Driftkings.wotmod', size=len(data),
                sha256=hashlib.sha256(data).hexdigest(), download=BASE + 'v' + version + '/Driftkings.wotmod')


class VersionsTests(RuntimeTest):
    def test_semver_precedence_and_build_metadata(self):
        Version = self.load('core.updater.versioning').Version
        ordered = ['1.0.0-alpha', '1.0.0-alpha.1', '1.0.0-alpha.beta', '1.0.0-beta',
                   '1.0.0-beta.2', '1.0.0-beta.11', '1.0.0-rc.1', '1.0.0', '1.0.1', '2.0.0']
        self.assertEqual(sorted(Version(value) for value in reversed(ordered)), [Version(value) for value in ordered])
        self.assertEqual(Version('1.0.0+first'), Version('1.0.0+second'))
        self.assertEqual(hash(Version('1.0.0+first')), hash(Version('1.0.0')))

    def test_invalid_versions_and_channels(self):
        Version = self.load('core.updater.versioning').Version
        for value in (None, 123, '', '1.2', 'v1.2.3', '01.2.3', '1.2.3-beta.01', '1.2.3\n'):
            self.assertRaises(ValueError, Version, value)
        for version, stable, beta in (('1.0.0', True, True), ('1.0.0-beta.1', False, True),
                                     ('1.0.0-rc.2', False, True), ('1.0.0-alpha', False, False)):
            self.assertEqual(Version(version).allowed('stable'), stable)
            self.assertEqual(Version(version).allowed('beta'), beta)
        self.assertRaises(ValueError, Version('1.0.0').allowed, 'preview')

    def test_game_version_normalization_and_unknown_versions(self):
        api = self.load('core.updater.versioning')
        self.assertEqual(api.normalize_game_version(' v.2.04.1.0 #970 '), '2.4.1.0')
        self.assertGreater(api.game_key('2.10.0.0'), api.game_key('2.9.0.0'))
        for value in (None, '', '2.4.1', '2.4.1.0-beta', '2.4.1.0 garbage'):
            self.assertIsNone(api.normalize_game_version(value))
            self.assertRaises(ValueError, api.game_key, value)


class MetadataTests(RuntimeTest):
    def test_manifest_roundtrip_channel_and_compatibility(self):
        Manifest = self.load('core.updater.manifest').Manifest
        document = manifest('1.1.0-beta.2')
        parsed = Manifest.parse(json.dumps(document))
        self.assertEqual(Manifest(parsed.document()).version.text, document['version'])
        self.assertTrue(parsed.compatible('v.2.4.1.0 #970'))
        self.assertFalse(parsed.compatible('2.4.2.0'))
        self.assertFalse(parsed.compatible(None))
        document['channel'] = 'stable'
        self.assertRaises(ValueError, Manifest, document)

    def test_invalid_bounded_json_and_manifest_fields(self):
        api = self.load('core.updater.manifest')
        for raw in ('{"schema":1,"schema":2}', '{', b'\xff', None):
            self.assertRaises((ValueError, UnicodeError), api.bounded_json, raw)
        self.assertRaises(ValueError, api.bounded_json, '1234', 3)
        for key, value in (('schema', True), ('size', -1), ('size', True), ('sha256', 'bad'),
                           ('download', 'http://github.com/file'), ('file', '../other.wotmod'), ('unknown', True)):
            document = manifest()
            document[key] = value
            self.assertRaises(ValueError, api.Manifest, document)

    def run_checker(self, channel, responses):
        Response = self.load('core.updater.transport').Response
        requests, results = [], []

        class Transport(object):
            def request(self, url, callback, timeout, maximum):
                requests.append(url)
                self_test.assertGreater(maximum, 0)
                self_test.assertGreater(timeout, 0)
                value, error = responses[url]
                callback(Response(200, json.dumps(value).encode('utf-8'), url), error)

        self_test = self
        checker = self.load('core.updater.checker').Checker(Transport())
        checker.check('1.0.0', channel, '2.4.1.0', lambda result, error: results.append((result, error)))
        self.assertEqual(len(results), 1)
        return checker, requests, results[0]

    def test_checker_selects_latest_allowed_channel_without_downloading_packages(self):
        endpoints = self.load('core.updater.endpoints')
        releases, responses = [], {}
        for version in ('1.1.0', '1.2.0-beta.2', '1.2.0-beta.10', '1.3.0-alpha'):
            url = BASE + 'v' + version + '/release.json'
            releases.append(dict(draft=False, prerelease='-' in version, tag_name='v' + version,
                                 assets=[dict(name='release.json', browser_download_url=url)]))
            if 'alpha' not in version:
                responses[url] = (manifest(version), None)
        responses[endpoints.RELEASES] = (releases, None)
        for channel, expected in (('stable', '1.1.0'), ('beta', '1.2.0-beta.10')):
            checker, requests, (result, error) = self.run_checker(channel, responses)
            self.assertIsNone(error)
            self.assertEqual(result['latestVersion'], expected)
            self.assertEqual(checker.selected_manifest.version.text, expected)
            self.assertTrue(all(not url.endswith('.wotmod') for url in requests))

    def test_checker_rejects_invalid_responses_and_transport_errors(self):
        endpoints = self.load('core.updater.endpoints')
        for document, error, expected in (({}, None, 'invalidReleaseList'),
                                           ([{'tag_name': 'bad'}], None, 'invalidManifest'),
                                           ([], 'timeout', 'timeout'), ([], 'unexpected', 'networkError')):
            checker, requests, (result, actual) = self.run_checker('stable', {endpoints.RELEASES: (document, error)})
            self.assertIsNone(result)
            self.assertEqual(actual, expected)
            self.assertIsNone(checker.selected_manifest)

    def test_bad_http_json_and_late_callback_after_cancel(self):
        api = self.load('core.updater.checker')
        Response = self.load('core.updater.transport').Response
        pending, results = [], []

        class Deferred(object):
            def request(self, url, callback, timeout, maximum):
                pending.append((url, callback))

        checker = api.Checker(Deferred())
        checker.check('1.0.0', 'stable', '2.4.1.0', lambda *args: results.append(args))
        self.assertFalse(checker.check('1.0.0', 'stable', '2.4.1.0', lambda *args: None))
        checker.cancel()
        url, callback = pending.pop()
        callback(Response(200, b'[]', url), None)
        self.assertEqual(results, [])
        for status, body in ((500, b'[]'), (200, b'{'), (200, b'\xff')):
            checker.check('1.0.0', 'stable', '2.4.1.0', lambda *args: results.append(args))
            url, callback = pending.pop()
            callback(Response(status, body, url), None)
            self.assertEqual(results.pop(), (None, 'invalidResponse'))


class FileTests(RuntimeTest):
    def setUp(self):
        super(FileTests, self).setUp()
        self.folder = tempfile.mkdtemp(prefix='dk-updater-test-')
        self.addCleanup(shutil.rmtree, self.folder)

    def test_install_plan_never_replaces_or_removes_existing_configs(self):
        Inventory = self.load('core.updater.inventory').Inventory
        game = '2.4.1.0'
        code = 'mods/' + game + '/Driftkings.wotmod'
        config = 'mods/configs/Driftkings/default/example.json'

        def entry(path, kind):
            return dict(path=path, kind=kind, size=3, sha256='a' * 64)

        document = dict(schema=1, packageId='driftkings.modpack', version='1.1.0', channel='stable', gameVersion=game,
                        distribution=dict(file='Driftkings-1.1.0-WoT-2.4.1.0.zip', size=10, sha256='b' * 64),
                        files=[entry(code, 'code'), entry('Driftkings-defaults.zip', 'defaults'), entry('INSTALL.txt', 'instructions')],
                        defaults=[entry(config, 'config')])
        inventory = Inventory(document, '1.1.0', 'stable', game)
        path = os.path.join(self.folder, 'personal.json')
        with open(path, 'wb') as stream:
            stream.write(b'{"personal":true}')
        for observed in ({code: None}, {code: dict(size=3, sha256='c' * 64)}):
            actions = inventory.plan(observed)
            self.assertEqual([item['path'] for item in actions], [code])
            self.assertNotIn(config, [item['path'] for item in actions])
            with open(path, 'rb') as stream:
                self.assertEqual(stream.read(), b'{"personal":true}')
        self.assertRaises(ValueError, inventory.plan, {})

    def test_staging_file_error_and_exclusive_ticket_preserve_existing_file(self):
        api = self.load('core.updater.downloader')
        installer = self.load('core.updater.installer')
        path = os.path.join(self.folder, 'occupied')
        with open(path, 'wb') as stream:
            stream.write(b'personal data')
        self.assertRaises(api.TransferError, api.safe_directory, path)
        self.assertRaises(OSError, installer.write_new, path, {'new': True})
        with open(path, 'rb') as stream:
            self.assertEqual(stream.read(), b'personal data')
        self.assertRaises((IOError, OSError), installer.digest, os.path.join(self.folder, 'missing'))

    def test_staging_validates_size_hash_and_package_before_ready(self):
        api = self.load('core.updater.downloader')
        Manifest = self.load('core.updater.manifest').Manifest
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', zipfile.ZIP_STORED) as archive:
            archive.writestr('meta.xml', b'<root><id>driftkings.unified</id><version>1.1.0</version></root>')
            archive.writestr('res/scripts/client/gui/mods/mod_Driftkings.pyc', b'\x03\xf3\x0d\x0a' + b'bytecode')
        data = stream.getvalue()
        for content, expected in ((data[:-1], 'sizeMismatch'), (b'x' * len(data), 'hashMismatch')):
            sink = api.StagingSink(self.folder, Manifest(manifest(data=data)))
            sink.write(content)
            with self.assertRaises(api.TransferError) as error:
                sink.finish()
            self.assertEqual(error.exception.code, expected)
            self.assertIsNone(sink.ready)
            sink.abort()
        sink = api.StagingSink(self.folder, Manifest(manifest(data=data)))
        sink.write(data)
        ready = sink.finish()
        self.assertTrue(os.path.isfile(ready))
        with open(ready, 'rb') as package:
            self.assertEqual(package.read(), data)
        sink.abort()


class ServiceTests(RuntimeTest):
    def setUp(self):
        super(ServiceTests, self).setUp()
        self.folder = tempfile.mkdtemp(prefix='dk-service-test-')
        self.addCleanup(shutil.rmtree, self.folder)
        self.options = {'updateChannel': 'beta', 'autoCheckUpdates': True}
        self.now = [1000]
        self.api = module(client_version='2.4.1.0', get=lambda section, key, default: self.options.get(key, default))
        self.transport = self.load('core.updater.transport').UnavailableTransport()
        self.service = self.load('core.updater').UpdaterService(
            api=self.api, transport=self.transport, clock=lambda: self.now[0],
            safe_spaces=('login', 'lobby'), staging_root=self.folder)
        self.service.active = True

    def test_manual_check_reports_unavailable_transport_and_automatic_check_skips_it(self):
        self.assertFalse(self.service.check())
        self.assertTrue(self.service.check(manual=True))
        self.assertEqual(self.service.state.snapshot()['error'], 'transportUnavailable')
        self.assertEqual(self.service.state.snapshot()['channel'], 'beta')

    def test_automatic_checks_obey_interval_and_manual_checks_bypass_it(self):
        self.transport.available = True
        self.assertTrue(self.service.check())
        self.assertFalse(self.service.check())
        self.assertTrue(self.service.check(manual=True))
        self.now[0] += self.load('core.updater').INTERVAL
        self.assertTrue(self.service.check())
        self.options['autoCheckUpdates'] = False
        self.assertFalse(self.service.check())

    def test_context_changes_and_channel_changes_clear_stale_update_state(self):
        self.service.context = 'battle'
        self.service.onContextLeft('lobby')
        self.assertEqual(self.service.context, 'battle')
        self.service.onContextLeft('battle')
        self.assertIsNone(self.service.context)
        self.service.onContextEntered('battle')
        self.assertEqual(self.service.context, 'battle')
        self.assertIsNone(self.service.state.snapshot()['lastCheck'])
        self.service.state.update(channel='stable', latestVersion='1.1.0', compatible=True, canDownload=True)
        self.service._preferences_changed({})
        snapshot = self.service.state.snapshot()
        self.assertEqual(snapshot['channel'], 'beta')
        self.assertIsNone(snapshot['latestVersion'])
        self.assertFalse(snapshot['canDownload'])

    def test_install_and_download_fail_closed_without_ready_data_or_context(self):
        self.assertFalse(self.service.download())
        self.assertFalse(self.service.schedule_install())
        self.assertEqual(self.service._blocked_reason(), 'unknownContext')
        self.assertFalse(self.service._safe_install_context())
