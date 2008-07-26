/* Libvoikko: Finnish spellchecker and hyphenator library
 * Copyright (C) 2008 Harri Pitkänen <hatapitk@iki.fi>
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

#include "gcerror.h"
#include "voikko_defs.h"
#include <string.h>

const char * voikko_error_message_cstr(int error_code, const char * language) {
	if (strncmp(language, "fi", 2) == 0) {
		// ä=\xc3\xa4, ö=\xc3\xb6, Ä=\xc3\x84, Ö=\xc3\x96
		switch (error_code) {
			case GCERR_WRITE_TOGETHER:
				return "Sanat on kirjoitettava yhteen.";
			case GCERR_EXTRA_WHITESPACE:
				return "Poista ylim\xc3\xa4\xc3\xa4r\xc3\xa4inen v\xc3\xa4li.";
			case GCERR_SPACE_BEFORE_PUNCTUATION:
				return "Ylim\xc3\xa4\xc3\xa4r\xc3\xa4inen v\xc3\xa4li v\xc3\xa4limerkin edess\xc3\xa4.";
			case GCERR_EXTRA_COMMA:
				return "Poista ylim\xc3\xa4\xc3\xa4r\xc3\xa4inen pilkku.";
			case GCERR_INVALID_SENTENCE_STARTER:
				return "Virheellinen virkkeen aloittava merkki.";
			case GCERR_WRITE_FIRST_LOWERCASE:
				return "Sana on kirjoitettava pienell\xc3\xa4 alkukirjaimella.";
			case GCERR_WRITE_FIRST_UPPERCASE:
				return "Sana on kirjoitettava isolla alkukirjaimella.";
		}
		return "Tuntematon virhe";
	}
	else {
		switch (error_code) {
			case GCERR_WRITE_TOGETHER:
				return "Remove space between words.";
			case GCERR_EXTRA_WHITESPACE:
				return "Remove extra space.";
			case GCERR_SPACE_BEFORE_PUNCTUATION:
				return "Remove space before punctuation.";
			case GCERR_EXTRA_COMMA:
				return "Remove extra comma.";
			case GCERR_INVALID_SENTENCE_STARTER:
				return "Invalid character at the start of a sentence.";
			case GCERR_WRITE_FIRST_LOWERCASE:
				return "Change first letter to lower case.";
			case GCERR_WRITE_FIRST_UPPERCASE:
				return "Change first letter to upper case.";
		}
		return "Unknown error";
	}
}
