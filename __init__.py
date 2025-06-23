# Copyright (c) 2020 Samia
# Copyright (c) 2025 mugi
import bpy
import os
import zipfile
import tempfile
import urllib.request
import shutil

from .operator import OBJECT_OT_vertex_groups_move_by_filter_order, OBJECT_OT_vertex_groups_move_by_sortlist,\
    OBJECT_OT_vertex_groups_sortlist_text_export,DATA_PT_sort_vertex_groups_list,MESH_UL_sort_vertex_groups_list, MVGBF_ToolSettings, FilterItems


bl_info = {
    "name": "Move Vertex Groups test",
    "author": "Samia(mod mugi)",
    "version": (1, 3),
    "blender": (3, 1, 0),
    "location": "Properties > Data",
    "description": "Add a panel to move the list of vertex groups with update button.",
    "category": "User Interface"
}

class MVGBF_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Move Vertex Groups Addon Settings")
        layout.operator("mvg.update_addon", icon='FILE_REFRESH')

class OBJECT_OT_update_move_vertex_groups(bpy.types.Operator):
    bl_idname = "mvg.update_addon"
    bl_label = "アドオンを更新"
    bl_description = "GitHubから最新版をダウンロードして上書きします"

    def execute(self, context):
        url = "https://github.com/mugi-mmder/move_vertex_groups_V4/archive/refs/heads/main.zip"

        try:
            tmp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(tmp_dir, "update.zip")

            self.report({'INFO'}, "Downloading update...")
            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)

            extracted_folder = os.path.join(tmp_dir, "move_vertex_groups_V4-main")

            addon_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(addon_dir)

            self.report({'INFO'}, "Replacing addon files...")
            for item in os.listdir(extracted_folder):
                s = os.path.join(extracted_folder, item)
                d = os.path.join(parent_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            self.report({'INFO'}, "更新完了しました。再起動してください。")
        except Exception as e:
            self.report({'ERROR'}, f"更新失敗: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

classes = (
   # コレクションクラスのインポートの順番に注意
    FilterItems,
    MVGBF_ToolSettings,
    OBJECT_OT_vertex_groups_move_by_filter_order,
    OBJECT_OT_vertex_groups_move_by_sortlist,
    OBJECT_OT_vertex_groups_sortlist_text_export,
    DATA_PT_sort_vertex_groups_list,
    MESH_UL_sort_vertex_groups_list,

    OBJECT_OT_update_move_vertex_groups,
    MVGBF_AddonPreferences,
)

# 翻訳用辞書
translation_dict = {
    "ja_JP" :
        {("*", "Enable Regular Expressions.") : "正規表現を有効",
         ("*", "Sort_by_text") : "txt順にソート",
         ("*", "text_export") : "ソート用txtを出力",

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
