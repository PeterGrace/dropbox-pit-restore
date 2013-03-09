from dropbox import client, rest, session
import pdb
from dateutil import parser

APP_KEY = ''
APP_SECRET = ''

ACCESS_TYPE = 'dropbox'  # should be 'dropbox' or 'app_folder' as configured for your app


class StoredSession(session.DropboxSession):
    """a wrapper around DropboxSession that stores a token to a file on disk"""
    TOKEN_FILE = "token_store.txt"

    def load_creds(self):
        try:
            stored_creds = open(self.TOKEN_FILE).read()
            self.set_token(*stored_creds.split('|'))
            print "[loaded access token]"
	    return True
        except IOError:
            pass # don't worry if it's not there
    	   
    	return False

    def write_creds(self, token):
        f = open(self.TOKEN_FILE, 'w')
        f.write("|".join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(self.TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        print "url:", url
        print "Please authorize in the browser. After you're done, press enter."
        raw_input()

        self.obtain_access_token(request_token)
        self.write_creds(self.token)

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)

def main():
    mydate=parser.parse("Tue, 18 Dec 2012 22:40:00 -0500")
    if APP_KEY == '' or APP_SECRET == '':
        exit("You need to set your APP_KEY and APP_SECRET!")
    sess = StoredSession(APP_KEY,APP_SECRET, access_type=ACCESS_TYPE)
    if not sess.load_creds():
	    sess.link()
    miclient = client.DropboxClient(sess)
    print "Checking for revisions of file"
    #pdb.set_trace()
    filelist = miclient.search('/minecraft-saves/HC-2012-12-17','.')
    for f in filelist:
	    revs = miclient.revisions(f['path'])
	    for r in revs:
		    revdate = parser.parse(r['client_mtime'])
		    if revdate < mydate:
		    	print "Rstoring File: %s Edited: %s Revision %s" % (r['path'],r['client_mtime'],r['revision'])
			miclient.restore(r['path'],r['rev'])
			break

if __name__ == '__main__':
    main()
