from kitty.cmds import set_colors
from kitty.config import parse_config
from kitty.constants import config_dir
from kitty.rgb import color_as_int, Color
import os

def main(args):
    pass

def handle_result(args, data, target_window_id, boss):
    colors = {}

    for spec in args[1:]:
        if '=' in spec:
            colors.update(parse_config((spec.replace('=', ' '),)))
        else:
            with open(os.path.join(config_dir, spec), encoding='utf-8', errors='replace') as f:
                colors.update(parse_config(f))

    colors = {k: color_as_int(v) for k, v in colors.items() if isinstance(v, Color)}
    set_colors(boss, boss.window_id_map.get(target_window_id),
            { 'all': False, 'match_window': False, 'match_tab': False, 'reset': False, 'configured': False, 'colors': colors })

handle_result.no_ui = True

if __name__ == '__main__':
    import sys
    main(sys.argv)
