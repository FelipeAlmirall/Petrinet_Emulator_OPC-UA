import xml.etree.ElementTree as ET
import re
import random
import asyncio


class Place():
    
    
    def __init__(self, parser_place, verify_input = False):
        
        self._id       = parser_place.attrib['id'].upper()
        self._capacity = int(parser_place.findall('.//capacity')[0].findall('.//value')[0].text)
        self._type     = 'place'
        init_marking  = parser_place.findall('.//initialMarking')[0].findall('.//value')[0].text
        init_marking  = init_marking.split(',')
        dictionary    = {}
        for i in range(len(init_marking)//2):
            dictionary.update({init_marking[2*i]:int(init_marking[(2*i)+1])})
        self.marking  = dictionary
        self._actions = self.process_name_actions()
        if verify_input:
            self.check_name()
        return
    
    def process_name_actions(self):
        
        if "(" in self._id and ")" in self._id:
            ios = self._id[self._id.find("(")+1:self._id.find(")")]
        else:
            return {}
        chars_to_be_ignoreds = [' ', '-']
        pattern = '[' + ''.join(chars_to_be_ignoreds) + ']'
        name = re.sub(pattern, '', ios)
        names = name.split(",")
        dict_names = {}
        for n in names:
            listed = n.split("~")
            if len(listed) > 1:
                dict_names[listed[1]] = False
            else:
                dict_names[listed[0]] = True
        return dict_names
    
    def check_name(self):
        
        if "(" not in self._id or ")" not in self._id:
            raise ValueError('%s is not a valid Place Name.\nCheck if IOs are inside ().' %self._id)
        ios = self._id[self._id.find("(")+1:self._id.find(")")]
        chars_to_be_ignoreds = [' ', '-']
        pattern = '[' + ''.join(chars_to_be_ignoreds) + ']'
        name = re.sub(pattern, '', ios)
        names = re.split('~|,|/| |{|}', name)
        valid_names = ['D' + io + str(i) for io in ['I','O'] for i in range(0,8)]
        valid_names.append('')
        for n in names:
            if n not in valid_names:
                raise ValueError('%s is not a valid Place Name.\nCheck if IOs are inside ().' %self._id)
        return
    
    def update(self, markings, consume=False):
        
        for key, value in markings.items():
            if consume:
                self.marking[key] -= value
            else:
                self.marking[key] += value

    def trigger(self, signals):
        
        for key, value in self._actions.items():
            signals[key] = value
        return signals        

    def __repr__(self):
        
        return '%s' %(self._id) 
    
    
class Transition():
    
    
    def __init__(self, parser_transition, verify_input = False):
        
        self._id       = parser_transition.attrib['id'].upper()
        timed_bool     = parser_transition.findall('.//timed')[0].findall('.//value')[0].text
        self._timed    = True if timed_bool == 'true' else False
        self._rate     = None
        if self._timed:
            self._rate     = float(parser_transition.findall('.//rate')[0].findall('.//value')[0].text)
        #self._timer    = self.process_name_timer()
        self._priority = int(parser_transition.findall('.//priority')[0].findall('.//value')[0].text)
        self._type     = 'transition'
        #DESCRIBE SENSOR CONDITION NEEDED FOR THIS TRANSITION TO BE TRIGGERED
        self._conditions = self.process_name_conditions()
        if verify_input:
            self.check_name()
        return
    
    def process_name_conditions(self):
        
        if "(" in self._id and ")" in self._id:
            ios = self._id[self._id.find("(")+1:self._id.find(")")]
        else:
            return {}
        chars_to_be_ignoreds = [' ', '-']
        pattern = '[' + ''.join(chars_to_be_ignoreds) + ']'
        name = re.sub(pattern, '', ios)
        names = name.split(",")
        dict_names = {}
        for n in names:
            listed = n.split("~")
            if len(listed) > 1:
                dict_names[listed[1]] = False
            else:
                dict_names[listed[0]] = True
        return dict_names
    
#    def process_name_timer(self):
#
#        if "{" not in self._id or "}" not in self._id:
#            return None
#        timer = self._id[self._id.find("{")+1:self._id.find("}")]
#        chars_to_be_ignoreds = [' ', '-']
#        pattern = '[' + ''.join(chars_to_be_ignoreds) + ']'
#        timer = re.sub(pattern, '', timer)
#        return float(timer)    

    def check_name(self):
        
        if "(" not in self._id or ")" not in self._id:
            raise ValueError('%s is not a valid Place Name.\nCheck if IOs are inside ().' %self._id)
        ios = self._id[self._id.find("(")+1:self._id.find(")")]
        chars_to_be_ignoreds = [' ', '-']
        pattern = '[' + ''.join(chars_to_be_ignoreds) + ']'
        name = re.sub(pattern, '', ios)
        names = re.split('~|,|/| |{|}', name)
        valid_names = ['D' + io + str(i) for io in ['I','O'] for i in range(0,8)]
        valid_names.append('')
        for n in names:
            if n not in valid_names:
                raise ValueError('%s is not a valid Place Name.\nCheck if IOs are inside ().' %self._id)
        return
    
    def __repr__(self):
        
        return '%s' %(self._id)

    
class Arc():
    
    
    def __init__(self, parser_arc, places, transitions):
        
        self._id     = parser_arc.attrib['id'].upper()
        places_transitions = places + transitions
        for i in places_transitions:
            if str(i) == parser_arc.attrib['source']:
                self._source = i
                break
        for i in places_transitions:
            if str(i) == parser_arc.attrib['target']:
                self._target = i
        insc = parser_arc.findall('.//inscription')[0].findall('.//value')[0].text
        insc = insc.split(',')
        dictionary = {}
        for i in range(len(insc)//2):
            dictionary.update({insc[2*i]:int(insc[(2*i)+1])})
        self._inscription = dictionary
        return
    
    def __repr__(self):
        
        return '%s→%s' %(self._source, self._target)
    
    
class Petrinet():
    
    
    def __init__(self, petrinet_xml_file, verify_input = False):
        
        petrinet   = ET.parse(petrinet_xml_file)
        places_xml = petrinet.findall('.//place')
        places     = []
        for place in places_xml:
            places.append(Place(place, verify_input))

        transitions_xml = petrinet.findall('.//transition')
        transitions = []
        for transition in transitions_xml:
            transitions.append(Transition(transition, verify_input))

        arcs_xml        = petrinet.findall('.//arc')
        arcs = []
        for arc in arcs_xml:
            arcs.append(Arc(arc, places, transitions))
        
        self.places      = places
        self.transitions = transitions
        self.arcs        = arcs
        
        arcs_pointing_to = {}
        for transition in transitions:
            arcs_pointing_to_transition = []
            for arc in arcs:
                if arc._target == transition:
                    arcs_pointing_to_transition.append(arc)
            arcs_pointing_to[transition] = arcs_pointing_to_transition
        self.arcs_pointing_to = arcs_pointing_to
        
        arcs_pointed_by = {}
        for transition in transitions:
            arcs_pointed_by_transition = []
            for arc in arcs:
                if arc._source == transition:
                    arcs_pointed_by_transition.append(arc)
            arcs_pointed_by[transition] = arcs_pointed_by_transition                    
        self.arcs_pointed_by = arcs_pointed_by
        return
    
    def active_transitions(self, signals):
        
        transitions = []
        for transition in self.transitions:
            # CHECK SIGNAL CONDITION IN TRANSITION:
            is_active = True
            for io, state in transition._conditions.items():
                if signals[io] != state:
                    is_active = False
                    break
            # CHECK MARKINGS CONDITION IN TRANSITION:                    
            for arc in self.arcs_pointing_to[transition]:
                for key, marking_needed in arc._inscription.items():
                    if arc._source.marking[key] < marking_needed:
                        is_active = False
                        break
            if is_active:
                transitions.append(transition)
        return transitions
    
    def activate_transition(self, signals): #, async_function=asyncio
        
        active_transitions = self.active_transitions(signals)
        ######################################################################   
        # CHECK TIMER
        ######################################################################   
        active_with_timer    = [t for t in active_transitions if t._timed]
        active_without_timer = [t for t in active_transitions if not t._timed]
        active_transitions = active_without_timer
        if not active_without_timer:
            active_transitions = active_with_timer
        
        random.shuffle(active_transitions)
        if isinstance(active_transitions, list) and len(active_transitions) > 0:
            print("Transition", active_transitions[0],"is being activated.")
            return active_transitions[0]
        return None

    def move_marks(self, signals, active_transition, set_reset):
        
        # REMOVE ON SOURCE
        for arc in self.arcs_pointing_to[active_transition]:
            arc._source.update(arc._inscription, consume=True)
        # ADD ON TARGET
        print("New Markings on: ", self.arcs_pointed_by[active_transition])
        for arc in self.arcs_pointed_by[active_transition]:
            arc._target.update(arc._inscription, consume=False)
            signals = arc._target.trigger(signals)
            print("Triggering DO: ", arc._target._actions)
        if not set_reset:
            signals = {"D"+IO+str(i): False for IO in ['I', 'O'] for i in range(0,8)}
            for place in self.places:
                if sum(place.marking.values()) > 0:
                    for io, value in place._actions.items():
                        signals[io] = value        
        return signals, {k:v for k,v in signals.items() if k.startswith('DO')}

    
class ExchangeableVariables():
    
    
    def __init__(self):
        
        self._DI  = {"DI"+str(i)   : False for i in range(0,8)}
        self._DO  = {"DO"+str(i)   : False for i in range(0,8)}
        self._address  = 'opc.tcp://127.0.0.1:12345'
        self._file_xml = '.xml'
        self._set_reset      = True
        self._running        = True
        self._connected      = False
        self._petrinet_ready = False
        self._gui_ready      = False
        self._opcua_ready    = False
        self.COLLOR_SCHEME = {True:'green', False:'red'}
        self.DI_LIST = ["DI"+str(i) for i in range(0,8)]
        self.DO_LIST = ["DO"+str(i) for i in range(0,8)]
        self.IO_LIST = ["D" + io +str(i) for io in ['I','O'] for i in range(0,8)]
        self.INIT_PRINT_TITLE = 'PetriNet -> OPC-UA [2021]'
        self.INIT_PRINT_AUTOR = 'Authors: Almirall & Godoy'
        self.INIT_PRINT_INTRODUCTION = '''Hello there! This software intends to run an OPC-UA Server from a Petri net file [.XML]. Built to control a DigitalTwin on Visual Components, it accepts files from Pipe v4.3.\n
To run it properly, we established a name pattern for Places and Transitions.
You define the IOs inside parentheses.
By default, they will be set to HIGH. To set it to LOW use ~.\n
Here are two examples:\n
P1(DO1, ~DO2)
T1(DI1,~DI2)\n
Enjoy!\n'''
        self._print_gui = print
        return

    @property
    def set_reset(self):
        return self._set_reset
    
    @set_reset.setter
    def set_reset(self, boolean):
        if (
            not isinstance(boolean, bool)
        ):
            raise ValueError('%s is not a Boolean.' %bool)
        self._set_reset = boolean
    
    @property
    def print_gui(self):
        return self._print_gui
    
    @print_gui.setter
    def print_gui(self, function):
        if (
            not callable(function)
        ):
            raise ValueError('%s is not a Function.' %function)
        self._print_gui = function
    
    @property
    def petrinet_ready(self):
        return self._petrinet_ready
    
    @petrinet_ready.setter
    def petrinet_ready(self, boolean):
        if (
            not isinstance(boolean, bool)
        ):
            raise ValueError('%s is not a Boolean.' %boolean)
        self._petrinet_ready = boolean
        
    @property
    def gui_ready(self):
        return self._gui_ready
    
    @gui_ready.setter
    def gui_ready(self, boolean):
        if (
            not isinstance(boolean, bool)
        ):
            raise ValueError('%s is not a Boolean.' %boolean)
        self._gui_ready = boolean
        
    @property
    def opcua_ready (self):
        return self._running
    
    @opcua_ready .setter
    def opcua_ready (self, boolean):
        if (
            not isinstance(boolean, bool)
        ):
            raise ValueError('%s is not a Boolean.' %boolean)
        self._opcua_ready = boolean
      
    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, boolean):
        if (
            not isinstance(boolean, bool)
        ):
            raise ValueError('%s is not a Boolean.' %boolean)
        self._running = boolean
        
    @property
    def file_xml(self):
        return self._file_xml
    
    @file_xml.setter
    def file_xml(self, filepath):
        if (
            not filepath.endswith('.xml')
        ):
            raise ValueError('%s is not a proper XML File.' %filepath)
        self._file_xml = filepath
        
    @property
    def address(self):
        return self._address
    
    @address.setter
    def address(self, opcua_address):
        if (
            not opcua_address.startswith('opc.tcp://')
        ):
            raise ValueError('%s is not a valid OPC-UA Address.' %connection)
        self._address = opcua_address
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, connection):
        if (
            not isinstance(connection, bool)
        ):
            raise ValueError('%s is not a valid Connection.' %connection)
        self._connected = connection
    
    @property
    def DI(self):
        return self._DI
    
    @DI.setter
    def DI(self, DI):
        if (
            len(DI.keys()) != 8
            or
            any([1 for di in DI.keys()   if di not in ['DI'+str(i) for i in range(0,8)]])
            or 
            any([1 for di in DI.values() if not isinstance(di, bool)])
        ):
            raise ValueError('%s is not a valid DigitalInput.' %DI)
        for k,v in DI.items():
            self._DI[k] = v
    
    @property
    def DO(self):
        return self._DO
            
    @DO.setter
    def DO(self, DO):
        if (
            len(DO.keys()) != 8
            or
            any([1 for do in DO.keys()   if do not in ['DO'+str(i) for i in range(0,8)]])
            or 
            any([1 for do in DO.values() if not isinstance(do, bool)])
        ):
            raise ValueError('%s is not a valid DigitalOutput.' %DO)
        for k,v in DO.items():
            self._DO[k] = v


def print_msg_box(msg, indent=1, width=None, title=None, print=print):
    """Print message-box with optional title."""
    lines = msg.split('\n')
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)

#!pip install nest_asyncio
#!pip install trio
import nest_asyncio
nest_asyncio.apply()

import trio
import PySimpleGUI as sg
import nest_asyncio

from opcua import Server
import datetime
import time

init_time = datetime.datetime.now()

async def petrinet_loop(variables):
    
    while not variables.gui_ready or not variables.opcua_ready:
        if not variables.gui_ready and not variables.running:
            print("Petrinet Closed")
            return
        await trio.sleep(0.0)
    petri = Petrinet(variables.file_xml)
    variables.petrinet_ready = True
    while variables.running:
        IOS = {k:v for io in [variables.DI,variables.DO] for k,v in io.items()}
        #IOS, DO = petri.net_update(IOS) #, async_function = trio
        transition = petri.activate_transition(IOS)
        
        if transition is not None:
            variables.print_gui("Activating transition: ", transition)
            if transition._timed:
                variables.print_gui("Timer starting: %d s" %transition._rate)
                await trio.sleep(transition._rate)
            IOS, DO = petri.move_marks(IOS, transition, variables.set_reset)
            variables.DO = DO
        await trio.sleep(0.0)
    print("Petrinet Closed")

async def opcua_connection(variables):

    server = Server()
    server.set_endpoint(variables.address)

    name = "OPCUA_DIGITAL_TWIN"
    addspace = server.register_namespace(name)
    
    node = server.get_objects_node()

    param = node.add_object(addspace, "Parameters")
    ###################################
    # VARIABLES ON INPUTS AND OUTPUTS #
    ###################################
    IOS_opcua = {
        DIO : param.add_variable(addspace, (DIO), False) 
        for DIO in (variables.DI_LIST + variables.DO_LIST)
    }
    for io in IOS_opcua.values():
        io.set_writable()
    server.start()
    variables.connected = True
    variables.opcua_ready = True
    variables.print_gui("Server started at {}".format(variables.address))
    variables.print_gui("At " + str(datetime.datetime.now()))
    variables.print_gui()
    DIGITAL_INPUTS = {
        DI : IOS_opcua[DI]
        for DI in variables.DI_LIST
    }
    DIGITAL_OUTPUTS = {
        DO : IOS_opcua[DO]
        for DO in variables.DO_LIST
    }
    while variables.running:
        variables.DI = {k:v.get_value() for k,v in DIGITAL_INPUTS.items()}
        for k,v in DIGITAL_OUTPUTS.items():                
            v.set_value(variables.DO[k])            
        await trio.sleep(0.0)
    print("Disconnecting.")
    server.stop()
    variables.connected = False
    print("OPC-UA Closed")

async def gui_window(variables):
    
    # p0: OPC-UA
    p0_r0_c0 = sg.T('OPC-UA Address:')
    p0_r0_c1 = sg.InputText(
          variables.address
        , size=(45, 1)
        , key='-OPCUA_ADDRESS-'
        , disabled=True
    )
    p0_r0_c2 = sg.Canvas(size=(15, 15), background_color='red', key= '-OPCUA-')
    
    # p2: PetriNet XML Browser
    p2_r0_c0 = sg.Text('_' * 80)     
    p2_r1_c0 = sg.Text('Choose a PetriNet (XML) file:', size=(35, 1))
    p2_r2_c0 = sg.Text('File', size=(15, 1), auto_size_text=False, justification='right')
    p2_r2_c1 = sg.InputText('Your File')
    p2_r2_c2 = sg.FileBrowse(file_types=(("XML Files", "*.xml"),), key="-FILE-")
    p2_r3_c0 = sg.Radio('Set/Reset', "RADIO1", default=True, key="-CHECK-")
    p2_r4_c0 = sg.Radio('High on Place', "RADIO1", default=False)
    p2_r5_c0 = sg.Text(' ' * 62)
    p2_r5_c1 = sg.Submit(tooltip='Click to submit this XML File')
    p2_r6_c0 = sg.Text('_' * 80) 
    
    # p3: IOS Signals
    p3_r0_desc  = [sg.T('    ', size=(5, 1))]
    for i in range(0,8):
        p3_r0_desc.append(sg.T(str(i)))

    p3_r1_c0  = [sg.T('DIs: ')]
    p3_r1_c   = [sg.Canvas(size=(15, 15), background_color='red', key= '-'+DI+'-') for DI in variables.DI_LIST]
    p3_r1_dis = p3_r1_c0 + p3_r1_c

    p3_r2_c0  = [sg.T('DOs: ')]
    p3_r2_c   = [sg.Canvas(size=(15, 15), background_color='red', key= '-'+DO+'-') for DO in variables.DO_LIST]
    p3_r2_dos = p3_r2_c0 + p3_r2_c    
    
    cols = [[[r0],[r1],[r2]] for r0,r1,r2 in zip(p3_r0_desc, p3_r1_dis, p3_r2_dos)]
    p3_r = [sg.Frame(layout=col, title='', border_width=0) for col in cols]

    
    # p4: LOG
    p4_r0_c0 = sg.Text('_' * 80) 
    p4_r1_c0 = sg.Multiline(
        size=(80, 25), 
        key='-OUT-', 
        font=('Courier New', 9),
        text_color='grey70',
        autoscroll=True, 
        disabled=True,
        background_color='black'
    )
    
    layout = [      
        [p0_r0_c0, p0_r0_c1, p0_r0_c2],  
        [p2_r0_c0                    ],
        [p2_r1_c0                    ],
        [p2_r2_c0, p2_r2_c1, p2_r2_c2],
        [p2_r3_c0                    ],
        [p2_r4_c0                    ],
        [p2_r5_c0, p2_r5_c1          ],
        [p2_r6_c0                    ],
        [p3_r                        ],
        [p4_r0_c0                    ],
        [p4_r1_c0                    ]
    ]
    
    window = sg.Window('Petrinet OPC-UA Control', layout, finalize=True, font=('Courier New', 9))
    print = window['-OUT-'].print
    variables.print_gui = print
    print_msg_box(
        variables.INIT_PRINT_AUTOR, 
        indent=26, 
        width=None, 
        title=variables.INIT_PRINT_TITLE, 
        print=print
    )
    print()
    print(variables.INIT_PRINT_INTRODUCTION)
    sqr     = window['-OPCUA-'].TKCanvas.create_rectangle(-1, -1, 16, 16)
    sqrs_di = [window['-'+DI+'-'].TKCanvas.create_rectangle(-1, -1, 16, 16) for DI in variables.DI_LIST]
    sqrs_do = [window['-'+DO+'-'].TKCanvas.create_rectangle(-1, -1, 16, 16) for DO in variables.DO_LIST]
    while variables.running:
        await trio.sleep(0.0)
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED: 
            window.close()
            variables.running = False
            break
        if event == 'Submit':
            variables.file_xml  = values["-FILE-"]
            variables.gui_ready = True
            variables.set_reset = values["-CHECK-"]
            print('Loading XML File:')
            print(variables.file_xml)
            print()
            if variables.set_reset:
                print('Processing PetriNet as Set/Reset.\n')
            else:
                print('Processing PetriNet as HIGH on Place.\n')
        window['-OPCUA-'].TKCanvas.itemconfig(sqr, fill=variables.COLLOR_SCHEME[variables.connected])
        for di, do, i, o in zip(sqrs_di, sqrs_do, variables.DI_LIST, variables.DO_LIST):
            window['-'+i+'-'].TKCanvas.itemconfig(di, fill=variables.COLLOR_SCHEME[variables.DI[i]])
            window['-'+o+'-'].TKCanvas.itemconfig(di, fill=variables.COLLOR_SCHEME[variables.DO[o]])
        

async def main() -> None:
    variables = ExchangeableVariables()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(gui_window, variables)
        nursery.start_soon(opcua_connection, variables)
        nursery.start_soon(petrinet_loop, variables)
        print(f"INITIALIZING {main=}.")
    print()
    print(f"CLOSING {main=}.")

trio.run(main)