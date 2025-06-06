import pygame as py
import sys
from pianoroll import *
from pypianoroll import *
from jarvis import *
from instrument_panel import *
import time
from add_instruments_panel import *
from model_panel import *
from change_model_panel import *
from file_panel import *
from Transformer import *



class Display:

    def __init__(self, mes, file="", inp_length=256):
        self.help = False
        py.display.init()

        self.width = 1000
        self.height = 800
        self.win = py.display.set_mode((self.width, self.height))
        self.measure_limit = mes
        self.measure_length = 91
        self.pianoroll = Pianoroll(self.measure_limit)
        self.roll_index = 0
        self.j = 10

        self.model_name = "models/inference.h5"
        self.controls = {"right_click": False, "play": False, "move_piano_roll_left": False, "update_ipanel": True,
                         "move_piano_roll_right": False, "playing": False, "show_map": False, "microplay": False}
        self.events = {"update_pianoroll": True}
        self.event_handled = True
        self.rem_tok_for_generation = str(10000)
        self.quit = False
        self.window = None
        self.instrument_panel = InstrumentPanel()
        self.model_panel = ModelPanelListener()
        self.file_panel = FilePanelListener()
        self.jarv = None
        self.loaded_model = None
        self.openfile = False
        self.input_length = inp_length

        self.helper = Helper(self.pianoroll.notes, self.model_name, self.input_length, 512)

        if file == "":
            self.openfile = False
            self.file = ""

        else:
            self.openfile = True
            self.file = file
            try:
                parsed_track = self.parse_first_track(file)
                print("ParsedTrack", parsed_track)
                self.pianoroll.load_file(parsed_track, self.measure_limit * self.measure_length)
            except Exception:
                print("No file in that name")
                pass

        print(self.file)
        py.mixer.init()
        self.image_loc = "../images/"
        self.button_play = py.image.load(self.image_loc + "play.png")
        self.button_pause = py.image.load(self.image_loc + "pause.png")
        self.button_file = py.image.load(self.image_loc + "file.png")
        self.button_save = py.image.load(self.image_loc + "save.png")
        self.button_shiftup = py.image.load(self.image_loc + "shiftup.png")
        self.button_shiftdown = py.image.load(self.image_loc + "shiftdown.png")
        self.button_selection = py.image.load(self.image_loc + "selection_false.png")
        self.button_paste = py.image.load(self.image_loc + "paste.png")
        self.button_note = py.image.load(self.image_loc + str(
            2 ** self.pianoroll.controls["nthnote"]) + "_on.png")
        self.button_addm = py.image.load(self.image_loc + "add_m.png")
        self.button_subm = py.image.load(self.image_loc + "sub_m.png")
        self.symbol_measure = py.image.load(self.image_loc + "measure.png")
        self.sx = -1
        self.sy = -1
        self.tx = -1
        self.ty = -1

    def file_opener(self, filename):
        document = "documents/" + filename
        print(document)
        if document[-3:] == "mid":
            parsed_track = self.parse_first_track(document)
            self.pianoroll.load_file(parsed_track, self.measure_limit * self.measure_length)

        elif document[-3:] == "npz":
            self.loader(document, npz=True)
            self.events["update_pianoroll"] = True

        elif document[-3:] == "npy":
            self.loader(document)
            self.events["update_pianoroll"] = True

    def save_file(self):
        np.save("documents/" + str(int(time.time())), self.pianoroll.notes)
        print("Saved successfully")

    def draw(self):
        # For minimizing the frequency of the pianoroll surface updates

        if self.events["update_pianoroll"] or self.pianoroll.controls["bar_move_velocity"] != 0:
            self.win.fill((30, 30, 40))
            self.pianoroll.update()
            self.events["update_pianoroll"] = False
            self.win.blit(self.pianoroll.pianoroll, (180, 100))
            self.draw_controls()
            self.win.blit(self.instrument_panel.surface_panel, (10, 100))
            if self.window != None:
                self.window.draw()
                self.window.rect.topleft = (100, 100)
                self.win.blit(self.window.surface_panel, self.window.rect)
            py.display.update()

        if self.controls["update_ipanel"]:
            self.controls["update_ipanel"] = False
            self.instrument_panel.update()
            self.events["update_pianoroll"] = True
            self.win.blit(self.instrument_panel.surface_panel, (10, 100))

        if self.instrument_panel.state["delete"]:
            self.instrument_panel.update()
            self.events["update_pianoroll"] = True
            self.win.blit(self.instrument_panel.surface_panel, (10, 100))

        if self.controls["play"]:
            self.events["update_pianoroll"] = True
            time_start = self.pianoroll.controls["time_start"]
            ratio = self.pianoroll.controls["tempo"] / 60
            time_measures = ((time.time() - time_start) * ratio) / (4)
            # print("time_measures", time_measures)
            if time_measures > self.pianoroll.controls["measure_passed"]:
                self.pianoroll.controls["measure_passed"] = time_measures
                self.pianoroll.controls["timebar"] = -self.pianoroll.controls["measure_passed"] * 640 * \
                                                     self.pianoroll.controls["h_zoom"]

    def draw_controls(self):
        self.button_note = py.image.load(self.image_loc + str(
            2 ** self.pianoroll.controls["nthnote"]) + "_on.png")

        if self.controls["play"] == False:
            self.win.blit(self.button_play, (500, 30))
        else:
            self.win.blit(self.button_pause, (500, 30))

        self.win.blit(self.button_note, (450, 30))
        self.win.blit(self.symbol_measure, (550, 30))
        self.win.blit(self.button_addm, (580, 30))
        self.win.blit(self.button_subm, (580, 46))
        self.win.blit(self.button_file, (30, 30))
        self.win.blit(self.button_save, (70, 30))
        self.win.blit(self.model_panel.image, (620, 45))
        self.win.blit(self.button_shiftup, (425, 32))
        self.win.blit(self.button_shiftdown, (425, 48))
        # if self.pianoroll.note_selection:
        #     self.button_selection = py.image.load(self.image_loc + "selection_true.png")
        self.win.blit(self.button_selection, (375, 30))
        self.win.blit(self.button_paste, (325, 30))
        font = Font(14)
        # print()

        surf, rec = font.text_object(self.rem_tok_for_generation)
        self.win.blit(surf, (670, 30))
        # self.image.blit(surf, (5, 5))

        if self.controls["move_piano_roll_left"] or self.controls["move_piano_roll_right"]:
            self.pianoroll.controls["make_velocity_0"] = False
            if self.controls["move_piano_roll_left"]:
                if self.pianoroll.controls["fast_move_piano_roll"]:
                    if self.pianoroll.controls["bar_move_velocity"] > -30.0:
                        self.pianoroll.controls["bar_move_velocity"] -= 1.0
                else:
                    if self.pianoroll.controls["bar_move_velocity"] > -10.0:
                        self.pianoroll.controls["bar_move_velocity"] -= 0.2
                    else:
                        self.pianoroll.controls["bar_move_velocity"] += 1.0

            if self.controls["move_piano_roll_right"]:
                if self.pianoroll.controls["fast_move_piano_roll"]:
                    if self.pianoroll.controls["bar_move_velocity"] < 30.0:
                        self.pianoroll.controls["bar_move_velocity"] += 1.0
                else:
                    if self.pianoroll.controls["bar_move_velocity"] < 10.0:
                        self.pianoroll.controls["bar_move_velocity"] += 0.2
                    else:
                        self.pianoroll.controls["bar_move_velocity"] -= 1.0
            # print("B",self.pianoroll.controls["bar_move_velocity"])
        else:
            self.pianoroll.controls["make_velocity_0"] = True

    def event_handler(self):

        for event in py.event.get():
            if event.type == py.QUIT:
                self.quit = True

            if event.type == py.MOUSEMOTION:
                if self.controls["right_click"]:
                    x, y = py.mouse.get_pos()
                    if x >= 200 and x <= 980 and y >= 110 and y <= 590:
                        s = int((x - 200))
                        k = int((y - 110))
                        s = int((s - self.pianoroll.controls["timebar"]) / (20 * self.pianoroll.controls["h_zoom"]))
                        k = int(k / 10)
                        self.pianoroll.deletenote(s, k)
                        self.events["update_pianoroll"] = True

            if event.type == py.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.controls["right_click"] = True

                if self.pianoroll.note_selection:
                    self.pianoroll.paste_selected = False
                    x, y = py.mouse.get_pos()
                    s = int((x - 200))
                    k = int((y - 110))
                    s = int((s - self.pianoroll.controls["timebar"]) / (20 * self.pianoroll.controls["h_zoom"]))
                    k = int(k / 10)
                    self.sy = s
                    self.sx = k

            if event.type == py.MOUSEBUTTONUP:
                self.event_handled = True
                self.events["update_pianoroll"] = True
                x, y = py.mouse.get_pos()
                print(x, y)

                if 325 < x < 325 + 32 and 30 < y < 30 + 32:
                    self.pianoroll.paste_selected = not self.pianoroll.paste_selected

                    if self.pianoroll.paste_selected:
                        self.button_paste = py.image.load(self.image_loc + "paste_selected.png")
                        self.pianoroll.note_selection = False

                    else:
                        self.button_paste = py.image.load(self.image_loc + "paste.png")

                if 375 < x < 375 + 32 and 30 < y < 30 + 32:
                    self.pianoroll.note_selection = not self.pianoroll.note_selection
                    if self.pianoroll.note_selection:
                        self.button_selection = py.image.load(self.image_loc + "selection_true.png")
                        self.pianoroll.paste_selected = False

                    else:
                        self.button_selection = py.image.load(self.image_loc + "selection_false.png")

                if 425 < x < 425 + 16 and 32 < y < 32 + 16:
                    self.pianoroll.shiftup()

                if 425 < x < 425 + 16 and 48 < y < 48 + 16:
                    self.pianoroll.shiftdown()

                if 34 < x < 34 + 16 and 36 < y < 36 + 16:
                    self.file_panel.handle_events((x, y))

                if 75 < x < 75 + 16 and 36 < y < 36 + 16:
                    print("Saving file")
                    self.save_file()

                if self.window is not None:
                    if (100 < x < (100 + self.window.width)) and (100 < y < (100 + self.window.height)):
                        self.window.handle_events((x - 100, y - 100))

                if 620 < x < (620 + 150) and 30 < y < 60:
                    self.model_panel.handle_events((x, y))

                if 10 < x < 175 and 100 < y < 600:
                    self.instrument_panel.handle_events((x - 10, y - 100))

                if 500 < x < 532 and 30 < y < 62:
                    self.controls["play"] = not self.controls["play"]

                # On clicking the pianoroll for entering notes
                if 200 <= x <= 980 and 110 <= y <= 590 and self.controls["right_click"] == False:
                    if self.pianoroll.note_selection:
                        x, y = py.mouse.get_pos()
                        s = int((x - 200))
                        k = int((y - 110))
                        s = int((s - self.pianoroll.controls["timebar"]) / (20 * self.pianoroll.controls["h_zoom"]))
                        k = k // 10
                        self.ty = s
                        self.tx = k
                        self.pianoroll.copy_selection(self.sx, self.sy, self.tx, self.ty)
                    elif self.pianoroll.paste_selected:

                        x, y = py.mouse.get_pos()
                        s = int((x - 200))
                        k = int((y - 110))
                        s = int((s - self.pianoroll.controls["timebar"]) / (20 * self.pianoroll.controls["h_zoom"]))
                        k = k // 10
                        self.pianoroll.paste_notes(kpos=(s, k))
                    else:
                        x, y = py.mouse.get_pos()
                        s = int((x - 200))
                        k = int((y - 110))
                        s = int((s - self.pianoroll.controls["timebar"]) / (20 * self.pianoroll.controls["h_zoom"]))
                        k = int(k / 10)
                        self.pianoroll.enternote(s, k)
                        self.play(1)
                        self.token_generator()

                        if self.help:
                            if not self.helper.is_alive():
                                self.helper.model_name = self.model_name
                                self.helper.start()
                                print(self.helper.is_alive())
                            else:
                                self.helper.changed = True

                if x >= 580 and x <= 596 and y >= 30 and y <= 62:
                    if y >= 30 and y <= 46:
                        self.pianoroll.measures += 1
                        self.pianoroll.send_event("measure_increased")

                    elif y >= 46 and y <= 62:
                        if self.pianoroll.measures > 1:
                            self.pianoroll.measures -= 1
                            self.pianoroll.send_event("measure_decreased")
                        # print("measure_decreased")
                if event.button == 3:
                    self.controls["right_click"] = False
                    # print(self.pianoroll.notes)

            if event.type == py.KEYDOWN:

                self.event_handled = True
                if event.key == py.K_1:
                    self.pianoroll.controls["nthnote"] = 0
                if event.key == py.K_2:
                    self.pianoroll.controls["nthnote"] = 1
                if event.key == py.K_3:
                    self.pianoroll.controls["nthnote"] = 2
                if event.key == py.K_4:
                    self.pianoroll.controls["nthnote"] = 3
                if event.key == py.K_5:
                    self.pianoroll.controls["nthnote"] = 4
                if event.key == py.K_6:
                    self.pianoroll.controls["nthnote"] = 5
                if event.key == py.K_p:
                    self.pianoroll.play_notes()

                if event.key == py.K_j:
                    print(self.pianoroll.selected_track)
                    print(self.pianoroll.notes_index)
                    print(self.pianoroll.notes[self.pianoroll.selected_track])
                    print(self.instrument_panel.instruments_used)

                if event.key == py.K_o:
                    self.load_from_npy("generated.npy")
                    self.events["update_pianoroll"] = True

                if event.key == py.K_c:
                    self.pianoroll.clear_current_track()
                    self.events["update_pianoroll"] = True

                if event.key == py.K_g:
                    np.save("temp.npy", self.pianoroll.notes[self.pianoroll.selected_track])
                    print("Saved Temp")
                    self.model_name, self.input_length = self.model_panel.get_model_detail()
                    # jarv = Melody("models/" + self.model_name + ".h5")
                    # jarv.input_length = self.input_length
                    # jarv.use_model()
                    # jarv.generate_tune()
                    print(self.model_name, self.loaded_model)
                    if self.jarv is None:
                        self.jarv = DifferenceMelody("models/" + self.model_name + ".h5",
                                                     input_length=self.input_length)
                    if self.loaded_model != self.model_name:

                        if self.model_name != "inference" and self.model_name != "transformer" and self.model_name != "transformer2":
                            if self.loaded_model == "transformer":
                                self.jarv = DifferenceMelody("models/" + self.model_name + ".h5",
                                                             input_length=self.input_length)
                            # self.jarv = DifferenceMelody("models/" + self.model_name + ".h5",input_length=self.input_length)
                            print("some other")
                            self.jarv.model_name = "models/" + self.model_name + ".h5"
                            print("Model name", self.jarv.model_name)
                            self.jarv.input_length = self.input_length
                            # self.jarv.generate_tune()
                            self.loaded_model = self.model_name
                            self.jarv.new_generator()


                        elif self.model_name == "transformer":

                            print("In transformer")
                            self.jarv = MusicTransformer()
                            self.jarv.input_length = self.input_length
                            self.jarv.pe_input = 40
                            self.jarv.pe_target = 128
                            self.jarv.build_transformer()
                            self.loaded_model = "transformer"
                            self.jarv.new_generator()

                        elif self.model_name == "transformer2":
                            print("In transformer")
                            self.jarv = MusicTransformer()
                            self.jarv.model_name = "transformer2"
                            self.jarv.checkpoint_path = "models/transformer2/"
                            self.jarv.input_length = self.input_length
                            self.jarv.pe_input = 60
                            self.jarv.pe_target = 196
                            self.jarv.build_transformer()
                            self.loaded_model = "transformer2"
                            self.jarv.t2_generator()

                        else:
                            print("inference")
                            self.jarv = DifferenceMelody("models/" + self.model_name + ".h5",
                                                         input_length=self.input_length)

                            self.jarv.model_name = "models/" + self.model_name + ".h5"
                            self.jarv.input_length = self.input_length
                            self.loaded_model = self.model_name
                            self.jarv.inf_generator()


                    else:
                        print(self.jarv.model_name)
                        if self.jarv.model_name == "transformer":
                            self.loaded_model = "transformer"
                            self.jarv.new_generator()

                        elif self.jarv.model_name == "transformer2":
                            self.loaded_model = "transformer2"
                            self.jarv.t2_generator()

                        elif self.jarv.model_name == "models/inference.h5":
                            self.loaded_model = self.model_name
                            self.jarv.inf_generator()

                        else:
                            self.loaded_model = self.model_name
                            self.jarv.new_generator()


                if event.key == py.K_f:
                    np.save("temp.npy", self.pianoroll.notes[self.pianoroll.selected_track])
                    # print("Saved Temp")
                    jarv = Melody(self.model_name)
                    print(jarv.model.summary())
                    jarv.input_length = self.input_length
                    jarv.use_model()

                if event.key == py.K_e:
                    """Uses only the notes that is present in the 
                    pianoroll.notes_index"""
                    if self.loaded_model is None:
                        self.loaded_model = Melody(self.model_name)

                    use_notes = list()

                    for note_index in self.pianoroll.notes_index[self.pianoroll.selected_track]:
                        s, t = note_index
                        # print(note_index, note_index[0] * 6 + self.pianoroll.notes[self.pianoroll.selected_track][s][t])
                        use_notes.append(note_index[0] * 6 + self.pianoroll.notes[self.pianoroll.selected_track][s][t])
                    self.loaded_model.input_length = self.input_length
                    self.loaded_model.input_data_to_model(self.pianoroll.notes[self.pianoroll.selected_track])
                    self.loaded_model.random_noise()

                # if event.key == py.K_m:
                #     self.controls["show_map"] = not self.controls["show_map"]

                # if event.key == py.K_t:
                #     parsed_track = self.parse_first_track(self.file)
                #     print("ParsedTrack", parsed_track)
                #     self.pianoroll.load_file(parsed_track, self.measure_limit * self.measure_length)


                if event.key == py.K_q:
                    np.save('train_data.npy', self.pianoroll.notes)

                if event.key == py.K_UP:
                    if self.pianoroll.controls["h_zoom"] >= 1 and not self.controls["playing"]:
                        self.pianoroll.controls["h_zoom"] += 1
                        self.events["update_pianoroll"] = True
                        print(self.pianoroll.controls["h_zoom"])

                    else:
                        if not self.controls["playing"]:
                            self.pianoroll.controls["h_zoom"] *= 2
                            self.events["update_pianoroll"] = True
                    # print(self.pianoroll.controls["h_zoom"])

                if event.key == py.K_DOWN:

                    if self.pianoroll.controls["h_zoom"] > 1 and not self.controls["playing"]:
                        self.pianoroll.controls["h_zoom"] -= 1
                        self.events["update_pianoroll"] = True

                    elif self.pianoroll.controls["h_zoom"] > 0.50 and not self.controls["playing"]:
                        self.pianoroll.controls["h_zoom"] /= 2
                        self.events["update_pianoroll"] = True
                    # print(self.pianoroll.controls["h_zoom"])

                if event.key == py.K_LEFT:
                    self.events["update_pianoroll"] = True
                    self.controls["move_piano_roll_left"] = True

                if event.key == py.K_RIGHT:
                    self.events["update_pianoroll"] = True
                    self.controls["move_piano_roll_right"] = True

                if event.key == py.K_RSHIFT:
                    # print("shift pressed")
                    self.pianoroll.controls["fast_move_piano_roll"] = True

                if event.key == py.K_SPACE:
                    self.controls["play"] = not self.controls["play"]
                    self.pianoroll.controls["time_start"] = time.time()
                    self.pianoroll.controls["measure_passed"] = 0

            if event.type == py.KEYUP:
                self.events["update_pianoroll"] = True
                if event.key == py.K_LEFT:
                    self.controls["move_piano_roll_left"] = False

                if event.key == py.K_RIGHT:
                    self.controls["move_piano_roll_right"] = False

                if event.key == py.K_RSHIFT:
                    self.pianoroll.controls["fast_move_piano_roll"] = False

            if event.type == py.USEREVENT:
                self.controls["play"] = False
                self.controls["playing"] = False
                self.controls["microplay"] = False
                # print("Stopping Music")
                py.mixer.music.stop()

    def loader(self, file, npz=False):
        array = np.load(file)
        if npz:
            array = array["arr_0"]
        else:
            if len(array) > 0:
                print("array shape", array.shape)
                array = array[0]
        print("array shape", array.shape)
        self.pianoroll.notes[self.pianoroll.selected_track] = array
        self.pianoroll.notes_index[self.pianoroll.selected_track] = []
        ind = 0
        for _notes in self.pianoroll.notes:
            note_index = []
            # print("Before Error", _notes, _notes.shape)
            for i in range(_notes.shape[1]):
                row = _notes[:, i]
                for v in range(len(row)):
                    if row[v] != -1:
                        note_index.append([v, i])
            # print(len(note_index))
            self.pianoroll.notes_index[ind] = note_index
            ind += 1
        if array.shape[0] < self.measure_limit:
            diff = self.measure_limit - array.shape[1]
            while diff > 0:
                np.append(self.pianoroll.notes[self.pianoroll.selected_track], np.ones((48)) * -1)
                diff -= 1

    def load_from_npy(self, file):
        array = np.load(file)

        try:
            array = array["arr_0"]
        except Exception:
            pass
        # print("Array Shape", array.shape)
        self.pianoroll.notes[self.pianoroll.selected_track] = array
        self.pianoroll.notes_index[self.pianoroll.selected_track] = []
        ind = 0
        for _notes in range(len(self.pianoroll.notes)):
            note_index = []
            # print("Before Error", _notes, _notes.shape)
            self.pianoroll.indexit(_notes)

        print("Measure Len", self.measure_limit, array.shape)
        if array.shape[1] < self.measure_limit:
            print("executed measure insuff")
            diff = self.measure_limit * self.measure_length - array.shape[1]
            meas_size_array = np.ones((48, self.measure_length * self.measure_limit)) * -1
            meas_size_array[:, :array.shape[1]] = array
            self.pianoroll.notes[self.pianoroll.selected_track] = meas_size_array
            # while diff > 0:
            #     self.pianoroll.notes[self.pianoroll.selected_track] = np.append(
            #         self.pianoroll.notes[self.pianoroll.selected_track], np.ones((48, 1)) * -1,axis=1)
            #     diff -= 1

        # print("Note_indexs", self.pianoroll.notes_index[self.pianoroll.selected_track])
        # print("notes_index", self.pianoroll.notes_index)
        # print("Successfully Loaded")

    def play(self, option=0):
        if option == 0 and not self.controls["microplay"]:
            if self.controls["play"] == True and self.controls["playing"] == False:
                self.pianoroll.play_notes(self.controls["show_map"])
                py.mixer.music.load("create1.mid")
                py.mixer.music.set_endevent(py.USEREVENT)
                self.controls["playing"] = True
                py.mixer.music.play()
                # print("index", self.pianoroll.notes_index)

            elif self.controls["play"] == False:
                self.controls["playing"] = False
                py.mixer.music.stop()
        else:

            if self.controls["play"] == False and self.controls["playing"] == False and not self.controls["microplay"]:
                py.mixer.music.load("play_note.mid")
                py.mixer.music.set_endevent(py.USEREVENT)
                py.mixer.music.play()
                self.controls["microplay"] = True

    def find_closer(self, x):
        """
        Returns the closest resemblance of the note type
        such as whole(96),half(48),half+quarter.
        Currently ex_dura feature is turned off, because of
        reducing complexity
        :param x:
        :return:
        """
        # ex_dura = [96,72,48,36,24,18,12,9,6,4,3]
        dura = [self.measure_length, self.measure_length / 2, self.measure_length / 4, self.measure_length / 8,
                self.measure_length / 16, self.measure_length / 32]
        dura.reverse()
        dura = np.array(dura)
        my_dura = [0.125, 0.25, 0.5, 1, 2, 4]
        my_dura = np.array(my_dura)
        duration = my_dura[np.argmin(np.abs(x - dura))] * 8
        # print(duration)
        return duration

    def get_notes(self, key_row):
        """
        Returns a list of list of starting position
        and duration of a particular note in the entire track
        :param key_row:
        :return:
        """
        nonzeros = np.nonzero(key_row)[0]
        # print("Nonzeros1",nonzeros)
        notes = []
        if len(nonzeros) > 0:
            start = int(nonzeros[0])
            prestart = start
            length = 0
            # tuple stores length start,length
            for i in range(1, len(nonzeros)):
                if start + 1 == nonzeros[i] and i < len(nonzeros) - 1:
                    length += 1
                    start += 1
                else:
                    notes.append([prestart, self.find_closer(length)])
                    length = 0
                    prestart = int(nonzeros[i])
                    start = prestart
                pass
            # print("Notes", notes)
            return notes
        else:
            return []
        # print(nonzeros.shape)

    def parse_first_track(self, file):
        """
        Parses the midi file and converts it into the format
        required for my pianoroll function.
        :param file:
        :return:
        """
        track = Multitrack(file).tracks[0]
        print("Track", track.pianoroll)
        shortened_track = []
        for i in range(128):
            range_array = self.get_notes(track.pianoroll[:self.measure_limit * self.measure_length, i])
            # print(range_array)
            if len(range_array) > 0:
                shortened_track.append([i, range_array])
        shortened_track = np.array(shortened_track)
        # print("shape", shortened_track.shape)
        modified_track = []
        for each_note_row in shortened_track:
            n = each_note_row[0]
            ranges = np.array(each_note_row[1])
            # print(ranges.shape)
            ranges[:, 0] = ranges[:, 0] / 3
            modified_track.append([n, ranges])
        return modified_track

    def request_handler(self):
        """Checks the requests in other classes request queues"""
        # print(self.instrument_panel.requests, self.window)

        if len(self.instrument_panel.requests) > 0:
            if self.window is None:
                req = self.instrument_panel.requests.pop(0)
                print(req)
                if req == "instruments":
                    if self.window is None:
                        self.window = AddInstrumentPanel()
                    # print("Window:", self.window)

                elif type(req) == type({}):
                    if "clicked" in req.keys():
                        instrument_selected = req["clicked"]
                        # print("PProgramno", instrument_selected)
                        # self.pianoroll.add_track(instrument_selected)
                        self.pianoroll.selected_track = instrument_selected
                        self.events["update_pianoroll"] = True
                    if "delete" in req.keys():
                        delete_instrument_index = req["delete"]

                        if self.pianoroll.n_tracks > 1:
                            self.pianoroll.selected_track = 0
                            if delete_instrument_index > self.pianoroll.selected_track:
                                self.pianoroll.n_tracks -= 1
                                # print(type(self.pianoroll.notes),delete_instrument_index)

                                self.pianoroll.notes.pop(delete_instrument_index)
                                self.pianoroll.notes_index.pop(delete_instrument_index)
                                self.pianoroll.programs.pop(delete_instrument_index)
                                self.instrument_panel.instruments_used.pop(delete_instrument_index)
                                self.instrument_panel.instruments_sprites.pop(delete_instrument_index)

                                start = 0
                                for sprite in self.instrument_panel.instruments_sprites:
                                    sprite.index = start
                                    start += 1
                                self.instrument_panel.update()
                            else:
                                self.pianoroll.selected_track -= 1
                                self.pianoroll.n_tracks -= 1
                                # print(type(self.pianoroll.notes),delete_instrument_index)

                                self.pianoroll.notes.pop(delete_instrument_index)
                                self.pianoroll.notes_index.pop(delete_instrument_index)
                                self.pianoroll.programs.pop(delete_instrument_index)
                                self.instrument_panel.instruments_used.pop(delete_instrument_index)
                                self.instrument_panel.instruments_sprites.pop(delete_instrument_index)

                                start = 0
                                for sprite in self.instrument_panel.instruments_sprites:
                                    sprite.index = start
                                    start += 1
                                self.instrument_panel.update()

        if len(self.model_panel.requests) > 0:
            # print("@Request")
            # print(self.window)
            if self.window is None:
                req = self.model_panel.requests.pop(0)

                if req == "open":
                    self.window = ChangeModelPanel(self.model_panel.get_models_list())

        if len(self.file_panel.requests) > 0:
            if self.window is None:
                req = self.file_panel.requests.pop(0)
                if req == "open":
                    self.window = FilePanelWindow()
            pass

        if self.window != None:
            if len(self.window.requests) > 0:
                req = self.window.requests.pop(0)
                if req == "close":
                    # Get the value returned from the window
                    if isinstance(self.window, AddInstrumentPanel):
                        self.instrument_panel.add_instrument(self.window.result)
                        self.pianoroll.add_track(self.window.result)
                        self.controls["update_ipanel"] = True
                        self.window = None
                    elif isinstance(self.window, ChangeModelPanel):
                        self.model_panel.selected_model_index = self.window.result[0]
                        self.model_panel.update()
                        self.window = None
                        self.controls["update_ipanel"] = True
                    elif isinstance(self.window, FilePanelWindow):

                        if self.window.result[0] > -1:
                            list_of_files = os.listdir("documents/")
                            open_file = list_of_files[self.window.result[0]]
                            print("Opening File")
                            self.file_opener(open_file)
                        else:
                            print("No files")
                        self.window = None

        if self.helper.finished:
            self.helper.finished = False
            self.pianoroll.apply_generated(self.helper.generated)

    def encode_track(self, nparray):
        """Receives a array of shape (48,)"""

        def get_top_index(quant_notes):
            for i in range(len(quantum_notes)):
                if quantum_notes[i] >= 0:
                    return i
            return -1

        starting = True
        startnote = None
        encoded = [0]
        rest = 0
        for quantum in range(nparray.shape[1]):
            quantum_notes = nparray[:, quantum]
            if len(np.nonzero(quantum_notes + 1)[0]) > 0:
                if starting:
                    i = get_top_index(quantum_notes)
                    if i > -1:
                        starting = False
                        print(starting, (not starting))
                        startnote = i
                        time_quantum = quantum_notes[i]
                        curnote = 24
                        encoded.extend([curnote + 7,
                                        time_quantum + 1])

                elif not starting:
                    i = get_top_index(quantum_notes)
                    if i > -1:
                        if rest > 0:
                            if rest > 32:
                                rest = 32
                            encoded.append(54 + rest)
                            rest = 0
                        time_quantum = quantum_notes[i]
                        curnote = 24 + startnote - i
                        if 0 <= curnote <= 47:
                            encoded.extend([curnote + 7,
                                            time_quantum + 1])
            elif not starting:
                rest += 1

        return encoded

    def token_generator(self):
        nparray = self.pianoroll.notes[self.pianoroll.selected_track]

        encoded = self.encode_track(nparray)
        _, self.input_length = self.model_panel.models_available[self.model_panel.selected_model_index]
        self.rem_tok_for_generation = str(self.input_length - len(encoded))


    def run(self):
        while not self.quit:
            self.draw()
            self.event_handler()
            self.play()

            self.request_handler()

        # print(self.pianoroll.notes)


def open_mid_randomly():
    mids = os.listdir("data/")
    mid = mids[np.random.randint(len(mids))]
    return mid


if __name__ == '__main__':

    # file = "data/"+open_mid_randomly()
    file = "data/" + "My_Melancholy_Blues.mid"
    if len(sys.argv) == 2:
        file = sys.argv[1]
    d = Display(mes=80, inp_length=1024, file=file)
    d.model_name = "models/master.h5"
    d.run()
