#!/bin/env/ python

# Emajourn - turn emails into Day One entries -- dayoneapp.com
#
# Author: Isaac Grant
#
# Copyright (C) 2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import imaplib, json, email, subprocess, os, time, sys


class Image(object):
	def __init__(self, name, file_type, data):
		self.name = name
		self.file_type = file_type
		self.data = data

	def get_filename(self):
		return '{name}.{f_type}'.format(name=self.name, f_type=self.file_type)

	def save(self, location):
		ffile = '{root}{filename}'.format(root=location, filename=self.get_filename())
		with open(ffile, 'wb') as fb:
			fb.write(self.data)

	def delete(self, location):
		os.remove('{root}{filename}'.format(root=location, filename=self.get_filename()))

	def __str__(self):
		return '%s.%s' % (self.name, self.file_type)



class DayOneEntry(object):
	def __init__(self, body, date, image=None):
		self.body = body
		if date[-5] in ['+', '-']:
			self.date = time.strptime(date, '%a, %d %b %Y %H:%M:%S {zone}'.format(zone=date[-5:]))
		else:
			self.date = time.strptime(date, '%a, %d %b %Y %H:%M:%S')
		self.image = image

	def create(self, image_dir):
		cmd = 'dayone'
		if self.date: cmd += ' -d=\"%s\"' % time.strftime('%m/%d/%Y %I:%M:%S%p', self.date)
		if self.image: cmd += ' -p={dirr}{filename}'.format(dirr=image_dir, filename=self.image.get_filename())
		cmd += ' new'
		subprocess.check_call('echo \"%s\" | %s' % (self.body, cmd))

	def __str__(self):
		return '{date} (Contains images: {image}): {body}'.format(date=time.strftime('%m/%d/%Y %I:%M:%S%p', self.date), image=True if self.image else False, body=self.body)


# Dummy exception for problems with the MailHandler.get_mail function
class IMAPException(Exception): pass

class MailHandler(object):
	def __init__(self, server, port, ssl, username, password):
		if ssl:
			self._connection = imaplib.IMAP4_SSL(server, port)
		else:
			self._connection = imaplib.IMAP4(server, port)

		self._connection.login(username, password)
		self.logged_in = True

	def terminate(self):
		self._connection.logout()
		self._connection.close()
		self.logged_in = False

	def get_mail(self, folder, maxx, delete_processed=True):
		mail = []
		status, _ = self._connection.select(folder)
		if str(status) == 'OK':
			status, data = self._connection.search(None, 'ALL')
			if str(status) == 'OK':
				n = 0
				for i in data[0].split():
					status, data = self._connection.fetch(i, '(RFC822)')
					if str(status) == 'OK':
						if delete_processed:
							self._connection.store(i, '+FLAGS', '\\Deleted')
						mail.append(email.message_from_string('\n'.join(str(data[0][1]).split('\\r\\n'))))
						n += 1
						if n == maxx: break
					else:
						raise IMAPException('Error fetching email from {folder} with id: {id}'.format(folder=folder, id=i))
			else:
				raise IMAPException('Error getting ids of emails in \"%s\" folder' % folder)
		else:
			raise IMAPException('Error selecting folder: %s' % folder)
		return mail



def convert_email_to_entry(message):
	if message.is_multipart():
		entry = DayOneEntry(None, message['date'])
		for _message in message.get_payload():
			if 'image' in _message.get_content_type():
				raw = str(_message.get_payload(decode=1))[5:].replace('\\n', '\n')
				filename = raw.split('\n')[0][9:].replace('"', '')
				raw = raw[raw.find('\n')+1:]
				attachment = email.message_from_string(raw)
				entry.image = Image(filename[:filename.rfind('.')], filename[filename.rfind('.')+1:], attachment.get_payload(decode=1))
			elif 'text/plain' == _message.get_content_type():
				entry.body = _message.get_payload(decode=1).decode()
			elif 'multipart/alternative' == _message.get_content_type():
				for part in _message.get_payload():
					if 'text/plain' == part.get_content_type():
						entry.body = part.get_payload(decode=1).decode()
		return entry
	else:
		if 'text/plain' == message.get_content_type():
			entry = DayOneEntry(message.get_payload(decode=1).decode(), message['date'])
			return entry

def get_settings():
	with open('config.json', 'r') as config:
		settings = json.load(config)
	return settings


if __name__ == '__main__':
	settings = get_settings()
	if not os.path.exists(settings['images_folder']):
		os.mkdir(settings['images_folder'])

	mailbox = MailHandler(settings['imap_server'], settings['imap_port'],
						  settings['use_ssl'], settings['imap_username'],
						  settings['imap_password'])
	
	mail = mailbox.get_mail(settings['folder'], settings['processing_count'], not '--no-delete' in sys.argv)
	for message in mail:
		e = convert_email_to_entry(message)
		if e.image:
			e.image.save(settings['images_folder'])
			e.create(settings['images_folder'])
			e.image.delete(settings['images_folder'])
	print('Successfully processed %s emails!' % len(mail))