# Copyright (c) 2020 Samia
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


def make_annotations(cls):
    if has_bl_major_version(2) and get_bl_minor_version() < 80:
        return cls

    props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


@make_annotations
class MVGBF_ToolSettings(bpy.types.PropertyGroup):
# PropertyGroupの定義は”＝”でなく”：”に
    #use_regex = bpy.props.BoolProperty(
    use_regex : BoolProperty(
        name="Enable Regular Expressions",
        description="Enable Regular Expressions.",
        default=False,
        options={'HIDDEN'},
    )


@make_annotations
class FilterItems(bpy.types.PropertyGroup):
    flt_flags = []
    flt_neworder = []


@make_annotations
class OBJECT_OT_vertex_groups_move_by_filter_order(bpy.types.Operator):
    bl_idname = "object.vertex_groups_move_by_filter_order"
    bl_label = "Move Vertex Groups test"
    bl_description = "あくちぶのとこに移動"
    bl_options = {'REGISTER', 'UNDO'}

# PropertyGroupの定義は”＝”でなく”：”に
    filter_items : PointerProperty(
        type=FilterItems,
        options={'HIDDEN'}
    )

    bitflag_filter_item : IntProperty(
        default=0,
        options={'HIDDEN'},
    )
    use_filter_sort_alpha : BoolProperty(
        default=False,
        options={'HIDDEN'},
    )
    use_filter_sort_reverse : BoolProperty(
        default=False,
        options={'HIDDEN'},
    )
    use_filter_invert : BoolProperty(
        default=False,
        options={'HIDDEN'},
    )

    # def __init__(self):
    #     pass

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH', 'LATTICE'} and context.object.vertex_groups

    # def invoke(self, context, event):
    #     return self.execute(context)

    def execute(self, context):
        if not len(self.filter_items.flt_flags) == 0:
            v_list = []
            bitflag = 0 if self.use_filter_invert else self.bitflag_filter_item

            for i, item in enumerate(self.filter_items.flt_flags):
                if item == bitflag:
                    if len(self.filter_items.flt_neworder) == 0:
                        v_list.append([i, context.object.vertex_groups.keys()[i], i])
                    else:
                        v_list.append([i, context.object.vertex_groups.keys()[i], self.filter_items.flt_neworder[i]])

            v_list.sort(key=lambda x: x[2], reverse=self.use_filter_sort_reverse)

            toIndex = context.object.vertex_groups.active_index

            for i, list_item in enumerate(v_list):
                context.object.vertex_groups.active_index = context.object.vertex_groups[list_item[1]].index
                nowIndex = context.object.vertex_groups.active_index

                if not toIndex - nowIndex == 0:
                    rangeCount = 0
                    if toIndex < nowIndex:
                        rangeCount = nowIndex - toIndex if i == 0 else nowIndex - toIndex - 1
                        direction = 'UP'
                    elif toIndex > nowIndex:
                        rangeCount = toIndex - nowIndex
                        direction = 'DOWN'
                    for j in range(rangeCount):
                        bpy.ops.object.vertex_group_move(direction=direction)
                toIndex = context.object.vertex_groups.active_index
        return {'FINISHED'}


@make_annotations
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
        
        # slct_basename = os.path.basename(self.filepath)
        f_name = os.path.splitext(self.filename)[0]       #  splitextでファイル名を分解　0＝ファイル名　1＝拡張子
        f_exe = os.path.splitext(self.filename)[1]

        print("test---->",os.path.basename(self.filepath))
        print("fname---->",f_name,"fexe---->",f_exe,"filename---->",self.filename)
        if(f_exe != ".txt"):                                                        #  拡張子が .txt か否か
            self.report({'ERROR'}, f"'{self.filename}' is not txt file.")   #  拡張子が .txt でない場合はエラーメッセージを表示する
            return {'CANCELLED'}

        VGname = []
        VGsortLIST = []
        IndexList = []

        for vg in obj.vertex_groups:                         #　選択オブジェクトの頂点グループ取得
            VGname.append(vg.name)
        # print("****選択オブジェクトの頂点グループ取得****\n",VGname)
        
        # b_path = bpy.path.abspath("//") 
        #test_fpat = "//date.txt"
        #fullpath = bpy.path.abspath(test_fpat)
        fullpath = self.filepath                    #　WMからファイルパスをもらう  

        # print("fullpath===========" + fullpath)   #　blendファイルと同じ階層のdate.txtから名称取得
        #is_file = os.path.isfile(fullpath)
        #if is_file:                                #　blendファイルと同じ階層にdate.txtがあるか確認
        #    self.report({'INFO'}, "date.txt順に並び替え開始")
        with open(fullpath, mode="r", encoding = "utf-8") as f:
                Vgstr = f.readlines()
                VgstrLR = [Vg.rstrip("\n") for Vg in Vgstr] #　改行削除
                for VG_LRchk in VgstrLR:                    #　左右判定とあれば書き換え
                    if (VG_LRchk.startswith("左")):
                        vgg = VG_LRchk[1:] + ".L"
                        print(VG_LRchk.startswith("左"),"==書き換え＝＝",VG_LRchk,"==>",vgg)
                        VGsortLIST.append(vgg)
                    elif(VG_LRchk.startswith("右")):
                        vgg = VG_LRchk[1:] + ".R"
                        print(VG_LRchk.startswith("右"),"==書き換え＝＝",VG_LRchk,"==>",vgg)
                        VGsortLIST.append(vgg)
                    else:
                        VGsortLIST.append(VG_LRchk)  
            # print("****並び替え用の頂点グループ取得****\n",VGsortLIST)

        VGsortLIST = list(dict.fromkeys(VGsortLIST))           #　重複登録削除
        # print("****並び替え用の頂点グループ重複削除****\n",VGsortLIST)
        # print("" in VGsortLIST)
        if "" in VGsortLIST:                                    #　空行check　＆　空行削除
            VGsortLIST.remove("")
        #print("****並び替え用の頂点グループ空行削除****\n",VGsortLIST)
        match_list = []

        for matchchk in VGsortLIST :                                #　現頂点グループにあるものだけtxtから抽出
            if matchchk in VGname :
                match_list.append(matchchk)
        # print("****並び替え用の頂点グループ共通リスト****\n",match_list)
        # bpy.context.object.vertex_groups.active_index = 2
        for i, name in enumerate(match_list):                   #　並び替え用のINDEX付リストを作成
            IndexList.append([i , name])
        # print("**************IndexList*****************\n", IndexList)
        for i in range(len(IndexList)):
            MoveVGname = IndexList[i][1]
            # print("MoveVGname========",MoveVGname)

            toIndex = IndexList[i][0]
            # toname = IndexList[i][1]
            nowIndex = bpy.context.object.vertex_groups.keys().index(MoveVGname) # 並び替えリストの名称順に頂点グループ選択
            # print("toIndex==",toIndex,"toname==",toname,"nowIndex==",nowIndex)
            bpy.context.object.vertex_groups.active_index = nowIndex
            # print(toIndex == bpy.context.object.vertex_groups.active_index)

            if not toIndex == bpy.context.object.vertex_groups.active_index:    # 頂点リストと並び替えリストのINDEXが同じならパス
                rangeCount = 0
                rangeCount = nowIndex - toIndex
                # print("rangeCount========",rangeCount)
                for j in range(rangeCount):                                     # INDEXの番号差だけUP連打
                        bpy.ops.object.vertex_group_move(direction='UP')
        self.report({'INFO'}, "txt順に並び替え完了")
       
        return {'FINISHED'}

    def invoke(self, context, event): # ファイルブラウザ表示
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}




@make_annotations
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

class MESH_UL_sort_vertex_groups_list(UIList):
    @staticmethod
    def filter_items_by_regex(pattern, bitflag, items, propname='name', flags=None, reverse=False):
        # flags = flags if flags else [bitflag] * len(items)
        flags = flags if flags else [0] * len(items)

        try:
            compile = re.compile(pattern)
        except Exception as e:
            # 文字の入力途中や、正規表現の書式のエラーはすべてスルーする
            # print(e)
            return flags

        for i, item in enumerate(items):
            flags[i] = bitflag if re.search(compile, getattr(item, propname)) else 0
        return flags.reverse() if reverse else flags

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        vgroup = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.alignment = 'CENTER'
            layout.label(text=str(index))
            layout.alignment = 'EXPAND'
            layout.prop(vgroup, "name", text="", emboss=False, icon_value=icon)
            icon = 'LOCKED' if vgroup.lock_weight else 'UNLOCKED'
            layout.prop(vgroup, "lock_weight", text="", icon=get_icon(icon), emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=get_icon(icon))

    def draw_filter(self, context, layout):
        layout.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(self, 'filter_name', text='')

        row.alignment = 'RIGHT'
        row.prop(context.scene.MVGBF_tool_settings, 'use_regex', text='.*', toggle=True)

        row.alignment = 'EXPAND'
        icon = 'ZOOM_OUT' if self.use_filter_invert else 'ZOOM_IN'
        row.prop(self, 'use_filter_invert', text='', icon=get_icon(icon))

        row.separator()
        icon = 'SORTALPHA'
        row.prop(self, "use_filter_sort_alpha", text="", icon=get_icon(icon))

        icon = 'TRIA_UP' if self.use_filter_sort_reverse else 'TRIA_DOWN'
        row.prop(self, "use_filter_sort_reverse", text="", icon=get_icon(icon))


        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(context.object.vertex_groups, "active_index")
        op = row.operator(OBJECT_OT_vertex_groups_move_by_filter_order.bl_idname, text="Move")  # type: OBJECT_OT_vertex_groups_move_by_filter_order
        op.bitflag_filter_item = self.bitflag_filter_item
        op.use_filter_sort_reverse = self.use_filter_sort_reverse
        op.use_filter_invert = self.use_filter_invert
        op.use_filter_sort_alpha = self.use_filter_sort_alpha
        op.filter_items.flt_flags[:], op.filter_items.flt_neworder[:] = self.filter_items(context, context.active_object, "vertex_groups")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(OBJECT_OT_vertex_groups_move_by_sortlist.bl_idname, text=translat.pgettext("Sort_by_text"))
        row.separator()
        row.operator(OBJECT_OT_vertex_groups_sortlist_text_export.bl_idname, text=translat.pgettext("text_export"))

    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_neworder = []
        vgroups = getattr(data, propname)

        if self.filter_name:
            if context.scene.MVGBF_tool_settings.use_regex:
                # Filtering by Regular Expressions
                flt_flags = MESH_UL_sort_vertex_groups_list.filter_items_by_regex(self.filter_name,
                                                                                  self.bitflag_filter_item, vgroups,
                                                                                  "name")
            else:
                # Filtering by name
                flt_flags = bpy.types.UI_UL_list.filter_items_by_name(self.filter_name, self.bitflag_filter_item, vgroups,
                                                              "name")

        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(vgroups)

        # Reorder by name
        if self.use_filter_sort_alpha:
            flt_neworder = bpy.types.UI_UL_list.sort_items_by_name(vgroups, "name")

        return flt_flags, flt_neworder


class DATA_PT_sort_vertex_groups_list(Panel):
    bl_label = "Move Vertex Groups ver4.X"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    # COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES'}

    @classmethod
    def poll(cls, context):
        engine = get_engine(context)
        obj = context.object
        return obj and obj.type in {'MESH', 'LATTICE'}
    def draw(self, context):
        layout = self.layout

        ob = bpy.context.object
        group = ob.vertex_groups.active

        rows = 3
        if group:
            rows = 5

        row = layout.row()
        row.template_list("MESH_UL_sort_vertex_groups_list", "", ob, "vertex_groups", ob.vertex_groups, "active_index",
                          rows=rows)

        col = row.column(align=True)
        icon = get_icon('ADD')
        col.operator("object.vertex_group_add", icon=icon, text="")
        icon = get_icon('REMOVE')
        props = col.operator("object.vertex_group_remove", icon=icon, text="")
        props.all_unlocked = props.all = False

        col.separator()

        icon = get_icon('DOWNARROW_HLT')
        col.menu(get_menu("MESH_MT_vertex_group_context_menu"), icon=icon, text="")
        if group:
            col.separator()
            col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.vertex_groups and (ob.mode == 'EDIT' or (
                ob.mode == 'WEIGHT_PAINT' and ob.type == 'MESH' and ob.data.use_paint_mask_vertex)):
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("object.vertex_group_assign", text="Assign")
            sub.operator("object.vertex_group_remove_from", text="Remove")

            sub = row.row(align=True)
            sub.operator("object.vertex_group_select", text="Select")
            sub.operator("object.vertex_group_deselect", text="Deselect")

            layout.prop(context.tool_settings, "vertex_group_weight", text="Weight")
