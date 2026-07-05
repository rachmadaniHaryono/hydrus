import re

from hydrus.core import HydrusData
from hydrus.core import HydrusExceptions
from hydrus.core.files import HydrusFFMPEG
from hydrus.core.files import HydrusFFMPEGParsing
from hydrus.core.processes import HydrusSubprocess

def ParseFFMPEGAudio( lines ):
    
    audio_lines = HydrusFFMPEGParsing.GetAudioStreamLines( lines )
    
    audio_found = len( audio_lines ) > 0
    audio_format = 'unknown'
    
    audio_stream_mapping = '0:0'
    image_stream_mapping = None
    
    if audio_found:
        
        line = audio_lines[0]
        
        try:
            
            match = re.search(" [0-9]* Hz", line)
            
            audio_fps = int(line[match.start()+1:match.end()])
            
        except Exception as e:
            
            audio_fps = 'unknown'
            
        
        try:
            
            match = re.search( r'(?<=Audio:\s).+?(?=,)', line )
            
            audio_format = match.group()
            
        except Exception as e:
            
            audio_format = 'unknown'
            
        
        try:
            
            audio_stream_mapping = HydrusFFMPEGParsing.ParseStreamMappingFromStreamLine( line )
            
        except Exception as e:
            
            pass # default to 0:0
            
        
        video_lines = HydrusFFMPEGParsing.GetVideoStreamLines( lines )
        
        def looks_like_image_stream( line ):
            
            return 'Video: png' in line or 'Video: jpg' in line
            
        
        def looks_like_attached_pic( line ):
            
            return 'attached pic' in line or 'attached_pic' in line
            
        
        # Stream #0:1: Video: png, rgb24(pc, gbr/unknown/unknown), 300x300 [SAR 2835:2835 DAR 1:1], 90k tbr, 90k tbn (attached pic)
        image_lines = [ line for line in video_lines if looks_like_image_stream( line ) or looks_like_attached_pic( line ) ]
        
        if len( image_lines ) > 0:
            
            image_line = image_lines[0]
            
            try:
                
                image_stream_mapping = HydrusFFMPEGParsing.ParseStreamMappingFromStreamLine( image_line )
                
            except Exception as e:
                
                pass # tricky situation, let's not push it
                
            
        
    
    return ( audio_found, audio_format, audio_stream_mapping, image_stream_mapping )
    

def RenderAnyAttachedStillImageToPath( file_path, output_path ):
    
    lines = HydrusFFMPEG.GetFFMPEGInfoLines( file_path )
    
    ( audio_found, audio_format, audio_stream_mapping, image_stream_mapping ) = ParseFFMPEGAudio( lines )
    
    if image_stream_mapping is None:
        
        return False
        
    
    ffmpeg_path = HydrusFFMPEG.GetCurrentFFMPEGPath()
    
    # no dimensions here, so called is responsible for reshaping numpy array or whatever
    
    # ffmpeg -xerror -y -i m.mp3 -map 0:1 -frames:v 1 -update 1 -f image2 -c:v png output.png
    # note the "-update 1" says "keep overwriting every frame onto the output" just to suppress a warning; -frames:v 1 makes it moot
    cmd = [ ffmpeg_path, "-xerror", '-y', '-i', file_path, '-map', image_stream_mapping, '-frames:v', '1', '-update', '1', '-f', 'image2', '-c:v', 'png', output_path ]
    
    HydrusData.CheckProgramIsNotShuttingDown()
    
    try:
        
        HydrusSubprocess.RunSubprocess( cmd, timeout = HydrusFFMPEG.FFMPEG_SUBPROCESS_TIMEOUT, bufsize = 1024 * 512, text = False )
        
    except HydrusExceptions.SubprocessTimedOut:
        
        raise HydrusExceptions.DamagedOrUnusualFileException( 'ffmpeg could not render it quick enough!' )
        
    except FileNotFoundError as e:
        
        raise HydrusFFMPEG.HandleFFMPEGFileNotFoundAndGenerateException( e, file_path )
        
    
    return True
    

