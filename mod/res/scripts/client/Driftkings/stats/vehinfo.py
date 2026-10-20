# -*- coding: utf-8 -*-
"""
Vehicle information and statistics module for Driftkings.
Handles loading, processing and calculation of various tank statistics.
"""
import json
import logging
import math
import os
import urllib2
from contextlib import closing

import ResMgr
import nations
from items import vehicles

from Driftkings.core.callbacks import callback
from Driftkings.common.utils.filesystem import atomicWrite, recoverFile
from Driftkings.core.cache import cache_directory
LOG = logging.getLogger('Driftkings.Stats')
try:
    integer_types = (int, long)
except NameError:
    integer_types = (int,)


def finite_number(value):
    return isinstance(value, integer_types + (float,)) and not (math.isnan(value) or math.isinf(value))


def valid_scale(values):
    return (isinstance(values, (list, tuple)) and bool(values) and
            all(finite_number(value) for value in values) and
            all(left <= right for left, right in zip(values, values[1:])))


_FLAVOR = 'wg'
HOST = 'https://static.modxvm.com/'
URL_WN8 = HOST + 'wn8-data-exp/json/%s/wn8exp.json' % _FLAVOR
URL_XTE = HOST + 'xte.json'
URL_XTDB = HOST + 'xtdb.json'
URL_XVM_SCALE = HOST + 'xvmscales-%s.json' % _FLAVOR
VEHICLE_TYPE_XML_PATH = 'scripts/item_defs/vehicles/'
VEHICLE_CLASS_TAGS = frozenset(('lightTank', 'mediumTank', 'heavyTank', 'SPG', 'AT-SPG'))


UNKNOWN_VEHICLE_DATA = {
    'vehCD': 0,
    'key': 'unknown',
    'nation': '',
    'level': 0,
    'vClass': '',
    'localizedName': 'unknown',
    'localizedShortName': 'unknown',
    'localizedFullName': 'unknown',
    'premium': False,
    'special': False,
    'tierLo': 0,
    'tierHi': 0,
    'shortName': 'unknown',
    'isReserved': False
}

XVM_SCALE_TO_SUP_CACHE = [str(i) for i in range(1, 101)]


class ScaleValues(object):

    def __init__(self):
        self.NAME = 'stats'
        self.modsGroup = 'Driftkings'
        self.vehicleInfoData = None
        self.wn8_data = {}
        self.xte_data = {}
        self.xvmScale_data = {}
        self.xtdb_data = {}
        self.config_path = cache_directory('stats')
        self.settings = {'onlineUpdateData': True, 'showExpectedTankValuesMessage': True}
        self.init()
        self._initialize_callbacks()

    def _initialize_callbacks(self):
        callback(0, self._loadXvmScaleData)
        callback(0, self._loadWn8Data)
        callback(0, self._loadXteData)
        callback(0, self._loadXtdbData)

    def init(self):
        res = [dict(UNKNOWN_VEHICLE_DATA)]
        try:
            for nation in nations.NAMES:
                nationID = nations.INDICES[nation]
                vehicle_list = vehicles.g_list.getList(nationID)

                for descr in vehicle_list.values():
                    if descr.name.endswith('training'):
                        continue
                    try:
                        data = self.createVehicleData(descr, nation)
                        res.append(data)
                    except Exception:
                        LOG.exception('Error creating vehicle data for %s', descr.name)
                ResMgr.purge(os.path.join(VEHICLE_TYPE_XML_PATH, nation, 'components', 'guns.xml'), True)
        except Exception:
            LOG.exception('Failed to initialize vehicle data')
        finally:
            self.vehicleInfoData = dict((item['vehCD'], item) for item in res)

    @staticmethod
    def createVehicleData(descr, nation):
        vClass = next(iter(VEHICLE_CLASS_TAGS & descr.tags), '')
        return {
            'vehCD': descr.compactDescr,
            'key': descr.name,
            'nation': nation,
            'level': descr.level,
            'vClass': vClass,
            'localizedName': descr.shortUserString,
            'localizedShortName': descr.shortUserString,
            'localizedFullName': descr.userString,
            'premium': 'premium' in descr.tags and 'special' not in descr.tags,
            'special': 'special' in descr.tags,
            'isReserved': False
        }

    @staticmethod
    def XvmScaleToSup(x=None):
        if x is None:
            return None
        if not finite_number(x):
            return None
        return XVM_SCALE_TO_SUP_CACHE[min(100, max(1, int(x))) - 1] if x > 0 else 0.0

    @staticmethod
    def loadJsonData(url, local_path):
        """Keep the last valid cache if a download or publication fails."""
        try:
            with closing(urllib2.urlopen(url, timeout=10)) as response:
                data = response.read()
            document = json.loads(data.decode('utf-8-sig'))
            if not isinstance(document, dict) or not document:
                raise ValueError('Expected a non-empty JSON object')
            atomicWrite(local_path, data)
            return True
        except (IOError, OSError, ValueError):
            LOG.exception('Could not update statistics cache %s from %s', local_path, url)
            return False

    def _loadData(self, filename, url):
        path = os.path.join(self.config_path, filename)
        if self.settings.get('onlineUpdateData', True):
            self.loadJsonData(url, path)
        try:
            recoverFile(path)
            with open(path, 'rb') as stream:
                data = json.loads(stream.read().decode('utf-8-sig'))
            if not isinstance(data, dict):
                raise ValueError('Expected a JSON object')
            return data
        except (IOError, OSError, ValueError):
            LOG.exception('Could not load statistics cache %s', path)
            return {}

    def _loadXvmScaleData(self):
        self.xvmScale_data = self._loadData('xvmScales.json', URL_XVM_SCALE)

    def _loadWn8Data(self):
        self.wn8_data = self._loadData('wn8exp.json', URL_WN8)
        records = self.wn8_data.get('data', [])
        if not isinstance(records, list):
            LOG.warning('Ignored invalid WN8 records')
            return
        for record in records:
            try:
                vinfo = self.getVehicleInfoData(int(record['IDNum']))
                values = dict((name, float(record[key])) for name, key in (
                    ('wn8expDamage', 'expDamage'), ('wn8expSpot', 'expSpot'),
                    ('wn8expWinRate', 'expWinRate'), ('wn8expDef', 'expDef'), ('wn8expFrag', 'expFrag')))
                if not all(finite_number(value) for value in values.values()):
                    raise ValueError('Non-finite WN8 expected value')
                if vinfo is not None:
                    vinfo.update(values)
            except (KeyError, ValueError, TypeError, OverflowError):
                LOG.exception('Ignored invalid WN8 vehicle record')

    def _loadXteData(self):
        self.xte_data = self._loadData('xte.json', URL_XTE)
        for key, values in self.xte_data.items():
            try:
                vinfo = self.getVehicleInfoData(int(key))
                expected = dict((name, float(values.get(field, 0))) for name, field in (
                    ('avgdmg', 'ad'), ('topdmg', 'td'), ('avgfrg', 'af'), ('topfrg', 'tf')))
                if not all(finite_number(value) for value in expected.values()):
                    raise ValueError('Non-finite XTE expected value')
                if vinfo is not None:
                    vinfo.update(expected)
            except (ValueError, KeyError, TypeError, AttributeError, OverflowError):
                LOG.exception('Ignored invalid XTE vehicle record %s', key)

    def _loadXtdbData(self):
        self.xtdb_data = self._loadData('xtdb.json', URL_XTDB)

    def getVehicleInfoData(self, vehCD):
        if not isinstance(vehCD, integer_types):
            return None
        return self.vehicleInfoData.get(vehCD) if self.vehicleInfoData is not None else None

    def getVehicleInfoDataArray(self):
        return list(self.vehicleInfoData.values()) if self.vehicleInfoData is not None else []

    def resetReserve(self):
        if self.vehicleInfoData is not None:
            for vinfo in self.vehicleInfoData.values():
                vinfo['isReserved'] = False

    def updateReserve(self, vehCD, isReserved):
        if self.vehicleInfoData is not None and vehCD in self.vehicleInfoData:
            self.vehicleInfoData[vehCD]['isReserved'] = isReserved

    def getXvmScaleData(self, rating):
        if self.xvmScale_data is None:
            return None
        return self.xvmScale_data.get('x{}'.format(rating))

    def getXteData(self, vehCD):
        if self.xte_data is None:
            return None
        return self.xte_data.get(str(vehCD))

    def getXtdbData(self, vehCD):
        if self.xtdb_data is None:
            return None
        return self.xtdb_data.get(str(vehCD))

    def calculateXvmScale(self, rating, value):
        data = self.getXvmScaleData(rating)
        if not valid_scale(data) or not finite_number(value):
            return -1
        for i, v in enumerate(data):
            if v > value:
                return i
        return 100

    def calculateXTE(self, vehCD, dmg_per_battle, frg_per_battle):
        data = self.getXteData(vehCD)
        if (not isinstance(data, dict) or not valid_scale(data.get('x')) or
                not all(finite_number(data.get(key)) for key in ('td', 'ad', 'tf', 'af')) or
                not finite_number(dmg_per_battle) or not finite_number(frg_per_battle)):
            return -1
        if data['td'] <= data['ad'] or data['tf'] <= data['af'] or data['ad'] <= 0 or data['af'] <= 0:
            return -1
        CD = 3.0  # Damage coefficient
        CF = 1.0  # Frag coefficient
        avgD = float(data['ad'])  # Average damage
        topD = float(data['td'])  # Top damage
        avgF = float(data['af'])  # Average frags
        topF = float(data['tf'])  # Top frags
        dD = dmg_per_battle - avgD
        dF = frg_per_battle - avgF
        minD = avgD * 0.4
        minF = avgF * 0.4
        if dmg_per_battle >= avgD:
            d = 1 + dD / (topD - avgD)
        else:
            d = 1 + dD / (avgD - minD)

        if frg_per_battle >= avgF:
            f = 1 + dF / (topF - avgF)
        else:
            f = 1 + dF / (avgF - minF)
        d = max(0, d)
        f = max(0, f)
        t = (d * CD + f * CF) / (CD + CF) * 1000.0
        for i, v in enumerate(data['x']):
            if v > t:
                return i
        return 100

    def calculateXTDB(self, vehCD, dmg_per_battle):
        data = self.getXtdbData(vehCD)
        if not isinstance(data, dict) or not valid_scale(data.get('x')) or not finite_number(dmg_per_battle):
            return -1
        for i, v in enumerate(data['x']):
            if v > dmg_per_battle:
                return i
        return 100

    def getXtdbDataArray(self, vehCD):
        data = self.getXtdbData(vehCD)
        return data['x'] if isinstance(data, dict) and valid_scale(data.get('x')) else []


try:
    scaleValuesInstance = ScaleValues()
    getVehicleInfoData = scaleValuesInstance.getVehicleInfoData
    calculateXvmScale = scaleValuesInstance.calculateXvmScale
    calculateXTDB = scaleValuesInstance.calculateXTDB
    calculateXTE = scaleValuesInstance.calculateXTE
except ImportError:
    LOG.exception('Statistics scale could not be imported')
