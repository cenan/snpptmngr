#!/usr/bin/env python
# (C) 2011 cenan ozen <cenan.ozen@gmail.com>

import os
from os.path import dirname, join, abspath
import sqlite3
from Tkinter import *
from ScrolledText import *
from tkFont import *
import tkMessageBox

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

class MainWnd:
	def __init__(self, parent):
		self.parent = parent

		root.protocol("WM_DELETE_WINDOW", self.ask_quit)

		self.parent.title("snippets")
		self.parent.configure(padx=10, pady=10)
		self.parent.minsize(600, 480)
		self.create_widgets()

		dbpath = os.path.join(abspath(dirname(__file__)),"snip.db")
		dbexists = os.path.isfile(dbpath)
		self.connection = sqlite3.connect(dbpath)
		self.connection.row_factory = dict_factory
		self.cursor = self.connection.cursor()

		if not dbexists:
			self.cursor.execute('create table snippet (caption, content)')

		self.fill_list()
		self.snip_content.focus_set()

	def ask_quit(self):
		if tkMessageBox.askokcancel("Quit", "You want to quit now?"):
			self.parent.destroy()

	def __del__(self):
		self.connection.close()

	def create_widgets(self):
		self.search_str = StringVar()
		self.search_box = Entry(self.parent, textvariable=self.search_str)
		self.search_str.set("New snippet")
		self.search_box.pack(fill=X)

		self.toolbar_f = Frame(self.parent, pady=5)
		self.toolbar_f.pack(fill=X)

		self.newbtn = Button(self.toolbar_f, text="New", command=self.on_new)
		self.newbtn.pack(side=LEFT)

		self.savebtn = Button(self.toolbar_f, text="Save", command=self.on_save)
		self.savebtn.pack(side=LEFT)

		self.updatebtn = Button(self.toolbar_f, text="Update", command=self.on_update)
		self.updatebtn.pack(side=LEFT)

		self.delbtn = Button(self.toolbar_f, text="Delete", command=self.on_delete)
		self.delbtn.pack(side=LEFT)
		
		self.copybtn = Button(self.toolbar_f, text="Copy to clipboard", command=self.on_copy)
		self.copybtn.pack(side=LEFT)

		self.quitbtn = Button(self.toolbar_f, text="Quit", command=self.on_quit)
		self.quitbtn.pack(side=LEFT)

		self.pwin = PanedWindow(self.parent, showhandle=True)
		self.pwin.pack(fill=BOTH, expand=1)

		self.list_f = Frame(self.pwin)
		self.list_sb = Scrollbar(self.list_f, orient=VERTICAL)
		self.snip_list = Listbox(self.list_f, yscrollcommand=self.list_sb.set)
		self.list_sb.config(command=self.snip_list.yview)
		self.snip_list.bind('<ButtonRelease-1>',self.on_snipselect)
		self.snip_list.pack(side=LEFT, fill=BOTH, expand=1)
		self.list_sb.pack(side=RIGHT, fill=Y)
		self.pwin.add(self.list_f)
		self.pwin.paneconfigure(self.list_f, minsize=150)

		self.snippetFont = Font(family="courier", size=11, weight=NORMAL)
		self.snip_content = ScrolledText(self.pwin, height=20, width=40,
										 padx=5, pady=5, 
										 font=self.snippetFont)
		self.pwin.add(self.snip_content)


	def fill_list(self):
		self.snip_list.delete(0, END)
		self.cursor.execute('select * from snippet')
		for r in self.cursor.fetchall():
			self.snip_list.insert(END,r['caption'])

	def on_new(self):
		self.search_str.set("")
		self.snip_content.delete(1.0, END)

	def on_save(self):
		self.cursor.execute(
			'insert into snippet (caption,content) values (?,?)', 
			(self.search_str.get(),self.snip_content.get(1.0, END),))
		self.connection.commit()
		self.fill_list()

	def on_update(self):
		self.cursor.execute(
			'update snippet set content=? where caption=?',
			(self.snip_content.get(1.0, END),self.search_str.get()))
		self.connection.commit()

	def on_delete(self):
		index = self.snip_list.curselection()[0]
		seltext = self.snip_list.get(index)
		self.cursor.execute(
			'delete from snippet where caption=?',
			(seltext,))
		self.connection.commit()
		self.snip_list.delete(ANCHOR)
		self.on_new()

	def on_copy(self):
		self.parent.clipboard_clear()
		self.parent.clipboard_append(self.snip_content.get(1.0, END))

	def on_quit(self):
		self.parent.destroy()

	def on_snipselect(self, event):
		index = self.snip_list.curselection()[0]
		seltext = self.snip_list.get(index)
		self.snip_content.delete(1.0, END)
		self.cursor.execute(
			'select * from snippet where caption=?',
			(seltext,))
		r = self.cursor.fetchone()
		if r['caption']:
			self.search_str.set(r['caption'])
		if r['content']:
			self.snip_content.insert(INSERT, r['content'])
		self.snip_content.focus_set()

if __name__=="__main__":
	root = Tk()
	wnd = MainWnd(root)
	root.mainloop()
