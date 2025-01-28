from tkinter import *
from tkinter import ttk
import tkinter.filedialog as fdl
import tkinter.messagebox as msb
from ttkthemes import ThemedTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy, math, random, threading, time, copy, librosa
import sounddevice as sd
import soundfile as sf
import requests, copy, os, json
#TamCN coding / DangNhanTam

Window_main = ThemedTk(theme = "arc")
Window_main.title("Tgp Cùng với biểu đồ nào")
Window_main.geometry("1270x700")

#variable:
list_theme = Window_main.themes
languages = json.load(open("BIN/languages.json", "r", encoding = "utf-8"))
variables = []
libs = [
    "fdl", "msb", "Image", "ImageTk", "numpy", "math", "random",
    "threading", "time", "copy", "librosa", "sd", "sf","requests",
    "copy","Data"
]
DONE = "Done: "
SHOW = "Show"
HIDDEN = "Hidden"
LOADINGVIEW = "Loading View...: "
NOTHING = "Nothing: "
FINDHIDDEN = "Find hidden"
languagel = languages["English"]

class Data:
    mouse: dict = {"X": Window_main.winfo_pointerxy()[0],"Y": Window_main.winfo_pointerxy()[1]}
    zoom: float = 1
    song_path: str = "a.mp3"
    song_data, song_sr = librosa.load(song_path)
    print(song_sr)
    song_data = list(song_data)
    width: float = 100
    height: float = 100
    loop: int = 0
    step: float = 1000
    hz: float = 120
    def update(self):
        self.mouse: dict = {"X": Window_main.winfo_pointerxy()[0],"Y": Window_main.winfo_pointerxy()[1]}

class Command:
    def load_tgp():
        global variables, Y_LINE
        path = fdl.askopenfilename(filetypes = [["Tgp file", "*.tgp"]])
        with open(path, "r", encoding = "utf-8") as f:
            data = f.read()
        data = data.replace("\n", "")
        dataline = data.split(";")
        ldataline = len(dataline)
        mode = ""
        call = ""
        Label_title_state.config(text = "Load file")
        for index,item in enumerate(dataline):
            command = item.split("# ")[0]
            value = item.split("# ")[1]
            if command == "mode":
                mode = value
            elif command == "call":
                call = value
            elif command == "variable":
                variables = [variables[0]]
                try:
                    valuev = eval(value)
                    for i in valuev:
                        variables.append(i)
                    Variable.update()
                except Exception as e:
                    Label_title_state.config(text = "Error")
                    Label_state.config(text = "")
                    var_progressbar_load.set(0)
                    Progressbar_load.update()
                    msb.showerror(title = "Error at read file: ", message = f"{e}\nVariable in this file has error")
                    return None
            elif command == "data":
                if mode == "normal":
                    Entry_command.delete(0, END)
                    Entry_command.insert(0, value)
                    if call == "y=":
                        ComboBox_mode.current(0)
                    elif call == "findhidden":
                        ComboBox_mode.current(1)
                    calculator.run(ComboBox_mode.get(), view = False)
                    Label_title_state.config(text = "Done")
                    Label_state.config(text = "")
                    var_progressbar_load.set(0)
                    Progressbar_load.update()
                elif mode == "database":
                    try:
                        if call == "line_main":
                            line_main.set_visible(True)
                            ComboBox_setting_line_main.set(SHOW)
                            Y_LINE = eval(value)
                            line_main.set_ydata(Y_LINE)
                        elif call == "dot_main":
                            dot_main.set_visible(True)
                            ComboBox_setting_dot_main.set(SHOW)
                            X_DOT, Y_DOT = eval(value)
                            dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT])
                        display.draw()
                    except Exception as e:
                        Label_title_state.config(text = "Error")
                        Label_state.config(text = "")
                        var_progressbar_load.set(0)
                        Progressbar_load.update()
                        msb.showerror(title= f"Error at read file:", message = f"{e}\nData in this file has error")
                        return None
            Progressbar_load.step(100 / ldataline)
            Progressbar_load.update()
            Label_state.config(text = f"{(index+1)/ ldataline * 100}%")
    def new_tgp():
        def path_chosse():
            Entry_input_path_new_file.delete(0, END)
            Entry_input_path_new_file.insert(0, fdl.askdirectory())
        def add_commands(commands: list):
            nonlocal datafile
            for command, value in commands[0:-1]:
                datafile += command+ "# " + value + ";\n"
            datafile += commands[-1][0] + "# " + commands[-1][1]
        def save():
            ax.set_title(f"Normal mode (name: {Entry_input_name_new_file.get()})")
            path = Entry_input_path_new_file.get()
            name = Entry_input_name_new_file.get()
            mode = ComboBox_mode_new_file.get()
            call = ComboBox_call_new_file.get()
            if mode == "normal":
                add_commands(
                    [
                        ["mode", mode],
                        ["call", "y=" if ComboBox_mode.get() == "y = " else "findhidden"],
                        ["variable", str(variables)],
                        ["data", Entry_command.get()]
                    ]
                )
            elif mode == "database":
                add_commands(
                    [
                        ["mode", mode],
                        ["call", call],
                        ["data", str(list(Y_LINE)) if call == "plot_line" else str([list(X_DOT), list(Y_DOT)])]
                    ]
                )
            with open(f"{os.path.join(path, name)}.tgp", "w", encoding = "utf-8") as f:
                f.write(datafile)
            Window_new_file.destroy()
        datafile = ""
        Window_new_file = Toplevel(Window_main)
        Window_new_file.geometry("600x400")

        Label_input_path_new_file = Label(Window_new_file, text = "Path: ", font = ("Arial", 12))
        Label_input_path_new_file.grid(row = 0, column = 0, sticky = W)
        Entry_input_path_new_file = ttk.Entry(Window_new_file, width = 20, font = ("Arial", 12))
        Entry_input_path_new_file.grid(row = 0, column = 1, sticky = W)
        Button_input_path_new_file = ttk.Button(Window_new_file, text = "Path", command = path_chosse)
        Button_input_path_new_file.grid(row = 0, column = 2, sticky = W)

        Label_input_name_new_file= Label(Window_new_file, text = "Name (*.tgp): ", font = ("Arial", 12))
        Label_input_name_new_file.grid(row = 1, column = 0, sticky = W)
        Entry_input_name_new_file = ttk.Entry(Window_new_file, width = 20, font = ("Arial", 12))
        Entry_input_name_new_file.grid(row = 1, column = 1, sticky = W)

        Label_input_mode_new_file= Label(Window_new_file, text = "Mode: ", font = ("Arial", 12))
        Label_input_mode_new_file.grid(row = 2, column = 0, sticky = W)
        ComboBox_mode_new_file = ttk.Combobox(Window_new_file, width = 20, values = ["normal", "database"],  font = ("Arial", 12))
        ComboBox_mode_new_file.grid(row = 2, column = 1, sticky = W)

        Label_input_call_new_file= Label(Window_new_file, text = "Call: ", font = ("Arial", 12))
        Label_input_call_new_file.grid(row = 3, column = 0, sticky = W)
        ComboBox_call_new_file = ttk.Combobox(Window_new_file, width = 20, values = ["line_main", "dot_main"],  font = ("Arial", 12))
        ComboBox_call_new_file.grid(row = 3, column = 1, sticky = W)

        Button_ok_new_file = ttk.Button(Window_new_file, text = "Ok", command = save)
        Button_ok_new_file.grid(row = 4, column = 0, sticky = W)
    def convert_to_sound():
        def path_chosse():
            Entry_input_path_sound.delete(0, END)
            Entry_input_path_sound.insert(0, fdl.askdirectory())
        def save():
            import os
            print(Y_LINE)
            path = Entry_input_path_sound.get()
            name = Entry_input_name_sound.get()
            sr = Spinbox_input_sr.get()
            if os.path.exists(path):
                try:
                    sf.write(os.path.join(path, name), Y_LINE, int(sr), subtype='PCM_24')
                except IndexError as e:
                    msb.showerror(f"Error at write file: \n{e}\nYour simple rate is False")
                    return None
            Window_convert_sound.destroy()
            
        Window_convert_sound = Toplevel(Window_main)
        Window_convert_sound.geometry("400x200")
        Window_convert_sound.title("Convert to sound")

        Label_input_path_sound = Label(Window_convert_sound, text = "Path: ", font = ("Arial", 12))
        Label_input_path_sound.grid(row = 0, column = 0, sticky = W)
        Entry_input_path_sound = ttk.Entry(Window_convert_sound, width = 20, font = ("Arial", 12))
        Entry_input_path_sound.grid(row = 0, column = 1, sticky = W)
        Button_input_path_sound = ttk.Button(Window_convert_sound, text = "Path", command = path_chosse)
        Button_input_path_sound.grid(row = 0, column = 2, sticky = W)

        Label_input_name_sound = Label(Window_convert_sound, text = "Name (*.wav)", font = ("Arial", 12))
        Label_input_name_sound.grid(row = 1, column = 0, sticky = W)
        Entry_input_name_sound = ttk.Entry(Window_convert_sound, width = 20, font = ("Arial", 12))
        Entry_input_name_sound.grid(row = 1, column = 1, sticky = W)

        Label_input_sr= Label(Window_convert_sound, text = "Simple rate (Hz): ", font = ("Arial", 12))
        Label_input_sr.grid(row = 2, column = 0, sticky = W)
        Spinbox_input_sr = ttk.Spinbox(Window_convert_sound, from_ = 1, to = 2147483647, width = 18, font = ("Arial", 12))
        Spinbox_input_sr.grid(row = 2, column = 1, sticky = W)        

        Button_save_to_sound = ttk.Button(Window_convert_sound, text = "Save", command = save)
        Button_save_to_sound.grid(row = 3, column = 0, sticky = W)
    def event():
        threading.Thread(target = os.system, args=("2025.mp4",)).start()

class Tool:
    def average(x: list):
        re = 0
        for item in x:
            re += item
        return re / len(x)
    def sum(x: list):
        re = 0
        for item in x:
            re += item
        return re
    def it(x: list):
        re = 1
        for item in x:
            re *= item
        return re
    def less(x: list, step: int):
        re: list = []
        key = 0
        for key in range(0, len(x), step):
            re.append(Tool.average(x[key: key + 1]))
        print(re)
        return re
    def add_data_by_json():
        pass
class Setting:
    def update():
        global line_sprt_x, line_sprt_y, line_main, zoomy, point
        global NONE_AX, SEPARATOR_AX, X_LINE, Y_LINE
        Setting.width()
        Setting.height()
        Setting.step()
        Setting.theme()
        Setting.progressbar()
        Setting.state()
        Setting.language()
        Setting.line_sprt_x()
        Setting.line_sprt_y()
        Setting.line_main()
        Setting.dot_main()
        zoomy = 1
        point = [0, 0]
        ax.set_xlim(-(Data.width + round(Data.width / 10)), Data.width + round(Data.width / 10))
        ax.set_ylim(-(Data.height + round(Data.height / 10)), Data.height + round(Data.height / 10))
        Data.zoom = 1
        NONE_AX = numpy.linspace(0, 0, Data.step)
        SEPARATOR_AX = {"X": numpy.linspace(-Data.width, Data.width, Data.step), "Y": numpy.linspace(-Data.height, Data.height, Data.step)}
        X_LINE = numpy.linspace(-Data.width, Data.width, Data.step)
        Y_LINE = numpy.linspace(-Data.height, Data.height, Data.step)
        line_sprt_x.set_xdata(SEPARATOR_AX["X"])
        line_sprt_x.set_ydata(NONE_AX)
        line_sprt_y.set_xdata(NONE_AX)
        line_sprt_y.set_ydata(SEPARATOR_AX["Y"])
        line_main.set_xdata(X_LINE)
        line_main.set_ydata(Y_LINE)
        display.draw()

    def width():
        Listbox_error.delete(0, END)
        try:
            Data.width = float(Spinbox_setting_width.get())
        except Exception as e:
            for line in str(e).split("\n"):
                Listbox_error.insert(END, line)
    def height():
        Listbox_error.delete(0, END)
        try:
            Data.height = float(Spinbox_setting_height.get())

        except Exception as e:
            for line in str(e).split("\n"):
                Listbox_error.insert(END, line)
    def step():
        Listbox_error.delete(0, END)
        try:
            Data.step = int(Spinbox_setting_step.get())
        except Exception as e:
            for line in str(e).split("\n"):
                Listbox_error.insert(END, line)
    def hz():
        Data.hz = float(Spinbox_setting_hz.get())
        pass
    def theme():
        Window_main.set_theme(ComboBox_setting_theme.get())
    def progressbar():
        if ComboBox_setting_progressbar.get() == SHOW:
            Progressbar_load.grid(row = 0, column = 2)
        elif ComboBox_setting_progressbar.get() == HIDDEN:
            Progressbar_load.grid_forget() 
    def state():
        if ComboBox_setting_state.get() == SHOW:
            Label_state.grid(row = 0, column = 3)
        elif ComboBox_setting_state.get() == HIDDEN:
            Label_state.grid_forget()
    def language():
        global DONE, SHOW, HIDDEN, LOADINGVIEW, NOTHING, FINDHIDDEN, languagel
        language = languages[ComboBox_setting_language.get()]
        DONE = language["DONE"]
        SHOW = language["SHOW"]
        HIDDEN = language["HIDDEN"]
        LOADINGVIEW = language["LOADINGVIEW"]
        NOTHING = language["NOTHING"]
        FINDHIDDEN = language["FINDHIDDEN"]

        Labelframe_error.config(text = language["Labelframe_error"])
        Labelframe_graph.config(text = language["Labelframe_graph"])
        Labelframe_window.config(text = language["Labelframe_window"])
        #Labelframe_plot_elements.config(text = language["Labelframe_plot_elements"])
        Labelframe_variable_add.config(text = language["Labelframe_variable_add"])
        Labelframe_variable_control.config(text = language["Labelframe_variable_control"])

        Label_setting_width.config(text = language["Label_setting_width"])
        Label_setting_height.config(text = language["Label_setting_height"])
        Label_setting_step.config(text = language["Label_setting_step"])
        Label_setting_theme.config(text = language["Label_setting_theme"])
        Label_setting_progressbar.config(text = language["Label_setting_progressbar"])
        Label_setting_state.config(text = language["Label_setting_state"])
        Label_setting_language.config(text = language["Label_setting_language"])
        Label_variable_name.config(text = language["Label_variable_name"])
        Label_variable_value.config(text = language["Label_variable_value"])

        Button_save.config(text = language["Button_save"])
        Button_variable_add.config(text = language["Button_variable_add"])

        ComboBox_setting_progressbar.config(values = language["ComboBox_setting_progressbar"])
        ComboBox_setting_progressbar.current(languagel["ComboBox_setting_progressbar"].index(ComboBox_setting_progressbar.get()))
        ComboBox_setting_state.config(values = language["ComboBox_setting_state"])
        ComboBox_setting_state.current(languagel["ComboBox_setting_state"].index(ComboBox_setting_state.get()))
        ComboBox_mode.config(values = language["ComboBox_mode"])

        Tab_tools.tab(0, text = language["Tab_tools"][0])
        Tab_tools.tab(1, text = language["Tab_tools"][1])
        Tab_tools.tab(2, text = language["Tab_tools"][2])

        Menu_top.entryconfig(1, label = language["Menu_top"]["1"])
        Menu_top_file.entryconfig(0, label = language["Menu_top"]["Menu_top_file"]["0"])
        Menu_top_file.entryconfig(2, label = language["Menu_top"]["Menu_top_file"]["2"])
        Menu_top_file.entryconfig(3, label = language["Menu_top"]["Menu_top_file"]["3"])
        Menu_top_file.entryconfig(5, label = language["Menu_top"]["Menu_top_file"]["5"])
        Menu_top_file.entryconfig(6, label = language["Menu_top"]["Menu_top_file"]["6"])
        Menu_top_file.entryconfig(7, label = language["Menu_top"]["Menu_top_file"]["7"])
        Menu_top.entryconfig(2, label = language["Menu_top"]["2"])
        Menu_top_tool.entryconfig(0, label = language["Menu_top"]["Menu_top_tool"]["0"])
        Menu_top.entryconfig(3, label = language["Menu_top"]["3"])

        languagel = languages[ComboBox_setting_language.get()]
    def line_sprt_x():
        if ComboBox_setting_line_sprt_x.get() == SHOW:
            line_sprt_x.set_visible(True)
        elif ComboBox_setting_line_sprt_x.get() == HIDDEN:
            line_sprt_x.set_visible(False)
    def line_sprt_y():
        if ComboBox_setting_line_sprt_y.get() == SHOW:
            line_sprt_y.set_visible(True)
        elif ComboBox_setting_line_sprt_y.get() == HIDDEN:
            line_sprt_y.set_visible(False)
    def line_main():
        if ComboBox_setting_line_main.get() == SHOW:
            line_main.set_visible(True)
        elif ComboBox_setting_line_main.get() == HIDDEN:
            line_main.set_visible(False)
    def dot_main():
        if ComboBox_setting_dot_main.get() == SHOW:
            dot_main.set_visible(True)
        elif ComboBox_setting_dot_main.get() == HIDDEN:
            dot_main.set_visible(False)
class Zoom:
    def zooms(event):
        global zoomy
        if event.delta > 0: 
            size[0] /= zoom
            size[1] /= zoom
            zoomy = size[1] / lsizey
            ax.set_xlim(-size[0] + point[0], size[0] + point[0])
            ax.set_ylim(-size[1] + point[1], size[1] + point[1])
            display.draw()
        else:
            size[0] *= zoom
            size[1] *= zoom
            zoomy = size[1] / lsizey
            ax.set_xlim(-size[0] + point[0], size[0] + point[0])
            ax.set_ylim(-size[1] + point[1], size[1] + point[1])
            display.draw()
    def zoom(event = ""):
        global zoomy
        size[0] /= zoom
        size[1] /= zoom
        zoomy = size[1] / lsizey
        ax.set_xlim(-size[0] + point[0], size[0] + point[0])
        ax.set_ylim(-size[1] + point[1], size[1] + point[1])
        display.draw()        
    def unzoom(event = ""):
        global zoomy
        size[0] *= zoom
        size[1] *= zoom
        zoomy = size[1] / lsizey
        ax.set_xlim(-size[0] + point[0], size[0] + point[0])
        ax.set_ylim(-size[1] + point[1], size[1] + point[1])
        display.draw()
class Move:
    def hold():
        global point
        lx, ly = ax.transData.inverted().transform([
            display.get_tk_widget().winfo_pointerx(),
            display.get_tk_widget().winfo_pointery()
        ])
        while move:
            x, y = ax.transData.inverted().transform([
                display.get_tk_widget().winfo_pointerx(),
                display.get_tk_widget().winfo_pointery()
            ])
            point[0] += -(x - lx)
            point[1] += y - ly
            ax.set_xlim(-size[0] + point[0] , size[0] + point[0])
            ax.set_ylim(-size[1] + point[1] , size[1] + point[1])
            lx, ly = ax.transData.inverted().transform([
                display.get_tk_widget().winfo_pointerx(),
                display.get_tk_widget().winfo_pointery()
            ])
            display.draw()
            #
    def on(event):
        global move
        move = True
        display.get_tk_widget().config(cursor = "fleur")
        threading.Thread(target = Move.hold, daemon = True).start()
    def off(event):
        global move
        move = False
        display.get_tk_widget().config(cursor = "arrow") 
class Draw:
    def hold():
        global X_DOT, Y_DOT
        while draw:
            x, y = ax.transData.inverted().transform([
                display.get_tk_widget().winfo_pointerx() - display.get_tk_widget().winfo_rootx(),
                display.get_tk_widget().winfo_pointery() - display.get_tk_widget().winfo_rooty()
            ])
            print(display.get_tk_widget().winfo_rootx(), display.get_tk_widget().winfo_rooty())
            X_DOT.append(x)
            Y_DOT.append(-y + 2 * zoomy + 2 * point[1])
            print(X_DOT[-1], Y_DOT[-1], zoomy)
            dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT]) 
            display.draw()
    def undo(event = ""):
        global undox, undoy
        global X_DOT, Y_DOT
        print("work")
        if len(X_DOT) > 0 and len(Y_DOT) > 0:
            if len(undox) < 1000 and len(undoy) < 1000:
                undox.append(X_DOT[-1])
                undoy.append(Y_DOT[-1])
            X_DOT.pop()
            Y_DOT.pop()
            dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT]) 
            display.draw()
    def redo(event = ""):
        global undox, undoy
        global X_DOT, Y_DOT
        if len(undox) > 0 and len(undoy) > 0:
            X_DOT.append(undox[-1])
            Y_DOT.append(undoy[-1])
            undox.pop()
            undoy.pop()
            dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT]) 
            display.draw()
    def clear(event = ""):
        global X_DOT, Y_DOT
        X_DOT = []
        Y_DOT = []
        dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT]) 
        display.draw()
    def on(event):
        global draw 
        draw = True
        display.get_tk_widget().config(cursor = "tcross")
        threading.Thread(target = Draw.hold, daemon = True).start()
    def off(event):
        global draw
        draw = False
        display.get_tk_widget().config(cursor = "arrow") 
class Variable:
    def replace_in(event):
        item = TreeView_variable.selection()
        value = TreeView_variable.item(item)["values"]
        Entry_variable_name.delete(0, END)
        Entry_variable_value.delete(0, END)
        try:
            Entry_variable_name.insert(0, value[0].replace("$", ""))
            Entry_variable_value.insert(0, value[1])
        except IndexError:
            pass

    def post_menu(event):
        Menu_variable.post(event.x_root, event.y_root)
    def get_var_by_name(name: str):
        for variable in variables:
            if variable[0] == name:
                return variable[1]
    def scale_var_update(event = ""):           
        try:
            Scale_variable.config(state = NORMAL)
            Scale_variable.config(from_ = -(float(Variable.get_var_by_name(ComboBox_variable_name.get()))),
                                to = float(Variable.get_var_by_name(ComboBox_variable_name.get())))
        except ValueError:
            Scale_variable.config(state = DISABLED)
    def update_var_by_scale(event):
        Variable.set_var(ComboBox_variable_name.get(), str(round(Scale_variable.get(), len(str(Scale_variable.get())) + 4)))
        for key, variable in enumerate(variables):
            if variable[0] == ComboBox_variable_name.get():
                item = TreeView_variable.get_children()[key]
                TreeView_variable.item(item, values = variable) 
    def del_var():
        for item in TreeView_variable.selection():
            index = TreeView_variable.index(item)
            variables.pop(index)
            TreeView_variable.delete(item)
        ComboBox_variable_name.config(values = [variable[0] for variable in variables])
    def edit_var():
        for item in TreeView_variable.selection():
            index = TreeView_variable.index(item)
            if Entry_variable_name.get().strip().replace(" ","") != "":
                variables[index][0] = "$" + Entry_variable_name.get()
                if Variable.check_var_in_string(Entry_variable_value.get()):
                    variables[index][1] = Entry_variable_value.get()
        for item in TreeView_variable.get_children():
            TreeView_variable.delete(item)
        for variable in variables:
            TreeView_variable.insert("", END, values = variable)
        ComboBox_variable_name.config(values = [variable[0] for variable in variables])
        Variable.scale_var_update()
    def set_var(name: str, value: str = "0"):
        for key, variable in enumerate(variables):
            if variable[0] == name:
                variables[key][1] = value
                break
    def replace_var(string: str):
        value = string
        finnish = False
        start = time.time()
        while True:
            for variable in variables:
                value = value.replace(variable[0], f"({variable[1]})")
            try:
                eval(value)
                finnish = True
            except:
                pass
            if time.time() - start >= 0.5:
                finnish = True
            if finnish:
                break
        return value
    def check_var_exist(value: str):
        check = False
        for variable in variables:
            if variable[0] == value:
                check = True
        return check
    def check_var_in_string(string: str):
        value = string
        start = time.time()
        while True:
            for variable in variables:
                value = value.replace(variable[0], f"({variable[1]})")
            try:
                eval(value)
                break
            except:
                pass
            if time.time() - start >= 1:
                return False
        return True
    def add_to_tree():
        if Entry_variable_name.get().strip().replace(" ","") != "" and not Variable.check_var_exist("$" + Entry_variable_name.get().strip()):
            if Variable.check_var_in_string(Entry_variable_value.get()):
                variables.append(["$" + Entry_variable_name.get().replace("$", ""), Entry_variable_value.get()])
        for item in TreeView_variable.get_children():
            TreeView_variable.delete(item)
        for variable in variables:
            TreeView_variable.insert("", END, values = variable)
        ComboBox_variable_name.config(values = [variable[0] for variable in variables])
    def update():
        for item in TreeView_variable.get_children():
            TreeView_variable.delete(item)
        for variable in variables:
            TreeView_variable.insert("", END, values = variable)
        ComboBox_variable_name.config(values = [variable[0] for variable in variables])
def post_menu():
    x_mouse, y_mouse = Window_main.winfo_pointerxy()
    Menu_light.post(x_mouse, y_mouse)
def tips(event):
    for item in libs:
        if Entry_command.get().rfind(item) > -1 and Entry_command.get().rfind(item) + len(item) == Entry_command.index("insert"):
            if Menu_light.index(END) is not None:
                Menu_light.delete(0, END)
            for item in dir(eval(item)):
                Menu_light.add_command(label = item, command = lambda i = item:Entry_command.insert(Entry_command.index("insert"), f".{i}"))
            post_menu()
class Calculator:
    def run(self, mode, view = True):
        if mode == "y = ":
            line_main.set_visible(True)
            ComboBox_setting_line_main.set(SHOW)
            if view:
                return self.cal1()
            else:
                return self.cal1nv()
        elif mode == FINDHIDDEN:
            line_main.set_visible(True)
            ComboBox_setting_dot_main.set(SHOW)
            if view:
                return self.cal2()
            else:
                return self.cal2nv()
    def cal1(self, event = ""):
        global loop
        global X_LINE
        global Y_LINE
        X_LINE = numpy.linspace(-Data.width, Data.width, Data.step)
        Y_LINE = numpy.linspace(-Data.height, Data.height, Data.step)
        Listbox_error.delete(0, END)
        len_x = len(list(X_LINE))
        Button_stop.config(state = NORMAL)
        def core(x):
            Data.update(Data)
            Variable.set_var("$x", str(round(x, 10)))
            Data.loop += 1
            Progressbar_load.step(round(1 / len_x * 100, 10))
            Progressbar_load.update()
            Label_state.config(text = f"{round(Data.loop/ len_x * 100, 10)}%")
            try:
                result = eval(Variable.replace_var(Entry_command.get()))
                return result
            except ZeroDivisionError:
                return None
        def main():
            global Y_LINE
            try:
                Y_LINE = numpy.array(list(map(core, list(X_LINE))))
                Data.loop = 0
                line_main.set_ydata(Y_LINE)  
                display.draw()
            except Exception as e:
                self.loop_stop()
                for index, line in enumerate(str(e).split("\n")):
                    Listbox_error.insert(END, line)
                    Listbox_error.itemconfigure(index, fg="#f55545")
                Data.loop = 0
        Label_title_state.config(text = LOADINGVIEW)
        main()
        while loop:
            main()
            time.sleep(1 / Data.hz)
        var_progressbar_load.set(0)
        Progressbar_load.update()
        Label_title_state.config(text = DONE)
        Label_state.config(text = "")
    def cal1nv(self, event = ""):
        global loop
        global X_LINE
        global Y_LINE
        X_LINE = numpy.linspace(-Data.width, Data.width, Data.step)
        Y_LINE = numpy.linspace(-Data.height, Data.height, Data.step)
        Listbox_error.delete(0, END)
        len_x = len(list(X_LINE))
        Button_stop.config(state = NORMAL)
        def core(x):
            Data.update(Data)
            Variable.set_var("$x", str(round(x, 10)))
            Data.loop += 1
            try:
                result = eval(Variable.replace_var(Entry_command.get()))
                return result
            except ZeroDivisionError:
                return None
        def main():
            global Y_LINE
            try:
                Y_LINE = numpy.array(list(map(core, list(X_LINE))))
                Data.loop = 0
                line_main.set_ydata(Y_LINE)  
                display.draw()
            except Exception as e:
                self.loop_stop()
                for index, line in enumerate(str(e).split("\n")):
                    Listbox_error.insert(END, line)
                    Listbox_error.itemconfigure(index, fg="#f55545")
                Data.loop = 0
        main()
        while loop:
            main()
            time.sleep(1 / Data.hz)
    def cal2(self, event = ""):
        global loop
        global X_LINE, Y_LINE
        global X_DOT, Y_DOT
        X_DOT = []
        Y_DOT = []
        Listbox_error.delete(0, END)
        len_x = len(list(X_LINE))
        Button_stop.config(state = NORMAL)
        dot_main_state = True
        dot_main.set_visible(dot_main_state)
        def main():
            global Y_LINE
            try:
                for x in SEPARATOR_AX["X"]:
                    Variable.set_var("$x", str(round(x, 10)))
                    for y in SEPARATOR_AX["Y"]:
                        Variable.set_var("$y", str(round(y, 10)))
                        Data.update(Data)
                        print(eval(Variable.replace_var(Entry_command.get())))
                        if eval(Variable.replace_var(Entry_command.get())):
                            Y_DOT.append(y)
                            X_DOT.append(x)
                    Data.loop += 1
                    Progressbar_load.step(round(1 / len_x * 100, 10))
                    Progressbar_load.update()
                    Label_state.config(text = f"{round(Data.loop/ len_x * 100, 10)}%")

                Data.loop = 0
                dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT]) 
                display.draw()
            except Exception as e:
                self.loop_stop()
                for index, line in enumerate(str(e).split("\n")):
                    Listbox_error.insert(END, line)
                    Listbox_error.itemconfigure(index, fg="#f55545")
                Data.loop = 0
        Label_title_state.config(text = LOADINGVIEW)
        main()
        while loop:
            main()
            time.sleep(1 / Data.hz)
        var_progressbar_load.set(0)
        Progressbar_load.update()
        Label_title_state.config(text = DONE)
        Label_state.config(text = "")
    def cal2nv(self, event = ""):
        global loop
        global X_LINE, Y_LINE
        global X_DOT, Y_DOT
        X_DOT = []
        Y_DOT = []
        Listbox_error.delete(0, END)
        len_x = len(list(X_LINE))
        Button_stop.config(state = NORMAL)
        dot_main_state = True
        dot_main.set_visible(dot_main_state)
        def main():
            global Y_LINE
            try:
                for x in SEPARATOR_AX["X"]:
                    Variable.set_var("$x", str(round(x, 10)))
                    for y in SEPARATOR_AX["Y"]:
                        Variable.set_var("$y", str(round(y, 10)))
                        Data.update(Data)
                        print(eval(Variable.replace_var(Entry_command.get())))
                        if eval(Variable.replace_var(Entry_command.get())):
                            Y_DOT.append(y)
                            X_DOT.append(x)
                    Data.loop += 1
                Data.loop = 0
                dot_main.set_offsets(numpy.c_[X_DOT, Y_DOT]) 
                display.draw()
            except Exception as e:
                self.loop_stop()
                for index, line in enumerate(str(e).split("\n")):
                    Listbox_error.insert(END, line)
                    Listbox_error.itemconfigure(index, fg="#f55545")
                Data.loop = 0
        main()
        while loop:
            main()
            time.sleep(1 / Data.hz)
    def loop_start(self):
        global loop
        loop = True
        threading.Thread(target = self.run, args = (ComboBox_mode.get(),)).start()
        Button_loop.config(state = DISABLED)
        Button_run.config(state = DISABLED)
        Entry_command.config(state = DISABLED)
    def loop_stop(self):
        global loop
        loop = False
        Button_loop.config(state = NORMAL)
        Button_run.config(state = NORMAL)
        Button_stop.config(state = DISABLED)
        Entry_command.config(state = NORMAL)

image_logo = Image.open("BIN/logo.png")
image_logo = ImageTk.PhotoImage(image_logo.resize([round(image_logo.size[0] * (25 / image_logo.size[1])), 25]))
image_run = Image.open("BIN/Run.png")
image_run = ImageTk.PhotoImage(image_run.resize([23, 23]))
image_stop = Image.open("BIN/Stop.png")
image_stop = ImageTk.PhotoImage(image_stop.resize([23, 23]))
image_loop = Image.open("BIN/Loop.png")
image_loop = ImageTk.PhotoImage(image_loop.resize([23, 23]))
image_zoom = Image.open("BIN/Zoom.png")
image_zoom = ImageTk.PhotoImage(image_zoom.resize([23, 23]))
image_unzoom = Image.open("BIN/Unzoom.png")
image_unzoom = ImageTk.PhotoImage(image_unzoom.resize([23, 23]))
image_2025 = Image.open("BIN/2025.jpeg")
image_2025 = ImageTk.PhotoImage(image_2025.resize([50, 23]))

Menu_top = Menu(Window_main)
Menu_top_file = Menu(Menu_top, tearoff = 0)

Menu_top_file.add_command(label = "New graph", command = Command.new_tgp)
Menu_top_file.add_separator()
Menu_top_file.add_command(label = "Load graph", command = Command.load_tgp)
Menu_top_file.add_command(label = "Load variable")
Menu_top_file.add_separator()
Menu_top_file.add_command(label = "Save graph")
Menu_top_file.add_command(label = "Save graph with invide mode")
Menu_top_file.add_command(label = "Save variable")

Menu_top.add_cascade(menu = Menu_top_file, label = "File")

Menu_top_tool = Menu(Menu_top, tearoff = 0)

Menu_top_tool.add_command(label = "Convert to sound(Have in 1.1 version)", command = Command.convert_to_sound)

Menu_top.add_cascade(menu = Menu_top_tool, label = "Tool")

Menu_top.add_command(label = "Help")

Window_main.config(menu = Menu_top)

Frame_status = PanedWindow(Window_main)

Label_creator = Label(Frame_status, image = image_logo)
Label_creator.grid(row = 0, column = 0)

Label_title_state = Label(Frame_status, text = "Nothing: ")
Label_title_state.grid(row = 0, column = 1)

var_progressbar_load = IntVar()

Progressbar_load = ttk.Progressbar(Frame_status, variable=var_progressbar_load, orient = HORIZONTAL, length = 250)
Progressbar_load.grid(row = 0, column = 2)

Label_state = Label(Frame_status)
Label_state.grid(row = 0, column = 3)

Button_new_year = ttk.Button(Frame_status, image = image_2025, padding = 0, command = Command.event)
Button_new_year.grid(row = 0, column = 4)

Frame_status.pack(fill = X, side = BOTTOM, ipady = 2)

Tab_tools = ttk.Notebook(Window_main, width = 270)

Frame_notification = Frame(Tab_tools)

Labelframe_error = ttk.Labelframe(Frame_notification, text = "Notification")

Listbox_error = Listbox(Labelframe_error, width = 26, height = 20, font = ("Arial", 12))
Listbox_error.grid(row = 0, column = 0)

Scrollbar_x_listbox = ttk.Scrollbar(Labelframe_error, orient = HORIZONTAL, command = Listbox_error.xview)
Scrollbar_x_listbox.grid(row = 1, column = 0, ipadx = 100)

Scrollbar_y_listbox = ttk.Scrollbar(Labelframe_error, orient = VERTICAL, command = Listbox_error.yview)
Scrollbar_y_listbox.grid(row = 0, column = 1, ipady = 175)

Listbox_error.config(xscrollcommand = Scrollbar_x_listbox.set,
                     yscrollcommand = Scrollbar_y_listbox.set) 

Labelframe_error.grid(row = 0, column = 0, columnspan = 2)

Entry_input = ttk.Entry(Frame_notification, width = 26, font = ("Arial", 12))
Entry_input.grid(row = 1, column = 0)

Tab_tools.add(Frame_notification, text = "Console")

Frame_setting = Frame(Tab_tools)

Labelframe_graph = ttk.Labelframe(Frame_setting, text = "Graph")

Label_setting_width = Label(Labelframe_graph, text = "Width: ", font = ("Arial", 12))
Label_setting_width.grid(row = 0, column = 0, sticky = W)
Spinbox_setting_width = ttk.Spinbox(Labelframe_graph, from_ = -2147483647, to = 2147483647, font = ("Arial", 12))
Spinbox_setting_width.grid(row = 0, column = 1, sticky = W)

Label_setting_height = Label(Labelframe_graph, text =  "Height: ", font = ("Arial", 12))
Label_setting_height.grid(row = 1, column = 0, sticky = W)
Spinbox_setting_height = ttk.Spinbox(Labelframe_graph, from_ = -2147483647, to = 2147483647, font = ("Arial", 12))
Spinbox_setting_height.grid(row = 1, column = 1, sticky = W)

Label_setting_step = Label(Labelframe_graph, text = "Step: ", font = ("Arial", 12))
Label_setting_step.grid(row = 2, column = 0, sticky = W)
Spinbox_setting_step = ttk.Spinbox(Labelframe_graph, from_ = -2147483647, to = 2147483647, font = ("Arial", 12))
Spinbox_setting_step.grid(row = 2, column = 1, sticky = W)

Label_setting_hz = Label(Labelframe_graph, text = "Hz: ", font = ("Arial", 12))
Label_setting_hz.grid(row = 3, column = 0, sticky = W)
Spinbox_setting_hz = ttk.Spinbox(Labelframe_graph, from_ = 30, to = 360, font = ("Arial", 12))
Spinbox_setting_hz.grid(row = 3, column = 1, sticky = W)

Labelframe_graph.grid(row = 0, column = 0, sticky = W)

Labelframe_window = ttk.Labelframe(Frame_setting, text = "Window")

Label_setting_theme = Label(Labelframe_window, text = "Theme: ", font = ("Arial", 12))
Label_setting_theme.grid(row = 0, column = 0, sticky = W)
ComboBox_setting_theme = ttk.Combobox(Labelframe_window, values = list_theme, width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_theme.current(list_theme.index("arc"))
ComboBox_setting_theme.grid(row = 0, column = 1, sticky = W)

Label_setting_progressbar = Label(Labelframe_window, text = "Progressbar: ", font = ("Arial", 12))
Label_setting_progressbar.grid(row = 1, column = 0, sticky = W)
ComboBox_setting_progressbar = ttk.Combobox(Labelframe_window, values = [SHOW, HIDDEN], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_progressbar.current(0) 
ComboBox_setting_progressbar.grid(row = 1, column = 1, sticky = W)

Label_setting_state = Label(Labelframe_window, text = "State (%): ", font = ("Arial", 12))
Label_setting_state.grid(row = 2, column = 0, sticky = W)
ComboBox_setting_state = ttk.Combobox(Labelframe_window, values = [SHOW, HIDDEN], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_state.current(0) 
ComboBox_setting_state.grid(row = 2, column = 1, sticky = W)

Label_setting_language = Label(Labelframe_window, text = "Language: ", font = ("Arial", 12))
Label_setting_language.grid(row = 3, column = 0, sticky = W)
ComboBox_setting_language = ttk.Combobox(Labelframe_window, values = list(languages.keys()), width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_language.current(0) 
ComboBox_setting_language.grid(row = 3, column = 1, sticky = W)

Labelframe_window.grid(row = 1, column = 0, sticky = W)

Labelframe_plot_elements = ttk.Labelframe(Frame_setting, text = "Plot elements")

Label_setting_line_sprt_x = Label(Labelframe_plot_elements, text = "line_sprt_x: ", font = ("Arial", 12))
Label_setting_line_sprt_x.grid(row = 0, column = 0, sticky = W)
ComboBox_setting_line_sprt_x = ttk.Combobox(Labelframe_plot_elements, values = [SHOW, HIDDEN], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_line_sprt_x.current(0) 
ComboBox_setting_line_sprt_x.grid(row = 0, column = 1, sticky = W)

Label_setting_line_sprt_y = Label(Labelframe_plot_elements, text = "line_sprt_y: ", font = ("Arial", 12))
Label_setting_line_sprt_y.grid(row = 1, column = 0, sticky = W)
ComboBox_setting_line_sprt_y = ttk.Combobox(Labelframe_plot_elements, values = [SHOW, HIDDEN], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_line_sprt_y.current(0) 
ComboBox_setting_line_sprt_y.grid(row = 1, column = 1, sticky = W)

Label_setting_line_main = Label(Labelframe_plot_elements, text = "line_main: ", font = ("Arial", 12))
Label_setting_line_main.grid(row = 2, column = 0, sticky = W)
ComboBox_setting_line_main = ttk.Combobox(Labelframe_plot_elements, values = [SHOW, HIDDEN], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_line_main.current(0) 
ComboBox_setting_line_main.grid(row = 2, column = 1, sticky = W)

Label_setting_dot_main = Label(Labelframe_plot_elements, text = "dot_main: ", font = ("Arial", 12))
Label_setting_dot_main.grid(row = 3, column = 0, sticky = W)
ComboBox_setting_dot_main = ttk.Combobox(Labelframe_plot_elements, values = [SHOW, HIDDEN], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_dot_main.current(1) 
ComboBox_setting_dot_main.grid(row = 3, column = 1, sticky = W)

Labelframe_plot_elements.grid(row = 2, column = 0, sticky = W)

Button_save = ttk.Button(Frame_setting, text = "Save", command = Setting.update)
Button_save.grid(row = 3, column = 0, sticky = E)

Tab_tools.add(Frame_setting, text = "Setting")

Frame_variable = Frame(Tab_tools)

TreeView_variable = ttk.Treeview(Frame_variable, columns = ["Name", "Value"], show = "tree headings")
TreeView_variable.heading("Name", text = "Name", anchor = CENTER)
TreeView_variable.heading("Value", text = "Value", anchor = CENTER)
TreeView_variable.column("#0", width = 25)
TreeView_variable.column("Name", width = 70)
TreeView_variable.column("Value", width = 130)

Scrollbar_y_treeview = ttk.Scrollbar(Frame_variable, orient = VERTICAL, command = TreeView_variable.yview)
Scrollbar_y_treeview.grid(row = 0, column = 1, ipady = 116)
Scrollbar_x_treeview = ttk.Scrollbar(Frame_variable, orient = HORIZONTAL, command = TreeView_variable.xview)
Scrollbar_x_treeview.grid(row = 1, column = 0, ipadx = 100)

TreeView_variable.config(yscrollcommand = Scrollbar_y_treeview.set, 
                         xscrollcommand = Scrollbar_x_treeview.set)

TreeView_variable.bind("<<TreeviewSelect>>", Variable.replace_in)

Menu_variable = Menu(TreeView_variable, tearoff = 0)
Menu_variable.add_command(label = "Delete", command = Variable.del_var)
Menu_variable.add_command(label = "Edit", command = Variable.edit_var)

TreeView_variable.grid(row = 0, column = 0)
TreeView_variable.bind("<Button-3>", Variable.post_menu)

Labelframe_variable_add = ttk.Labelframe(Frame_variable, text = "Add Variable")

Label_variable_name = Label(Labelframe_variable_add, text = "Name: ", font = ("Arial", 12))
Label_variable_name.grid(row = 0, column = 0, sticky = W)
Entry_variable_name = ttk.Entry(Labelframe_variable_add, font = ("Arial", 12))
Entry_variable_name.grid(row = 0, column = 1, sticky = W)

Label_variable_value = Label(Labelframe_variable_add, text = "Value: ", font = ("Arial", 12))
Label_variable_value.grid(row = 1, column = 0, sticky = W)
Entry_variable_value = ttk.Entry(Labelframe_variable_add, font = ("Arial", 12))
Entry_variable_value.grid(row = 1, column = 1, sticky = W)

Button_variable_add = ttk.Button(Labelframe_variable_add, text = "Add", command = Variable.add_to_tree)
Button_variable_add.grid(row = 2, column = 1, sticky = E)

Labelframe_variable_add.grid(row = 2, column = 0, sticky = W)

Labelframe_variable_control = ttk.Labelframe(Frame_variable, text = "Control Variable")

ComboBox_variable_name = ttk.Combobox(Labelframe_variable_control, width = 3, font = ("Arial", 12))
ComboBox_variable_name.grid(row = 0, column = 0)
ComboBox_variable_name.bind("<<ComboboxSelected>>", Variable.scale_var_update)
Scale_variable = ttk.Scale(Labelframe_variable_control, length = 210, command = Variable.update_var_by_scale)
Scale_variable.grid(row = 0, column = 1)

Labelframe_variable_control.grid(row = 3, column = 0, sticky = W)

Tab_tools.add(Frame_variable, text = "Variable")

Tab_tools.pack(fill = Y, side = RIGHT, pady = 1)

Frame_in = Frame(Window_main)

ComboBox_mode = ttk.Combobox(Frame_in, values = ["y = ", FINDHIDDEN], font = ("Arial", 12, "bold"), width = 10, state = "readonly")
ComboBox_mode.current(0)
ComboBox_mode.pack(side = LEFT)

Entry_command = ttk.Entry(Frame_in, font = ("Arial", 12), width = 50)
Entry_command.pack(fill = X, side = LEFT)
Entry_command.bind("<KeyRelease>", tips)

Menu_light = Menu(Window_main, tearoff = 0)
calculator = Calculator()
Button_run = ttk.Button(Frame_in, image = image_run, command = lambda: calculator.run(ComboBox_mode.get()))
Button_run.pack(side = LEFT, padx = 1)

Button_loop = ttk.Button(Frame_in, image =  image_loop, command = calculator.loop_start)
Button_loop.pack(side = LEFT, padx = 1)

Button_stop = ttk.Button(Frame_in, image = image_stop, state = DISABLED, command = calculator.loop_stop)
Button_stop.pack(side = LEFT, padx = 1)

Button_zoom = ttk.Button(Frame_in, image =  image_zoom, command = Zoom.zoom)
Button_zoom.pack(side = LEFT, padx = 1)

Button_unzoom = ttk.Button(Frame_in, image = image_unzoom, command = Zoom.unzoom)
Button_unzoom.pack(side = LEFT, padx = 1)

Frame_in.pack(fill = X, side = BOTTOM)

Frame_main = Frame(Window_main)


loop = None
point = [0, 0]
zoomy = 1
undox = []
undoy = []
size = [Data.width, Data.height]
lsizey = size[1]
zoom = 1.1
move = False
draw = False
figure = Figure([10, 10], 100)
ax = figure.add_subplot(1, 1, 1)
ax.grid(True, which = 'both')
NONE_AX = numpy.linspace(0, 0, Data.step)
SEPARATOR_AX = {"X": numpy.linspace(-Data.width, Data.width, Data.step), "Y": numpy.linspace(-Data.height, Data.height, Data.step)}
X_LINE = numpy.linspace(-Data.width, Data.width, Data.step)
Y_LINE = numpy.linspace(-Data.height, Data.height, Data.step)
X_DOT = []
Y_DOT = []
line_sprt_x,  = ax.plot(SEPARATOR_AX["X"], NONE_AX, color = "blue")
line_sprt_y,  = ax.plot(NONE_AX, SEPARATOR_AX["Y"], color = "blue")
line_main, = ax.plot(X_LINE, Y_LINE, color = "red")
dot_main = ax.scatter(X_DOT, Y_DOT, color = "green")
line_sprt_x_state = True
line_sprt_y_state = True
line_main_state = True
dot_main_state = False
line_sprt_x.set_visible(line_sprt_x_state)
line_sprt_y.set_visible(line_sprt_y_state)
line_main.set_visible(line_main_state)
dot_main.set_visible(dot_main_state)
ax.set_xlim(-size[0] + point[0], size[0] + point[0])
ax.set_ylim(-size[1] + point[1], size[1] + point[1])

ax.set_title("Test mode")
ax.set_xlabel("X →")
ax.set_ylabel("Y →")

variables.append(["$x",list(X_LINE)[0]])
variables.append(["$y",list(X_LINE)[0]])
for item in TreeView_variable.get_children():
    TreeView_variable.delete(item)
for variable in variables:
    TreeView_variable.insert("", END, values = variable)

ComboBox_variable_name.config(values = [variable[0] for variable in variables])
ComboBox_variable_name.current(0)
Variable.scale_var_update()

display = FigureCanvasTkAgg(figure, Window_main)
display.draw()
display.get_tk_widget().pack(fill = BOTH, expand = True)
display.get_tk_widget().bind("<ButtonPress-1>", Move.on)
display.get_tk_widget().bind("<ButtonRelease-1>", Move.off)
display.get_tk_widget().bind("<ButtonPress-3>",Draw.on)
display.get_tk_widget().bind("<ButtonRelease-3>", Draw.off)
Window_main.bind("<Control-Key-z>", Draw.undo)
Window_main.bind("<Control-Key-y>", Draw.redo)
Window_main.bind("<Control-Key-d>", Draw.clear)
display.get_tk_widget().bind("<MouseWheel>", Zoom.zooms)
#display.bind()

Frame_main.pack(fill = BOTH, expand = True)

Window_main.mainloop()