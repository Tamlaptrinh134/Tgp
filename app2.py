from tkinter import *
from tkinter import ttk
import tkinter.filedialog as fdl
import tkinter.messagebox as msb
from ttkthemes import ThemedTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy, math, random, threading, time, copy, librosa
#TamCN coding / DangNhanTam

Window_main = ThemedTk(theme = "arc")
Window_main.title("Tgp Cùng với biểu đồ nào")
Window_main.geometry("1270x700")

#variable:
list_theme = Window_main.themes
variables = []

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
    hz: float = 60
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
        Label_title_state.config(text = "Load file")
        for index,item in enumerate(dataline):
            command = item.split(": ")[0]
            value = item.split(": ")[1]
            if command == "mode":
                mode = value
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
                elif mode == "invide":
                    try:
                        Y_LINE = eval(value)
                    except Exception as e:
                        Label_title_state.config(text = "Error")
                        Label_state.config(text = "")
                        var_progressbar_load.set(0)
                        Progressbar_load.update()
                        msb.showerror(f"Error at read file: \n{e}\nData in this file has error")
                        return None
            Progressbar_load.step(100 / ldataline)
            Progressbar_load.update()
            Label_state.config(text = f"{index / ldataline * 100}%")
        math_low()
        Label_title_state.config(text = "Done")
        Label_state.config(text = "")
        var_progressbar_load.set(0)
        Progressbar_load.update()
    def new_tgp():
        Window_new_file = Toplevel(Window_main)
        Window_new_file.geometry("600x400")
class Tool:
    def average(x: list):
        re = 0
        for item in x:
            re += item
        return re / len(x)
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
        global line_sprt_x, line_sprt_y, line_main
        global NONE_AX, SEPARATOR_AX, X_LINE, Y_LINE
        Setting.width()
        Setting.height()
        Setting.step()
        Setting.theme()
        Setting.progressbar()
        Setting.state()
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
        #Data.hz = float(Spinbox_setting_width.get())
        pass
    def theme():
        Window_main.set_theme(ComboBox_setting_theme.get())
    def progressbar():
        if ComboBox_setting_progressbar.get() == "Show":
            Progressbar_load.grid(row = 0, column = 2)
        elif ComboBox_setting_progressbar.get() == "Hidden":
            Progressbar_load.grid_forget() 
    def state():
        if ComboBox_setting_state.get() == "Show":
            Label_state.grid(row = 0, column = 3)
        elif ComboBox_setting_state.get() == "Hidden":
            Label_state.grid_forget() 
class Zoom:
    def zoom(event = ""):
        ax.set_xlim(ax.get_xlim()[0] + ax.get_xlim()[0] /  -2, ax.get_xlim()[1] - ax.get_xlim()[1] / 2)
        ax.set_ylim(ax.get_ylim()[0] + ax.get_ylim()[0] / -2, ax.get_ylim()[1] - ax.get_ylim()[1] / 2)
        display.draw()        
    def unzoom(event = ""):
        ax.set_xlim(ax.get_xlim()[0] - ax.get_xlim()[0] / -2, ax.get_xlim()[1] + ax.get_xlim()[1] / 2)
        ax.set_ylim(ax.get_ylim()[0] - ax.get_ylim()[0] / -2, ax.get_ylim()[1] + ax.get_ylim()[1] / 2)
        display.draw()      
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
def math_low(event = ""):
    global loop
    Listbox_error.delete(0, END)
    len_x = len(list(X_LINE))
    def core(x):
        Data.update(Data)
        Variable.set_var("$x", str(x))
        Data.loop += 1
        Progressbar_load.step(round(1 / len_x * 100, 10))
        Progressbar_load.update()
        Label_state.config(text = f"{round(Data.loop/ len_x * 100, 10)}%")
        return eval(Variable.replace_var(Entry_command.get()))
    def main():
        try:
            Y_LINE = numpy.array(list(map(core, list(X_LINE))))
            Data.loop = 0
            line_main.set_ydata(Y_LINE)  
            display.draw()
        except Exception as e:
            if Entry_command.get().rfind("math") > -1 and Entry_command.get()[len(Entry_command.get()) - 1] == "h":
                if Menu_light.index(END) is not None:
                    Menu_light.delete(0, END)
                for item in dir(math):
                    Menu_light.add_command(label = item, command = lambda i = item:Entry_command.insert(END, f".{i}"))
                post_menu()
            elif Entry_command.get().rfind("random") > -1 and Entry_command.get()[len(Entry_command.get()) - 1] == "m":
                if Menu_light.index(END) is not None:
                    Menu_light.delete(0, END)
                for item in dir(random):
                    Menu_light.add_command(label = item, command = lambda i = item:Entry_command.insert(END, f".{i}"))
                post_menu()
            elif Entry_command.get().rfind("Data") > -1 and Entry_command.get()[len(Entry_command.get()) - 1] == "a":
                if Menu_light.index(END) is not None:
                    Menu_light.delete(0, END)
                for item in dir(Data):
                    Menu_light.add_command(label = item, command = lambda i = item:Entry_command.insert(END, f".{i}"))
                post_menu()
            else:
                loop_stop()
            
            for index, line in enumerate(str(e).split("\n")):
                Listbox_error.insert(END, line)
                Listbox_error.itemconfigure(index, fg="#f55545")
            Data.loop = 0
    Label_title_state.config(text = "Loading View...: ")
    main()
    while loop:
        main()
        time.sleep(1 / Data.hz)
    var_progressbar_load.set(0)
    Progressbar_load.update()
    Label_title_state.config(text = "Done: ")
    Label_state.config(text = "")
def loop_start():
    global loop
    loop = True
    threading.Thread(target = math_low).start()
    Button_loop.config(state = DISABLED)
    Button_run.config(state = DISABLED)
    Button_stop.config(state = NORMAL)
    Entry_command.config(state = DISABLED)
def loop_stop():
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

Labelframe_graph.grid(row = 0, column = 0, sticky = W)

Labelframe_window = ttk.Labelframe(Frame_setting, text = "Window")

Label_setting_theme = Label(Labelframe_window, text = "Theme: ", font = ("Arial", 12))
Label_setting_theme.grid(row = 0, column = 0, sticky = W)
ComboBox_setting_theme = ttk.Combobox(Labelframe_window, values = list_theme, width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_theme.current(list_theme.index("arc"))
ComboBox_setting_theme.grid(row = 0, column = 1, sticky = W)

Label_setting_progressbar = Label(Labelframe_window, text = "Progressbar: ", font = ("Arial", 12))
Label_setting_progressbar.grid(row = 1, column = 0, sticky = W)
ComboBox_setting_progressbar = ttk.Combobox(Labelframe_window, values = ["Show", "Hidden"], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_progressbar.current(0) 
ComboBox_setting_progressbar.grid(row = 1, column = 1, sticky = W)

Label_setting_state = Label(Labelframe_window, text = "State (%): ", font = ("Arial", 12))
Label_setting_state.grid(row = 2, column = 0, sticky = W)
ComboBox_setting_state = ttk.Combobox(Labelframe_window, values = ["Show", "Hidden"], width = 16, state = "readonly", font = ("Arial", 12))
ComboBox_setting_state.current(0) 
ComboBox_setting_state.grid(row = 2, column = 1, sticky = W)

Labelframe_window.grid(row = 1, column = 0, sticky = W)

Button_save = ttk.Button(Frame_setting, text = "Save", command = Setting.update)
Button_save.grid(row = 2, column = 0, sticky = E)

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

Label_XY = Label(Frame_in, text = "y = ", font = ("Arial", 12, "bold"))
Label_XY.pack(side = LEFT)

Entry_command = ttk.Entry(Frame_in, font = ("Arial", 12), width = 50)
Entry_command.pack(fill = X, side = LEFT)
#Entry_command.bind("<KeyRelease>", math_low)

Menu_light = Menu(Window_main, tearoff = 0)

Button_run = ttk.Button(Frame_in, image = image_run, command = math_low)
Button_run.pack(side = LEFT, padx = 1)

Button_loop = ttk.Button(Frame_in, image =  image_loop, command = loop_start)
Button_loop.pack(side = LEFT, padx = 1)

Button_stop = ttk.Button(Frame_in, image = image_stop, state = DISABLED, command = loop_stop)
Button_stop.pack(side = LEFT, padx = 1)

Button_zoom = ttk.Button(Frame_in, image =  image_zoom, command = Zoom.zoom)
Button_zoom.pack(side = LEFT, padx = 1)

Button_unzoom = ttk.Button(Frame_in, image = image_unzoom, command = Zoom.unzoom)
Button_unzoom.pack(side = LEFT, padx = 1)

Frame_in.pack(fill = X, side = BOTTOM)

Frame_main = Frame(Window_main)


loop = None
figure = Figure([10, 10], 100)
ax = figure.add_subplot(1, 1, 1)
ax.grid(True, which = 'both')
NONE_AX = numpy.linspace(0, 0, Data.step)
SEPARATOR_AX = {"X": numpy.linspace(-Data.width, Data.width, Data.step), "Y": numpy.linspace(-Data.height, Data.height, Data.step)}
X_LINE = numpy.linspace(-Data.width, Data.width, Data.step)
Y_LINE = numpy.linspace(-Data.height, Data.height, Data.step)
line_sprt_x,  = ax.plot(SEPARATOR_AX["X"], NONE_AX, color = "blue")
line_sprt_y,  = ax.plot(NONE_AX, SEPARATOR_AX["Y"], color = "blue")
line_main,  = ax.plot(X_LINE, Y_LINE, color = "red")

variables.append(["$x",list(X_LINE)[0]])
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
#display.bind()

Frame_main.pack(fill = BOTH, expand = True)

Window_main.mainloop()