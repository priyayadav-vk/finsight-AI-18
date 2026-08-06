import io
import json
import time
import unittest
from unittest.mock import mock_open, patch
from backend.config import ALL_INDIAN_COMPANIES, AVAILABILITY_CACHE_TTL
from backend.utils.data_fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):
    def test_bse_ticker_resolves_to_nse_symbol(self):
        fetcher = DataFetcher()
        self.assertEqual(fetcher._resolve_ticker_for_yahoo('500002.BO'), '3MINDIA.NS')

    def test_get_supported_companies_does_not_use_local_data_when_yahoo_unavailable(self):
        fetcher = DataFetcher()

        with patch('backend.utils.data_fetcher.os.path.exists', return_value=False):
            with patch.object(fetcher, '_load_availability_cache', return_value={}):
                with patch.object(fetcher, '_is_yahoo_service_available', return_value=False):
                    with patch.object(fetcher, 'has_local_data', return_value=True):
                        supported = fetcher.get_supported_companies(force_refresh=True)
                        self.assertEqual(supported, {})

    def test_get_supported_companies_uses_cached_list_when_yahoo_unavailable(self):
        fetcher = DataFetcher()
        cache_data = {
            'timestamp': time.time(),
            'supported_companies': ['Adani Total Gas']
        }

        with patch('backend.utils.data_fetcher.os.path.exists', return_value=False):
            with patch.object(fetcher, '_load_availability_cache', return_value=cache_data):
                with patch.object(fetcher, '_is_yahoo_service_available', return_value=False):
                    supported = fetcher.get_supported_companies(force_refresh=True)
                    self.assertIn('Adani Total Gas', supported)
                    self.assertEqual(len(supported), 1)

    def test_get_supported_companies_uses_live_mapping_when_yahoo_unavailable(self):
        fetcher = DataFetcher()
        live_names = ['Asian Paints India', 'Adani Enterprises']
        live_data = json.dumps(live_names)

        def exists(path):
            return path.endswith('live_supported_companies.json')

        m = mock_open(read_data=live_data)

        with patch('backend.utils.data_fetcher.os.path.exists', side_effect=exists):
            with patch('backend.utils.data_fetcher.open', m):
                with patch.object(fetcher, '_load_availability_cache', return_value={}):
                    with patch.object(fetcher, '_is_yahoo_service_available', return_value=False):
                        supported = fetcher.get_supported_companies(force_refresh=True)
                        self.assertIn('Asian Paints India', supported)
                        self.assertEqual(supported['Asian Paints India']['NSE'], ALL_INDIAN_COMPANIES['Asian Paints India']['NSE'])
                        self.assertEqual(len(supported), 2)

    def test_get_supported_companies_merges_local_and_verified_data_on_force_refresh(self):
        fetcher = DataFetcher()
        live_names = ['3M India Limited', 'Asian Paints India']
        live_data = json.dumps(live_names)
        verified_data = json.dumps({
            'Asian Paints India': {
                'NSE': 'ASIANPAINT.NS',
                'BSE': '500820.BO',
                'sector': 'Paint'
            }
        })

        def exists(path):
            return path.endswith('live_supported_companies.json') or path.endswith('yahoo_live_companies.json')

        def fake_open(path, mode='r', encoding=None):
            if path.endswith('live_supported_companies.json'):
                return io.StringIO(live_data)
            if path.endswith('yahoo_live_companies.json'):
                return io.StringIO(verified_data)
            raise FileNotFoundError(path)

        with patch('backend.utils.data_fetcher.os.path.exists', side_effect=exists):
            with patch('backend.utils.data_fetcher.open', fake_open):
                with patch.object(fetcher, '_is_yahoo_service_available', return_value=True):
                    supported = fetcher.get_supported_companies(force_refresh=True)
                    self.assertIn('3M India Limited', supported)
                    self.assertIn('Asian Paints India', supported)
                    self.assertEqual(supported['3M India Limited']['NSE'], ALL_INDIAN_COMPANIES['3M India Limited']['NSE'])
                    self.assertEqual(supported['Asian Paints India']['NSE'], 'ASIANPAINT.NS')

    def test_get_supported_companies_rejects_stale_cache_when_yahoo_unavailable(self):
        fetcher = DataFetcher()
        cache_data = {
            'timestamp': time.time() - (AVAILABILITY_CACHE_TTL + 10),
            'supported_companies': ['Adani Total Gas']
        }

        with patch('backend.utils.data_fetcher.os.path.exists', return_value=False):
            with patch.object(fetcher, '_load_availability_cache', return_value=cache_data):
                with patch.object(fetcher, '_is_yahoo_service_available', return_value=False):
                    supported = fetcher.get_supported_companies(force_refresh=True)
                    self.assertEqual(supported, {})

    def test_check_yahoo_status_returns_status_dict(self):
        fetcher = DataFetcher()
        with patch.object(fetcher, '_is_yahoo_service_available', return_value=False):
            status = fetcher.check_yahoo_status()
            self.assertIsInstance(status, dict)
            self.assertIn('available', status)
            self.assertIn('message', status)
            self.assertIn('last_checked', status)
            self.assertFalse(status['available'])

    def test_check_yahoo_status_message_is_fallback_friendly(self):
        fetcher = DataFetcher()
        with patch.object(fetcher, '_probe_yahoo_status', return_value=(False, 'HTTP Error 401: Unauthorized')):
            status = fetcher.check_yahoo_status('RELIANCE.NS')
            self.assertFalse(status['available'])
            self.assertIn('fallback', status['message'].lower())

    def test_check_yahoo_status_uses_ist_timestamp(self):
        fetcher = DataFetcher()
        with patch.object(fetcher, '_probe_yahoo_status', return_value=(False, 'HTTP Error 401: Unauthorized')):
            status = fetcher.check_yahoo_status('RELIANCE.NS')
            self.assertIn('IST', status['last_checked'])

    def test_live_fetch_uses_demo_when_recent_failure_exists(self):
        fetcher = DataFetcher()
        fetcher._set_recent_failure('RELIANCE_NS', 'live', 'recent failure')
        with patch('backend.utils.data_fetcher.yf.Ticker', side_effect=AssertionError('Yahoo should not be called')):
            result = fetcher.fetch_live_data('RELIANCE.NS')
        self.assertTrue(result.get('is_demo'))
        self.assertTrue(result.get('is_fallback'))


if __name__ == '__main__':
    unittest.main()
