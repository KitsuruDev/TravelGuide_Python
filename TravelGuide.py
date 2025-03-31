import psycopg2 as ps
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog, messagebox, END
from io import BytesIO
import os

def onClickMenuList():
    cmd.execute('select name from cities')
    for i in sorted(cmd): listbox.insert(END, i)
    labelMain['text'] = "Выберите город"
    list_menu.entryconfig(0, state="disabled")
    main_menu.entryconfig(1, state="active")

def updateTextbox(name_city = ''):
    textbox.config(state="normal")
    textbox.delete("1.0", END)
    if name_city: textbox.insert("1.0", name_city)
    textbox.config(state="disabled")

def onClickListbox(event=None):
    if listbox.curselection():
        for i in range(0, 2): edit_menu.entryconfig(i, state="active")
        cmd.execute(f'select * from cities where name = \'{listbox.get(listbox.curselection())[0]}\'')
        city = cmd.fetchone()
        labelMain['text'] = str(city[0])
        updateTextbox(str(city[1]))
        if city[2] is not None:
            image = PhotoImage(data=BytesIO(city[2]).read())
            labelImage1.configure(image=image)
            labelImage1.image = image
        else:
            labelImage1.config(image='')
        if city[3] is not None:
            image = PhotoImage(data=BytesIO(city[3]).read())
            labelImage2.configure(image=image)
            labelImage2.image = image
        else:
            labelImage2.config(image='')
    else:
        for i in range(0, 2): edit_menu.entryconfig(i, state="disabled")

def updateListbox():
    listbox.delete(0, END)
    cmd.execute('select name from cities')
    for i in sorted(cmd): listbox.insert(END, i)

def onClickDelete():
    if listbox.curselection():
        name_city = listbox.get(int(listbox.curselection()[0]))[0]
        if messagebox.askyesno("Удаление записи о городе",f"Вы уверены, что хотите удалить запись \"{name_city}\"?"):
            cmd.execute(f'delete from cities where name = \'{name_city}\'')
            connection.commit() # записываем изменения в БД
            labelMain['text'] = "Выберите город"
            updateTextbox()
            updateListbox()

def onClickEdit(mode):
    def onCloseFormEdit(): formEdit.destroy()
    def loadImage(index, image):
        if index == 1:
            labelEditImage1.configure(image=image)
            labelEditImage1.image = image
            buttonEditImageDelete1['state'] = 'active'
        else:
            labelEditImage2.configure(image=image)
            labelEditImage2.image = image
            buttonEditImageDelete2['state'] = 'active'
    def onClickImageOpen(index):
        nonlocal object_image_1, object_image_2
        file_path = filedialog.askopenfilename(title="Выберите изображение...", initialdir=os.getcwd(), filetypes=(("Изображения(*.png)", "*.png"), ("Изображения(*.jpg)", "*.jpg")))
        if file_path:
            if index == 1: object_image_1 = file_path
            else: object_image_2 = file_path
            loadImage(index, PhotoImage(file=file_path, width=180, height=105))
    def onClickImageDelete(index):
        nonlocal object_image_1, object_image_2
        if index == 1:
            labelEditImage1.config(image='')
            buttonEditImageDelete1['state'] = 'disabled'
            object_image_1 = "null"
        else:
            labelEditImage2.config(image='')
            buttonEditImageDelete2['state'] = 'disabled'
            object_image_2 = "null"
    def onClickButtonAccept(mode, row_id):
        nonlocal object_image_1, object_image_2
        if textboxEditName.compare("end-1c", "!=", "1.0") and textboxEditDesc.compare("end-1c", "!=", "1.0"): # проверка без новой строки по умолчанию
            raw_name_city = textboxEditName.get("1.0", END).rstrip().split()
            if len(raw_name_city) > 1:
                name_city = ' '.join(word[0].upper() + word[1:].lower() for word in raw_name_city)
                query = f"select count(name) from cities where name = \'{name_city}\' and id <> {row_id} limit 1" if mode == \
                        "Редактирование записи о городе" else f"select count(name) from cities where name = \'{name_city}\' limit 1"
                cmd.execute(query)
                if int(cmd.fetchone()[0]) == 0:
                    if mode == "Редактирование записи о городе":
                        query = "update cities set name = \'" + name_city + "\', description = \'" + textboxEditDesc.get("1.0", END) + "\'"
                        if object_image_1 != "empty":
                            image1 = ps.Binary(open(object_image_1, 'rb').read()) if object_image_1 != "null" else None
                            query += f", img_1 = %s"
                        if object_image_2 != "empty":
                            image2 = ps.Binary(open(object_image_2, 'rb').read()) if object_image_2 != "null" else None
                            query += f", img_2 = %s"
                        query += f" where id = {row_id}"
                        if object_image_1 != "empty" and object_image_2 != "empty": cmd.execute(query, (image1, image2))
                        elif object_image_1 != "empty": cmd.execute(query, (image1,))
                        elif object_image_2 != "empty": cmd.execute(query, (image2,))
                        else: cmd.execute(query)
                    else:
                        if object_image_1 != "empty" and object_image_1 != "null": image1 = ps.Binary(open(object_image_1, 'rb').read())
                        else: image1 = None
                        if object_image_2 != "empty" and object_image_2 != "null": image2 = ps.Binary(open(object_image_2, 'rb').read())
                        else: image2 = None
                        cmd.execute("insert into cities values (%s,%s,%s,%s)", (name_city, textboxEditDesc.get("1.0", END), image1, image2))
                    connection.commit() # записываем изменения в БД
                    updateListbox()
                    onClickListbox()
                    listbox.selection_set(listbox_row_id)
                    listbox.activate(listbox_row_id)
                    onClickListbox()
                    onCloseFormEdit()
                else:
                    messagebox.showerror("Существующая запись","Запись о городе с таким названием уже внесена в список!")
            else:
                messagebox.showerror("Название из одного символа", "Название города не может состоять из одной буквы!")
        else:
            messagebox.showerror("Пустые значения", "Заполните обязательные поля \"Название\" и \"Описание\"!")

    object_image_1, object_image_2, listbox_row_id = "empty", "empty", 0

    formEdit = Toplevel()
    formEdit.geometry("{}x{}+{}+{}".format(750, 450, (formEdit.winfo_screenwidth()-750)//2, (formEdit.winfo_screenheight()-450)//2))
    formEdit.title(mode)
    formEdit.resizable(False, False)
    formEdit.protocol("WM_DELETE_WINDOW", onCloseFormEdit)

    Label(formEdit, text="Помощь:\n1) поля \"Название\" и \"Описание\" должны быть обязательно заполнены;\n"
                    "2) название города не должно повторяться;\n3) чтобы отменить редактирование, закройте данное окно.",
          font=('Segoe UI', 14)).place(x=12, y=9, width=684, height=100)

    Label(formEdit, text="Название:", font=('Segoe UI', 12)).place(x=15, y=153, width=105, height=25)
    textboxEditName = Text(formEdit, wrap="none", font=('Segoe UI', 10))
    textboxEditName.place(x=123, y=153, width=243, height=26)

    Label(formEdit, text="Описание:", font=('Segoe UI', 12)).place(x=12, y=215, width=105, height=25)
    textboxEditDesc = Text(formEdit, wrap="word", font=('Segoe UI', 10))
    textboxEditDesc.place(x=123, y=215, width=233, height=158)
    scrollbar_textboxEditDesc = Scrollbar(formEdit, orient="vertical", command=textboxEditDesc.yview)
    scrollbar_textboxEditDesc.place(x=356, y=207, height=158)
    textboxEditDesc['yscrollcommand'] = scrollbar_textboxEditDesc.set

    Label(formEdit, text="Фото №1:", font=('Segoe UI', 12)).place(x=420, y=150, width=105, height=25)
    Label(formEdit, text="Фото №2:", font=('Segoe UI', 12)).place(x=420, y=264, width=105, height=25)
    labelEditImage1, labelEditImage2 = Label(formEdit, background='white'), Label(formEdit, background='white')
    labelEditImage1.place(x=504, y=150, width=180, height=105)
    labelEditImage2.place(x=504, y=267, width=180, height=105)

    Button(formEdit, text="...", command=lambda:onClickImageOpen(1)).place(x=693, y=153, width=38, height=25)
    Button(formEdit, text="...", command=lambda:onClickImageOpen(2)).place(x=693, y=269, width=38, height=25)
    buttonEditImageDelete1 = Button(formEdit, text="X", state='disabled', command=lambda:onClickImageDelete(1))
    buttonEditImageDelete1.place(x=693, y=184, width=37, height=23)
    buttonEditImageDelete2 = Button(formEdit, text="X", state='disabled', command=lambda:onClickImageDelete(2))
    buttonEditImageDelete2.place(x=693, y=300, width=37, height=23)

    Button(formEdit, text="Изменить" if mode == "Редактирование записи о городе" else "Добавить", command=lambda:onClickButtonAccept(mode, row_id)).place(x=335, y=390, width=100, height=50)

    if mode == "Редактирование записи о городе":
        listbox_row_id = listbox.curselection()
        cmd.execute(f'select * from cities where name = \'{listbox.get(listbox_row_id)[0]}\'')
        city = cmd.fetchone()
        textboxEditName.insert("1.0", str(city[0]))
        textboxEditDesc.insert("1.0", str(city[1]))
        if city[2] is not None: loadImage(1, PhotoImage(data=BytesIO(city[2]).read(), width=180, height=105))
        if city[3] is not None: loadImage(2, PhotoImage(data=BytesIO(city[3]).read(), width=180, height=105))
        row_id = city[4]
    else:
        row_id = 0

    formEdit.grab_set()
    formEdit.mainloop()

def onClickKeyF1():
    def onCloseFormRef(): formRef.destroy()
    formRef = Toplevel()
    formRef.geometry("{}x{}+{}+{}".format(500, 180, (formRef.winfo_screenwidth()-500)//2, (formRef.winfo_screenheight()-180)//2))
    formRef.title('О программе')
    formRef.resizable(False, False)
    formRef.protocol("WM_DELETE_WINDOW", onCloseFormRef)
    Label(formRef, text="Путеводитель по городам - версия 1.0.\n© KitsuruDev, 2025. Все права защищены.", font=('Segoe UI', 13)).place(x=8, y=8, width=483, height=150)
    formRef.grab_set()
    formRef.mainloop()

def onCloseFormMain():
    cmd.close()
    connection.close()
    formMain.destroy()

connection = ps.connect(user="user", password="password", host="host", port="port", dbname="dbname") # заменить на своё
cmd = connection.cursor()

formMain = Tk()
formMain.geometry("{}x{}+{}+{}".format(1105, 596, (formMain.winfo_screenwidth()-1105)//2, (formMain.winfo_screenheight()-596)//2))
formMain.title('Путеводитель по городам России')
formMain.resizable(False, False)
formMain.protocol("WM_DELETE_WINDOW", onCloseFormMain)
formMain.bind("<F1>", lambda j: onClickKeyF1())
formMain.option_add("*tearOff", FALSE) # убираем лишние полосы в начале списков подменю

Style().configure(style=".", foreground="black", font=('Segoe UI', 10))

main_menu, list_menu, edit_menu, about_menu = Menu(background="white"), Menu(background="white"), Menu(background="white"), Menu(background="white")
formMain.config(menu=main_menu)
dict_main_menu = {1:["Список городов", "active", 'list_menu'], 2:["Редактирование", "disabled", 'edit_menu'], 3:["Справка", "active", 'about_menu']}
for i in dict_main_menu: main_menu.add_cascade(label=dict_main_menu[i][0], state=dict_main_menu[i][1], menu=eval(dict_main_menu[i][2]))
list_menu.add_command(label="Вывести на экран...", command=onClickMenuList)
dict_list_menu = {1:["Изменить выделенный город...", "disabled", 'lambda:onClickEdit("Редактирование записи о городе")'], 2:["Удалить выделенный город...", "disabled", 'onClickDelete'], 3:["Добавить новый город...", "active", 'lambda:onClickEdit("Добавление записи о городе")']}
for i in dict_list_menu: edit_menu.add_command(label=dict_list_menu[i][0], state=dict_list_menu[i][1], command=eval(dict_list_menu[i][2]))
about_menu.add_command(label="О программе", accelerator="F1", command=onClickKeyF1)

listbox = Listbox(font=('Segoe UI', 14))
listbox.place(x=12, y=12, width=254, height=574)
listbox.bind('<<ListboxSelect>>', onClickListbox)
scrollbar_listbox = Scrollbar(orient="vertical", command=listbox.yview)
scrollbar_listbox.place(x=266, y=12, height=574)
listbox["yscrollcommand"] = scrollbar_listbox.set

labelImage1, labelImage2, labelMain = Label(), Label(), Label(text="Выведите список городов", font=('Segoe UI', 16), anchor="center")
labelImage1.place(x=295, y=50, width=428, height=211)
labelImage2.place(x=295, y=335, width=428, height=211)
labelMain.place(x=790, y=100, width=255, height=32)
textbox = Text(wrap="word", state="disabled", font=('Segoe UI', 12))
textbox.place(x=740, y=164, width=339, height=373)
scrollbar_textbox = Scrollbar(orient="vertical", command=textbox.yview)
scrollbar_textbox.place(x=1079, y=164, height=373)
textbox['yscrollcommand'] = scrollbar_textbox.set

formMain.mainloop()