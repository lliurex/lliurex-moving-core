import n4d.client

import re
import fnmatch
import os
import subprocess
import shutil
import glob
import logging

import locale
import gettext

locale.textdomain("xdg-user-dirs")
gettext.textdomain("xdg-user-dirs")

logging.basicConfig(format='%(levelname)s %(funcName)s %(message)s',
                    level=logging.INFO)


class Client:
    def __init__(self, address="https://server:9779"):

        self.ignore = {
            "/": [".xinputrc"],
            ".config": [
                "/user-dirs.*", "/google-chrome/Singleton*",
                "/chromium/Singleton*", "/libreoffice/4/.lock", "/pulse"
            ],
            ".mozilla":
            ["/firefox/*.default/storage", "/firefox/*.default/lock"],
            ".local": [
                "/share/teamviewer*", "/share/Trash/*",
                "/share/gvfs-metadata/*", "/share/kscreen/*"
            ]
        }

        self.client = n4d.client.Client(address)
        #perform a cached read
        self.cfg = self.client.MovingProfiles.get_list()

    def is_include(self, filename):

        reti = []
        for name in self.cfg["include"]:
            value = self.cfg["include"][name]
            if fnmatch.fnmatchcase(filename, value):
                reti.append(name)

        if len(reti) == 0:
            return None
        else:
            return reti

    def is_exclude(self, filename):

        rete = []
        for name in self.cfg["exclude"]:
            value = self.cfg["exclude"][name]
            if fnmatch.fnmatchcase(filename, value):
                rete.append(name)

        if len(rete) == 0:
            return None
        else:
            return rete

    def match(self, fname):

        include = False

        for name in self.cfg["include"]:
            value = self.cfg["include"][name]
            if fnmatch.fnmatchcase(fname, value):
                include = True

                break

        if include:
            for name in self.cfg["exclude"]:
                value = self.cfg["exclude"][name]
                if fnmatch.fnmatchcase(fname, value):

                    return False

            return True

        else:
            return False

    def match_folder(self, path):

        mlist = []

        for fname in os.listdir(path):
            if (self.match(fname)):
                mlist.append(fname)

        return mlist

    def clear(self):
        self.cfg = {"include": {}, "exclude": {}}

    def save(self):
        self.client.MovingProfiles.save_conf(self.cfg)

    def get_profile_path(self):

        try:

            home = os.path.expanduser("~")
            exec(open(home + "/.config/user-dirs.dirs").read())
            documents_dir = locals()["XDG_DOCUMENTS_DIR"].split("/")[1]
            moving_profiles = "%s/%s/.moving_profiles/" % (home, documents_dir)

        except Exception as e:

            try:
                user = os.getenv("USER")
                documents = gettext.gettext("Documents")
                moving_profiles = "/home/%s/%s/.moving_profiles/" % (user,
                                                                     documents)

            except:
                raise RuntimeError("Failed to construct home path")

        return moving_profiles

    def final_actions(self):

        path = "/usr/share/lliurex-moving-core/postactions/"

        for f in sorted(glob.glob(path + "*")):
            logging.info("* Executing %s ..." % f)
            os.system(f + " || true")

    #def FinalActions

    def load_session(self):
        moving_path = self.get_profile_path()
        home = os.path.expanduser("~")

        if not os.path.exists(moving_path):
            # at least execute final actions before exiting
            self.final_actions()
            raise RuntimeError("Profile dir not found, aborting load")

        logging.info("Synchronization")
        logging.info("Stage 1")

        cmd = ["rsync", "-aAX", "--delete", "--ignore-errors"]
        logging.debug("rsync cmd:" + str(cmd))

        profile_files = self.match_folder(moving_path)

        for fname in profile_files:
            logging.info("[rsync] " + fname)

            ecmd = []
            if (fname in self.ignore):
                elist = self.ignore[fname]
                for erule in elist:
                    ecmd.append("--exclude=%s" % erule)
                    logging.info("* excluding: " + erule)

            source = '%s/%s' % (moving_path, fname)
            destination = '%s/%s' % (home, fname)

            if (os.path.isdir(source)):
                source = source + "/"
                destination = destination + "/"

            source = '"%s"' % source
            destination = '"%s"' % destination

            rcmd = cmd + ecmd + [source, destination]
            plain_cmd = " ".join(rcmd)
            plain_cmd += " || true"

            subprocess.call(plain_cmd, shell=True)

        logging.info("Stage 2")

        home_files = self.match_folder(home)

        for hname in home_files:
            if not hname in profile_files:
                hpath = home + "/" + hname

                logging.info("[rm] " + hname)

                rm = os.remove

                if (os.path.isdir(hpath)):
                    rm = shutil.rmtree

                rm(hpath)

        # Stage 3
        logging.info("Stage 3")
        self.final_actions()

    def save_session(self):
        moving_path = self.get_profile_path()
        logging.info("Moving path: " + moving_path)

        if not os.path.exists(moving_path):
            logging.info("Creating profile path")
            try:
                os.makedirs(moving_path)
            except:
                raise

        cmd = ["rsync", "-aAX", "--delete", "--ignore-errors"]
        logging.debug("rsync cmd:" + str(cmd))

        home = os.path.expanduser("~")
        logging.info("Synchronization")
        logging.info("Stage 1")

        home_files = self.match_folder(home)
        for fname in home_files:
            fpath = home + "/" + fname

            if (os.path.isdir(fpath)):
                fpath = fpath + "/"

            logging.info("[rsync] " + fname)

            ecmd = []

            if (fname in self.ignore):
                elist = self.ignore[fname]
                for erule in elist:
                    ecmd.append("--exclude=%s" % erule)
                    logging.info("* excluding: " + erule)

            source = home + "/" + fname
            destination = moving_path + "/" + fname

            if (os.path.isdir(source)):
                source = source + "/"
                destination = destination + "/"

            source = '"%s"' % source
            destination = '"%s"' % destination

            rcmd = cmd + ecmd + [source, destination]
            plain_cmd = " ".join(rcmd)
            subprocess.call(plain_cmd, shell=True)

        logging.info("Stage 2")

        for fname in os.listdir(moving_path):
            if not fname in home_files:
                fpath = moving_path + "/" + fname

                logging.info("[rm] " + fname)

                rm = os.remove

                if (os.path.isdir(fpath)):
                    rm = shutil.rmtree

                rm(fpath)

    def backup(self, name):
        backup_path = self.get_profile_path(
        ) + "../.moving_profiles_backup/" + name

        logging.info("Backup path: " + backup_path)

        if (os.path.exists(backup_path)):
            logging.warning(name + " already exists")
            return
        else:
            try:
                os.makedirs(backup_path)
            except:
                raise RuntimeError("Cannot create backup path")

        cmd = ["rsync", "-az", "--delete"]
        logging.debug("rsync cmd:" + str(cmd))

        home = os.path.expanduser("~")

        logging.info("Backing up as " + name)

        home_files = self.match_folder(home)
        for fname in home_files:
            fpath = home + "/" + fname

            if (os.path.isdir(fpath)):
                fpath = fpath + "/"

            logging.info("[rsync] " + fname)

            rcmd = cmd + [fpath, backup_path + "/" + fname]
            subprocess.call(rcmd)
