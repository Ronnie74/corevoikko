/* Libvoikko: Finnish spellchecker and hyphenator library
 * Copyright (C) 2006 Harri Pitkänen <hatapitk@iki.fi>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *********************************************************************************/

#ifndef VOIKKO_UTILS_H
#define VOIKKO_UTILS_H

#include <stddef.h>

#ifdef DEBUG
#define LOG(x) printf x
#else
#define LOG(X)
#endif

#define VOIKKO_CONSONANTS L"bcdfghjklmnpqrstvwxz\u0161\u017e"
#define VOIKKO_VOWELS L"aeiouy\u00e4\u00f6"

enum casetype {CT_NO_LETTERS, CT_ALL_LOWER, CT_FIRST_UPPER, CT_COMPLEX, CT_ALL_UPPER};

wchar_t * voikko_cstrtoucs4(const char * word, const char * encoding);

char * voikko_ucs4tocstr(const wchar_t * word, const char * encoding);

/** Simple string hashing algorithm
 * @param word string to hash
 * @param len length of the word
 * @param order order of the resulting hash value
 * @return integer from range [0, 2^order - 1]
 */
int voikko_hash(const wchar_t * word, size_t len, int order);

/** Returns the type of given string wrt the use of character cases.
 * @param word string to check
 * @param nchars length of the string
 * @return character case type of the string
 */
enum casetype voikko_casetype(const wchar_t * word, size_t nchars);

#endif
