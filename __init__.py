# Copyright (c) 2020 Samia
# Copyright (c) 2025 mugi
import bpy
from .operator import OBJECT_OT_vertex_groups_move_by_filter_order, OBJECT_OT_vertex_groups_move_by_sortlist,\
    OBJECT_OT_vertex_groups_sortlist_text_export,DATA_PT_sort_vertex_groups_list,MESH_UL_sort_vertex_groups_list, MVGBF_ToolSettings, FilterItems

bl_info = {
    "name": "Move Vertex Groups test",
    "author": "Samia(mod mugi)",
    "version": (1, 2),
    "blender": (4, 2, 0),
    "location": "Properties > Data",
    "description": "Add a panel to move the list of vertex groups.",
    "warning": "Trying to sort dozens of vertex groups can take a long time and render Blender busy.",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "User Interface"
}

classes = (
    # コレクションクラスのインポートの順番に注意
    FilterItems,
    MVGBF_ToolSettings,
    OBJECT_OT_vertex_groups_move_by_filter_order,
    OBJECT_OT_vertex_groups_move_by_sortlist,
    OBJECT_OT_vertex_groups_sortlist_text_export,
    DATA_PT_sort_vertex_groups_list,
    MESH_UL_sort_vertex_groups_list,
     )

# 翻訳用辞書
translation_dict = {
    "ja_JP" :
        {("*", "Enable Regular Expressions.") : "正規表現を有効",
         ("*", "Sort_by_text") : "txt順にソート",
         ("*", "text_export") : "ソート用txtを出力",
        },
}



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.MVGBF_tool_settings = bpy.props.PointerProperty(type=MVGBF_ToolSettings)
    bpy.app.translations.register(__name__, translation_dict)   # 辞書の登録

def unregister():
    bpy.app.translations.unregister(__name__)   # 辞書の削除
    del bpy.types.Scene.MVGBF_tool_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
