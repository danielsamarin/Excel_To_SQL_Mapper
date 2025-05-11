import dearpygui.dearpygui as dpg
from excel_utils import read_excel_columns
from mssql_utils import get_mssql_table_columns
from mapping_utils import generate_insert_scripts
import os

# Global state
state = {
    'excel_path': None,
    'excel_columns': [],
    'excel_df': None,
    'mssql_info': {},
    'table_columns': [],
    'mapping': {},  # {target: source}
    'sql_scripts': [],
    'log_messages': '',
    'node_ids': {},  # {col_name: node_id}
    'attr_ids': {},  # {col_name: attr_id}
    'link_ids': {},  # {link_id: (src, tgt)}
}

# Constants for drawing
CANVAS_WIDTH = 300
CANVAS_HEIGHT = 300
LISTBOX_TOP = 40
ITEM_HEIGHT = 30
LISTBOX_X_OFFSET = 20
SOURCE_X = LISTBOX_X_OFFSET
TARGET_X = CANVAS_WIDTH - LISTBOX_X_OFFSET
DOT_RADIUS = 18
NODE_WIDTH = 120  # Fixed width for all nodes
NODE_ATTR_HEIGHT = 30  # Height for easier clicking

# Store the last right-clicked link
last_right_clicked_link = {'link_id': None}

def log_message(message, level='info'):
    msg = f"[{level.upper()}] {message}\n"
    state['log_messages'] += msg
    if dpg.does_item_exist('log_output'):
        dpg.set_value('log_output', state['log_messages'])
    print(msg, end='')

def import_excel_callback(sender, app_data, user_data):
    file_path = dpg.get_value('excel_file_path')
    if not file_path or not os.path.exists(file_path):
        log_message('Invalid Excel file path.', 'error')
        return
    try:
        columns, df = read_excel_columns(file_path)
        state['excel_path'] = file_path
        state['excel_columns'] = columns
        state['excel_df'] = df
        log_message(f'Loaded Excel columns: {columns}', 'info')
        state['mapping'].clear()
        refresh_node_editor()
    except Exception as e:
        log_message(str(e), 'error')

def connect_mssql_callback(sender, app_data, user_data):
    if dpg.get_value('mock_mode'):
        columns = [col.strip() for col in dpg.get_value('mock_columns').split(',') if col.strip()]
        state['table_columns'] = columns
        log_message(f'Loaded mock table columns: {columns}', 'info')
        state['mapping'].clear()
        refresh_node_editor()
        return
    server = dpg.get_value('server')
    database = dpg.get_value('database')
    username = dpg.get_value('username')
    password = dpg.get_value('password')
    table = dpg.get_value('table')
    try:
        columns = get_mssql_table_columns(server, database, username, password, table)
        state['mssql_info'] = {'server': server, 'database': database, 'username': username, 'password': password, 'table': table}
        state['table_columns'] = columns
        log_message(f'Loaded table columns: {columns}', 'info')
        state['mapping'].clear()
        refresh_node_editor()
    except Exception as e:
        log_message(str(e), 'error')

def refresh_node_editor():
    if not dpg.does_item_exist('node_editor'):
        return
    dpg.delete_item('node_editor', children_only=True)
    state['node_ids'].clear()
    state['attr_ids'].clear()
    state['link_ids'].clear()
    # Add source nodes (left)
    for i, src in enumerate(state['excel_columns']):
        node_id = dpg.generate_uuid()
        attr_id = dpg.generate_uuid()
        with dpg.node(label=src, parent='node_editor', pos=[20, 60 + i * 100], tag=node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=attr_id):
                dpg.add_spacer(width=NODE_WIDTH, height=NODE_ATTR_HEIGHT)
                dpg.add_button(label="", width=NODE_WIDTH, height=NODE_ATTR_HEIGHT, callback=lambda s,a,u: None, user_data=src, tag=f"src_btn_{src}", show=False)
        state['node_ids'][src] = node_id
        state['attr_ids'][src] = attr_id
    # Add target nodes (right)
    for i, tgt in enumerate(state['table_columns']):
        node_id = dpg.generate_uuid()
        attr_id = dpg.generate_uuid()
        with dpg.node(label=tgt, parent='node_editor', pos=[500, 60 + i * 100], tag=node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=attr_id):
                dpg.add_spacer(width=NODE_WIDTH, height=NODE_ATTR_HEIGHT)
                dpg.add_button(label="", width=NODE_WIDTH, height=NODE_ATTR_HEIGHT, callback=lambda s,a,u: None, user_data=tgt, tag=f"tgt_btn_{tgt}", show=False)
        state['node_ids'][tgt] = node_id
        state['attr_ids'][tgt] = attr_id
    # Redraw links for current mapping
    for tgt, src in state['mapping'].items():
        src_attr = state['attr_ids'].get(src)
        tgt_attr = state['attr_ids'].get(tgt)
        if src_attr and tgt_attr:
            link_id = dpg.generate_uuid()
            dpg.add_node_link(src_attr, tgt_attr, parent='node_editor', tag=link_id)
            state['link_ids'][link_id] = (src, tgt)
    dpg.set_value('mappings_display', str(state['mapping']))

def on_link_created(sender, app_data):
    src_attr, tgt_attr = app_data
    src = next((k for k, v in state['attr_ids'].items() if v == src_attr), None)
    tgt = next((k for k, v in state['attr_ids'].items() if v == tgt_attr), None)
    if src and tgt:
        state['mapping'][tgt] = src
        link_id = dpg.generate_uuid()
        dpg.add_node_link(src_attr, tgt_attr, parent='node_editor', tag=link_id)
        state['link_ids'][link_id] = (src, tgt)
        log_message(f'Created mapping: {src} -> {tgt}', 'info')
        dpg.set_value('mappings_display', str(state['mapping']))
        refresh_node_editor()

def on_link_deleted(sender, app_data):
    link_id = app_data
    if link_id in state['link_ids']:
        src, tgt = state['link_ids'][link_id]
        if tgt in state['mapping'] and state['mapping'][tgt] == src:
            del state['mapping'][tgt]
        del state['link_ids'][link_id]
        log_message(f'Deleted mapping: {src} -> {tgt}', 'info')
        dpg.set_value('mappings_display', str(state['mapping']))
        refresh_node_editor()

def on_node_editor_right_click(sender, app_data):
    # app_data: (mouse_pos, link_id)
    mouse_pos, link_id = app_data
    if link_id in state['link_ids']:
        last_right_clicked_link['link_id'] = link_id
        dpg.configure_item('delete_link_menu', show=True)
        dpg.set_item_pos('delete_link_menu', [mouse_pos[0], mouse_pos[1]])

def delete_selected_link():
    link_id = last_right_clicked_link.get('link_id')
    if link_id:
        on_link_deleted(None, link_id)
        dpg.configure_item('delete_link_menu', show=False)
        last_right_clicked_link['link_id'] = None

def generate_sql_callback(sender, app_data, user_data):
    if not state['mapping'] or state['excel_df'] is None:
        log_message('Missing mapping or Excel data.', 'error')
        return
    scripts = generate_insert_scripts(
        state['mssql_info'].get('table', 'TargetTable'),
        state['table_columns'],
        state['excel_columns'],
        state['excel_df'],
        state['mapping']
    )
    state['sql_scripts'] = scripts
    dpg.set_value('sql_output', '\n'.join(scripts[:10]) + ('\n... (truncated)' if len(scripts) > 10 else ''))
    log_message(f'Generated {len(scripts)} SQL insert statements.', 'info')

def auto_map_matching_columns():
    # Clear existing mappings
    state['mapping'].clear()
    excel_cols = {col.lower(): col for col in state['excel_columns']}
    for tgt in state['table_columns']:
        src = excel_cols.get(tgt.lower())
        if src:
            state['mapping'][tgt] = src
    log_message('Auto-mapped matching columns (case-insensitive).', 'info')
    refresh_node_editor()

def clear_all_mappings():
    state['mapping'].clear()
    refresh_node_editor()
    log_message('All mappings cleared.', 'info')

def main():
    dpg.create_context()
    with dpg.window(label='Excel to SQL Mapper', width=1100, height=900):
        dpg.add_text('Step 1: Import Excel File')
        dpg.add_input_text(tag='excel_file_path', label='Excel File Path', width=400)
        dpg.add_button(label='Import Excel', callback=import_excel_callback)
        dpg.add_spacer(height=10)
        dpg.add_text('Step 2: Connect to MSSQL')
        dpg.add_checkbox(label='Enable Mock MSSQL Table', tag='mock_mode')
        dpg.add_input_text(label='Mock Table Columns (comma-separated)', tag='mock_columns', width=400, default_value='id, name, age')
        dpg.add_input_text(tag='server', label='Server')
        dpg.add_input_text(tag='database', label='Database')
        dpg.add_input_text(tag='username', label='Username')
        dpg.add_input_text(tag='password', label='Password', password=True)
        dpg.add_input_text(tag='table', label='Table')
        dpg.add_button(label='Connect to MSSQL', callback=connect_mssql_callback)
        dpg.add_spacer(height=10)
        dpg.add_text('Step 3: Map Columns')
        dpg.add_button(label='Auto Map Matching Columns', callback=lambda s,a,u: auto_map_matching_columns())
        dpg.add_button(label='Clear All Mappings', callback=lambda s,a,u: clear_all_mappings())
        dpg.add_node_editor(tag='node_editor', width=800, height=500, callback=on_link_created, delink_callback=on_link_deleted)
        dpg.add_text('Current Mappings:')
        dpg.add_input_text(tag='mappings_display', default_value='', readonly=True, width=400)
        dpg.add_spacer(height=10)
        dpg.add_text('Step 4: Generate SQL Insert Scripts')
        dpg.add_button(label='Generate SQL', callback=generate_sql_callback)
        dpg.add_input_text(tag='sql_output', multiline=True, readonly=True, width=700, height=200)
        dpg.add_spacer(height=10)
        dpg.add_text('Log Output:')
        dpg.add_input_text(tag='log_output', multiline=True, readonly=True, width=700, height=150, default_value='')
        # Context menu for deleting a link (if supported)
        with dpg.window(label="Delete Link", tag="delete_link_menu", show=False, no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_background=True):
            dpg.add_button(label="Delete Link", callback=lambda s,a,u: delete_selected_link())
    dpg.create_viewport(title='Excel to SQL Mapper', width=1120, height=1000)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == '__main__':
    main() 