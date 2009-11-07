/* Copyright (C) 1995 Bjoern Beutel. */

/* Description. =============================================================*/

/* This module contains structures and functions for the run-time lexicon. */

/* Includes. ================================================================*/

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "morphology/malaga/basic.hpp"
#include "morphology/malaga/pools.hpp"
#include "morphology/malaga/values.hpp"
#include "morphology/malaga/tries.hpp"
#include "morphology/malaga/files.hpp"
#include "morphology/malaga/malaga_files.hpp"
#include "morphology/malaga/lexicon.hpp"
#include "morphology/malaga/MalagaState.hpp"

namespace libvoikko { namespace morphology { namespace malaga {

/* Functions. ===============================================================*/

void 
search_for_prefix(string_t string, trie_search_state & state, MalagaState * malagaState)
/* Search lexicon for prefixes of STRING in increasing length. 
 * The results are obtained by calling "get_next_prefix". */
{
  state.trie_node = malagaState->lexicon.trie_root;
  state.prefix_end = string;
  state.feat_list_index = -1;
}

/*---------------------------------------------------------------------------*/

bool 
get_next_prefix(string_t *string_p, value_t *feat, trie_search_state & state, MalagaState * malagaState)
/* Get the next lexicon entry that is a prefix of STRING. 
 * Return false iff no more entries exist.
 * If another entry exists, set *STRING_P to the remainder of STRING
 * and *FEAT to the feature structure assigned to the lexicon entry.
 * STRING must have been set by "search_for_prefix". */
{
  if (state.feat_list_index == -1) 
    lookup_trie(malagaState->lexicon.trie, &state.trie_node, &state.prefix_end, &state.feat_list_index);
  if (state.feat_list_index == -1) 
    return false;
  int_t feat_index = malagaState->lexicon.feat_lists[state.feat_list_index++];
  if (feat_index < 0) 
  { 
    state.feat_list_index = -1;
    feat_index = - feat_index - 1;
  }
  *string_p = state.prefix_end;
  *feat = malagaState->lexicon.values + feat_index;
  return true;
}

/*---------------------------------------------------------------------------*/

void 
init_lexicon(string_t file_name, MalagaState * malagaState)
/* Initialise this module. Read lexicon from file FILE_NAME. */
{ 
  lexicon_header_t *header; /* Lexicon file header. */

  /* Map the lexicon file into memory. */
  map_file( file_name, &(malagaState->lexicon.lexicon_data), &(malagaState->lexicon.lexicon_length));

  /* Check lexicon header. */
  header = (lexicon_header_t *) malagaState->lexicon.lexicon_data;
  check_header( &header->common_header, file_name, LEXICON_FILE,
                MIN_LEXICON_CODE_VERSION, LEXICON_CODE_VERSION );
  
  /* Init trie. */
  malagaState->lexicon.trie = (int_t *) (header + 1);
  malagaState->lexicon.trie_root = header->trie_root;

  /* Init feature structure lists. */
  malagaState->lexicon.feat_lists = (int_t *) (malagaState->lexicon.trie + header->trie_size);

  /* Init values. */
  malagaState->lexicon.values = (cell_t *) (malagaState->lexicon.feat_lists + header->feat_lists_size);
}

/*---------------------------------------------------------------------------*/

void 
terminate_lexicon(MalagaState * malagaState)
/* Terminate this module. */
{ 
  unmap_file(&(malagaState->lexicon.lexicon_data), malagaState->lexicon.lexicon_length);
}

}}}
