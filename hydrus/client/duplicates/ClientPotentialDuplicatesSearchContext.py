import collections
import random
import typing

from hydrus.core import HydrusSerialisable
from hydrus.core import HydrusLists

from hydrus.client import ClientConstants as CC
from hydrus.client import ClientGlobals as CG
from hydrus.client import ClientLocation
from hydrus.client.duplicates import ClientDuplicates
from hydrus.client.media import ClientMediaResult

from hydrus.client.search import ClientSearchFileSearchContext
from hydrus.client.search import ClientSearchPredicate

POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE = 4096

class PotentialDuplicateIdPairsAndDistances( object ):
    
    def __init__( self, potential_id_pairs_and_distances: collections.abc.Collection[ tuple[ int, int, int ] ] ):
        
        self._potential_id_pairs_and_distances = list( potential_id_pairs_and_distances )
        
        self._media_ids_to_other_media_ids_and_distances = collections.defaultdict( list )
        self._mapping_initialised = False
        
    
    def __len__( self ):
        
        return len( self._potential_id_pairs_and_distances )
        
    
    def _InitialiseMapping( self ):
        
        for ( smaller_media_id, larger_media_id, distance ) in self._potential_id_pairs_and_distances:
            
            self._media_ids_to_other_media_ids_and_distances[ smaller_media_id ].append( ( larger_media_id, distance ) )
            self._media_ids_to_other_media_ids_and_distances[ larger_media_id ].append( ( smaller_media_id, distance ) )
            
        
        self._mapping_initialised = True
        
    
    def Duplicate( self ) -> "PotentialDuplicateIdPairsAndDistances":
        
        return PotentialDuplicateIdPairsAndDistances( self._potential_id_pairs_and_distances )
        
    
    def FilterWiderPotentialGroup( self, media_id ):
        
        # ok, the caller wants to process a 'whole group' of similar files all at once, so let's get them all. recall that merging a pair merges peasant potentials to the king too
        # given this file (of a pair), what are all the other pairs this file has? what are all the potentials those other files have? keep searching until the whole network is mapped
        
        if not self._mapping_initialised:
            
            self._InitialiseMapping()
            
        
        searched = set()
        still_to_search = [ media_id ]
        rows_found = []
        
        while len( still_to_search ) > 0:
            
            search_media_id = still_to_search.pop()
            
            searched.add( search_media_id )
            
            for ( result_media_id, distance ) in self._media_ids_to_other_media_ids_and_distances[ search_media_id ]:
                
                if result_media_id in searched:
                    
                    continue
                    
                
                rows_found.append( ( min( search_media_id, result_media_id ), max( search_media_id, result_media_id ), distance ) )
                
                still_to_search.append( result_media_id )
                
            
        
        return PotentialDuplicateIdPairsAndDistances( rows_found )
        
    
    def IterateBlocks( self ):
        
        for block in HydrusLists.SplitListIntoChunks( self._potential_id_pairs_and_distances, POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE ):
            
            yield PotentialDuplicateIdPairsAndDistances( block )
            
        
    
    def IteratePairs( self ):
        
        for ( smaller_media_id, larger_media_id, distance ) in self._potential_id_pairs_and_distances:
            
            yield ( smaller_media_id, larger_media_id )
            
        
    
    def GetPairs( self ) -> list[ tuple[ int, int ] ]:
        
        return [ ( smaller_media_id, larger_media_id ) for ( smaller_media_id, larger_media_id, distance ) in self._potential_id_pairs_and_distances ]
        
    
    def GetPairListsBySmallestDistanceFirst( self ) -> list[ list[ tuple[ int, int ] ] ]:
        
        distance_to_pairs = collections.defaultdict( list )
        
        for ( smaller_media_id, larger_media_id, distance ) in self._potential_id_pairs_and_distances:
            
            distance_to_pairs[ distance ].append( ( smaller_media_id, larger_media_id ) )
            
        
        distances = sorted( distance_to_pairs.keys() )
        
        return [ distance_to_pairs[ distance ] for distance in distances ]
        
    
    def GetRows( self ):
        
        return list( self._potential_id_pairs_and_distances )
        
    
    def IterateRows( self ):
        
        return self._potential_id_pairs_and_distances.__iter__()
        
    
    def PopBlock( self, block_size = None ):
        
        if block_size is None:
            
            block_size = POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE
            
        
        block_of_id_pairs_and_distances = self._potential_id_pairs_and_distances[ : block_size ]
        
        self._potential_id_pairs_and_distances = self._potential_id_pairs_and_distances[ block_size : ]
        
        self._mapping_initialised = False
        
        return PotentialDuplicateIdPairsAndDistances( block_of_id_pairs_and_distances )
        
    
    def RandomiseBlocks( self ):
        
        self._potential_id_pairs_and_distances = HydrusLists.RandomiseListByChunks( self._potential_id_pairs_and_distances, POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE )
        
    

class PotentialDuplicateMediaResultPairsAndDistances( object ):
    
    def __init__( self, potential_media_result_pairs_and_distances: collections.abc.Collection[ tuple[ ClientMediaResult.MediaResult, ClientMediaResult.MediaResult, int ] ] ):
        
        self._potential_media_result_pairs_and_distances = list( potential_media_result_pairs_and_distances )
        
    
    def __len__( self ):
        
        return len( self._potential_media_result_pairs_and_distances )
        
    
    def AppendRow( self, row ):
        
        self._potential_media_result_pairs_and_distances.append( row )
        
    
    def Duplicate( self ) -> "PotentialDuplicateMediaResultPairsAndDistances":
        
        return PotentialDuplicateMediaResultPairsAndDistances( self._potential_media_result_pairs_and_distances )
        
    
    def IterateBlocks( self ):
        
        for block in HydrusLists.SplitListIntoChunks( self._potential_media_result_pairs_and_distances, POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE ):
            
            yield PotentialDuplicateMediaResultPairsAndDistances( block )
            
        
    
    def IteratePairs( self ):
        
        for ( media_result_1, media_result_2, distance ) in self._potential_media_result_pairs_and_distances:
            
            yield ( media_result_1, media_result_2 )
            
        
    
    def IterateRows( self ):
        
        return self._potential_media_result_pairs_and_distances.__iter__()
        
    
    def GetPairs( self ) -> list[ tuple[ ClientMediaResult.MediaResult, ClientMediaResult.MediaResult ] ]:
        
        return [ ( media_result_1, media_result_2 ) for ( media_result_1, media_result_2, distance ) in self._potential_media_result_pairs_and_distances ]
        
    
    def GetRows( self ):
        
        return list( self._potential_media_result_pairs_and_distances )
        
    
    def PopBlock( self ):
        
        block_of_media_result_pairs_and_distances = self._potential_media_result_pairs_and_distances[ : POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE ]
        
        self._potential_media_result_pairs_and_distances = self._potential_media_result_pairs_and_distances[ POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE : ]
        
        return PotentialDuplicateMediaResultPairsAndDistances( block_of_media_result_pairs_and_distances )
        
    
    def RandomiseBlocks( self ):
        
        self._potential_media_result_pairs_and_distances = HydrusLists.RandomiseListByChunks( self._potential_media_result_pairs_and_distances, POTENTIAL_DUPLICATE_PAIRS_BLOCK_SIZE )
        
    
    def Sort( self, duplicate_pair_sort_type: int, sort_asc: bool ):
        
        handle_invalid = lambda i: 1 if i is None or i == 0 else i
        
        if duplicate_pair_sort_type == ClientDuplicates.DUPE_PAIR_SORT_SIMILARITY:
            
            def sort_key( row: tuple[ ClientMediaResult.MediaResult, ClientMediaResult.MediaResult, int ] ):
                
                ( m_r_1, m_r_2, distance ) = row
                
                m_r_1_size = handle_invalid( m_r_1.GetSize() )
                m_r_2_size = handle_invalid( m_r_2.GetSize() )
                
                return ( distance, max( m_r_1_size, m_r_2_size ) / min( m_r_1_size, m_r_2_size ) )
                
            
        elif duplicate_pair_sort_type == ClientDuplicates.DUPE_PAIR_SORT_MAX_FILESIZE:
            
            def sort_key( row: tuple[ ClientMediaResult.MediaResult, ClientMediaResult.MediaResult, int ] ):
                
                ( m_r_1, m_r_2, distance ) = row
                
                m_r_1_size = handle_invalid( m_r_1.GetSize() )
                m_r_2_size = handle_invalid( m_r_2.GetSize() )
                
                return ( max( m_r_1_size, m_r_2_size ), min( m_r_1_size, m_r_2_size ) )
                
            
        elif duplicate_pair_sort_type == ClientDuplicates.DUPE_PAIR_SORT_MIN_FILESIZE:
            
            # what I would like auto-resolution to hook into, but I think it isn't easy to wangle
            
            def sort_key( row: tuple[ ClientMediaResult.MediaResult, ClientMediaResult.MediaResult, int ] ):
                
                ( m_r_1, m_r_2, distance ) = row
                
                m_r_1_size = handle_invalid( m_r_1.GetSize() )
                m_r_2_size = handle_invalid( m_r_2.GetSize() )
                
                return ( min( m_r_1_size, m_r_2_size ), max( m_r_1_size, m_r_2_size ) )
                
            
        elif duplicate_pair_sort_type == ClientDuplicates.DUPE_PAIR_SORT_RANDOM:
            
            random.shuffle( self._potential_media_result_pairs_and_distances )
            
            return
            
        else:
            
            raise NotImplementedError( 'Did not understand that duplicate sort!' )
            
        
        self._potential_media_result_pairs_and_distances.sort( key = sort_key )
        
        if not sort_asc:
            
            self._potential_media_result_pairs_and_distances.reverse()
            
        
    

class PotentialDuplicatesSearchContext( HydrusSerialisable.SerialisableBase ):
    
    SERIALISABLE_TYPE = HydrusSerialisable.SERIALISABLE_TYPE_POTENTIAL_DUPLICATES_SEARCH_CONTEXT
    SERIALISABLE_NAME = 'Potential Duplicates Search Context'
    SERIALISABLE_VERSION = 1
    
    def __init__( self, location_context: typing.Optional[ ClientLocation.LocationContext ] = None, initial_predicates = None ):
        
        if location_context is None:
            
            try:
                
                location_context = CG.client_controller.new_options.GetDefaultLocalLocationContext()
                
            except:
                
                location_context = ClientLocation.LocationContext.STATICCreateSimple( CC.COMBINED_LOCAL_MEDIA_SERVICE_KEY )
                
            
        
        if initial_predicates is None:
            
            initial_predicates = [ ClientSearchPredicate.Predicate( ClientSearchPredicate.PREDICATE_TYPE_SYSTEM_EVERYTHING ) ]
            
        
        file_search_context = ClientSearchFileSearchContext.FileSearchContext( location_context = location_context, predicates = initial_predicates )
        
        self._file_search_context_1 = file_search_context
        self._file_search_context_2 = file_search_context.Duplicate()
        self._dupe_search_type = ClientDuplicates.DUPE_SEARCH_ONE_FILE_MATCHES_ONE_SEARCH
        self._pixel_dupes_preference = ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_ALLOWED
        self._max_hamming_distance = 4
        
    
    def __eq__( self, other ):
        
        if isinstance( other, PotentialDuplicatesSearchContext ):
            
            return self.GetSerialisableTuple() == other.GetSerialisableTuple()
            
        
        return NotImplemented
        
    
    def _GetSerialisableInfo( self ):
        
        serialisable_file_search_context_1 = self._file_search_context_1.GetSerialisableTuple()
        serialisable_file_search_context_2 = self._file_search_context_2.GetSerialisableTuple()
        
        return ( serialisable_file_search_context_1, serialisable_file_search_context_2, self._dupe_search_type, self._pixel_dupes_preference, self._max_hamming_distance )
        
    
    def _InitialiseFromSerialisableInfo( self, serialisable_info ):
        
        ( serialisable_file_search_context_1, serialisable_file_search_context_2, self._dupe_search_type, self._pixel_dupes_preference, self._max_hamming_distance ) = serialisable_info
        
        self._file_search_context_1 = HydrusSerialisable.CreateFromSerialisableTuple( serialisable_file_search_context_1 )
        self._file_search_context_2 = HydrusSerialisable.CreateFromSerialisableTuple( serialisable_file_search_context_2 )
        
    
    def GetDupeSearchType( self ) -> int:
        
        return self._dupe_search_type
        
    
    def GetFileSearchContext1( self ) -> ClientSearchFileSearchContext.FileSearchContext:
        
        return self._file_search_context_1
        
    
    def GetFileSearchContext2( self ) -> ClientSearchFileSearchContext.FileSearchContext:
        
        return self._file_search_context_2
        
    
    def GetMaxHammingDistance( self ) -> int:
        
        return self._max_hamming_distance
        
    
    def GetPixelDupesPreference( self ) -> int:
        
        return self._pixel_dupes_preference
        
    
    def GetSummary( self ) -> str:
        
        if self._dupe_search_type == ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_DIFFERENT_SEARCHES:
            
            search_string = f'files matching [{self._file_search_context_1.GetSummary()}] and [{self._file_search_context_2.GetSummary()}]'
            
        elif self._dupe_search_type == ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH:
            
            search_string = f'both files matching [{self._file_search_context_1.GetSummary()}]'
            
        else:
            
            search_string = f'one file matching [{self._file_search_context_1.GetSummary()}]'
            
        
        pixel_dupes_string = ''
        
        if self._pixel_dupes_preference == ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_REQUIRED:
            
            pixel_dupes_string = ', pixel duplicates'
            
        elif self._pixel_dupes_preference == ClientDuplicates.SIMILAR_FILES_PIXEL_DUPES_EXCLUDED:
            
            pixel_dupes_string = ', not pixel duplicates'
            
        
        return search_string + pixel_dupes_string
        
    
    def OptimiseForSearch( self ):
        
        if self._dupe_search_type == ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_ONE_SEARCH and ( self._file_search_context_1.IsJustSystemEverything() or self._file_search_context_1.HasNoPredicates() ):
            
            self._dupe_search_type = ClientDuplicates.DUPE_SEARCH_ONE_FILE_MATCHES_ONE_SEARCH
            
        elif self._dupe_search_type == ClientDuplicates.DUPE_SEARCH_BOTH_FILES_MATCH_DIFFERENT_SEARCHES:
            
            if self._file_search_context_1.IsJustSystemEverything() or self._file_search_context_1.HasNoPredicates():
                
                f = self._file_search_context_1
                self._file_search_context_1 = self._file_search_context_2
                self._file_search_context_2 = f
                
                self._dupe_search_type = ClientDuplicates.DUPE_SEARCH_ONE_FILE_MATCHES_ONE_SEARCH
                
            elif self._file_search_context_2.IsJustSystemEverything() or self._file_search_context_2.HasNoPredicates():
                
                self._dupe_search_type = ClientDuplicates.DUPE_SEARCH_ONE_FILE_MATCHES_ONE_SEARCH
                
            
        
    
    def SetDupeSearchType( self, value: int ):
        
        self._dupe_search_type = value
        
    
    def SetFileSearchContext1( self, value: ClientSearchFileSearchContext ):
        
        self._file_search_context_1 = value
        
    
    def SetFileSearchContext2( self, value : ClientSearchFileSearchContext ):
        
        self._file_search_context_2 = value
        
    
    def SetMaxHammingDistance( self, value : int ):
        
        self._max_hamming_distance = value
        
    
    def SetPixelDupesPreference( self, value : int ):
        
        self._pixel_dupes_preference = value
        
    

HydrusSerialisable.SERIALISABLE_TYPES_TO_OBJECT_TYPES[ HydrusSerialisable.SERIALISABLE_TYPE_POTENTIAL_DUPLICATES_SEARCH_CONTEXT ] = PotentialDuplicatesSearchContext
