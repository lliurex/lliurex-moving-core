# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension
import os
import subprocess




setup(  name             = "Lliurex-moving-core",
        version          = "2.0",
        author           = "Enrique Medina Gremaldos",
        author_email     = "quiqueiii@gmail.com",
        url              = "http://lliurex.net/home/",
        package_dir      = {'': 'src'},
        packages         = ['net','net.Lliurex','net.Lliurex.Classroom','net.Lliurex.Classroom.MovingProfiles'],
        data_files       = [("/usr/bin/",["bin/llx-moving-cmd","bin/llx-moving-gnome"]),("/etc/profile.d/",["profile.d/llx-moving-load.sh"]),
                                 ("/etc/systemd/logind.conf.d/",["logind.conf.d/llx-moving-gnome.conf"]),("/etc/xdg/autostart/",["llx-moving-gnome.desktop"]),
                                 ("/usr/share/lliurex-moving-core/postactions/",["postactions/050-whiskermenu.sh","postactions/060-remove_libreoffice_lock.sh","postactions/065-fix_libreoffice_save_path","postactions/070-remove_firefox_lock.sh"])]
     )


