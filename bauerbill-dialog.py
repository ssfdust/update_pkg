from dialog import Dialog
import subprocess
import os
import sys
from pickle import dump, load
from datetime import datetime, timedelta

cmds = {
    'search': 'echo {} | sudo -S bauerbill -Ss {} --aur-only',
    'install': 'echo {} | sudo -S bauerbill -S {} --aur-only',
    'update': 'echo {} | sudo -S bauerbill -Su --aur-only'
}
session_file = '/tmp/bauerbill-dialog.session'

def execute(cmd, window):
    subp = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    out, err = subp.communicate()
    out = out.decode()
    err = err.decode()
    if subp.returncode != 0:
        window.msgbox(out + '\n' + err, title="Fatal Error")
        sys.exit(2)
    elif len(err) > 0:
        window.msgbox(err, title="Erro Message")
    return out, err

def build(window):
    if os.path.exists('build'):
        os.chdir('build')
        ret = os.system('bash download.sh')
        if ret != 0:
            window.msgbox('Error occured on downloading...')
            sys.exit(3)
        ret = os.system('MAKEFLAGS="-j$(nproc)" bash build.sh')
        if ret != 0:
            window.msgbox('Error occured on building...')
            sys.exit(3)
        os.chdir('..')
        answer = window.yesno("Would you delete the build directory")
        if answer == 'ok':
            os.system('rm -rf build')
    else:
        window.msgbox("No package directory found", width=38, height=5)

def parse_packages(info, window):
    if len(info) > 0:
        nodes = list(filter(None, info.split('AUR/')))
        choices = []
        for node in nodes:
            package, desc = node.split('\n', 1)
            desc = list(filter(None, desc.split('\n')))
            node_c = [(package if c == 0 else "", i.strip(), 0) for c, i in enumerate(desc)]
            choices.extend(node_c)
        code, tag = window.checklist("Select Packages", choices=choices)
        if code != 'ok':
            window.msgbox("Canceled.Bye~", title='message')
        else:
            tag = list(filter(None, tag))
            tag = [ele.split()[0] for ele in tag]
            packages = ' '.join(tag)

            return packages
    else:
            window.msgbox("No packages.", title='message')

    sys.exit(2)

def main():
    window = Dialog('dialog', autowidgetsize=True)
    passwd = fetchpasswd(window)
    code, mode = window.menu("Would you install new packages or update packages",
                             choices=[
                                 ("install", "install new aur packages"),
                                 ("update", "update local aur packages"),
                             ], title="Mode Selection")
    if mode == 'install':
        code, package = window.inputbox("Please enter the package name:")
        if code == 'ok':
            info, err = execute(cmds['search'].format(passwd, package), window)
            packages = parse_packages(info, window)
            info, err = execute(cmds['install'].format(passwd, packages), window)
            if len(info) > 0:
                window.msgbox(info)
            else:
                window.msgbox("No packages need to update.", width=25, height=5)
        else:
            window.msgbox("Bye~")
            sys.exit(0)
    elif mode == 'update':
        info, err = execute(cmds['update'].format(passwd), window)
        if 'Installed orphans' in err:
            answer = window.yesno("Do you want to delete the orphan packages?")
            if answer == 'ok':
                orphans(err, passwd, window)
        if len(info) > 0:
            window.msgbox(info)

    build(window)

def fetchpasswd(window):
    passwd = restorepasswd()
    use_sotre = False
    if passwd is None:
        code, passwd = window.passwordbox("Please enter your user password:")
        use_sotre = True
    else:
        code = 'ok'
    if code == 'ok':
        chk = subprocess.Popen('sudo -k'.format(passwd), shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        chk.communicate()
        chk = subprocess.Popen('echo {} | sudo -S ls'.format(passwd), shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        chk.communicate()
        while chk.returncode != 0:
            window.msgbox("Wrong password!", width=25, height=5)
            code, passwd = window.passwordbox("Please enter your user password:")
            if code == 'ok':
                chk = subprocess.Popen('echo {} | sudo -S ls'.format(passwd), shell=True,
                                       stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                chk.communicate()
            else:
                window.msgbox("No password.Abort!", width=25, height=5)
                sys.exit(3)
    else:
        window.msgbox("No password.Abort!", width=25, height=3)
        sys.exit(3)

    if use_sotre:
        storepasswd(passwd)
    return passwd

def orphans(err, passwd, window):
    packages = err.split('Installed orphans:')[1].strip()
    pac_list = [(i, "", True) for i in packages.split()]
    code, tag = window.checklist("Select Packages", choices=pac_list)
    if code == 'ok':
        packages = ' '.join(tag)
        cmd = 'echo {} | sudo -S pacman -R --noconfirm {}'.format(passwd, packages)
        info, err = execute(cmd, window)
        window.msgbox(info, title="Pacman Log")

def storepasswd(passwd):
    session = {'passwd': passwd, 'time': datetime.now()}
    with open(session_file, 'wb') as f:
        dump(session, f)

    return True

def restorepasswd():
    passwd = None
    if os.path.exists(session_file):
        with open(session_file, 'rb') as f:
            session = load(f)
            if session['time'] > datetime.now() - timedelta(minutes=180):
                passwd = session['passwd']

    return passwd


if __name__ == '__main__':
    main()
