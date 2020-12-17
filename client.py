#!/usr/bin/env python3

# Hydrus is released under WTFPL
# You just DO WHAT THE FUCK YOU WANT TO.
# https://github.com/sirkris/WTFPL/blob/master/WTFPL.md

try:
    
    import locale
    
    try: locale.setlocale( locale.LC_ALL, '' )
    except: pass
    
    import os
    import argparse
    import traceback
    
    from hydrus.core import HydrusBoot
    
    HydrusBoot.AddBaseDirToEnvPath()
    
    # initialise Qt here, important it is done early
    from hydrus.client.gui import QtPorting as QP
    
    from hydrus.core import HydrusConstants as HC
    from hydrus.core import HydrusPaths
    from hydrus.core import HydrusGlobals as HG
    
    argparser = argparse.ArgumentParser( description = 'hydrus network client (console)' )
    
    argparser.add_argument( '-d', '--db_dir', help = 'set an external db location' )
    argparser.add_argument( '--temp_dir', help = 'override the program\'s temporary directory' )
    argparser.add_argument( '--db_journal_mode', default = 'WAL', choices = [ 'WAL', 'TRUNCATE', 'PERSIST', 'MEMORY' ], help = 'change db journal mode (default=WAL)' )
    argparser.add_argument( '--db_synchronous_override', type = int, choices = range(4), help = 'override SQLite Synchronous PRAGMA (default=2)' )
    argparser.add_argument( '--no_db_temp_files', action='store_true', help = 'run db temp operations entirely in memory' )
    argparser.add_argument( '--boot_debug', action='store_true', help = 'print additional bootup information to the log' )
    argparser.add_argument( '--no_daemons', action='store_true', help = 'run without background daemons' )
    argparser.add_argument( '--no_wal', action='store_true', help = 'OBSOLETE: run using TRUNCATE db journaling' )
    argparser.add_argument( '--db_memory_journaling', action='store_true', help = 'OBSOLETE: run using MEMORY db journaling (DANGEROUS)' )
    
    result = argparser.parse_args()
    
    if result.db_dir is None:
        
        db_dir = HC.DEFAULT_DB_DIR
        
        if not HydrusPaths.DirectoryIsWritable( db_dir ) or HC.RUNNING_FROM_MACOS_APP:
            
            db_dir = HC.USERPATH_DB_DIR
            
        
    else:
        
        db_dir = result.db_dir
        
    
    db_dir = HydrusPaths.ConvertPortablePathToAbsPath( db_dir, HC.BASE_DIR )
    
    try:
        
        HydrusPaths.MakeSureDirectoryExists( db_dir )
        
    except:
        
        raise Exception( 'Could not ensure db path "{}" exists! Check the location is correct and that you have permission to write to it!'.format( db_dir ) )
        
    
    if not os.path.isdir( db_dir ):
        
        raise Exception( 'The given db path "{}" is not a directory!'.format( db_dir ) )
        
    
    if not HydrusPaths.DirectoryIsWritable( db_dir ):
        
        raise Exception( 'The given db path "{}" is not a writable-to!'.format( db_dir ) )
        
    
    HG.no_daemons = result.no_daemons
    
    HG.db_journal_mode = result.db_journal_mode
    
    if result.no_wal:
        
        HG.db_journal_mode = 'TRUNCATE'
        
    if result.db_memory_journaling:
        
        HG.db_journal_mode = 'MEMORY'
        
    
    if result.db_synchronous_override is not None:
        
        HG.db_synchronous = int( result.db_synchronous_override )
        
    else:
        
        if HG.db_journal_mode == 'WAL':
            
            HG.db_synchronous = 1
            
        else:
            
            HG.db_synchronous = 2
            
        
    
    HG.no_db_temp_files = result.no_db_temp_files
    
    HG.boot_debug = result.boot_debug
    
    if result.temp_dir is not None:
        
        HydrusPaths.SetEnvTempDir( result.temp_dir )
        
    
    from hydrus.core import HydrusData
    from hydrus.core import HydrusLogger
    
    try:
        
        from twisted.internet import reactor
        
    except:
        
        HG.twisted_is_broke = True
        
    
except Exception as e:
    
    try:
        
        from hydrus.core import HydrusData
        
        HydrusData.DebugPrint( 'Critical boot error occurred! Details written to crash.log!' )
        HydrusData.PrintException( e )
        
    except:
        
        pass
        
    
    error_trace = traceback.format_exc()
    
    print( error_trace )
    
    if 'db_dir' in locals() and os.path.exists( db_dir ):
        
        emergency_dir = db_dir
        
    else:
        
        emergency_dir = os.path.expanduser( '~' )
        
        possible_desktop = os.path.join( emergency_dir, 'Desktop' )
        
        if os.path.exists( possible_desktop ) and os.path.isdir( possible_desktop ):
            
            emergency_dir = possible_desktop
            
        
    
    dest_path = os.path.join( emergency_dir, 'hydrus_crash.log' )
    
    with open( dest_path, 'w', encoding = 'utf-8' ) as f:
        
        f.write( error_trace )
        
    
    print( 'Critical boot error occurred! Details written to hydrus_crash.log in either db dir or user dir!' )
    
    import sys
    
    sys.exit( 1 )
    
controller = None

with HydrusLogger.HydrusLogger( db_dir, 'client' ) as logger:
    
    try:
        
        HydrusData.Print( 'hydrus client started' )
        
        if not HG.twisted_is_broke:
            
            import threading
            
            threading.Thread( target = reactor.run, name = 'twisted', kwargs = { 'installSignalHandlers' : 0 } ).start()
            
        
        from hydrus.client import ClientController
        
        controller = ClientController.Controller( db_dir )
        
        controller.Run()
        
    except:
        
        HydrusData.Print( 'hydrus client failed' )
        
        HydrusData.Print( traceback.format_exc() )
        
    finally:
        
        HG.view_shutdown = True
        HG.model_shutdown = True
        
        if controller is not None:
            
            controller.pubimmediate( 'wake_daemons' )
            
        
        if not HG.twisted_is_broke:
            
            reactor.callFromThread( reactor.stop )
            
        
        HydrusData.Print( 'hydrus client shut down' )
        
    
HG.shutdown_complete = True

if HG.restart:
    
    HydrusData.RestartProcess()
    

