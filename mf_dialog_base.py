# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MFDialogBase
###########################################################################

class MFDialogBase ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Generate Manufacture Docs", pos = wx.DefaultPosition, size = wx.Size( 736,328 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		try:
			self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		except:
			self.SetSizeHints( wx.DefaultSize.width, wx.DefaultSize.height, wx.DefaultSize.width, wx.DefaultSize.height )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		fgSizer3 = wx.FlexGridSizer( 4, 0, 0, 0 )
		fgSizer3.AddGrowableRow( 3 )
		fgSizer3.SetFlexibleDirection( wx.VERTICAL )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		fgSizer4 = wx.FlexGridSizer( 0, 8, 0, 0 )
		fgSizer4.AddGrowableCol( 6 )
		fgSizer4.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.chkBOM = wx.CheckBox( self, wx.ID_ANY, u"BOM List", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.chkBOM.SetValue(True)
		self.chkBOM.SetToolTipString( u"Generate BOM" )

		fgSizer4.Add( self.chkBOM, 0, wx.ALL, 5 )

		self.chkPos = wx.CheckBox( self, wx.ID_ANY, u"Position File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.chkPos.SetValue(True)
		self.chkPos.SetToolTipString( u"Generate Position file" )

		fgSizer4.Add( self.chkPos, 0, wx.ALL, 5 )

		self.chkGerber = wx.CheckBox( self, wx.ID_ANY, u"Gerber File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.chkGerber.SetValue(True)
		self.chkGerber.SetToolTipString( u"Generate Gerber file" )

		fgSizer4.Add( self.chkGerber, 0, wx.ALL, 5 )

		self.chkPlotRef = wx.CheckBox( self, wx.ID_ANY, u"Plot Reference", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.chkPlotRef.SetValue(True)
		self.chkPlotRef.SetToolTipString( u"Plot reference" )

		fgSizer4.Add( self.chkPlotRef, 0, wx.ALL, 5 )

		self.chkSplitSlot = wx.CheckBox( self, wx.ID_ANY, u"Split Slot", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.chkSplitSlot.SetToolTipString( u"Split slot hole into hole series" )

		fgSizer4.Add( self.chkSplitSlot, 0, wx.ALL, 5 )

		self.btnGen = wx.Button( self, wx.ID_ANY, u"Gen Manufacture Docs", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.btnGen, 0, wx.ALL, 5 )

		self.btnClearLog = wx.Button( self, wx.ID_ANY, u"Clear Log", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.btnClearLog, 0, wx.ALL, 5 )


		fgSizer4.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		fgSizer3.Add( fgSizer4, 1, wx.EXPAND, 5 )

		fgSizer2 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer2.AddGrowableCol( 1 )
		fgSizer2.AddGrowableRow( 0 )
		fgSizer2.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Exclude Ref:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		fgSizer2.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.exclude_ref_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.exclude_ref_text.SetToolTipString( u"Exclude reference, load from \"exclude.txt\"" )
		self.exclude_ref_text.SetMaxSize( wx.Size( -1,20 ) )

		fgSizer2.Add( self.exclude_ref_text, 0, wx.ALL|wx.EXPAND, 5 )


		fgSizer3.Add( fgSizer2, 1, wx.EXPAND, 5 )

		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Log:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		fgSizer3.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.area_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
		fgSizer3.Add( self.area_text, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( fgSizer3, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.btnGen.Bind( wx.EVT_BUTTON, self.OnGenBom )
		self.btnClearLog.Bind( wx.EVT_BUTTON, self.ClearLog )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnGenBom( self, event ):
		event.Skip()

	def ClearLog( self, event ):
		event.Skip()


