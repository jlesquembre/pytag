import unittest

from pytag.structures import CaseInsensitiveDict, PytagDict


class CaseInsensitiveDictTest(unittest.TestCase):

    def test_mapping_init(self):
        cid = CaseInsensitiveDict({'Foo': 'foo', 'BAr': 'bar'})
        self.assertEqual(len(cid), 2)
        self.assertTrue('foo' in cid)
        self.assertTrue('bar' in cid)

    def test_iterable_init(self):
        cid = CaseInsensitiveDict([('Foo', 'foo'), ('BAr', 'bar')])
        self.assertEqual(len(cid), 2)
        self.assertTrue('foo' in cid)
        self.assertTrue('bar' in cid)

    def test_kwargs_init(self):
        cid = CaseInsensitiveDict(FOO='foo', BAr='bar')
        self.assertEqual(len(cid), 2)
        self.assertTrue('foo' in cid)
        self.assertTrue('bar' in cid)

    def test_docstring_example(self):
        cid = CaseInsensitiveDict()
        cid['Key'] = 'value'
        self.assertEqual(cid['KEY'], 'value')
        self.assertEqual(cid['KEy'], 'value')
        self.assertEqual(list(cid), ['key'])

    def test_len(self):
        cid = CaseInsensitiveDict({'a': 'a', 'b': 'b'})
        cid['A'] = 'a'
        self.assertEqual(len(cid), 2)

    def test_getitem(self):
        cid = CaseInsensitiveDict({'Spam': 'blueval'})
        self.assertEqual(cid['spam'], 'blueval')
        self.assertEqual(cid['SPAM'], 'blueval')

    def test_setitem(self):
        """__setitem__ should behave case-insensitively."""
        cid = CaseInsensitiveDict()
        cid['spam'] = 'oneval'
        cid['Spam'] = 'twoval'
        cid['sPAM'] = 'redval'
        cid['SPAM'] = 'blueval'
        self.assertEqual(cid['spam'], 'blueval')
        self.assertEqual(cid['SPAM'], 'blueval')
        self.assertEqual(list(cid.keys()), ['spam'])

    def test_delitem(self):
        cid = CaseInsensitiveDict()
        cid['Spam'] = 'someval'
        del cid['sPam']
        self.assertFalse('spam' in cid)
        self.assertEqual(len(cid), 0)

    def test_contains(self):
        cid = CaseInsensitiveDict()
        cid['Spam'] = 'someval'
        self.assertTrue('Spam' in cid)
        self.assertTrue('spam' in cid)
        self.assertTrue('SPAM' in cid)
        self.assertTrue('sPam' in cid)
        self.assertFalse('notspam' in cid)

    def test_get(self):
        cid = CaseInsensitiveDict()
        cid['spam'] = 'oneval'
        cid['SPAM'] = 'blueval'
        self.assertEqual(cid.get('spam'), 'blueval')
        self.assertEqual(cid.get('SPAM'), 'blueval')
        self.assertEqual(cid.get('sPam'), 'blueval')
        self.assertEqual(cid.get('notspam', 'default'), 'default')

    def test_update(self):
        cid = CaseInsensitiveDict()
        cid['spam'] = 'blueval'
        cid.update({'sPam': 'notblueval'})
        self.assertEqual(cid['spam'], 'notblueval')
        cid = CaseInsensitiveDict({'Foo': 'foo', 'BAr': 'bar'})
        cid.update({'fOO': 'anotherfoo', 'bAR': 'anotherbar'})
        self.assertEqual(len(cid), 2)
        self.assertEqual(cid['foo'], 'anotherfoo')
        self.assertEqual(cid['bar'], 'anotherbar')

    def test_update_retains_unchanged(self):
        cid = CaseInsensitiveDict({'foo': 'foo', 'bar': 'bar'})
        cid.update({'foo': 'newfoo'})
        self.assertEquals(cid['bar'], 'bar')

    def test_iter(self):
        cid = CaseInsensitiveDict({'Spam': 'spam', 'Eggs': 'eggs'})
        keys = frozenset(['spam', 'eggs'])
        self.assertEqual(frozenset(iter(cid)), keys)

    def test_equality(self):
        cid = CaseInsensitiveDict({'SPAM': 'blueval', 'Eggs': 'redval'})
        othercid = CaseInsensitiveDict({'spam': 'blueval', 'eggs': 'redval'})
        self.assertEqual(cid, othercid)
        del othercid['spam']
        self.assertNotEqual(cid, othercid)
        self.assertEqual(cid, {'spam': 'blueval', 'eggs': 'redval'})

    def test_setdefault(self):
        cid = CaseInsensitiveDict({'Spam': 'blueval'})
        self.assertEqual(
            cid.setdefault('spam', 'notblueval'),
            'blueval'
        )
        self.assertEqual(
            cid.setdefault('notspam', 'notblueval'),
            'notblueval'
        )

    def test_make_key_lowercase(self):
        cid = CaseInsensitiveDict({
            'Accept': 'application/json',
            'user-Agent': 'requests',
        })
        keyset = frozenset(['accept', 'user-agent'])
        self.assertEqual(frozenset(i[0] for i in cid.items()), keyset)
        self.assertEqual(frozenset(cid.keys()), keyset)
        self.assertEqual(frozenset(cid), keyset)

    def test_preserve_last_key_case(self):
        cid = CaseInsensitiveDict({
            'Accept': 'application/json',
            'user-Agent': 'requests',
        })
        cid.update({'ACCEPT': 'application/json'})
        cid['USER-AGENT'] = 'requests'
        keyset = frozenset(['accept', 'user-agent'])
        self.assertEqual(frozenset(i[0] for i in cid.items()), keyset)
        self.assertEqual(frozenset(cid.keys()), keyset)
        self.assertEqual(frozenset(cid), keyset)

    def test_copy(self):
        cid = CaseInsensitiveDict({'SPAM': 'blueval', 'Eggs': 'redval'})
        othercid = cid.copy()
        d = {'spam': 'blueval', 'eggs': 'redval'}
        self.assertEqual(cid, othercid)
        self.assertEqual(cid, d)
        self.assertEqual(othercid, d)
        del othercid['spam']
        self.assertNotEqual(cid, othercid)
        self.assertEqual(cid, d)
        self.assertNotEqual(othercid, d)


class PytagDictTest(unittest.TestCase):

    def test_init_valid(self):
        cid = PytagDict({'TITLE': 'foo', 'album': 'bar'})
        self.assertEqual(len(cid), 2)
        self.assertTrue('title' in cid)
        self.assertTrue('album' in cid)

    def test_init_not_valid(self):
        cid = PytagDict({'Foo': 'foo', 'BAr': 'bar'})
        self.assertEqual(len(cid), 0)
        self.assertFalse('foo' in cid)
        self.assertFalse('bar' in cid)
