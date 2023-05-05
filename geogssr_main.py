import tkinter as tk
import tkintermapview
from geopy.geocoders import Nominatim
import csv
from random import randint
import json
import time 
import datetime
locator = Nominatim(user_agent='myGeocoder')





class Geogssr():

    def __init__(self):
        """
        Contains all the main variables initialisation and runs the startup functions in a specific order.
        
        parameters:
        None
        ------
        returns:
        None
        """

        #tk window creation
        self.root_tk = tk.Tk()
        self.root_tk.geometry(f"{1500}x{700}")
        self.root_tk.title("map_view_example.py")
        
        self.file = '/Users\jeand\OneDrive\Documentos\Programming\Python\Insa\countries.csv'
        self.flags_folder = "/Users\jeand\OneDrive\Documentos\Programming\Python\Insa\Flags/Flags_png/"
        self.neighbours_file = '/Users\jeand\OneDrive\Documentos\Programming\Python\Insa\country_neighbours.json'

        self.rules_text = 'description jeu'
        self.data_neighbours = {}
        self.data = {}
        self.flag_labels = []
        self.difficulty_dic = {'Easy : 60 seconds per country':60,'Medium : 30 seconds per country':30,'Hard : 10 seconds per country':10}
        self.max_flag_width = 200
        self.current_country = 'Germany'
        self.current_country_code = 'DE'

        self.country_is_displayed = False
        self.timer = True
        self.intro_done = False
        self.start_time = time.time()
        self.current_time = time.time()
        self.time_diff = datetime.timedelta(seconds = (self.current_time-self.start_time))

        self.bg_color = '#212227'
        self.fg_color = '#FFEF9F'

        self.difficulty = tk.StringVar()
        self.difficulty.set('Easy : 60 seconds per country')
        self.score = tk.IntVar()
        self.score.set(0)
        self.current_country_text = tk.StringVar()
        self.current_country_text.set(self.current_country.upper())

        self.number_plays = tk.IntVar()
        self.number_plays.set(0)
        
        self.number_plays_display = tk.StringVar()
        self.number_plays_display.set(str(self.number_plays.get()) +'/10' )
        self.create_widgets()
        
        #startup functions
        self.data =  self.load_data(self.file)
        self.data_neighbours = self.load_data_neighbours(self.neighbours_file)
        print(self.data_neighbours)
        self.country_display('de')
        time.sleep(1)
        
        #self.menu()

    def intro(self):
        """
        Complementary of the __init__ startup function, it only runs one, when the program is first launched.
        Its purpose is to create a TopLevel welcome screen that teaches the user how to handle the app. It is 
        separated from the __intro__ function so that the code is better organized and more readable.
        
        parameters:
        None
        ------
        returns:
        None
        """
        self.intro_window = tk.Toplevel(self.root_tk, bg=self.bg_color)
        self.intro_window.grab_set()

        self.intro_label = tk.Label(self.intro_window, text='Welcome to Geoguessr !', bg=self.bg_color, fg='white', font='Arial 20 bold')
        self.rules_textbox = tk.Text(self.intro_window, font = 'Arial 15', bg=self.bg_color, fg=self.fg_color)
        self.strat_game = tk.Button(self.intro_window, text='Start game', font='Arial 20 bold', bg=self.bg_color, fg=self.fg_color, command=self.intro_window.destroy)

        self.intro_label.pack()
        self.rules_textbox.pack()
        self.strat_game.pack()
        self.rules_textbox.insert(tk.END,self.rules_text)


    def create_widgets(self):  
        """
        Contains the code to create all of the tkinter widgets of the user interface. Two frames 
        are created inside our root tkinter window (frame_left and frame_right),then, placing the 
        elements according to their respective frames using the pack() geometry manager.
        
        parameters:
        None
        ------
        returns:
        None
        """


        #creating 2 frames to place items inside
        self.frame_left = tk.Frame(self.root_tk, width = 300, height = 700, background=self.bg_color)
        self.frame_left.grid(row = 0, column=0)
        self.frame_left.pack_propagate(False)
        
        self.frame_right = tk.Frame(self.root_tk, width=1200, height = 700)
        self.frame_right.grid(row=0,column=1)
        self.frame_right.pack_propagate(False)

        #create the map widget with tkintermapview and sets map
        self.map_widget = tkintermapview.TkinterMapView(self.frame_right, width=1200, height=700, corner_radius=10)
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png")

        #map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.add_left_click_map_command(self.add_marker_event)
        self.map_widget.pack(side=tk.LEFT)

        #create the score tracker at the top
        self.score_tracker_label = tk.Label(self.frame_right, textvariable = self.score, font='Arial 30 bold')
        self.score_tracker_label.place(bordermode=tk.OUTSIDE, x = (1200/2))

        #where's label
        self.label1 = tk.Label(self.frame_left, text="Where's", font = 'Arial 20 bold', bg =self.bg_color, fg='white',pady = 5 )
        self.label1.pack(fill='x')

        #country user is looking for
        self.current_country_display = tk.Label(self.frame_left, textvariable = self.current_country_text, font='Arial 15 bold', bg=self.bg_color, fg=self.fg_color,pady=20)
        self.current_country_display.pack(fill='x')

        #hint button
        self.hint_button = tk.Button(self.frame_left, text ='Hint', bg=self.bg_color,fg='white', font='Arial 20 bold', padx = '50', command=self.hint)
        self.hint_button.pack()

        #hint label
        #self.label2 = tk.Label(self.frame_left, text ="This country's neighbors are : ", bg='#24262f', fg='white', pady=25, font='Arial 20 bold')
        #self.label2.pack(fill='x')

        self.timer_label = tk.Label(self.frame_left, text=self.time_diff, font='Calibri 20 bold', bg = self.bg_color, fg=self.fg_color)
        self.timer_label.pack(fill='x')

        #hint textbox
        self.hint_textbox = tk.Text(self.frame_left, font = 'Arial 15 bold', bg=self.bg_color, fg=self.fg_color, height = 10)
        self.hint_textbox.pack()
        
        #number of plays label
        self.number_plays_label = tk.Label(self.frame_left, textvariable=self.number_plays_display, bg = self.bg_color, fg=self.fg_color, font = 'Arial 30 bold',pady=50)
        self.number_plays_label.pack()

        #select difficulty mode
        self.difficulty_change = tk.Button(self.frame_left, text = 'Change difficulty level', command=self.difficulty_toplevel, bg=self.bg_color, fg='white', font='Arial 15 bold')
        self.difficulty_change.pack()
        
        #quit button
        self.quit_button_mainframe = tk.Button(self.frame_left, text='Quit', font='Arial 15 bold', bg=self.bg_color,fg='white',command=self.root_tk.destroy)
        self.quit_button_mainframe.pack()
        

        self.intro()
        self.update_clock()
        
        #timer label


    def difficulty_toplevel(self):
        """
        Handles the creation of a TopLevel (and the widgets it contains) that opens when the user clicks
        on the « change difficulty level » button. This toplevel contains an OptionMenu widget that
        allows to choose between 3 difficulty setting (easy, medium, and hard). It also pauses the timer
        so that the game is « paused ».
        
        parameters:
        None
        ------
        returns:
        None
        """
        self.pause_time = self.current_time
        self.timer = False
        self.difficulty_window = tk.Toplevel(self.root_tk, bg=self.bg_color)
        self.difficulty_window.grab_set()
        self.label3 = tk.Label(self.difficulty_window, text='Choose your difficulty level :', font = 'Arial 20 bold', bg=self.bg_color, fg=self.fg_color)
        self.difficulty_options = tk.OptionMenu(self.difficulty_window, self.difficulty, 'Easy : 60 seconds per country','Medium : 30 seconds per country','Hard : 10 seconds per country')
        self.confirm_button = tk.Button(self.difficulty_window, text='Confirm', bg=self.bg_color, fg='white', font='Arial 15 bold', command=self.close_difficulty_menu)
        self.label3.pack()
        self.difficulty_options.pack()
        self.confirm_button.pack()
    
    def close_difficulty_menu(self):
        """
        Called when the user confirms the new difficulty choice. It destroys the
        difficulty_window object and handles the timer so that it keeps counting from 
        where it stopped before opening the difficulty window.

        parameters:
        None
        ------
        returns:
        None
        """
        self.current_time = time.time()
        self.time_diff = datetime.timedelta(seconds = int(self.current_time- self.pause_time))
        self.start_time = self.start_time + self.time_diff.seconds
        self.timer = True
        self.update_clock()
        self.difficulty_window.destroy()
        
        

    def update_clock(self):
        """
        Handles the timer for each guess of the game. Checks if the game is paused or not, and advances accordingly.
        In the case of the time running out, it resets itself and calls the functions necessary to start the guessing of a new flag.
        
        parameters:
        None
        ------
        returns:
        None
        """
        if self.intro_done:
            if self.timer:
                self.current_time = time.time()
                self.time_diff = datetime.timedelta(seconds=int(self.current_time-self.start_time))
                self.timer_label.config(text=self.time_diff)
            else:
                self.time_diff = datetime.timedelta(seconds=0)
        else: 
            try:
                self.intro_window.state()
            except:
                self.intro_done = True
                self.start_time = time.time()
        
        if self.time_diff.seconds >= self.difficulty_dic[self.difficulty.get()]:
                self.start_time = time.time()
                new_flag = self.random_flag()
                self.current_country_code = new_flag
                self.current_country = self.data[new_flag]
                self.current_country_text.set(self.current_country.upper())
                self.country_display(new_flag)
                self.hint_textbox.delete(1.0, tk.END)
                print('True', new_flag)
        self.timer_label.after(1000, self.update_clock)


    def add_marker_event(self, event):
        """
        handles a click on the map: checks if country is the right one, displays a new country if it is.
        
        parameters:
        event
        ------
        returns:
        None
        """
        location = locator.reverse((event[0], event[1]))
        print(location.raw['address'])
        country_code = location.raw['address']['country_code'].upper()
        country = self.data[country_code]
        print(country, self.current_country)
        if country == self.current_country:
            self.start_time = time.time() 
            self.score.set(self.score.get() + 1)
            new_flag = self.random_flag()
            self.current_country_code = new_flag
            self.current_country = self.data[new_flag]
            self.current_country_text.set(self.current_country.upper())
            self.country_display(new_flag)
            self.hint_textbox.delete(1.0, tk.END)
            print('True', new_flag)

        
        
    def load_data(self, file):
        """
        loads the csv file with country names/codes in a dictionnary.
        
        parameters: 
        file: a csv file
        ------
        returns:
        data(dictionnary): the data of the csv file
        """
            with open(file, newline = "") as csvfile:
                reader = csv.reader(csvfile, delimiter = ",")
                data = {}
                for country, country_code in reader:
                    if country_code not in data:
                        data[country_code] = country

            print(data)
            return data
        
    def load_data_neighbours(self,file):
        """
        loads the json file with neighbours of each country in a dictionnary.
        
        parameters: 
        file: a json file
        ------
        returns:
        jsondata(dictionnary): the data of the json file
        """
        jsondata= {}
        with open(file, 'r') as jsonfile:
            tmp = json.load(jsonfile)
            for i in tmp:
                str_list = ''
                for e in tmp[i]:
                    str_list += e[0] + ' '
                tmp[i] = str_list
                jsondata[i] = tmp[i]
        return jsondata



  
    def label_size(self, flag):
        """
        defines the size of the label depending on size of the displayed flag and a max threshold.
        
        parameters:
        flag(?)
        ------
        returns:
        max_flag_width(int) or width(int): width used to display the flag
        """
        max_flag_width = self.max_flag_width
        width = flag.width()
        if width > max_flag_width:
            return max_flag_width
        return width


    
    def random_flag(self):
        """
        picks a random country/flag.
        
        parameters:
        None
        ------
        returns:
        countries[number](string): a random country code
        """
        number = randint(0,len(self.data))
        countries = list(self.data.keys())
        self.number_plays.set(self.number_plays.get() + 1)
        self.number_plays_display.set(str(self.number_plays.get()) +'/10' )
        if self.number_plays.get() >= 10:
            self.end_of_game()
        return countries[number]


    def country_display(self, country_code):
        """
        updates displays to match the new flag
        
        parameters:
        country_code(string): a 2 letter country code
        ------
        returns:
        None
        """
        country_code = country_code.lower()
        flag_path = self.flags_folder + country_code + ".png"
        self.img = tk.PhotoImage(file=flag_path)
        self.img = self.img.subsample(2,2)
        self.img_label = tk.Label(self.frame_right, image=self.img,height=100,bg='lightblue', border = None,width = self.label_size(self.img)-5)
        
        for i in self.flag_labels:
            i.destroy()
            self.flag_labels.pop()
        self.flag_labels.append(self.img_label)
        self.img_label.photo = self.img
        self.img_label.place(relx=0, rely=1.0, anchor='sw')

    def hint(self):
        """
        looks for and displays a hint for the player, which is the neighbouring coutries to the one they are looking for.
        
        parameters:
        None
        ------
        returns:
        None
        """
        self.hint_text = self.data_neighbours[self.current_country_code.lower()]
        if self.hint_text:
            self.hint_text = f"{self.current_country}'s neighbors are : \n{self.hint_text}\n"
            self.hint_textbox.insert(tk.END, self.hint_text)
        else:
            self.hint_text = "Looks like this country's an island..."
            self.hint_textbox.insert(tk.END, self.hint_text)

    def end_of_game(self):
        """
        ends the game, shows the player they score and allows them to chooose between restarting a new game or quitting the app.
        
        parameters:
        None
        ------
        returns:
        None
        """
        self.timer = False
        self.endgame_window = tk.Toplevel(self.root_tk, bg = self.bg_color)
        self.endgame_window.grab_set()
        endscore = str(self.score.get()) + '/10'
        self.label4 = tk.Label(self.endgame_window, text='Your final score is :', font='Arial 30 bold', bg=self.bg_color, fg='white')
        self.end_score = tk.Label(self.endgame_window, text=endscore, fg=self.fg_color, bg=self.bg_color, font='Arial 40 bold',pady=100)
        self.label4.pack()
        self.end_score.pack()
        self.restart_game_button = tk.Button(self.endgame_window, text = 'Start new game', bg=self.bg_color, fg='white', font='Arial 15 bold',command = self.restart_game)
        self.restart_game_button.pack()
        self.quit_button = tk.Button(self.endgame_window, text='Quit', font='Arial 15 bold', bg=self.bg_color,fg='white',command=self.root_tk.destroy)
        self.quit_button.pack()

        
    
    def restart_game(self):
        """
        relaunches a new game.
        
        parameters:
        None
        ------
        returns:
        None
        """
        self.timer = True
        self.start_time = time.time()
        self.endgame_window.destroy()
        self.score.set(0)
        self.number_plays.set(0)
        self.difficulty.set('Easy : 60 seconds per country')


    # create map widget
    






if __name__ == '__main__':
    Geogssr_window = Geogssr()
    #Geogssr_window.root_tk.wm_attributes('-transparentcolor', 'red')
    Geogssr_window.root_tk.mainloop()



"""print(location.raw['address']['country'], location.raw['address']['country_code'])
    engine.say(country)
    engine.runAndWait()"""
