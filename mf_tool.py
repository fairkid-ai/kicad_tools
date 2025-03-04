#!/usr/bin/env python

import pcbnew
import csv
import re
import sys
import os
from . import gerber_drill as gd
import wx
import io
from . import loadnet
from . import mf_dialog_base
import traceback

import re
patten = re.compile(r'\d+')
def ref_comp(x):
    try:
        if type(x) == unicode:
            x = x.encode('gbk')
    except NameError:
        x = x
    if type(x) == str:
        t = patten.findall(x)
        if len(t)>0:
            hh = x.replace(t[0],'')
            vv = '0'*(6-len(hh)) + hh  + '0'*(6-len(t[0])) + t[0]
            return vv
        else:
            print(t)
    else:
        print(type(x))
    return x
def ref_sorted(iterable, key = None):
    return sorted(iterable, key = ref_comp)

def GetExcludeRefs():
    f = pcbnew.GetBoard().GetFileName()
    delimer = '/'
    pos = f.rfind('/')
    if pos < 0:
        delimer = '\\'
        pos = f.rfind('\\')
    f = f[0:pos] + delimer + "exclude.txt"
    if os.path.exists(f):
        file = io.open(f, "r")
        return file.read()
    return ""

class ExcludeRefClass:
    def __init__(self, refs):
        self.refNames = {}
        self.refPrefix = {}
        xx = re.findall(r'([A-Za-z]+[0-9]+)', refs.upper())
        for v in xx:
            self.refNames[v] = True
        xx = re.findall(r'([A-Za-z]+)\*', refs.upper())
        for v in xx:
            self.refPrefix[v] = True
    def contains(self, ref):
        if self.refNames.get(ref.upper()):
            return True
        xx = re.findall(r'[A-Za-z_]+', ref)
        if len(xx) > 0:
            return self.refPrefix.get(xx[0].upper())
        return False

unusedRef = None
    
class RefBuilder:
    ''' RefBuilder use to re-build the module referrence number
    Step 1:  use rb = RefBuilder() to create a RefBuilder object
    Step 2:  use rb.collect(ref) to collect current exist reference
    Step 3:  usb newRef = rb.build(oldRef) to build new ref, if oldRef already built
             use the last oldRef's new Ref
    '''
    def  __init__(self, init_ref = None):
        self.patten = re.compile(r'([a-zA-Z]+)\s*(\d+)')
        self.refMap = {}
        self.builtMap = {}
        if init_ref:
            self.refMap = init_ref
    def collect(self, ref):
        m = self.patten.match(ref)
        if m:
            if not (m.group(1) in self.refMap):
                self.refMap[m.group(1)] = m.group(2)
            else:
                max = self.refMap[m.group(1)]
                if int(m.group(2)) > int(max):
                    self.refMap[m.group(1)] = m.group(2)
    def collects(self, refs):
        for ref in refs:
            self.collect(ref)
    def build(self, oldRef):
        m = re.match(r'([a-zA-Z]+)\s*(\d+)',oldRef)
        if not m:
            print('Ref is invalid %s'%oldRef)
            return None
        if oldRef in self.builtMap:
            return self.builtMap[oldRef]
        newRef = ''
        if not (m.group(1) in self.refMap):
            self.refMap[m.group(1)] = m.group(2)
            newRef = oldRef
        else:
            max = int(self.refMap[m.group(1)])
            max = max + 1
            self.refMap[m.group(1)] = str(max)
            newRef = m.group(1) + str(max)
        self.builtMap[oldRef] = newRef
        return newRef
    def Show(self):
        print(self.refMap)
        
def testRefBuilder():
    rb = RefBuilder()
    rb.collects(['R1','R2','R14', 'R10', 'D1', 'D2', 'U3', 'U2', 'U1'])
    rb.Show()
    print('R1 -> %s'%rb.build('R1'))
    print('R2 -> %s'%rb.build('R2'))
    print('R3 -> %s'%rb.build('R3'))
    print('U1 -> %s'%rb.build('U1'))
    print('U2 -> %s'%rb.build('U2'))
    print('X2 -> %s'%rb.build('X2'))
    print('X1 -> %s'%rb.build('X1'))
    print('R? -> %s'%rb.build('R?'))
    print('R1 -> %s'%rb.build('R1'))
    print('R2 -> %s'%rb.build('R2'))
    print('X2 -> %s'%rb.build('X2'))
    rb.Show()

# Get Board Bounding rect by the margin layer element
#def GetBoardArea(brd = None, marginLayer = pcbnew.Margin):
#  if not brd:
#    brd = pcbnew.GetBoard()
#  rect = None
#  for dwg in brd.GetDrawings():
#    if dwg.GetLayer() == marginLayer:
#        box = dwg.GetBoundingBox()
#        if rect:
#            rect.Merge(box)
#        else:
#            rect = box
#  rect.SetX(rect.GetX() + 100001)
#  rect.SetY(rect.GetY() + 100001)
#  rect.SetWidth(rect.GetWidth() - 200002)
#  rect.SetHeight(rect.GetHeight() - 200002)
#  #print(rect.GetX(), rect.GetY(), rect.GetWidth(), rect.GetHeight())
#  return rect

def GetBoardBound(brd = None, marginLayer = pcbnew.Edge_Cuts):
    ''' Calculate board edge from the margin layer, the default margin layer is Edge_Cuts
        enum all the draw segment on the specified layer, and merge their bound rect
    '''
    if not brd:
        brd = pcbnew.GetBoard()
    rect = None
    l = None
    r = None
    t = None
    b = None
    is_6x = False
    for dwg in brd.GetDrawings():
        if dwg.GetLayer() == marginLayer:
            if hasattr(dwg, 'Cast_to_DRAWSEGMENT'):
                d = dwg.Cast_to_DRAWSEGMENT()
                w = d.GetWidth()
            elif hasattr(pcbnew, 'Cast_to_DRAWSEGMENT'):
                d = pcbnew.Cast_to_DRAWSEGMENT(dwg)
                w = d.GetWidth()
            else:
                is_6x = True
                d = pcbnew.Cast_to_BOARD_ITEM(dwg)
                w = dwg.GetWidth()
            box = d.GetBoundingBox()
            box.SetX(int(box.GetX() + w/2))
            box.SetY(int(box.GetY() + w/2))
            box.SetWidth(int(box.GetWidth() - w))
            box.SetHeight(int(box.GetHeight() - w))
            if rect:
                rect.Merge(box)
            else:
                rect = box
    w = 0 if is_6x else 2
    rect.SetX(int(rect.GetX() + w/2))
    rect.SetY(int(rect.GetY() + w/2))
    rect.SetWidth(int(rect.GetWidth() - w))
    rect.SetHeight(int(rect.GetHeight() - w))
    return rect

def GetOtherBoard(brd):
    r = brd
    curbrd = pcbnew.GetBoard()
    s = curbrd.GetFileName()
    if not brd:
        brd = curbrd
    elif type(brd) == str:
        if os.path.exists(brd):
            brd = pcbnew.LoadBoard(brd)
        elif os.path.exists(s[0:s.rfind('/')] + '/' + brd):
            brd = pcbnew.LoadBoard(s[0:s.rfind('/')] + '/' + brd)
        else:
            return None
    else:
        return brd
    return brd
    
class BoardItems:
    '''  Class to hold all interest board items
         Use Collect method to get all board items
   
    '''
    def __init__(self):
        self.rb = RefBuilder()
        self.orgItems = []
        self.mods = []
        self.rect = None
    def ItemValid(self, item):
        ''' Check the item is in the rect or not'''
        return item.HitTest(self.rect, False)
    def Collect(self, brd = None, rect = None):
        ''' Collect board items in specify rect'''
        brd = GetOtherBoard(brd)
        #if not brd:
        #    brd = pcbnew.GetBoard()
        if not rect:
            rect = GetBoardBound(brd)
        self.rect = rect
        for mod in brd.GetModules():
            if self.ItemValid(mod):
                self.orgItems.append(mod)
                self.mods.append(mod)
                self.rb.collect(mod.GetReference())
        for track in brd.GetTracks():
            if self.ItemValid(track):
                self.orgItems.append(track)
        for dwg in brd.GetDrawings():
            if self.ItemValid(dwg):
                self.orgItems.append(dwg)
            #print(dwg.GetLayer())
        area_cnt = brd.GetAreaCount()
        for i in range(area_cnt):
            area = brd.GetArea(i)
            if self.ItemValid(area):
                self.orgItems.append(area)
        self.brd = brd
        #self.rb.Show()
    def Mirror(self):
        rotPt = pcbnew.wxPoint(self.rect.GetX() + self.rect.GetWidth()/2, self.rect.GetY() + self.rect.GetHeight()/2)
        for item in self.orgItems:
            item.Flip(rotPt)
            item.Rotate(rotPt, 1800)
    def Rotate(self, angle = 90):
        rotPt = pcbnew.wxPoint(self.rect.GetX() + self.rect.GetWidth()/2, self.rect.GetY() + self.rect.GetHeight()/2)
        for item in self.orgItems:
            item.Rotate(rotPt, angle * 10)
    def MoveToMM(self, x, y):
        self.MoveTo(pcbnew.wxPointMM(x,y))
    def ShowRect(self):
        r = '('
        r += str(self.rect.GetX()/1000000) + ','
        r += str(self.rect.GetY()/1000000) + ','
        r += str(self.rect.GetWidth()/1000000) + ','
        r += str(self.rect.GetHeight()/1000000) + ')'
        return r
    def MoveTo(self, pos):
        off = pcbnew.wxPoint( pos.x - self.rect.GetX(), pos.y - self.rect.GetY() )
        #print('org is:', self.x, ',', self.y)
        #print('off is:', off)
        for item in self.orgItems:
            item.Move(off)
        print('Move item in ', self.ShowRect(), 'off = (', off.x/1000000, ',' ,off.y/1000000,')')
        self.rect.Move(off)
        print('Result is ', self.ShowRect())
        
    def Clone(self, brd = None):
        if not brd:
            brd = self.brd
        newBI = BoardItems()
        newBI.rect = self.rect
        for item in self.orgItems:
            newItem = item.Duplicate()
            newBI.orgItems.append(newItem)
            brd.Add(newItem)
        newBI.brd = brd
        return newBI
    def Remove(self):
        for item in self.orgItems:
            self.brd.Remove(item)
    def UpdateRef(self, rb):
        ''' Update items reference with specify ref builder'''
        for item in self.orgItems:
            if isinstance(item,pcbnew.MODULE):
                newRef = rb.build(item.GetReference())
                if newRef:
                    item.SetReference(newRef)
    def ChangeBrd(self, brd = None):
        if not brd:
            brd = pcbnew.GetBoard()
        if brd == self.brd:
            print('Same board, do nothing')
        for item in self.orgItems:
            self.brd.Remove(item)
            brd.Add(item)
        self.brd = brd
    def HideValue(self, hide = True):
        for m in self.mods:
            if hide:
                m.Value().SetVisible(False)
            else:
                m.Value().SetVisible(True)

def test2():
    # load board to be panelized
    #b1 = pcbnew.LoadBoard(r'test1.kicad_pcb')
    b2 = pcbnew.LoadBoard(r'test2.kicad_pcb')
    # Get current work borad, must be a empty board
    brd = pcbnew.GetBoard()
    # Collect items
    bi1 = BoardItems()
    bi2 = BoardItems()
    bi1.Collect(brd)
    bi2.Collect(b2)
    #bi1 = bi1.Clone(brd)
    #bi2 = bi2.Clone(brd)
    # Clone items in board 1
    bb1 = bi1.Clone()
    # Change the module reference 
    bi2.UpdateRef(bi1.rb)
    # Clone items in board 2
    bb2 = bi2.Clone()
    # Copy board items to current board
    #bi1.ChangeBrd(brd)
    #bb1.ChangeBrd(brd)
    bi2.ChangeBrd(brd)
    bb2.ChangeBrd(brd)
    # Move them
    bi2.MoveToMM(0,0)
    bi2.Rotate(180)
    
    bb1.Mirror()
    bb2.Rotate(180)
    bb2.Mirror()
    
    bb1.MoveToMM(54, -59)
    bb2.MoveToMM(54, -59)

def GetPad1(mod):
    '''Get the first pad of a module'''
    padx = None
    for pad in mod.Pads():
        if not padx:
            padx = pad
        if pad.GetPadName() == '1':
            return pad
    #print('Pad 1 not found, use the first pad instead')
    return padx
def IsSMD(mod):
    for pad in mod.Pads():
        attr_smd = pcbnew.PAD_SMD if hasattr(pcbnew,'PAD_SMD') else pcbnew.PAD_ATTRIB_SMD
        if pad.GetAttribute() != attr_smd:
            return False
    return True
def footPrintName(mod):
    fid = mod.GetFPID()
    f = fid.GetFootprintName().Cast_to_CChar() if hasattr(fid, 'GetFootprintName') else fid.GetLibItemName().Cast_to_CChar()
    return f

class BOMItem:
    def __init__(self, ref, footprint, value, pincount, netList = None):
        self.refs = [ref]
        self.fp = footprint
        self.value = value
        self.pincount = pincount
        kv = value
        #if kv.rfind('[') != -1:
        #    kv = kv[0:kv.rfind('[')]
        
        self.netKey = kv + "&" + footprint
        try:
            if not isinstance(self.netKey, unicode):
                self.netKey = unicode(self.netKey)
        except NameError:
            self.netKey = self.netKey
        self.partNumber = ""
        self.desc = "desc"
        self.url = ""
        self.libRef = "libref"
        if netList:
            if self.netKey in netList:
                comp = netList[self.netKey]
                if 'partNumber' in comp:
                    self.partNumber = comp['partNumber']
                if 'description' in comp:
                    self.desc = comp['description']
                if 'datasheet' in comp:
                    self.url = comp['datasheet']
                if 'comment' in comp:
                    self.libRef = self.value
                    self.value = comp['comment']
            else:
                print("fail to find ", self.netKey, " in net list")
        
    def Output(self, out = None):
        refs = ''
        for r in ref_sorted(self.refs):
           refs += r + ','
        if not out:
            out = csv.writer(sys.stdout, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
        out.writerow([self.value, self.desc, refs, self.fp, self.libRef, str(self.pincount), str(len(self.refs)), self.partNumber, self.url ])
    def AddRef(self, ref):
        self.refs.append(ref)
        self.refs = ref_sorted(self.refs)

def OutputBOMHeader(out = None):
    if not out:
        out = csv.writer(sys.stdout, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
    out.writerow(['Comment','Description','Designator','Footprint','LibRef','Pins','Quantity','PartNumber','url'])

def IsModExclude(mod, ExcludeRefs = [], ExcludeValues = []):
    r = mod.GetReference()
    v = mod.GetValue()
    for pat in ExcludeRefs:
        if pat.match(r):
            return True
    for pat in ExcludeValues:
        if pat.match(v):
            return True
    return False

removedRefs = {}
def GenBOM(brd = None, layer = pcbnew.F_Cu, type = 1, ExcludeRefs = [], ExcludeValues = [], netList = None):
    if not brd:
        brd = pcbnew.GetBoard()
    bomList = {}
    if hasattr(brd, "GetModules"):
        mods = brd.GetModules()
    else:
        mods = brd.GetFootprints()
    for mod in mods:
        needOutput = False
        needRemove = False
        if unusedRef:
            needRemove = unusedRef.contains(mod.GetReference())
        if needRemove:
            global removedRefs
            removedRefs[mod.GetReference()] = mod.GetValue()
        if (mod.GetLayer() == layer) and (not IsModExclude(mod, ExcludeRefs, ExcludeValues) and (not needRemove)):
            needOutput = IsSMD(mod) == (type == 1)
        if needOutput:
            v = mod.GetValue()
            f = footPrintName(mod)
            r = mod.GetReference()
            vf = v + f
            if vf in bomList:
            #if bomList.has_key(vf):
                bomList[vf].AddRef(r)
            else:
                bomList[vf] = BOMItem(r,f,v, mod.GetPadCount(), netList)
    print('there are ', len(bomList), ' items at layer ', layer)
    return sorted(bomList.values(), key = lambda item: ref_comp(item.refs[0]))

def layerName(layerId):
    if layerId == pcbnew.F_Cu:
       return 'T'
    if layerId == pcbnew.B_Cu:
       return 'B'
    return 'X'
def toMM(v):
    return str(v/1000000.0) + 'mm'
class POSItem:
    def __init__(self, mod, offx = 0, offy = 0):
        self.MidX = toMM(mod.GetPosition().x-offx)
        self.MidY = toMM(offy - mod.GetPosition().y)
        self.RefX = toMM(mod.GetPosition().x-offx)
        self.RefY = toMM(offy - mod.GetPosition().y)
        pad = GetPad1(mod)
        if pad:
            self.PadX = toMM(pad.GetPosition().x-offx)
            self.PadY = toMM(offy - pad.GetPosition().y)
        else:
            print('Pad1 not found for mod')
            self.PadX = self.MidX
            self.PadY = self.MidY
        if hasattr(mod, "GetOrientationDegrees"):
            self.rot = int(mod.GetOrientationDegrees())
        else:
            self.rot = int(mod.GetOrientation()/10)
        self.ref = mod.GetReference()
        self.val = mod.GetValue()
        self.layer = layerName(mod.GetLayer())
        self.fp = footPrintName(mod)
    def Output(self, out = None):
        if not out:
            out = csv.writer(sys.stdout, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
        out.writerow([self.ref, self.fp, str(self.MidX), str(self.MidY),
                     str(self.RefX), str(self.RefY), str(self.PadX), str(self.PadY),
                     self.layer, str(self.rot), self.val])

def GenPos(brd = None, layer = pcbnew.F_Cu, type = 1, ExcludeRefs = [], ExcludeValues = []):
    if not brd:
        brd = pcbnew.GetBoard()
    posList = []
    if hasattr(brd, 'GetAuxOrigin'):
        pt_org = brd.GetAuxOrigin()
    else:
        pt_org = brd.GetDesignSettings().GetAuxOrigin()
    if hasattr(brd, 'GetModules'):
        mods = brd.GetModules()
    else:
        mods = brd.Footprints()
    for mod in mods:
        needOutput = False
        if (mod.GetLayer() == layer) and (not IsModExclude(mod, ExcludeRefs, ExcludeValues)):
            needOutput = IsSMD(mod) == (type == 1)
        if needOutput:
            posList.append(POSItem(mod, pt_org.x, pt_org.y))
    posList = sorted(posList, key = lambda item: ref_comp(item.ref))
    return posList
def OutputPosHeader(out = None):
    if not out:
        out = csv.writer(sys.stdout, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
    out.writerow(['Designator','Footprint','Mid X','Mid Y','Ref X','Ref Y','Pad X','Pad Y','Layer','Rotation','Comment'])
def PrintBOM(boms):
    OutputBOMHeader()
    i = 1
    for bom in boms:
       print('BOM items for BOM', i)
       i = i + 1
       for k,v in bom.items():
           v.Output()
def PrintPOS(Poses):
    OutputPosHeader()
    i = 1
    for pos in Poses:
       print('Pos items ', i)
       i = i+ 1
       for v in pos:
           v.Output()
def CollectItemByName(filename = None):
    try:
        brd = pcbnew.LoadBoard(filename)
    except IOError:
        print('Can not open ', filename)
        filename = os.path.split(pcbnew.GetBoard().GetFileName())[0] + '\\' + filename
        print('Try to open ', filename)
    try:
        brd = pcbnew.LoadBoard(filename)
    except IOError:
        print('Can not open ', filename)
        return None
    bi = BoardItems()
    bi.Collect(brd)
    return bi

def CollectItem(brd = None):
    if not brd:
        brd = pcbnew.GetBoard()
    bi = BoardItems()
    bi.Collect(brd)
    return bi
    
def CopyItemTo(boardItem, x, y):
    newBI = boardItem.Clone()
    newBI.MoveToMM(x, y)
    return newBI

def MirrorItemTo(boardItem, x, y):
    newBI = boardItem.Clone()
    newBI.MoveToMM(x, y)
    newBI.Mirror()
    return newBI

class UnicodeWriter:
    def __init__(self, file, *a, **kw):
        self.file = file
    def writerow(self, data):
        for e in data:
            self.file.write(u'"')
            #print(isinstance(e, unicode))
            try:
                if not isinstance(e, unicode):
                    self.file.write(unicode(e))
                else:
                    self.file.write(e)
            except NameError:
                self.file.write(e)
            self.file.write(u'",')
        self.file.write(u'\n')
    

def OpenCSV(fileName):
    try:
        f = io.open(fileName, 'w+', encoding="utf-8")
    except IOError:
        e = "Can't open output file for writing: " + fileName
        print( __file__, ":", e, sys.stderr )
        f = sys.stdout
    #out = csv.writer( f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL )
    out = UnicodeWriter(f)
    return out

def PreCompilePattenList(pattenList):
    res = []
    for pat in pattenList:
        res.append(re.compile(pat))
    return res

def def_logger(*args):
    r = ""
    for t in args:
        r = r + str(t) + " "
    print(r)

    
def GenMFDoc(SplitTopAndBottom = False, ExcludeRef = [], ExcludeValue = [], brd = None, needGenBOM = True, needGenPos = True, logger = def_logger):
    if not brd:
        brd = pcbnew.GetBoard()
    if not needGenBOM and not needGenPos:
        return
    bound = GetBoardBound(brd)
    org_pt = pcbnew.wxPoint( bound.GetLeft(), bound.GetBottom())
    org_pt = pcbnew.VECTOR2I(org_pt.x, org_pt.y)
    logger("set board aux origin to left bottom point, at", org_pt)
    if hasattr(brd, 'SetAuxOrigin'):
        brd.SetAuxOrigin(org_pt)
    else:
        brd.GetDesignSettings().SetAuxOrigin(org_pt)
    fName = brd.GetFileName()
    path = os.path.split(fName)[0]
    fName = os.path.split(fName)[1]
    bomName = fName.rsplit('.',1)[0]
    netList = loadnet.loadNet(brd)
    
    excludeRefs = PreCompilePattenList(ExcludeRef)
    excludeValues = PreCompilePattenList(ExcludeValue)

    bomSMDTop = GenBOM(brd, pcbnew.F_Cu, 1, excludeRefs, excludeValues, netList)
    bomHoleTop = GenBOM(brd, pcbnew.F_Cu, 0, excludeRefs, excludeValues, netList)
    
    bomSMDBot = GenBOM(brd, pcbnew.B_Cu, 1, excludeRefs, excludeValues, netList)
    bomHoleBot = GenBOM(brd, pcbnew.B_Cu, 0, excludeRefs, excludeValues, netList)
    
    posSMDTop = GenPos(brd, pcbnew.F_Cu, 1, excludeRefs, excludeValues)
    posHoleTop = GenPos(brd, pcbnew.F_Cu, 0, excludeRefs, excludeValues)
    
    posSMDBot = GenPos(brd, pcbnew.B_Cu, 1, excludeRefs, excludeValues)
    posHoleBot = GenPos(brd, pcbnew.B_Cu, 0, excludeRefs, excludeValues)
    
    if SplitTopAndBottom:
        fName = bomName
        bomName = path + '/' + fName + '_BOM_TOP.csv'
        posName = path + '/' + fName + '_POS_TOP.csv'
        if needGenBOM:
            # Generate BOM for Top layer
            logger('Genertate BOM file ', bomName)
            csv = OpenCSV(bomName)
            OutputBOMHeader(csv)
            for v in bomSMDTop:
               v.Output(csv)
            if len(bomHoleTop)>0:
                csv.writerow(['Through Hole Items '])
                for v in bomHoleTop:
                    v.Output(csv)
        if needGenPos:
            # Generate POS for Top layer
            logger('Genertate POS file ', posName)
            csv = OpenCSV(posName)
            OutputPosHeader(csv)
            for v in posSMDTop:
               v.Output(csv)
            if len(posHoleTop)>0:
                csv.writerow(['Through Hole Items '])
                for v in posHoleTop:
                   v.Output(csv)
           
        bomName = path + '/' + fName + '_BOM_BOT.csv'
        posName = path + '/' + fName + '_POS_BOT.csv'
        if needGenBOM:
            # Generate BOM for Bottom layer
            logger('Genertate BOM file ', bomName)
            csv = OpenCSV(bomName)
            OutputBOMHeader(csv)
            for  v in bomSMDBot:
               v.Output(csv)
            if len(bomHoleBot)>0:
                csv.writerow(['Through Hole Items '])
                for v in bomHoleBot:
                   v.Output(csv)
        if needGenPos:
            # Generate POS for Bottom layer   
            logger('Genertate POS file ', posName)
            csv = OpenCSV(posName)
            OutputPosHeader(csv)        
            for v in posSMDBot:
               v.Output(csv)
            if len(posHoleBot)>0:
                csv.writerow(['Through Hole Items '])
                for v in posHoleBot:
                   v.Output(csv)
        
    else:
        posName = path + '/' + bomName + '_POS.csv'
        bomName = path + '/' + bomName + '_BOM.csv'
        # Generate BOM for both layer
        if needGenBOM:
            logger('Genertate BOM file ', bomName)
            csv = OpenCSV(bomName)
            OutputBOMHeader(csv)
            for v in bomSMDTop:
               v.Output(csv)
               
            for  v in bomSMDBot:
               v.Output(csv)
            if len(bomHoleTop)+len(bomHoleBot)>0:
                csv.writerow(['Through Hole Items '])
                for v in bomHoleTop:
                   v.Output(csv)
                   
                for v in bomHoleBot:
                   v.Output(csv)
        
        if needGenPos:
            # Generate POS for both layer
            logger('Genertate POS file ', posName)
        
            csv = OpenCSV(posName)
            OutputPosHeader(csv)
            for v in posSMDTop:
               v.Output(csv)
               
            for v in posSMDBot:
               v.Output(csv)
            if len(posHoleTop)+len(posHoleBot)>0:
                csv.writerow(['Through Hole Items '])
                for v in posHoleTop:
                   v.Output(csv)
                   
                for v in posHoleBot:
                   v.Output(csv)
    return bomName, posName
    
def version():
    print("1.2")

def GenSMTFiles():
    #reload(sys)
    #sys.setdefaultencoding("utf8")
    GenMFDoc()
    gd.GenGerberDrill(board = None, split_G85 = 0.2, plotDir = "gerber/")

    
    
def TestDialog():
    tt = MFDialog()
    tt.Show()

class MFDialog(mf_dialog_base.MFDialogBase):
    def __init__(self):
        try:
            mf_dialog_base.MFDialogBase.__init__(self, None)
        except TypeError:
            self = mf_dialog_base.MFDialogBase()
        best_size = self.BestSize
        best_size.IncBy(dx=0, dy=30)
        self.SetClientSize(best_size)

        self.exclude_ref_text.Clear()
        self.exclude_ref_text.AppendText(GetExcludeRefs())
    def OnGenBom(self, event):
        try:
            if self.chkBOM.GetValue():
                self.area_text.AppendText("Start generate BOM list\n")
            if self.chkPos.GetValue():
                self.area_text.AppendText("Start generate position file\n")
            global unusedRef
            unusedRef = ExcludeRefClass(self.exclude_ref_text.GetValue())
            global removedRefs
            removedRefs = {}
            GenMFDoc(needGenBOM = self.chkBOM.GetValue(), needGenPos = self.chkPos.GetValue(), logger = lambda *args: self.log(*args) )
            #self.area_text.AppendText("Removed refs in BOM: " + ",".join(ref_sorted(removedRefs.keys())) + "\n")
            self.area_text.AppendText("Removed refs in BOM:\n")
            for n in ref_sorted(removedRefs.keys()):
                self.area_text.AppendText(n+":" + removedRefs[n] + "\n")
            if self.chkGerber.GetValue():
                self.area_text.AppendText("Start generate gerber files\n")
                split_slot = None
                if self.chkSplitSlot.GetValue():
                    split_slot = 0.2
                gerberPath = gd.GenGerberDrill(
                    board = None,
                    split_G85 = split_slot,
                    plotDir = "gerber/",
                    plotReference = self.chkPlotRef.GetValue(),
                    logger = lambda *args: self.log(*args))
                self.area_text.AppendText( 'Gerber file dir is "%s"' % gerberPath)
        except Exception as e:
            self.area_text.AppendText("Error:\n")
            self.area_text.AppendText(traceback.format_exc())
    def ClearLog(self, event):
        self.area_text.SetValue("")
    def log(self, *args):
        for v in args:
            try:
                self.area_text.AppendText(str(v) + " ")
            except Exception as e:
                try:
                    self.area_text.AppendText(v + " ")
                except Exception as e1:
                    self.area_text.AppendText("\nError:\nfail to log content ")
                    self.area_text.AppendText(traceback.format_exc())
        self.area_text.AppendText("\n")    

class gen_mf_doc( pcbnew.ActionPlugin ):
    """
    gen_mf_doc: A plugin used to generate BOM and position file
    How to use:
    - just call the plugin
    - the BOM and Position file will generate under the PCB file folder
      BOM file name is <pcb file name>_BOM.csv
      Position file name is <pcb file name>_POS.csv
    - the Gerber and drill file will generate under gerber folder
    """

    def defaults( self ):
        """
        Method defaults must be redefined
        self.name should be the menu label to use
        self.category should be the category (not yet used)
        self.description should be a comprehensive description
          of the plugin
        """
        self.name = "Gen Manufacture Docs"
        self.category = "Modify PCB"
        self.description = "Automatically generate manufacture document, Gerber, Drill, BOM, Position"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./mf_tool.png")
        self.show_toolbar_button = True

    def Run( self ):
        tt = MFDialog()
        tt.Show()
        
gen_mf_doc().register()
    
    
    
    
    