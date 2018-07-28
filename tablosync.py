import subprocess
import sys
from os import listdir, path
import unicodedata
import re


class Tablosync():

    def __init__(self, ip):
        self.remote = {}
        self.local = {}
        self.new = {}
        self.localPath = "../../media/Movies"
        self.delete = '-d'
        self.export = '-e'
        self.filename = '-f'
        self.update = '-u'
        self.info = '-i'
        self.path = '-p'
        self.quiet = '-q'
        self.search = '-s'
        self.ip = '-ip'
        self.dump = '-dump'

        # Setup Tablo
        pipe = subprocess.Popen(["./capto", self.ip, ip, self.update], stdout=None)
        pipe.communicate()

    def tabloListFiles(self, term="MOVIES"):
        pipe = subprocess.Popen(["./capto", self.search, term], stdout=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        stdout = stdout.decode('utf-8').split("\n")
        stdout = filter(None, stdout)
        for file in stdout:
            file = file[8:]
            title = file.split(")")[1][1:] + ")"
            title = self.safeFileName(title)
            id = int(file[file.find("(") + 1:file.find(")")])
            timestamp = file[file.find("[") + 1:file.find("]")]
            self.remote[id] = {'title': title, 'datetime': timestamp}
        return self.remote

    def localListFiles(self):
        self.local = [path.splitext(i)[0] for i in listdir(self.localPath)]
        return self.local

    def compareLists(self):
        for key in self.remote:
            if self.remote[key]['title'] not in self.local:
                self.new[key] = self.remote[key]
        return self.new

    def safeFileName(self, name):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
        name = str(re.sub('[^\w\s[\-\(\)]', '', name).strip())
        return name

    def query_yes_no(self, question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    def sync(self, id):
        pipe = subprocess.Popen(["./capto", self.export, str(id), self.path, self.localPath], stdout=subprocess.PIPE)
        pipe.communicate()

if __name__ == '__main__':
    sync = Tablosync('192.168.1.166')
    sync.tabloListFiles()
    sync.localListFiles()
    new = sync.compareLists()
    # List new files
    for key in new:
        print(new[key]['title'])
    if sync.query_yes_no("Load these files?"):
        # Sync new files
        for key in new:
            print("Loading "+ new[key]['title'])
            sync.sync(key)
