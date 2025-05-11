import dearpygui.dearpygui as dpg
from typing import List, Dict, Tuple

def show_listbox(label: str, items: List[str], callback=None, user_data=None):
    """
    Displays a listbox with the given items and label using DearPyGui v2.0+ API.
    """
    dpg.add_listbox(label=label, items=items, callback=callback, user_data=user_data, num_items=10)

def show_mapping_arrows(mappings: Dict[str, str], source_positions: Dict[str, Tuple[float, float]], target_positions: Dict[str, Tuple[float, float]]):
    """
    Draws arrows between mapped source and target columns using DearPyGui drawing API.
    """
    for tgt, src in mappings.items():
        src_pos = source_positions.get(src)
        tgt_pos = target_positions.get(tgt)
        if src_pos and tgt_pos:
            dpg.draw_arrow(p1=src_pos, p2=tgt_pos, color=(0, 255, 0, 255), thickness=2) 