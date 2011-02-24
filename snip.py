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
		self.create_widgets()

		dbpath = os.path.join(abspath(dirname(__file__)),"snip.db")
		dbexists = os.path.isfile(dbpath)
		self.connection = sqlite3.connect(dbpath)
		self.connection.row_factory = dict_factory
		self.cursor = self.connection.cursor()

		if not dbexists:
			self.cursor.execute('create table snippet (caption, content)')

		self.fill_list()

	def ask_quit(self):
		if tkMessageBox.askokcancel("Quit", "You want to quit now?"):
			self.parent.destroy()

	def __del__(self):
		self.connection.close()

	def create_widgets(self):
		self.search_str = StringVar()
		self.search_box = Entry(self.parent, textvariable=self.search_str)
		self.search_str.set("")
		self.search_box.pack(fill=X)

		self.snip_list = Listbox(self.parent)
		self.snip_list.bind('<ButtonRelease-1>',self.on_snipselect)
		self.snip_list.pack(side=LEFT,fill=Y)

		self.snippetFont = Font(family="courier", size=11, weight=NORMAL)
		self.snip_content = ScrolledText(self.parent, height=20, width=40,
										 padx=5, pady=5, 
										 font=self.snippetFont)
		self.snip_content.pack(fill=BOTH,expand=1)

		self.newbtn = Button(self.parent, text="New", command=self.on_new)
		self.newbtn.pack(side=LEFT)

		self.savebtn = Button(self.parent, text="Save",
							  command=self.on_save)
		self.savebtn.pack(side=LEFT)

		self.updatebtn = Button(self.parent, text="Update",
								command=self.on_update)
		self.updatebtn.pack(side=LEFT)

		self.delbtn = Button(self.parent, text="Delete",
							 command=self.on_delete)
		self.delbtn.pack(side=LEFT)

		self.quitbtn = Button(self.parent, text="Quit",
							  command=self.on_quit)
		self.quitbtn.pack(side=LEFT)


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

if __name__=="__main__":
	root = Tk()
	wnd = MainWnd(root)
	root.mainloop()
