from termios import error, tcgetattr, ECHO, ICANON, ISIG, ECHOCTL, ECHOKE
import re
import subprocess
import sys

def main(args):
    if not sys.stdin.isatty():
        data = sys.stdin.read().strip().split('\n')[-1]
        return data
    else:
        print("\a")
        print("Tried to read a tty")

def handle_result(args, data, target_window_id, boss):
    w = boss.window_id_map.get(target_window_id)
    if w is not None:
        fd = w.child.child_fd
        try:
            c_lflag = tcgetattr(fd)[3]
        except error as err:
            errmsg = 'getecho() may not be called on this platform'
            if err.args[0] == errno.EINVAL:
                raise IOError(err.args[0], '%s: %s.' % (err.args[1], errmsg))
            raise

        def send_password():
            password = subprocess.run(args[1:], capture_output=True, text=True, check=True).stdout
            w.paste(password + '\r')

        def is_set(flag):
            return bool(c_lflag & flag)

        # print(f'c_lflag={c_lflag} icanon={c_lflag & ICANON} echo={c_lflag & ECHO} echoctl={c_lflag & ECHOCTL} echoke={c_lflag & ECHOKE} isig={c_lflag & ISIG} data={repr(data)}')
        if is_set(ISIG) and is_set(ICANON) and not is_set(ECHO):
            # ruby -rio/console -e 'STDIN.noecho { |io| puts io.gets.inspect }'
            # sudo <cmd>
            send_password()
        elif not is_set(ISIG) and not is_set(ICANON) and not is_set(ECHO) and re.match(r"Password.*:$", data):
            # ssh -t <host> <cmd> # same socket mode for kinit and cat :(
            send_password()
        else:
            print("\a")
            print("Ooops. Are you at a password prompt?")

handle_result.type_of_input = 'text'

if __name__ == '__main__':
    import sys
    main(sys.argv)
