# -*- coding: utf-8 -*-
from setuptools import setup

setup(  name             = "Lliurex-moving-core",
        version          = "4.5",
        author           = "Enrique Medina Gremaldos",
        author_email     = "quiqueiii@gmail.com",
        url              = "http://lliurex.net/home/",
        packages         = ['lliurex.moving'],
        data_files       = [("/usr/bin/",["bin/llx-moving-cmd","bin/llx-moving-service"]),
                                 ("/etc/X11/Xsession.d/",["95lliurex-moving-load"]),
                                 ("/etc/xdg/lliurex/desktop/plasma-workspace/shutdown",["95lliurex-moving-save"]),
                                 ("/etc/systemd/logind.conf.d/",["logind.conf.d/net.lliurex.moving-profiles.conf"]),
                                 ("/usr/share/lliurex-moving-core/postactions/",["postactions/050-fix-xbel","postactions/060-remove_libreoffice_lock.sh","postactions/065-fix_libreoffice_save_path","postactions/070-remove_firefox_lock.sh"])]
     )


