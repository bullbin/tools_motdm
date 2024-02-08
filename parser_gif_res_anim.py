from madhatter.hat_io.binary import BinaryReader
from PIL.Image import Image as ImageType
from PIL import Image
from typing import List, Tuple, Optional
from io import BytesIO

from os import path

class FrameRawData():
    def __init__(self, name : str, data : bytes):
        self.__decoded : bool = False
        self.__name : str = name
        self.__data : BytesIO = BytesIO(data)
        self.__decoded_image : Optional[ImageType] = None

    def get_image(self) -> Optional[ImageType]:
        if self.__decoded:
            return self.__decoded_image

        self.__decoded = True
        
        try:
            self.__decoded_image = Image.open(self.__data)
        except Exception as e:
            self.__decoded_image = None
        
        return self.__decoded_image
    
    def __str__(self) -> str:
        return self.__name

class FrameChunk():
    def __init__(self, frame_ref : FrameRawData, offset : Tuple[int,int], dimensions : Tuple[int,int]):
        self.__frame_ref = frame_ref
        self.__frame_subsection : Optional[ImageType] = None
        self.__offset = offset
        self.__dimensions = dimensions
    
    def __str__(self) -> str:
        return "Chunk %s %s from %s" % (self.__offset, self.__dimensions, self.__frame_ref)

    def get_subsection(self) -> Optional[ImageType]:
        if self.__frame_subsection != None:
            return self.__frame_subsection
        
        image = self.__frame_ref.get_image()
        if image == None:
            return None
        
        self.__frame_subsection = image.crop((self.__offset[0], self.__offset[1],
                                              self.__offset[0] + self.__dimensions[0], self.__offset[1] + self.__dimensions[1])).convert("RGBA")
        
        # TODO - This will return black if out of bounds
        return self.__frame_subsection

class FrameFromSegmentedChunks():
    def __init__(self, frame_params : List[int]):
        self.__decoded : bool = False
        self.__decoded_image : Optional[ImageType] = None
        self.__unk = frame_params[-1]
        
        self.__parts_bank : List[List[int]] = []
        for idx_group in range(len(frame_params) // 3):
            self.__parts_bank.append(frame_params[(idx_group * 3):((idx_group + 1) * 3)])
    
    def get_unk(self) -> int:
        return self.__unk
    
    def get_decoded_frame(self, frame_chunks : List[FrameChunk]) -> Optional[ImageType]:
        if self.__decoded:
            return self.__decoded_image
        
        self.__decoded = True

        output_size_x = 0
        output_size_y = 0

        for part in self.__parts_bank:
            idx_chunk = part[0]
            p_x = part[1]
            p_y = part[2]

            if idx_chunk >= len(frame_chunks):
                print("Chunk out of bounds...")
                continue
            
            chunk = frame_chunks[idx_chunk].get_subsection()
            if chunk == None:
                print("Chunk", idx_chunk, "failed decoding...")
                continue

            output_size_x = max(output_size_x, p_x + chunk.size[0])
            output_size_y = max(output_size_y, p_y + chunk.size[1])
        
        if output_size_x == 0 or output_size_y == 0:
            return None

        self.__decoded_image = Image.new("RGBA", (output_size_x, output_size_y))
        
        for part in self.__parts_bank:
            idx_chunk = part[0]
            p_x = part[1]
            p_y = part[2]

            if idx_chunk >= len(frame_chunks):
                continue
            
            chunk = frame_chunks[idx_chunk].get_subsection()
            if chunk == None:
                continue

            self.__decoded_image.alpha_composite(chunk, (p_x, p_y))
        
        return self.__decoded_image

def generate_spritesheet(reader : BinaryReader, path_output : str) -> bool:

    frames : List[FrameRawData] = []
    parts_bank : List[FrameChunk] = []
    anim_bank : List[List[FrameFromSegmentedChunks]] = []

    def decode_obj_block(reader : BinaryReader):
        offset_after_chunk = reader.readU32() + reader.tell()

        while reader.tell() < offset_after_chunk:
            
            name_chunk = reader.readPaddedString(reader.readU16(), 'ascii')
            if name_chunk == "parts":
                count_parts = reader.readU32()
                for idx in range(count_parts):
                    chunk_bank = reader.readU32List(5)
                    # TODO - Might not be able to do this out of order
                    parts_bank.append(FrameChunk(frames[chunk_bank[0]], (chunk_bank[1], chunk_bank[2]), (chunk_bank[3], chunk_bank[4])))
                
            elif name_chunk == "animation":
                for idx_anim in range(reader.readU32()):
                    anim_bank.append([])
                
                for idx_anim, arr_anim in enumerate(anim_bank):
                    count_mb_frame = reader.readU32()

                    for idx_frame in range(count_mb_frame):
                        arr_frame : List[int] = []

                        mb_count_parts = reader.readU32()
                        len_section = mb_count_parts * 3
                        arr_frame.extend([0] * len_section)

                        for idx_part in range(mb_count_parts):
                            for idx_data in range(3):
                                arr_frame[idx_part * 3 + idx_data] = reader.readU32()
                        
                        arr_frame.append(reader.readU32())
                        arr_anim.append(FrameFromSegmentedChunks(arr_frame))
            else:
                break

    if reader.read(3) != b'res':
        return False
    
    offset_after_anim = reader.readU32() + reader.tell()
    count_frames = reader.readU32()

    for idx_frame in range(count_frames):
        f_name = reader.readPaddedString(reader.readU16(), 'ascii')
        f_data = reader.read(reader.readU32())
        frames.append(FrameRawData(f_name, f_data))

    reader.seek(offset_after_anim)

    if reader.read(3) == b'obj':
        decode_obj_block(reader)
    
    # Decode all frames
    max_size_x = 0
    max_size_y = 0
    max_frame_count = 0

    for anim in anim_bank:
        for frame in anim:
            image = frame.get_decoded_frame(parts_bank)
            if image != None:
                max_size_x = max(max_size_x, image.size[0])
                max_size_y = max(max_size_y, image.size[1])
        
        max_frame_count = max(max_frame_count, len(anim))
    
    tilemap_size_x = int(max_size_x * max_frame_count)
    tilemap_size_y = int(max_size_y * len(anim_bank))

    debug = Image.new("RGBA", (tilemap_size_x, tilemap_size_y))
    p_x = 0
    p_y = 0
    for anim in anim_bank:
        p_x = 0
        for frame in anim:
            image = frame.get_decoded_frame(parts_bank)
            if image != None:
                debug.alpha_composite(image, (p_x, p_y))
            
            p_x += max_size_x
        p_y += max_size_y
    
    debug.save(path_output)

    return True

PATH_ANIM = r"assets\deathmirror\c06.dat"

reader = BinaryReader(filename=PATH_ANIM)
generate_spritesheet(reader, path.splitext(path.split(PATH_ANIM)[1])[0] + ".png")