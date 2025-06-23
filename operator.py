# Copyright (c) 2025 mugi
import re
import bpy
import os
import datetime

from bpy.types import Operator
from bpy.types import Panel, UIList
from bpy.props import *

from .utils.bl_version_helpers import has_bl_major_version, get_bl_minor_version
from .utils.bl_context_wrappers import get_engine
from .utils.bl_str_wrappers import get_icon, get_menu

translat = bpy.app.translations


class OBJECT_OT_vertex_groups_move_by_sortlist(bpy.types.Operator):
    bl_idname = "object.vertex_groups_move_by_sortlist"
    bl_label = "txt読み込み"
    bl_description = "date_textファイル順に並び替え"
    bl_options = {'REGISTER', 'UNDO'}
    #　WMのパラ種類は→(https://docs.blender.org/api/current/bpy.ops.wm.html)
    filepath : StringProperty(subtype = "FILE_PATH")    # ファイルパス用のプロパティ 
    filename:  StringProperty()  
    filter_glob : StringProperty(default = "*.txt",)    # 読み込みの拡張子をフィルタプロパティ(.txt)をここでは指定

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH', 'LATTICE'} and context.object.vertex_groups

    def execute(self, context):
        bpy.context.active_object.vertex_groups.active_index = 0
        obj = bpy.context.active_object
        
        # ファイル拡張子チェック
        f_name = os.path.splitext(self.filename)[0]
        f_exe = os.path.splitext(self.filename)[1]

        print("test---->", os.path.basename(self.filepath))
        print("fname---->", f_name, "fexe---->", f_exe, "filename---->", self.filename)
        
        if f_exe != ".txt":
            self.report({'ERROR'}, f"'{self.filename}' is not txt file.")
            return {'CANCELLED'}

        # 現在の頂点グループ名を取得
        current_vg_names = [vg.name for vg in obj.vertex_groups]
        
        # txtファイルから並び替え順序を読み込み
        try:
            with open(self.filepath, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            self.report({'ERROR'}, f"ファイル読み込みエラー: {str(e)}")
            return {'CANCELLED'}
        
        # 行を処理（改行削除、左右変換、重複削除、空行削除）
        processed_names = []
        seen = set()
        
        for line in lines:
            line = line.rstrip("\n")
            if not line:  # 空行はスキップ
                continue
                
            # 左右変換
            if line.startswith("左"):
                processed_name = line[1:] + ".L"
                print(line.startswith("左"), "==書き換え＝＝", line, "==>", processed_name)
            elif line.startswith("右"):
                processed_name = line[1:] + ".R"
                print(line.startswith("右"), "==書き換え＝＝", line, "==>", processed_name)
            else:
                processed_name = line
            
            # 重複チェック
            if processed_name not in seen:
                seen.add(processed_name)
                processed_names.append(processed_name)
        
        # 現在の頂点グループに存在するもののみをフィルタ
        valid_names = [name for name in processed_names if name in current_vg_names]
        
        if not valid_names:
            self.report({'WARNING'}, "並び替え対象の頂点グループが見つかりませんでした。")
            return {'FINISHED'}
        
        # 現在のインデックスマッピングを作成
        name_to_current_index = {vg.name: i for i, vg in enumerate(obj.vertex_groups)}
        
        # 並び替え処理：逆順で処理して効率化
        for target_index, vg_name in enumerate(valid_names):
            current_index = name_to_current_index[vg_name]
            
            if current_index != target_index:
                # 現在の位置から目標位置への移動回数を計算
                move_count = current_index - target_index
                
                # アクティブインデックスを設定
                obj.vertex_groups.active_index = current_index
                
                # 効率的な移動：一度に必要な回数だけ移動
                if move_count > 0:
                    for _ in range(move_count):
                        bpy.ops.object.vertex_group_move(direction='UP')
                
                # インデックスマッピングを更新
                # 移動したグループより後ろにあったグループのインデックスを更新
                for name, idx in name_to_current_index.items():
                    if target_index <= idx < current_index:
                        name_to_current_index[name] = idx + 1
                
                # 移動したグループのインデックスを更新
                name_to_current_index[vg_name] = target_index
        
        self.report({'INFO'}, "txt順に並び替え完了")
        return {'FINISHED'}

    def invoke(self, context, event): # ファイルブラウザ表示
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


class OBJECT_OT_vertex_groups_sortlist_text_export(bpy.types.Operator):
    bl_idname = "object.vertex_groups_sortlist_text_export"
    bl_label = "txt保存"
    bl_description = "txtファイルを出力"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH', 'LATTICE'} and context.object.vertex_groups

    def execute(self, context):
        obj = bpy.context.active_object
        VGname = []
        
        for vg in obj.vertex_groups:                         #　選択オブジェクトの頂点グループ取得　＆　左右判定とあれば書き換え
            if (vg.name.endswith(".L")):
                vgg = "左" + vg.name[0:-2]
                # print(vg.name.endswith(".L"),"==書き換え＝＝",vg.name,"==>",vgg)
                VGname.append(vgg)
            elif(vg.name.endswith(".R")):
                vgg = "右" + vg.name[0:-2]
                # print(vg.name.endswith(".R"),"==書き換え＝＝",vg.name,"==>",vgg)
                VGname.append(vgg)
            else:
                VGname.append(vg.name)    

        print("===========　VGname　============\n",VGname)
        w_fpath = f"//_VGsort-{datetime.date.today()}.txt"
        fullpath = bpy.path.abspath(w_fpath)                # 開いてるモデルからモデルのパスを取得 & _VGsort-日付.txtを指定
        with open(fullpath,"w",encoding = "utf-8") as file: # 取得した頂点グループ順をtxtに書き込み & 保存
            file.write("\n".join(VGname))
        self.report({'INFO'}, f"アクティブオブジェクトの頂点グループを{fullpath}に保存") 

        return {'FINISHED'}

    def invoke(self, context, event): # 確認メッセージ表示
        wm = context.window_manager

        return wm.invoke_confirm(self, event)

class DATA_PT_sort_vertex_groups_list(Panel):
    bl_label = "Move Vertex Groups ver3.X"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    # COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES'}

    @classmethod
    def poll(cls, context):
        engine = get_engine(context)
        obj = context.object
        return obj and obj.type in {'MESH', 'LATTICE'} and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        ob = bpy.context.object
        group = ob.vertex_groups.active

        rows = 3


class DATA_PT_sort_vertex_groups_list(Panel):
    bl_label = "Move Vertex Groups ver3.X"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH', 'LATTICE'} 

    def draw(self, context):

        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(OBJECT_OT_vertex_groups_move_by_sortlist.bl_idname, text = translat.pgettext("JP_name_all_clear"))
        row.separator()
        row.operator(OBJECT_OT_vertex_groups_sortlist_text_export.bl_idname, text = translat.pgettext("Eng_name_all_clear"))