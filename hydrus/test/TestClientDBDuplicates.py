import os
import time
import typing
import unittest

from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusData
from hydrus.core import HydrusNumbers

from hydrus.client import ClientConstants as CC
from hydrus.client import ClientLocation
from hydrus.client.db import ClientDB
from hydrus.client.duplicates import ClientDuplicates
from hydrus.client.duplicates import ClientPotentialDuplicatesSearchContext
from hydrus.client.importing import ClientImportFiles
from hydrus.client.importing.options import FileImportOptions
from hydrus.client.metadata import ClientContentUpdates
from hydrus.client.search import ClientSearchFileSearchContext
from hydrus.client.search import ClientSearchPredicate

from hydrus.test import TestController
from hydrus.test import TestGlobals as TG

class TestClientDBDuplicates( unittest.TestCase ):
    
    _db: typing.Any = None
    
    @classmethod
    def _clear_db( cls ):
        
        cls._delete_db()
        
        # class variable
        cls._db = ClientDB.DB( TG.test_controller, TestController.DB_DIR, 'client' )
        
    
    @classmethod
    def _delete_db( cls ):
        
        cls._db.Shutdown()
        
        while not cls._db.LoopIsFinished():
            
            time.sleep( 0.1 )
            
        
        db_filenames = list(cls._db._db_filenames.values())
        
        for filename in db_filenames:
            
            path = os.path.join( TestController.DB_DIR, filename )
            
            os.remove( path )
            
        
        del cls._db
        
    
    @classmethod
    def setUpClass( cls ):
        
        cls._db = ClientDB.DB( TG.test_controller, TestController.DB_DIR, 'client' )
        
        TG.test_controller.SetRead( 'hash_status', ClientImportFiles.FileImportStatus.STATICGetUnknownStatus() )
        
    
    @classmethod
    def tearDownClass( cls ):
        
        cls._delete_db()
        
    
    def _read( self, action, *args, **kwargs ): return TestClientDBDuplicates._db.Read( action, *args, **kwargs )
    def _write( self, action, *args, **kwargs ): return TestClientDBDuplicates._db.Write( action, True, *args, **kwargs )
    
    def _get_group_potential_count( self, file_duplicate_types_to_counts ):
        
        num_potentials = len( self._all_hashes ) - 1
        
        num_potentials -= len( self._our_main_dupe_group_hashes ) - 1
        num_potentials -= len( self._our_second_dupe_group_hashes ) - 1
        num_potentials -= len( self._our_alt_dupe_group_hashes ) - 1
        num_potentials -= len( self._our_fp_dupe_group_hashes ) - 1
        
        if HC.DUPLICATE_FALSE_POSITIVE in file_duplicate_types_to_counts:
            
            # this would not work if the fp group had mutiple alt members
            num_potentials -= file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ]
            
        
        if HC.DUPLICATE_ALTERNATE in file_duplicate_types_to_counts:
            
            num_potentials -= file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ]
            
        
        return num_potentials
        
    
    def _import_and_find_dupes( self ):
        
        perceptual_hash = os.urandom( 8 )
        
        # fake-import the files with the perceptual_hash
        
        ( size, mime, width, height, duration_ms, num_frames, has_audio, num_words ) = ( 65535, HC.IMAGE_JPEG, 640, 480, None, None, False, None )
        
        file_import_options = FileImportOptions.FileImportOptions()
        file_import_options.SetIsDefault( True )
        
        for hash in self._all_hashes:
            
            fake_file_import_job = ClientImportFiles.FileImportJob( 'fake path', file_import_options )
            
            fake_file_import_job._pre_import_file_status = ClientImportFiles.FileImportStatus( CC.STATUS_UNKNOWN, hash )
            fake_file_import_job._file_info = ( size, mime, width, height, duration_ms, num_frames, has_audio, num_words )
            fake_file_import_job._extra_hashes = ( b'abcd', b'abcd', b'abcd' )
            fake_file_import_job._perceptual_hashes = [ perceptual_hash ]
            
            self._write( 'import_file', fake_file_import_job )
            
        
        # run search maintenance
        
        self._write( 'maintain_similar_files_tree' )
        
        self._write( 'maintain_similar_files_search_for_potential_duplicates', 0 )
        
    
    def _test_initial_state( self ):
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertEqual( num_potentials, self._expected_num_potentials )
        
        result = self._read( 'random_potential_duplicate_hashes', potential_duplicates_search_context )
        
        self.assertEqual( len( result ), len( self._all_hashes ) )
        
        self.assertEqual( set( result ), self._all_hashes )
        
        filtering_pairs = self._read( 'duplicate_pairs_for_filtering', potential_duplicates_search_context )
        
        for ( a, b ) in filtering_pairs:
            
            self.assertIn( a.GetHash(), self._all_hashes )
            self.assertIn( b.GetHash(), self._all_hashes )
            
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[0] )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 1 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[0], HC.DUPLICATE_POTENTIAL )
        
        self.assertEqual( result[0], self._dupe_hashes[0] )
        
        self.assertEqual( set( result ), self._all_hashes )
        
    
    def _test_initial_better_worse( self ):
        
        row = ( HC.DUPLICATE_BETTER, self._king_hash, self._dupe_hashes[1], [ ClientContentUpdates.ContentUpdatePackage() ] )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        self._our_main_dupe_group_hashes.add( self._dupe_hashes[1] )
        
        row = ( HC.DUPLICATE_BETTER, self._dupe_hashes[1], self._dupe_hashes[2], [ ClientContentUpdates.ContentUpdatePackage() ] )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        self._our_main_dupe_group_hashes.add( self._dupe_hashes[2] )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self._num_free_agents -= 1
        
        self._expected_num_potentials -= self._num_free_agents
        
        self._num_free_agents -= 1
        
        self._expected_num_potentials -= self._num_free_agents
        
        self.assertEqual( num_potentials, self._expected_num_potentials )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[1] )
        
        self.assertEqual( result[ 'is_king' ], False )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[2] )
        
        self.assertEqual( result[ 'is_king' ], False )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[1], HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._dupe_hashes[1], self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[1], HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._dupe_hashes[1] )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[2], HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._dupe_hashes[2], self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[2], HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._dupe_hashes[2] )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
    
    def _test_initial_king_usurp( self ):
        
        self._old_king_hash = self._king_hash
        self._king_hash = self._dupe_hashes[3]
        
        row = ( HC.DUPLICATE_BETTER, self._king_hash, self._old_king_hash, {} )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        self._our_main_dupe_group_hashes.add( self._king_hash )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self._num_free_agents -= 1
        
        self._expected_num_potentials -= self._num_free_agents
        
        self.assertEqual( num_potentials, self._expected_num_potentials )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._old_king_hash )
        
        self.assertEqual( result[ 'is_king' ], False )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._old_king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._old_king_hash, self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._old_king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._old_king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
    
    def _test_initial_same_quality( self ):
        
        row = ( HC.DUPLICATE_SAME_QUALITY, self._king_hash, self._dupe_hashes[4], [ ClientContentUpdates.ContentUpdatePackage() ] )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        self._our_main_dupe_group_hashes.add( self._dupe_hashes[4] )
        
        row = ( HC.DUPLICATE_SAME_QUALITY, self._old_king_hash, self._dupe_hashes[5], [ ClientContentUpdates.ContentUpdatePackage() ] )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        self._our_main_dupe_group_hashes.add( self._dupe_hashes[5] )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self._num_free_agents -= 1
        
        self._expected_num_potentials -= self._num_free_agents
        
        self._num_free_agents -= 1
        
        self._expected_num_potentials -= self._num_free_agents
        
        self.assertEqual( num_potentials, self._expected_num_potentials )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[4] )
        
        self.assertEqual( result[ 'is_king' ], False )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[5] )
        
        self.assertEqual( result[ 'is_king' ], False )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], self._get_group_potential_count( file_duplicate_types_to_counts ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[4], HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._dupe_hashes[4], self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[4], HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._dupe_hashes[4] )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[5], HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._dupe_hashes[5], self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._dupe_hashes[5], HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._dupe_hashes[5] )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
    
    def _test_explicit_set_new_king( self ):
        
        self._write( 'duplicate_set_king', self._dupe_hashes[5] )
        
        self._king_hash = self._dupe_hashes[5]
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
    
    def _test_establish_second_group( self ):
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._second_group_king_hash, self._second_group_dupe_hashes[1], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._second_group_king_hash, self._second_group_dupe_hashes[2], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_BETTER, self._second_group_king_hash, self._second_group_dupe_hashes[3], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        self._our_second_dupe_group_hashes.add( self._second_group_dupe_hashes[1] )
        self._our_second_dupe_group_hashes.add( self._second_group_dupe_hashes[2] )
        self._our_second_dupe_group_hashes.add( self._second_group_dupe_hashes[3] )
        
    
    def _test_poach_better( self ):
        
        # better than not the king
        
        row = ( HC.DUPLICATE_BETTER, self._king_hash, self._second_group_dupe_hashes[1], [ ClientContentUpdates.ContentUpdatePackage() ] )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        self._our_second_dupe_group_hashes.discard( self._second_group_dupe_hashes[1] )
        self._our_main_dupe_group_hashes.add( self._second_group_dupe_hashes[1] )
        
        self._write( 'maintain_similar_files_search_for_potential_duplicates', 0 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        # TODO: sometimes this is 20 instead of 21
        # my guess is this is some complicated relationships due to random population of this test
        # the answer is to rewrite this monstrocity so the tests are simpler to understand and pull apart
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._second_group_king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_second_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._second_group_king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._second_group_king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._second_group_king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._second_group_king_hash )
        self.assertEqual( set( result ), self._our_second_dupe_group_hashes )
        
    
    def _test_poach_same( self ):
        
        # not the king is the same as not the king
        
        row = ( HC.DUPLICATE_SAME_QUALITY, self._old_king_hash, self._second_group_dupe_hashes[2], [ ClientContentUpdates.ContentUpdatePackage() ] )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        self._our_second_dupe_group_hashes.discard( self._second_group_dupe_hashes[2] )
        self._our_main_dupe_group_hashes.add( self._second_group_dupe_hashes[2] )
        
        self._write( 'maintain_similar_files_search_for_potential_duplicates', 0 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        # TODO: sometimes this is 20 instead of 21
        # my guess is this is some complicated relationships due to random population of this test
        # the answer is to rewrite this monstrocity so the tests are simpler to understand and pull apart
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._second_group_king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_second_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._second_group_king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._second_group_king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._second_group_king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._second_group_king_hash )
        self.assertEqual( set( result ), self._our_second_dupe_group_hashes )
        
    
    def _test_group_merge( self ):
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._dupe_hashes[6], self._dupe_hashes[7], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_BETTER, self._dupe_hashes[8], self._dupe_hashes[9], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_BETTER, self._dupe_hashes[10], self._dupe_hashes[11], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_BETTER, self._dupe_hashes[12], self._dupe_hashes[13], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._old_king_hash, self._dupe_hashes[6], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._king_hash, self._dupe_hashes[8], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_BETTER, self._old_king_hash, self._dupe_hashes[10], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_BETTER, self._king_hash, self._dupe_hashes[12], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        self._our_main_dupe_group_hashes.update( ( self._dupe_hashes[ i ] for i in range( 6, 14 ) ) )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 2 )
        
        result = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( result, result -1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_KING )
        
        self.assertEqual( result, [ self._king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_MEMBER )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), self._our_main_dupe_group_hashes )
        
    
    def _test_establish_false_positive_group( self ):
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._false_positive_king_hash, self._similar_looking_false_positive_hashes[1], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._false_positive_king_hash, self._similar_looking_false_positive_hashes[2], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        self._our_fp_dupe_group_hashes.add( self._similar_looking_false_positive_hashes[1] )
        self._our_fp_dupe_group_hashes.add( self._similar_looking_false_positive_hashes[2] )
        
    
    def _test_false_positive( self ):
        
        row = ( HC.DUPLICATE_FALSE_POSITIVE, self._king_hash, self._false_positive_king_hash, {} )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 3 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._false_positive_king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 3 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_fp_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_FALSE_POSITIVE )
        
        self.assertEqual( result, [ self._king_hash, self._false_positive_king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._false_positive_king_hash, HC.DUPLICATE_FALSE_POSITIVE )
        
        self.assertEqual( result, [ self._false_positive_king_hash, self._king_hash ] )
        
    
    def _test_establish_alt_group( self ):
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._alternate_king_hash, self._similar_looking_alternate_hashes[1], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._alternate_king_hash, self._similar_looking_alternate_hashes[2], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        self._our_alt_dupe_group_hashes.add( self._similar_looking_alternate_hashes[1] )
        self._our_alt_dupe_group_hashes.add( self._similar_looking_alternate_hashes[2] )
        
    
    def _test_alt( self ):
        
        row = ( HC.DUPLICATE_ALTERNATE, self._king_hash, self._alternate_king_hash, {} )
        
        self._write( 'duplicate_pair_status', [ row ] )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 5 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._alternate_king_hash, HC.DUPLICATE_POTENTIAL )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._alternate_king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 5 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_alt_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_ALTERNATE )
        
        self.assertEqual( result, [ self._king_hash, self._alternate_king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._alternate_king_hash, HC.DUPLICATE_ALTERNATE )
        
        self.assertEqual( result, [ self._alternate_king_hash, self._king_hash ] )
        
    
    def _test_expand_false_positive( self ):
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._false_positive_king_hash, self._similar_looking_false_positive_hashes[3], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._false_positive_king_hash, self._similar_looking_false_positive_hashes[4], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        self._our_fp_dupe_group_hashes.add( self._similar_looking_false_positive_hashes[3] )
        self._our_fp_dupe_group_hashes.add( self._similar_looking_false_positive_hashes[4] )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 5 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._false_positive_king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 3 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_fp_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 2 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_FALSE_POSITIVE )
        
        self.assertEqual( result[0], self._king_hash )
        self.assertEqual( set( result ), { self._king_hash, self._false_positive_king_hash } )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._false_positive_king_hash, HC.DUPLICATE_FALSE_POSITIVE )
        
        self.assertEqual( result[0], self._false_positive_king_hash )
        self.assertEqual( set( result ), { self._false_positive_king_hash, self._king_hash, self._alternate_king_hash } )
        
    
    def _test_expand_alt( self ):
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._alternate_king_hash, self._similar_looking_alternate_hashes[3], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        rows.append( ( HC.DUPLICATE_SAME_QUALITY, self._alternate_king_hash, self._similar_looking_alternate_hashes[4], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        max_hamming_distance = 4
        dupe_search_type = ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH
        
        potential_duplicates_search_context = ClientPotentialDuplicatesSearchContext.PotentialDuplicatesSearchContext()
        
        potential_duplicates_search_context.SetFileSearchContext1( self._file_search_context_1 )
        potential_duplicates_search_context.SetFileSearchContext2( self._file_search_context_2 )
        potential_duplicates_search_context.SetDupeSearchType( dupe_search_type )
        potential_duplicates_search_context.SetPixelDupesPreference( pixel_dupes_preference )
        potential_duplicates_search_context.SetMaxHammingDistance( max_hamming_distance )
        
        num_potentials = self._read( 'potential_duplicates_count', potential_duplicates_search_context )
        
        self.assertLess( num_potentials, self._expected_num_potentials )
        
        self._expected_num_potentials = num_potentials
        
        self._our_alt_dupe_group_hashes.add( self._similar_looking_alternate_hashes[3] )
        self._our_alt_dupe_group_hashes.add( self._similar_looking_alternate_hashes[4] )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 5 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._alternate_king_hash )
        
        self.assertEqual( result[ 'is_king' ], True )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 5 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_alt_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash, HC.DUPLICATE_ALTERNATE )
        
        self.assertEqual( result, [ self._king_hash, self._alternate_king_hash ] )
        
        result = self._read( 'file_duplicate_hashes', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._alternate_king_hash, HC.DUPLICATE_ALTERNATE )
        
        self.assertEqual( result, [ self._alternate_king_hash, self._king_hash ] )
        
    
    def _test_dissolve( self ):
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 5 )
        
        expected = self._get_group_potential_count( file_duplicate_types_to_counts )
        
        self.assertIn( file_duplicate_types_to_counts[ HC.DUPLICATE_POTENTIAL ], ( expected, expected - 1 ) )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        # remove potentials
        
        self._write( 'remove_potential_pairs', ( self._king_hash, ) )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 4 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        # remove member
        
        self._write( 'remove_duplicates_member', ( self._dupe_hashes[7], ) )
        
        self._our_main_dupe_group_hashes.discard( self._dupe_hashes[7] )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 4 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_FALSE_POSITIVE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        # clear fps
        
        self._write( 'clear_false_positive_relations', ( self._king_hash, ) )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 3 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        # remove alt
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_ALTERNATE, self._king_hash, self._false_positive_king_hash, [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 3 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 2 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 2 )
        
        self._write( 'remove_alternates_member', ( self._false_positive_king_hash, ) )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 3 )
        
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_MEMBER ], len( self._our_main_dupe_group_hashes ) - 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_ALTERNATE ], 1 )
        self.assertEqual( file_duplicate_types_to_counts[ HC.DUPLICATE_CONFIRMED_ALTERNATE ], 1 )
        
        # dissolve alt
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_ALTERNATE, self._king_hash, self._false_positive_king_hash, [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        self._write( 'dissolve_alternates_group', ( self._king_hash, ) )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 0 )
        
        # dissolve group
        
        rows = []
        
        rows.append( ( HC.DUPLICATE_BETTER, self._king_hash, self._dupe_hashes[1], [ ClientContentUpdates.ContentUpdatePackage() ] ) )
        
        self._write( 'duplicate_pair_status', rows )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 1 )
        
        self._write( 'dissolve_duplicates_group', ( self._king_hash, ) )
        
        result = self._read( 'file_duplicate_info', ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY ), self._king_hash )
        
        file_duplicate_types_to_counts = result[ 'counts' ]
        
        self.assertEqual( len( file_duplicate_types_to_counts ), 0 )
        
    
    def test_duplicates( self ):
        
        self._dupe_hashes = [ HydrusData.GenerateKey() for i in range( 16 ) ]
        self._second_group_dupe_hashes = [ HydrusData.GenerateKey() for i in range( 4 ) ]
        self._similar_looking_alternate_hashes = [ HydrusData.GenerateKey() for i in range( 5 ) ]
        self._similar_looking_false_positive_hashes = [ HydrusData.GenerateKey() for i in range( 5 ) ]
        
        self._all_hashes = set()
        
        self._all_hashes.update( self._dupe_hashes )
        self._all_hashes.update( self._second_group_dupe_hashes )
        self._all_hashes.update( self._similar_looking_alternate_hashes )
        self._all_hashes.update( self._similar_looking_false_positive_hashes )
        
        self._king_hash = self._dupe_hashes[0]
        self._second_group_king_hash = self._second_group_dupe_hashes[0]
        self._false_positive_king_hash = self._similar_looking_false_positive_hashes[0]
        self._alternate_king_hash = self._similar_looking_alternate_hashes[0]
        
        self._our_main_dupe_group_hashes = { self._king_hash }
        self._our_second_dupe_group_hashes = { self._second_group_king_hash }
        self._our_alt_dupe_group_hashes = { self._alternate_king_hash }
        self._our_fp_dupe_group_hashes = { self._false_positive_king_hash }
        
        n = len( self._all_hashes )
        
        self._num_free_agents = n
        
        # initial number pair combinations is (n(n-1))/2
        self._expected_num_potentials = int( n * ( n - 1 ) / 2 )
        
        size_pred = ClientSearchPredicate.Predicate( ClientSearchPredicate.PREDICATE_TYPE_SYSTEM_SIZE, ( '=', 65535, HydrusNumbers.UnitToInt( 'B' ) ) )
        png_pred = ClientSearchPredicate.Predicate( ClientSearchPredicate.PREDICATE_TYPE_SYSTEM_MIME, ( HC.IMAGE_PNG, ) )
        
        location_context = ClientLocation.LocationContext.STATICCreateSimple( CC.LOCAL_FILE_SERVICE_KEY )
        
        self._file_search_context_1 = ClientSearchFileSearchContext.FileSearchContext( location_context = location_context, predicates = [ size_pred ] )
        self._file_search_context_2 = ClientSearchFileSearchContext.FileSearchContext( location_context = location_context, predicates = [ png_pred ] )
        
        self._import_and_find_dupes()
        
        self._test_initial_state()
        
        self._test_initial_better_worse()
        self._test_initial_king_usurp()
        self._test_initial_same_quality()
        
        self._test_explicit_set_new_king()
        
        self._test_establish_second_group()
        self._test_poach_better()
        self._test_poach_same()
        self._test_group_merge()
        
        self._test_establish_false_positive_group()
        self._test_false_positive()
        
        self._test_establish_alt_group()
        self._test_alt()
        
        self._test_expand_false_positive()
        self._test_expand_alt()
        
        self._test_dissolve()
        
    
