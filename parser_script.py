from madhatter.hat_io.binary import BinaryReader
from typing import Callable, Dict

def parse_cmd_load_data(reader : BinaryReader):
    count_entries = reader.readUInt(1)
    entries = []
    for idx in range(count_entries):
        len_entry = reader.readUInt(1)
        entry = reader.read(len_entry)
        entry = entry.decode('ascii')
        entries.append(entry)
    print("LoadData   " + ', '.join(entries))

def parse_cmd_add_event(reader : BinaryReader):
    unk_0_type = reader.readUInt(1)
    unk_1 = reader.readS16()
    unk_2 = reader.readUInt(1)
    unk_3 = reader.readUInt(1)
    unk_4 = reader.readS16()
    unk_5 = reader.readS16()
    unk_6_len = reader.readS16()
    unk_string = reader.readPaddedString(unk_6_len, 'shift-jis')
    if unk_0_type == 4:
        unk_7 = reader.readUInt(1)
        unk_8 = reader.readUInt(1)
        print("LoadEvent ", unk_0_type, unk_1, unk_2, unk_3, unk_4, unk_5, unk_string, unk_7, unk_8)
    else:
        print("LoadEvent ", unk_0_type, unk_1, unk_2, unk_3, unk_4, unk_5, unk_string)

def parse_cmd_add_bg_obj(reader : BinaryReader):
    idx_obj = reader.readUInt(1)
    mb_px = reader.readS16()
    mb_py = reader.readS16()
    print("addBGObj  ", idx_obj, "->", (mb_px, mb_py))

def parse_cmd_set_obj_flip(reader : BinaryReader):
    idx_obj = reader.readUInt(1)
    print("setObjFlip", idx_obj)

def parse_cmd_if(reader : BinaryReader):
    id_cond = reader.readUInt(1)
    cond_unk_invert_check = reader.readUInt(1) == 1
    
    cond_type = reader.readUInt(1)
    cond_arg = reader.readS16()

    if cond_type <= 4:
        # if == 0, unk = value
        # if == 1, unk < value
        # if == 2, unk > value
        # if == 3, unk <= value
        # if == 4, unk >= value
        pass
    elif cond_type == 5:
        if cond_arg == 0:
            pass
        else:
            pass
        pass
    elif cond_type == 6:
        pass
    elif cond_type == 7:
        pass
    elif cond_type == 8:
        pass
    elif cond_type == 10:
        pass
    elif cond_type == 11:
        pass
    elif cond_type == 12:
        pass
    elif cond_type == 13:
        pass
    elif cond_type == 14:
        pass
    elif cond_type == 15:
        pass
    elif cond_type == 16:
        pass

    print("if        ", id_cond, cond_unk_invert_check, cond_type, cond_arg)

def parse_cmd_cevent(reader : BinaryReader):
    unk = reader.readS16()

    print("CEvent    ", unk)

def parse_cmd_endif(reader : BinaryReader):
    id_cond = reader.readUInt(1)
    print("endif     ", id_cond)

def parse_cmd_else(reader : BinaryReader):
    id_cond = reader.readUInt(1)
    print("else      ", id_cond)

def parse_cmd_text_window(reader : BinaryReader):
    unk_0 = reader.readUInt(1)
    char = reader.readUInt(1)
    len_str = reader.readS16()
    
    unk_string = reader.readPaddedString(len_str, 'shift-jis')
    print("TextWindow", unk_0, "Chr_%d" % char, unk_string)

def parse_cmd_add_exit(reader : BinaryReader):
    unk_0 = reader.readUInt(1)
    unk_1 = reader.readUInt(1)
    unk_2 = reader.readUInt(1)
    p_x = reader.readS16()
    p_y = reader.readS16()
    unk_5 = reader.readUInt(1)
    print("addExit   ", unk_0, unk_1, unk_2, (p_x, p_y), unk_5)

def parse_cmd_wait(reader : BinaryReader):
    unk_timing = reader.readUInt(1)
    print("Wait      ", unk_timing)

def parse_cmd_fade_in(reader : BinaryReader):
    unk_timing_gated = reader.readUInt(1)
    print("FadeIn    ", unk_timing_gated)

def parse_cmd_fade_out(reader : BinaryReader):
    unk_timing_gated = reader.readUInt(1)
    print("FadeOut   ", unk_timing_gated)

def parse_cmd_set_bg(reader : BinaryReader):
    idx_bg = reader.readUInt(1)
    print("SetBG     ", "room_%02d.jpg" % idx_bg)

def parse_cmd_play_sound(reader : BinaryReader):
    unk_0 = reader.readUInt(1)
    unk_string = reader.readPaddedString(reader.readUInt(1), 'shift-jis')
    unk_1 = reader.readUInt(1) == 1
    print("PlaySound ", unk_0, unk_string, unk_1)

def parse_cmd_play_r_sound(reader : BinaryReader):
    unk_0 = reader.readUInt(1)
    unk_string = reader.readPaddedString(reader.readUInt(1), 'shift-jis')
    unk_1 = reader.readUInt(1) == 1
    print("PlayRSound", unk_0, unk_string, unk_1)

def parse_cmd_add_sprite(reader : BinaryReader):
    unk_0 = reader.readUInt(1)
    p_x = reader.readU16()
    p_y = reader.readU16()
    unk_1 = reader.readUInt(1)
    print("AddSprite ", unk_0, unk_1, (p_x, p_y))

def parse_cmd_change_ani(reader : BinaryReader):
    unk_0 = reader.readUInt(1)
    unk_1 = reader.readUInt(1)
    print("ChangeAni ", unk_0, unk_1)

map_dict_to_function : Dict[str, Callable[[BinaryReader], None]] = {"LoadData"      : parse_cmd_load_data,
                                                                    "addEvent"      : parse_cmd_add_event,
                                                                    "addBGObj"      : parse_cmd_add_bg_obj,
                                                                    "setObjFlip"    : parse_cmd_set_obj_flip,
                                                                    "if"            : parse_cmd_if,
                                                                    "CEvent"        : parse_cmd_cevent,
                                                                    "endif"         : parse_cmd_endif,
                                                                    "else"          : parse_cmd_else,
                                                                    "addExit"       : parse_cmd_add_exit,
                                                                    "TextWindow"    : parse_cmd_text_window,
                                                                    "Wait"          : parse_cmd_wait,
                                                                    "FadeIn"        : parse_cmd_fade_in,
                                                                    "FadeOut"       : parse_cmd_fade_out,
                                                                    "SetBG"         : parse_cmd_set_bg,
                                                                    "PlaySound"     : parse_cmd_play_sound,
                                                                    "PlayRSound"    : parse_cmd_play_r_sound,
                                                                    "AddSprite"     : parse_cmd_add_sprite,
                                                                    "ChangeAni"     : parse_cmd_change_ani}

PATH_MOTDM_SCRIPT = r"assets\deathmirror\room_01.dat"
PATH_MOTDM_SCRIPT = r"assets\deathmirror\event_000.dat"
PATH_MOTDM_SCRIPT = r"assets\deathmirror\event_001.dat"

reader = BinaryReader(filename=PATH_MOTDM_SCRIPT)

while reader.hasDataRemaining():
    opcode = reader.readPaddedString(10, 'ascii', "\x20")
    length = reader.readU16()
    target_next_off = reader.tell() + length
    if opcode in map_dict_to_function:
        map_dict_to_function[opcode](reader)
    else:
        print("<UNK>", opcode + (" " * (10 - len(opcode))), reader.read(length).hex())
    
    if reader.tell() != target_next_off:
        print("Warning: Incorrect offset, last %s consumed incorrect length by %d. Re-aligned." % (opcode, target_next_off - reader.tell()))
        reader.seek(target_next_off)