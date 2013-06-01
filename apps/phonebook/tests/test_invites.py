from django.contrib.auth.models import User
from django.core import mail

from funfactory.urlresolvers import reverse
from nose.tools import eq_
from pyquery import PyQuery as pq

import apps.common.tests.init
from apps.common.browserid_mock import mock_browserid

from ..models import Invite


class InviteFlowTest(apps.common.tests.init.ESTestCase):
    fake_email = 'mr.fusion@gmail.com'
    fake_email2 = 'mrs.fusion@gmail.com'
    fake_email3 = 'ms.fusion@gmail.com'

    # Assertion doesn't matter since we monkey patched it for testing
    fake_assertion = 'mrfusionsomereallylongstring'
    fake_invite_message = 'Join Mozilla'
  
    fake_user = None
  
    def create_fake_user(self):
            fake_user = User.objects.create(email=self.fake_email3, username='mozymike')
            profile = fake_user.get_profile()
            profile.is_vouched = True
            profile.full_name='Michal Mozillianin'
            profile.country = 'pl'
            profile.save()        

    def invite_someone(self, email, invite_message):
        """This method will invite a user.

        This will verify that an email with link has been sent.
        """
        # login as fake user.
        d = dict(assertion=self.fake_assertion)
        with mock_browserid(self.fake_email3):
            self.client.post(reverse('browserid_verify'), d, follow=True)

        # Send an invite.
        url = reverse('invite')
        d = dict(recipient=email, message=invite_message)
        r = self.mozillian_client.post(url, d, follow=True)
        eq_(r.status_code, 200)
        assert ('%s has been invited to Mozillians.' % email in
                pq(r.content)('div.alert-success').text())

        # See that the email was sent.
        eq_(len(mail.outbox), 1)

        i = Invite.objects.get()
        invite_url = i.get_url()

        assert 'no-reply@mozillians.org' in mail.outbox[0].from_email
        assert invite_url in mail.outbox[0].body, "No link in email."
        return i

    def get_register(self, invite):
        r = self.client.get(invite.get_url(), follow=True)
        eq_(self.client.session['invite-code'], invite.code)
        return r

    def redeem_invite(self, invite, email):
        """Given an invite_url go to it and redeem an invite."""
        # Lets make sure we have a clean slate
        self.client.logout()
        assert not User.objects.filter(email=email), (
            "User shouldn't be in database.")

        # We need to store the invite code in the session
        self.client.get(invite.get_url(), follow=True)

        # BrowserID needs an assertion not to be whiney
        d = dict(assertion=self.fake_assertion)
        with mock_browserid(email):
            self.client.post(reverse('browserid_verify'), d, follow=True)

        # Now let's register
        d = dict(full_name='Desaaaaaaai',
                 username='aakash',
                 country='pl',
                 optin=True)
        with mock_browserid(email):
            self.client.post(reverse('register'), d, follow=True)

        # Return the New Users Profile
        invited_user_profile = User.objects.get(email=email).get_profile()
        return invited_user_profile

    def invite_without_message(self, email):
        """
        Make sure we can send an invite without the optional personal
        message and that the template doesn't use Personal message:
        when there's no personal message.
        """
        #login as fake user.
        d = dict(assertion=self.fake_assertion)
        with mock_browserid(self.fake_email3):
            self.client.post(reverse('browserid_verify'), d, follow=True)

        # Send an invite without a personal message.
        url = reverse('invite')
        d = dict(recipient=email)
        r = self.mozillian_client.post(url, d, follow=True)
        eq_(r.status_code, 200)
        assert ('%s has been invited to Mozillians.' % email in
                pq(r.content)('div.alert-success').text())

        # See that the email was sent.
        eq_(len(mail.outbox), 2)

        # Note it's mail.outbox[1] here because we're sending another
        # message in a previous test.
        assert not ("Personal message" in mail.outbox[1].body)

    def test_send_invite_flow(self):
        """
        Test the invitation flow.

        Send an invite.  See that email is sent.
        See that link allows us to sign in and be auto-vouched.
        Verify that we can't reuse the invite_url
        Verify we can't reinvite a vouched user
        """
        self.create_fake_user()
        invite = self.invite_someone(self.fake_email, self.fake_invite_message)
        self.invite_without_message(self.fake_email)
        self.get_register(invite)
        invited_user_profile = self.redeem_invite(invite, self.fake_email)
        assert(invited_user_profile.is_vouched)
        assert(invite.inviter == invited_user_profile.vouched_by)

        # Don't reuse codes.
        self.redeem_invite(invite, email='mr2@gmail.com')
        eq_(User.objects.get(email='mr2@gmail.com').get_profile().is_vouched,
            False)


class InviteEdgeTest(apps.common.tests.init.ESTestCase):

    def test_no_reinvite(self):
        """Don't reinvite a vouched user."""
        vouched_email = 'mr.fusion@gmail.com'
        create_vouched_user(vouched_email)
        url = reverse('invite')
        d = dict(recipient=vouched_email)
        r = self.mozillian_client.post(url, d, follow=True)
        eq_(r.status_code, 200)
        assert ('You cannot invite someone who has already been vouched.' in
                pq(r.content).text())

    def test_unvouched_cant_invite(self):
        """Let's make sure the unvouched don't let in their friends.

        Their stupid friends...
        """
        url = reverse('invite')
        data = {'recipient': 'mr.fusion@gmail.com'}
        response = self.pending_client.post(url, data, follow=True)
        eq_(response.status_code, 200)
        assert('You must be vouched to continue.' in response.content)


def create_vouched_user(email):
        user = User.objects.create(email=email, username=email)
        profile = user.get_profile()
        profile.is_vouched = True
        profile.full_name='Amandeep McIlrath'
        profile.save()
        return user
