from django import http

from nose.tools import eq_
import test_utils

from amo.urlresolvers import reverse
from reviews.models import Review, ReviewFlag


class TestViews(test_utils.TestCase):
    fixtures = ['reviews/dev-reply.json']

    def test_dev_reply(self):
        url = reverse('reviews.detail', args=[1865, 218468])
        r = self.client.get(url)


class TestFlag(test_utils.TestCase):
    fixtures = ['reviews/dev-reply.json', 'base/admin']

    def setUp(self):
        self.url = reverse('reviews.flag', args=[1865, 218468])
        self.client.login(username='jbalogh@mozilla.com', password='password')

    def test_no_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        assert isinstance(response, http.HttpResponseRedirect)

    def test_new_flag(self):
        response = self.client.post(self.url, {'flag': 'spam'})
        eq_(response.status_code, 200)
        eq_(response.content, '{"msg": "Thanks; this review has been '
                                       'flagged for editor approval."}')
        eq_(ReviewFlag.objects.filter(flag='spam').count(), 1)
        eq_(Review.objects.filter(editorreview=True).count(), 1)

    def test_update_flag(self):
        response = self.client.post(self.url, {'flag': 'spam'})
        eq_(response.status_code, 200)
        eq_(ReviewFlag.objects.filter(flag='spam').count(), 1)
        eq_(Review.objects.filter(editorreview=True).count(), 1)

        response = self.client.post(self.url, {'flag': 'language'})
        eq_(response.status_code, 200)
        eq_(ReviewFlag.objects.filter(flag='language').count(), 1)
        eq_(ReviewFlag.objects.count(), 1)
        eq_(Review.objects.filter(editorreview=True).count(), 1)

    def test_flag_with_note(self):
        response = self.client.post(self.url, {'flag': 'spam', 'note': 'xxx'})
        eq_(response.status_code, 200)
        eq_(ReviewFlag.objects.filter(flag='other').count(), 1)
        eq_(ReviewFlag.objects.count(), 1)
        eq_(ReviewFlag.objects.get(flag='other').note, 'xxx')
        eq_(Review.objects.filter(editorreview=True).count(), 1)

    def test_bad_flag(self):
        response = self.client.post(self.url, {'flag': 'xxx'})
        eq_(response.status_code, 400)
        eq_(Review.objects.filter(editorreview=True).count(), 0)
